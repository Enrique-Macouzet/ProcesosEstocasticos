"""
modulos/enumeracion_exhaustiva.py
Interfaz para Enumeración Exhaustiva de políticas.
"""

import streamlit as st
import pandas as pd
from algoritmos.exhaustiva import generar_politicas, enumeracion_exhaustiva
from guardado.sesion import get_mdp, mdp_completo

def _subindice(i):
    subs = "₀₁₂₃₄₅₆₇₈₉"
    return ''.join(subs[int(d)] for d in str(i))

st.set_page_config(page_title="Enumeración Exhaustiva — MDP", page_icon="🔍")

mdp = get_mdp()

st.markdown("""
<style>
.policy-box {
    background: #111827;
    border: 1px solid #1E2A3A;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
}
.policy-optimal {
    border-left: 4px solid #F5A800;
    background: #0f1a24;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom:1.5rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#F5A800;letter-spacing:.15em;margin-bottom:.4rem;">MÓDULO 03</div>
    <h1 style="font-family:'Sora',sans-serif;font-weight:700;font-size:1.8rem;color:#E8EAF0;margin:0;">Enumeración Exhaustiva</h1>
    <p style="color:#8FA0B8;font-size:.9rem;margin:.4rem 0 0 0;">Evalúa todas las políticas deterministas y encuentra la óptima.</p>
</div>
""", unsafe_allow_html=True)

if not mdp_completo():
    st.warning("El modelo no está completo. Ve al módulo de Ingreso de Datos para finalizarlo.")
    st.stop()

estados = mdp["estados"]
decisiones_data = mdp["decisiones_data"]
tipo = mdp["tipo"]

politicas = generar_politicas(estados, decisiones_data)
if not politicas:
    st.error("No se pueden generar políticas: algún estado no tiene decisiones aplicables.")
    st.stop()

politicas_dict = {}
for i, pol in enumerate(politicas):
    nombre = f"R{i+1}"
    politicas_dict[nombre] = pol

st.markdown("### Políticas disponibles")
cols = st.columns(4)
for i, (nombre, pol) in enumerate(politicas_dict.items()):
    with cols[i % 4]:
        texto = ", ".join([f"{s}:{d}" for s, d in pol.items()])
        st.markdown(f'<span class="chip chip-gold" style="margin:4px;">{nombre}: {texto}</span>', unsafe_allow_html=True)

st.markdown("---")

st.markdown("### Seleccionar políticas a evaluar")
opciones = list(politicas_dict.keys())
seleccionadas = st.multiselect(
    "Elige una o más políticas (si no seleccionas ninguna, se evaluarán todas)",
    options=opciones,
    default=opciones   # Todas seleccionadas por defecto
)

politicas_a_evaluar = []
if seleccionadas:
    for nombre in seleccionadas:
        politicas_a_evaluar.append(politicas_dict[nombre])
else:
    politicas_a_evaluar = politicas

mostrar_detalles = st.checkbox("Mostrar cálculos detallados (Gauss-Jordan y pasos intermedios)", value=False)

if st.button("Ejecutar Enumeración Exhaustiva", type="primary"):
    with st.spinner("Evaluando políticas..."):
        mejor, resultados = enumeracion_exhaustiva(
            estados, decisiones_data, tipo,
            politicas_seleccionadas=politicas_a_evaluar
        )

    if mejor is None:
        st.error("No se pudo evaluar ninguna política.")
    else:
        st.success("Evaluación completada.")

        st.markdown("## Política Óptima")
        nombre_optimo = [k for k, v in politicas_dict.items() if v == mejor["politica"]][0]
        st.markdown(f"""
        <div class="policy-box policy-optimal">
            <span style="color:#F5A800; font-weight:700;">{nombre_optimo}</span><br>
            {", ".join([f"{s} → {d}" for s, d in mejor["politica"].items()])}
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Valor esperado", f"{mejor['esperado']:.6f}")
        with col2:
            st.metric("Tipo de modelo", "Costos (minimizar)" if tipo == "costos" else "Ganancias (maximizar)")

        st.markdown("#### Probabilidades estacionarias (π)")
        pi_df = pd.DataFrame.from_dict(mejor["pi"], orient="index", columns=["π"])
        st.dataframe(pi_df, use_container_width=True)

        st.markdown("---")
        st.markdown("### Políticas evaluadas")

        if tipo == "costos":
            resultados_ordenados = sorted(resultados, key=lambda x: x["esperado"])
        else:
            resultados_ordenados = sorted(resultados, key=lambda x: x["esperado"], reverse=True)

        for res in resultados_ordenados:
            nombre = [k for k, v in politicas_dict.items() if v == res["politica"]][0]
            is_optimal = (res == mejor)
            border_style = "border-left: 4px solid #F5A800;" if is_optimal else ""

            with st.expander(f"{nombre} — Esperado: {res['esperado']:.6f}" + (" (ÓPTIMA)" if is_optimal else "")):
                st.markdown(f"""
                <div style="{border_style} padding-left: 1rem;">
                    <p><b>Decisiones:</b> {", ".join([f"{s} → {d}" for s, d in res["politica"].items()])}</p>
                </div>
                """, unsafe_allow_html=True)

                tab1, tab2, tab3, tab4 = st.tabs(["Matriz de Transición", "Sistema de Ecuaciones", "Probabilidades π", "Costo Esperado"])

                with tab1:
                    st.dataframe(res["P"], use_container_width=True)

                with tab2:
                    for linea in res["sistema"]:
                        st.markdown(f"`{linea}`")

                with tab3:
                    pi_df = pd.DataFrame.from_dict(res["pi"], orient="index", columns=["π"])
                    st.dataframe(pi_df, use_container_width=True)

                with tab4:
                    st.markdown(f"**Costo esperado:** `{res['esperado']:.6f}`")
                    expr = " + ".join([f"({res['c'][s]:.4f})·({res['pi'][s]:.4f})" for s in estados])
                    st.markdown(f"E = {expr} = {res['esperado']:.6f}")

                if mostrar_detalles and res.get("gauss_steps"):
                    with st.expander("🔍 Ver pasos de Gauss‑Jordan"):
                        for desc, matriz in res["gauss_steps"]:
                            st.markdown(f"**{desc}**")
                            cols = [f"π{_subindice(i)}" for i in range(len(estados))] + ["b"]
                            df_matriz = pd.DataFrame(matriz, columns=cols)
                            st.dataframe(df_matriz, use_container_width=True)
