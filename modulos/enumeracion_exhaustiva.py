"""
modulos/enumeracion_exhaustiva.py
Interfaz para la Enumeración Exhaustiva de políticas deterministas.

Permite:
- Visualizar todas las políticas disponibles como chips.
- Seleccionar manualmente cuáles políticas evaluar (por defecto todas).
- Ejecutar la evaluación con un botón, mostrando progreso.
- Mostrar la política óptima y sus detalles.
- Listar todas las políticas evaluadas en cajas expandibles, con pestañas para:
    * Matriz de transición
    * Sistema de ecuaciones estacionarias
    * Probabilidades π
    * Costo / Ganancia esperado
- Mostrar pasos de Gauss‑Jordan (opcional).
- Manejar políticas sin solución (matriz singular) mostrando mensaje adecuado.
- Incluir una sección final de análisis comparativo con tabla, gráfico de barras
  y resumen estadístico de las políticas válidas.
"""

import streamlit as st
import pandas as pd
from algoritmos.exhaustiva import generar_politicas, enumeracion_exhaustiva
from guardado.sesion import get_mdp, mdp_completo

def _subindice(i):
    """Convierte un número entero en subíndice Unicode (π₀, π₁, ...)."""
    subs = "₀₁₂₃₄₅₆₇₈₉"
    return ''.join(subs[int(d)] for d in str(i))

st.set_page_config(page_title="Enumeración Exhaustiva — MDP", page_icon="🔍")

mdp = get_mdp()

# ---------- ESTILOS ----------
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

# ---------- ENCABEZADO ----------
st.markdown("""
<div style="margin-bottom:1.5rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#F5A800;letter-spacing:.15em;margin-bottom:.4rem;">MÓDULO 03</div>
    <h1 style="font-family:'Sora',sans-serif;font-weight:700;font-size:1.8rem;color:#E8EAF0;margin:0;">Enumeración Exhaustiva</h1>
    <p style="color:#8FA0B8;font-size:.9rem;margin:.4rem 0 0 0;">Evalúa todas las políticas deterministas y encuentra la óptima.</p>
</div>
""", unsafe_allow_html=True)

# Verificar que el modelo esté completo
if not mdp_completo():
    st.warning("El modelo no está completo. Ve al módulo de Ingreso de Datos para finalizarlo.")
    st.stop()

estados = mdp["estados"]
decisiones_data = mdp["decisiones_data"]
tipo = mdp["tipo"]

# Generar todas las políticas posibles (producto cartesiano)
politicas = generar_politicas(estados, decisiones_data)
if not politicas:
    st.error("No se pueden generar políticas: algún estado no tiene decisiones aplicables.")
    st.stop()

# Crear diccionario de nombres legibles R1, R2, ...
politicas_dict = {}
for i, pol in enumerate(politicas):
    nombre = f"R{i+1}"
    politicas_dict[nombre] = pol

# Mostrar políticas disponibles como chips
st.markdown("### Políticas disponibles")
cols = st.columns(4)
for i, (nombre, pol) in enumerate(politicas_dict.items()):
    with cols[i % 4]:
        texto = ", ".join([f"{s}:{d}" for s, d in pol.items()])
        st.markdown(f'<span class="chip chip-gold" style="margin:4px;">{nombre}: {texto}</span>', unsafe_allow_html=True)

st.markdown("---")

# Selección de políticas a evaluar
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

# Opción para mostrar cálculos detallados
mostrar_detalles = st.checkbox("Mostrar cálculos detallados (Gauss-Jordan y pasos intermedios)", value=False)

# Botón para ejecutar
if st.button("Ejecutar Enumeración Exhaustiva", type="primary"):
    with st.spinner("Evaluando políticas..."):
        mejor, resultados = enumeracion_exhaustiva(
            estados, decisiones_data, tipo,
            politicas_seleccionadas=politicas_a_evaluar
        )

    if mejor is None:
        st.warning("No se encontró ninguna política con solución válida.")
    else:
        st.success("Evaluación completada.")

        # Mostrar política óptima
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

        # Probabilidades estacionarias de la política óptima
        st.markdown("#### Probabilidades estacionarias (π)")
        pi_df = pd.DataFrame.from_dict(mejor["pi"], orient="index", columns=["π"])
        st.dataframe(pi_df, use_container_width=True)

        st.markdown("---")
        st.markdown("### Políticas evaluadas")

        # Separar resultados válidos e inválidos
        resultados_validos = [r for r in resultados if not r.get("error", False)]
        resultados_invalidos = [r for r in resultados if r.get("error", False)]

        # Ordenar válidos según tipo de modelo
        if tipo == "costos":
            resultados_validos = sorted(resultados_validos, key=lambda x: x["esperado"])
        else:
            resultados_validos = sorted(resultados_validos, key=lambda x: x["esperado"], reverse=True)

        # Mostrar políticas válidas
        for res in resultados_validos:
            nombre = [k for k, v in politicas_dict.items() if v == res["politica"]][0]
            is_optimal = (res == mejor)
            border_style = "border-left: 4px solid #F5A800;" if is_optimal else ""

            with st.expander(f"{nombre} — Esperado: {res['esperado']:.6f}" + (" (ÓPTIMA)" if is_optimal else "")):
                st.markdown(f"""
                <div style="{border_style} padding-left: 1rem;">
                    <p><b>Decisiones:</b> {", ".join([f"{s} → {d}" for s, d in res["politica"].items()])}</p>
                </div>
                """, unsafe_allow_html=True)

                tab1, tab2, tab3, tab4 = st.tabs(["Matriz de Transición", "Sistema de Ecuaciones", "Probabilidades π", "Costo / Ganancia Esperado"])

                with tab1:
                    st.dataframe(res["P"], use_container_width=True)

                with tab2:
                    for linea in res["sistema"]:
                        st.markdown(f"`{linea}`")

                with tab3:
                    pi_df = pd.DataFrame.from_dict(res["pi"], orient="index", columns=["π"])
                    st.dataframe(pi_df, use_container_width=True)

                with tab4:
                    tipo_valor = "Costo" if tipo == "costos" else "Ganancia"
                    st.markdown(f"**{tipo_valor} esperado:** `{res['esperado']:.6f}`")
                    expr = " + ".join([f"({res['c'][s]:.4f})·({res['pi'][s]:.4f})" for s in estados])
                    st.markdown(f"E = {expr} = {res['esperado']:.6f}")

                if mostrar_detalles and res.get("gauss_steps"):
                    with st.expander("🔍 Ver pasos de Gauss‑Jordan"):
                        for desc, matriz in res["gauss_steps"]:
                            st.markdown(f"**{desc}**")
                            cols = [f"π{_subindice(i)}" for i in range(len(estados))] + ["b"]
                            df_matriz = pd.DataFrame(matriz, columns=cols)
                            st.dataframe(df_matriz, use_container_width=True)

        # Mostrar políticas inválidas (sin solución)
        for res in resultados_invalidos:
            nombre = [k for k, v in politicas_dict.items() if v == res["politica"]][0]
            with st.expander(f"{nombre} — ⚠️ {res.get('mensaje', 'Sin solución')}"):
                st.markdown(f"**Decisiones:** {', '.join([f'{s} → {d}' for s, d in res['politica'].items()])}")
                st.dataframe(res["P"], use_container_width=True)

        # ---------- ANÁLISIS COMPARATIVO ----------
        if resultados_validos:
            st.markdown("---")
            st.markdown("""
            <div style="margin-top:2rem;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#F5A800;letter-spacing:.15em;margin-bottom:.4rem;">ANÁLISIS COMPARATIVO</div>
                <h2 style="font-family:'Sora',sans-serif;font-weight:700;font-size:1.6rem;color:#E8EAF0;margin:0 0 0.5rem 0;">Rendimiento de Políticas</h2>
            </div>
            """, unsafe_allow_html=True)

            tipo_valor = "Costo" if tipo == "costos" else "Ganancia"
            opt_valor = mejor["esperado"]

            # Preparar datos para tabla comparativa
            data_comparativa = []
            for res in resultados_validos:
                nombre = [k for k, v in politicas_dict.items() if v == res["politica"]][0]
                decisiones_str = ", ".join([f"{s}→{d}" for s, d in res["politica"].items()])
                esperado = res["esperado"]
                diff_abs = esperado - opt_valor
                diff_pct = (diff_abs / opt_valor * 100) if opt_valor != 0 else 0.0
                es_optimo = (res == mejor)

                data_comparativa.append({
                    "Política": nombre,
                    "Decisiones": decisiones_str,
                    f"{tipo_valor} esperado": esperado,
                    "Diferencia absoluta": diff_abs,
                    "Diferencia (%)": diff_pct,
                    "Óptima": "✅" if es_optimo else ""
                })

            df_comp = pd.DataFrame(data_comparativa)
            df_comp = df_comp.sort_values(f"{tipo_valor} esperado", ascending=(tipo == "costos"))

            # Tabla comparativa
            st.markdown("#### 📋 Tabla comparativa")
            st.dataframe(
                df_comp.style.format({
                    f"{tipo_valor} esperado": "{:.6f}",
                    "Diferencia absoluta": "{:+.6f}",
                    "Diferencia (%)": "{:+.2f}%"
                }).map(lambda x: 'color: #10B981' if x == '✅' else '', subset=['Óptima']),
                use_container_width=True,
                hide_index=True
            )

            # Gráfico de barras
            st.markdown("#### 📊 Visualización de valores esperados")
            try:
                import altair as alt
                chart_data = pd.DataFrame({
                    "Política": [d["Política"] for d in data_comparativa],
                    f"{tipo_valor} esperado": [d[f"{tipo_valor} esperado"] for d in data_comparativa],
                    "Óptima": ["Óptima" if d["Óptima"] == "✅" else "Subóptima" for d in data_comparativa]
                })

                color_scale = alt.Scale(domain=["Óptima", "Subóptima"], range=["#F5A800", "#5B9BD5"])

                bars = alt.Chart(chart_data).mark_bar().encode(
                    y=alt.Y("Política:N", sort=None, title="Política"),
                    x=alt.X(f"{tipo_valor} esperado:Q", title=f"{tipo_valor} esperado"),
                    color=alt.Color("Óptima:N", scale=color_scale, legend=alt.Legend(title="Tipo")),
                    tooltip=["Política", f"{tipo_valor} esperado", "Óptima"]
                ).properties(height=100 + 30*len(chart_data))

                st.altair_chart(bars, use_container_width=True)
            except ImportError:
                st.bar_chart(
                    data=pd.DataFrame({
                        "Política": [d["Política"] for d in data_comparativa],
                        f"{tipo_valor} esperado": [d[f"{tipo_valor} esperado"] for d in data_comparativa]
                    }).set_index("Política")
                )

            # Estadísticas comparativas
            st.markdown("#### 📈 Estadísticas comparativas")
            suboptimas = [d for d in data_comparativa if d["Óptima"] != "✅"]
            num_optimas = len(data_comparativa) - len(suboptimas)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Políticas válidas evaluadas", len(data_comparativa))
            with col2:
                st.metric("Políticas óptimas", num_optimas)
            with col3:
                if suboptimas:
                    if tipo == "costos":
                        mejor_sub = min(suboptimas, key=lambda x: x[f"{tipo_valor} esperado"])
                        peor_sub = max(suboptimas, key=lambda x: x[f"{tipo_valor} esperado"])
                    else:
                        mejor_sub = max(suboptimas, key=lambda x: x[f"{tipo_valor} esperado"])
                        peor_sub = min(suboptimas, key=lambda x: x[f"{tipo_valor} esperado"])

                    st.markdown(f"""
                    **Subóptima más cercana**  
                    {mejor_sub['Política']} ({mejor_sub['Diferencia absoluta']:+.6f})  
                    **Subóptima más alejada**  
                    {peor_sub['Política']} ({peor_sub['Diferencia absoluta']:+.6f})
                    """)
                else:
                    st.markdown("Todas son óptimas")

            # Interpretación textual
            if suboptimas:
                st.markdown("---")
                st.markdown("**Interpretación:**")
                optima_nombre = [d['Política'] for d in data_comparativa if d['Óptima'] == '✅'][0]
                st.markdown(f"""
                - La política óptima es **{optima_nombre}** con un valor esperado de **{opt_valor:.6f}**.
                - Entre las subóptimas, **{mejor_sub['Política']}** es la más cercana al óptimo, con una diferencia de **{mejor_sub['Diferencia absoluta']:+.6f}** ({mejor_sub['Diferencia (%)']:+.2f}%).
                - La peor política evaluada es **{peor_sub['Política']}**, que se desvía en **{peor_sub['Diferencia absoluta']:+.6f}** ({peor_sub['Diferencia (%)']:+.2f}%).
                """)
        else:
            st.info("No hay políticas válidas para realizar análisis comparativo.")
