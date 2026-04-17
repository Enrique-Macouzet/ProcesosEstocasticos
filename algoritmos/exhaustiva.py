"""
algoritmos/exhaustiva.py
Enumeración Exhaustiva de políticas deterministas.
Incluye generación de políticas, evaluación vía sistema de ecuaciones estacionarias
(resuelto por Gauss-Jordan) y cálculo de costo/recompensa esperado.
"""

import itertools
import pandas as pd
from fractions import Fraction

def _subindice(i):
    """Convierte un número entero en subíndice Unicode."""
    subs = "₀₁₂₃₄₅₆₇₈₉"
    return ''.join(subs[int(d)] for d in str(i))

def generar_politicas(estados, decisiones_data):
    """
    Genera todas las políticas deterministas posibles.
    Para cada estado, se listan las decisiones que lo afectan.
    Retorna una lista de diccionarios {estado: decision}.
    """
    opciones_por_estado = {}
    for s in estados:
        opciones = []
        for d, data in decisiones_data.items():
            if s in data.get("estados_afectados", []):
                opciones.append(d)
        if not opciones:
            return []
        opciones_por_estado[s] = opciones

    claves = estados
    valores = [opciones_por_estado[s] for s in estados]
    politicas = []
    for combo in itertools.product(*valores):
        politicas.append(dict(zip(claves, combo)))
    return politicas

def evaluar_politica(politica, estados, decisiones_data, tipo="costos"):
    """
    Evalúa una política determinista.
    Retorna un diccionario con resultados y pasos intermedios.
    """
    n = len(estados)
    P = [[0.0]*n for _ in range(n)]
    c = [0.0]*n
    idx = {s: i for i, s in enumerate(estados)}

    for s in estados:
        i = idx[s]
        d = politica[s]
        data = decisiones_data[d]
        c[i] = data["costos"].get(s, 0.0)
        trans = data["transiciones"].get(s, {})
        for s2, prob in trans.items():
            j = idx[s2]
            P[i][j] = prob

    # Sistema de ecuaciones con subíndices
    sistema_str = []
    for j in range(n-1):
        terminos = []
        for i in range(n):
            if P[i][j] != 0:
                terminos.append(f"({P[i][j]:.4f})π{_subindice(i)}")
        ec = " + ".join(terminos) if terminos else "0"
        sistema_str.append(f"π{_subindice(j)} = {ec}")
    sistema_str.append(" + ".join([f"π{_subindice(i)}" for i in range(n)]) + " = 1")

    # Construir sistema cuadrado
    A_square = []
    b_square = []
    for j in range(n-1):
        fila = []
        for i in range(n):
            if i == j:
                fila.append(P[i][j] - 1.0)
            else:
                fila.append(P[i][j])
        A_square.append(fila)
        b_square.append(0.0)
    A_square.append([1.0]*n)
    b_square.append(1.0)

    def to_frac(x):
        return Fraction(x).limit_denominator(1000000)

    M = []
    for i in range(n):
        fila = [to_frac(A_square[i][j]) for j in range(n)] + [to_frac(b_square[i])]
        M.append(fila)

    pasos_gauss = []
    def guardar_estado(descripcion):
        matriz_actual = [[float(M[i][j]) for j in range(n+1)] for i in range(n)]
        pasos_gauss.append((descripcion, matriz_actual))

    guardar_estado("Matriz aumentada inicial")

    for col in range(n):
        max_row = col
        for row in range(col+1, n):
            if abs(M[row][col]) > abs(M[max_row][col]):
                max_row = row
        if max_row != col:
            M[col], M[max_row] = M[max_row], M[col]
            guardar_estado(f"Intercambio fila {col+1} ↔ fila {max_row+1}")

        pivote = M[col][col]
        if pivote == 0:
            raise ValueError("Matriz singular")
        for j in range(n+1):
            M[col][j] /= pivote
        guardar_estado(f"Fila {col+1} dividida por {float(pivote):.4f}")

        for row in range(n):
            if row != col:
                factor = M[row][col]
                if factor != 0:
                    for j in range(n+1):
                        M[row][j] -= factor * M[col][j]
                    guardar_estado(f"Fila {row+1} ← fila {row+1} - ({float(factor):.4f})·fila {col+1}")

    pi = [float(M[i][n]) for i in range(n)]
    esperado = sum(pi[i] * c[i] for i in range(n))

    P_df = pd.DataFrame(P, index=estados, columns=estados)

    return {
        "politica": politica,
        "P": P_df,
        "c": dict(zip(estados, c)),
        "sistema": sistema_str,
        "pi": dict(zip(estados, pi)),
        "esperado": esperado,
        "gauss_steps": pasos_gauss,
    }

def enumeracion_exhaustiva(estados, decisiones_data, tipo="costos", politicas_seleccionadas=None):
    if politicas_seleccionadas is not None:
        politicas = politicas_seleccionadas
    else:
        politicas = generar_politicas(estados, decisiones_data)

    if not politicas:
        return None, []

    resultados = []
    for pol in politicas:
        res = evaluar_politica(pol, estados, decisiones_data, tipo)
        resultados.append(res)

    if tipo == "costos":
        mejor = min(resultados, key=lambda x: x["esperado"])
    else:
        mejor = max(resultados, key=lambda x: x["esperado"])

    return mejor, resultados
