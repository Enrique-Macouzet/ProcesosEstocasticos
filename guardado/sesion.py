"""
guardado/sesion.py
Manejo del estado global del MDP durante la sesion de Streamlit.
Estructura centrada en decisiones con datos anidados.
"""

import streamlit as st

ESTADO_INICIAL = {
    "estados": [],
    "decisiones": [],
    "tipo": "costos",          # "costos" o "recompensas"
    "decisiones_data": {}
    # decisiones_data[d] = {
    #   "estados_afectados": [...],
    #   "costos": {estado: valor},
    #   "transiciones": {estado_origen: {estado_destino: probabilidad}}
    # }
}

def init_session():
    """Inicializa la estructura del MDP en st.session_state si no existe."""
    if "mdp" not in st.session_state:
        st.session_state.mdp = {
            "estados": [],
            "decisiones": [],
            "tipo": "costos",
            "decisiones_data": {}
        }

def get_mdp():
    """Retorna el diccionario completo del MDP."""
    init_session()
    return st.session_state.mdp

def reset_mdp():
    """Reinicia completamente el modelo (borra todos los datos)."""
    if "mdp" in st.session_state:
        del st.session_state.mdp
    init_session()

def mdp_completo():
    """
    Verifica si el MDP tiene la informacion minima para ejecutar algoritmos.
    - Existen estados y decisiones.
    - Cada decision tiene al menos un estado afectado.
    - Para cada estado afectado, la suma de probabilidades de transicion es 1.
    - Cada estado afectado tiene un costo/recompensa asignado.
    """
    mdp = get_mdp()
    if not mdp["estados"] or not mdp["decisiones"]:
        return False

    for d, data in mdp["decisiones_data"].items():
        afectados = data.get("estados_afectados", [])
        if not afectados:
            return False
        for s in afectados:
            # Verificar costos
            if s not in data.get("costos", {}):
                return False
            # Verificar transiciones
            probs = data.get("transiciones", {}).get(s, {})
            if not probs:
                return False
            total = sum(probs.values())
            if abs(total - 1.0) > 1e-6:
                return False
    return True

# ----------------------------------------------------------------------
# Funciones auxiliares para modificar el estado de manera segura
# ----------------------------------------------------------------------

def agregar_estado(nombre: str):
    """Agrega un nuevo estado si no existe."""
    mdp = get_mdp()
    if nombre and nombre not in mdp["estados"]:
        mdp["estados"].append(nombre)

def agregar_decision(nombre: str):
    """Agrega una nueva decision y su estructura asociada."""
    mdp = get_mdp()
    if nombre and nombre not in mdp["decisiones"]:
        mdp["decisiones"].append(nombre)
        mdp["decisiones_data"][nombre] = {
            "estados_afectados": [],
            "costos": {},
            "transiciones": {}
        }

def eliminar_estado(nombre: str):
    """Elimina un estado y limpia referencias en todas las decisiones."""
    mdp = get_mdp()
    if nombre in mdp["estados"]:
        mdp["estados"].remove(nombre)
        for d, data in mdp["decisiones_data"].items():
            if nombre in data["estados_afectados"]:
                data["estados_afectados"].remove(nombre)
            data["costos"].pop(nombre, None)
            data["transiciones"].pop(nombre, None)
            for origen in data["transiciones"]:
                data["transiciones"][origen].pop(nombre, None)

def eliminar_decision(nombre: str):
    """Elimina una decision y todos sus datos asociados."""
    mdp = get_mdp()
    if nombre in mdp["decisiones"]:
        mdp["decisiones"].remove(nombre)
        mdp["decisiones_data"].pop(nombre, None)

def set_estados_afectados(decision: str, estados: list):
    """Asigna la lista de estados a los que aplica una decision."""
    mdp = get_mdp()
    if decision in mdp["decisiones_data"]:
        mdp["decisiones_data"][decision]["estados_afectados"] = estados

def set_costo(estado: str, decision: str, valor: float):
    """Guarda el costo/recompensa de aplicar una decision en un estado."""
    mdp = get_mdp()
    if decision in mdp["decisiones_data"]:
        mdp["decisiones_data"][decision]["costos"][estado] = valor

def set_transicion(origen: str, decision: str, destino: str, probabilidad: float):
    """Establece la probabilidad de transicion desde 'origen' a 'destino' dada una decision."""
    mdp = get_mdp()
    if decision in mdp["decisiones_data"]:
        trans = mdp["decisiones_data"][decision]["transiciones"]
        if origen not in trans:
            trans[origen] = {}
        trans[origen][destino] = probabilidad
