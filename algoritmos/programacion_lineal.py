"""
algoritmos/programacion_lineal.py
Implementación del método de Programación Lineal para MDPs.

La notación Y_{ik} representa la probabilidad conjunta de estar en el estado i
y tomar la decisión k. El modelo se resuelve con scipy.optimize.linprog (método HiGHS).
"""

import numpy as np
from scipy.optimize import linprog
import pandas as pd

def _subindice(num_str):
    """Convierte una cadena numérica en subíndice Unicode (ej. '0' → '₀', '10' → '₁₀')."""
    subs = "₀₁₂₃₄₅₆₇₈₉"
    return ''.join(subs[int(d)] for d in str(num_str))

def _var_str(estado, decision):
    """Cadena Y_{estado,decisión} con subíndices (ej. Y₀₁)."""
    return f"Y{_subindice(estado)}{_subindice(decision)}"

def _prob_str(origen, destino, decision):
    """Cadena P_{origen,destino}(decisión) (ej. P₀₁(d₁))."""
    return f"P{_subindice(origen)}{_subindice(destino)}({decision})"

def construir_modelo_pl(estados, decisiones_data, tipo="costos"):
    """
    Construye el modelo de programación lineal.
    Retorna:
        c (list): Coeficientes de la función objetivo.
        A_eq (list of list): Matriz de restricciones de igualdad.
        b_eq (list): Lados derechos de las igualdades.
        bounds (list): Tuplas de cotas (0, None) para cada variable.
        variables (list of tuples): Lista de pares (estado, decisión) de cada variable.
        idx_map (dict): Mapeo (estado, decisión) → índice de variable.
    """
    # --- Lista de variables Y_{i,k} ---
    variables = []          # (estado, decision)
    idx_map = {}            # (estado, decision) -> índice
    for s in estados:
        for d, data in decisiones_data.items():
            if s in data.get("estados_afectados", []):
                idx = len(variables)
                variables.append((s, d))
                idx_map[(s, d)] = idx

    n_vars = len(variables)
    if n_vars == 0:
        raise ValueError("No hay variables: ningún estado tiene decisiones asignadas.")

    # --- Vector de costos c ---
    c = []
    for s, d in variables:
        costo = decisiones_data[d]["costos"].get(s, 0.0)
        c.append(costo)

    # Si es ganancias, linprog minimiza => multiplicar por -1
    if tipo == "ganancias":
        c = [-x for x in c]

    # --- Restricciones de igualdad ---
    A_eq = []
    b_eq = []

    # 1. Normalización: Σ Y_{ik} = 1
    A_eq.append([1.0] * n_vars)
    b_eq.append(1.0)

    # 2. Balance para cada estado excepto el último
    idx_estado = {s: i for i, s in enumerate(estados)}
    ultimo_estado = estados[-1]

    for s in estados:
        if s == ultimo_estado:
            continue
        fila = [0.0] * n_vars
        # Σ_k Y_{s,k}
        for d in decisiones_data:
            if (s, d) in idx_map:
                fila[idx_map[(s, d)]] = 1.0
        # - Σ_{j,l} Y_{j,l} · P(s | j,l)
        for (j, l), idx in idx_map.items():
            prob = decisiones_data[l]["transiciones"].get(j, {}).get(s, 0.0)
            if prob > 0:
                fila[idx] -= prob
        A_eq.append(fila)
        b_eq.append(0.0)

    # --- Cotas: Y >= 0 ---
    bounds = [(0, None) for _ in range(n_vars)]

    return c, A_eq, b_eq, bounds, variables, idx_map

def resolver_pl(estados, decisiones_data, tipo="costos"):
    """
    Resuelve el modelo de PL y retorna resultados más información textual para la UI.

    Returns:
        dict con claves:
            exito (bool)
            mensaje (str)
            valor_optimo (float)
            variables_y (dict)
            D (DataFrame)
            politica (dict)
            modelo (dict) con:
                funcion_objetivo, formula_general, restricciones_completas,
                restricciones_sin_ceros, restricciones_desarrollo,
                normalizacion, no_negatividad
    """
    c, A_eq, b_eq, bounds, variables, idx_map = construir_modelo_pl(estados, decisiones_data, tipo)

    # Resolver con linprog (método HiGHS, simplex/interior-point)
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    if not res.success:
        return {
            "exito": False,
            "mensaje": res.message,
            "valor_optimo": None,
            "variables_y": {},
            "D": None,
            "politica": {},
            "modelo": None
        }

    y_vals = res.x
    valor_optimo = res.fun if tipo == "costos" else -res.fun

    # --- Variables Y_{ik} ---
    variables_y = {}
    for (s, d), idx in idx_map.items():
        variables_y[(s, d)] = y_vals[idx]

    # --- Coeficientes D_{ik} = Y_{ik} / Σ_k Y_{ik} ---
    D = {}
    for s in estados:
        suma = sum(variables_y.get((s, d), 0.0) for d in decisiones_data if (s, d) in idx_map)
        for d in decisiones_data:
            if (s, d) in idx_map:
                D[(s, d)] = variables_y[(s, d)] / suma if suma > 1e-12 else 0.0

    # --- Política determinista (decisión con mayor D por estado) ---
    politica = {}
    for s in estados:
        mejor_d = None
        mejor_val = -1
        for d in decisiones_data:
            if (s, d) in D and D[(s, d)] > mejor_val:
                mejor_val = D[(s, d)]
                mejor_d = d
        if mejor_d is not None:
            politica[s] = mejor_d

    # ========== CONSTRUCCIÓN DE TEXTOS PARA LA UI ==========
    # --- Función objetivo (incluye todos los términos, incluso coeficiente 0) ---
    if tipo == "costos":
        objetivo = "Minimizar Z = "
    else:
        objetivo = "Maximizar Z = "
    terminos_obj = []
    for idx, (s, d) in enumerate(variables):
        coef = decisiones_data[d]["costos"].get(s, 0.0)
        var = _var_str(s, d)
        if idx == 0:
            pref = "" if coef >= 0 else "-"
        else:
            pref = "+ " if coef >= 0 else "- "
        if abs(coef) == 1:
            terminos_obj.append(f"{pref}{var}")
        else:
            terminos_obj.append(f"{pref}{abs(coef):g}{var}")
    objetivo += " ".join(terminos_obj)

    # --- Fórmula general (LaTeX) ---
    formula_general = (
        r"\sum_{k=1}^{K} Y_{ik} - \sum_{i=0}^{m} \sum_{k=1}^{k} "
        r"Y_{ik} \cdot P_{ij}(k) = 0"
    )

    # --- Restricciones (tres niveles) ---
    restricciones_completas = []   # todos los términos, incluso prob=0
    restricciones_sin_ceros = []   # eliminando términos con prob=0
    restricciones_desarrollo = []  # coeficientes numéricos finales
    ultimo_estado = estados[-1]

    for idx_fila, s in enumerate(estados):
        if s == ultimo_estado:
            continue

        # Positivos (siempre los mismos)
        positivos = [d for d in decisiones_data if (s, d) in idx_map]
        pos_str = " + ".join([_var_str(s, d) for d in positivos])

        # --- Todos los negativos (incluso prob=0) ---
        todos_neg = []
        for (j, l) in variables:
            prob = decisiones_data[l]["transiciones"].get(j, {}).get(s, 0.0)
            todos_neg.append((j, l, prob))
        neg_str_completa = " - (" + " + ".join([
            f"{_var_str(j, l)}·{_prob_str(j, s, l)}"
            for j, l, _ in todos_neg
        ]) + ")"
        ec_completa = f"{pos_str}{neg_str_completa} = 0"
        restricciones_completas.append(ec_completa)

        # --- Sin ceros (prob > 0) ---
        neg_sin_ceros = [(j, l, prob) for (j, l, prob) in todos_neg if prob > 0]
        if neg_sin_ceros:
            neg_str_sin = " - (" + " + ".join([
                f"{_var_str(j, l)}·{_prob_str(j, s, l)}"
                for j, l, _ in neg_sin_ceros
            ]) + ")"
        else:
            neg_str_sin = ""
        ec_sin_ceros = f"{pos_str}{neg_str_sin} = 0"
        restricciones_sin_ceros.append(ec_sin_ceros)

        # --- Desarrollo (coeficientes numéricos) ---
        fila = A_eq[1 + idx_fila]  # A_eq[0] es normalización
        terminos_des = []
        for jdx, coef in enumerate(fila):
            if abs(coef) > 1e-12:
                s2, d2 = variables[jdx]
                var = _var_str(s2, d2)
                if coef == 1:
                    terminos_des.append(("+ " if terminos_des else "") + var)
                elif coef == -1:
                    terminos_des.append(f"- {var}")
                else:
                    if not terminos_des:
                        terminos_des.append(f"{coef:g}{var}")
                    else:
                        terminos_des.append(f"+ {coef:g}{var}")
        ec_des = " ".join(terminos_des) + " = 0"
        restricciones_desarrollo.append(ec_des)

    # --- Normalización y no negatividad ---
    norm = " + ".join([_var_str(s, d) for (s, d) in variables]) + " = 1"
    no_neg = ", ".join([_var_str(s, d) for (s, d) in variables]) + " ≥ 0"

    modelo_info = {
        "funcion_objetivo": objetivo,
        "formula_general": formula_general,
        "restricciones_completas": restricciones_completas,
        "restricciones_sin_ceros": restricciones_sin_ceros,
        "restricciones_desarrollo": restricciones_desarrollo,
        "normalizacion": norm,
        "no_negatividad": no_neg,
        "variables": variables
    }

    return {
        "exito": True,
        "mensaje": res.message,
        "valor_optimo": valor_optimo,
        "variables_y": variables_y,
        "D": pd.DataFrame([
            (s, d, D.get((s, d), 0.0))
            for s in estados
            for d in decisiones_data
            if (s, d) in idx_map
        ], columns=["Estado", "Decisión", "D"]).pivot(index="Estado", columns="Decisión", values="D"),
        "politica": politica,
        "modelo": modelo_info
    }
