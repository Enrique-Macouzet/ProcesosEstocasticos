"""
modulos/ingreso_datos.py
Interfaz para definir estados, decisiones, costos y matrices de transicion.
"""

import streamlit as st
from guardado.sesion import get_mdp, reset_mdp, mdp_completo, init_session

st.set_page_config(page_title="Ingreso de Datos — MDP Solver", page_icon="📥")
init_session()

# Obtener el estado actual del MDP
mdp = get_mdp()

# ---------- ESTILOS COMPLEMENTARIOS (el CSS principal ya está en app.py) ----------
st.markdown("""
<style>
/* Aseguramos que los estilos específicos de este módulo se mantengan */
.main .block-container { padding-top: 2rem; max-width: 1100px; }
.section-header { display:flex; align-items:center; gap:.75rem; margin-bottom:1.25rem; }
.section-header .accent-bar { width:4px; height:28px; background:linear-gradient(180deg,#F5A800,#003F8A); border-radius:2px; flex-shrink:0; }
.section-header h3 { margin:0; font-family:'Sora',sans-serif; font-size:1rem; font-weight:600; color:#E8EAF0; letter-spacing:.03em; }
.chip { display:inline-block; background:rgba(0,63,138,.3); border:1px solid rgba(0,63,138,.6); color:#7EB3FF; font-family:'IBM Plex Mono',monospace; font-size:.78rem; padding:2px 10px; border-radius:20px; margin:2px; }
.badge-ok { display:inline-flex; align-items:center; gap:4px; background:rgba(16,185,129,.12); border:1px solid rgba(16,185,129,.3); color:#10B981; font-size:.75rem; padding:2px 10px; border-radius:20px; }
.badge-warn { display:inline-flex; align-items:center; gap:4px; background:rgba(245,168,0,.12); border:1px solid rgba(245,168,0,.3); color:#F5A800; font-size:.75rem; padding:2px 10px; border-radius:20px; }
.badge-err { display:inline-flex; align-items:center; gap:4px; background:rgba(239,68,68,.12); border:1px solid rgba(239,68,68,.3); color:#EF4444; font-size:.75rem; padding:2px 10px; border-radius:20px; }
hr { border-color:#1E2A3A; margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ---------- ENCABEZADO ----------
st.markdown("""
<div style="margin-bottom:1.5rem;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#F5A800;letter-spacing:.15em;margin-bottom:.4rem;">MODULO 01</div>
    <h1 style="font-family:'Sora',sans-serif;font-weight:700;font-size:1.8rem;color:#E8EAF0;margin:0;">Ingreso de Datos</h1>
    <p style="color:#8FA0B8;font-size:.9rem;margin:.4rem 0 0 0;">Define completamente tu Proceso Markoviano de Decision.</p>
</div>
""", unsafe_allow_html=True)

# ---------- SECCION 1: ESTADOS Y DECISIONES ----------
st.markdown("""
<div class="section-header">
    <div class="accent-bar"></div>
    <h3>1 · Estados y Decisiones</h3>
</div>
""", unsafe_allow_html=True)

col_tipo, col_est, col_dec = st.columns([1, 2, 2])

with col_tipo:
    tipo_actual = mdp.get("tipo", "costos")
    tipo = st.radio(
        "Tipo de modelo",
        ["costos", "recompensas"],
        index=0 if tipo_actual == "costos" else 1,
        format_func=lambda x: "Costos (minimizar)" if x == "costos" else "Recompensas (maximizar)",
        help="Define si el objetivo es minimizar costos o maximizar recompensas."
    )
    mdp["tipo"] = tipo

with col_est:
    estados_str = st.text_input(
        "Estados del sistema",
        value=", ".join(mdp["estados"]) if mdp["estados"] else "",
        placeholder="s0, s1, s2, ...",
        help="Ingresa los nombres de los estados separados por comas."
    )
    if estados_str.strip():
        nuevos_estados = [s.strip() for s in estados_str.split(",") if s.strip()]
        if nuevos_estados != mdp["estados"]:
            # Limpiar datos de estados eliminados
            eliminados = set(mdp["estados"]) - set(nuevos_estados)
            for estado in eliminados:
                for d, data in mdp["decisiones_data"].items():
                    if estado in data["estados_afectados"]:
                        data["estados_afectados"].remove(estado)
                    data["costos"].pop(estado, None)
                    data["transiciones"].pop(estado, None)
                    for origen in data["transiciones"]:
                        data["transiciones"][origen].pop(estado, None)
            mdp["estados"] = nuevos_estados

    if mdp["estados"]:
        chips = " ".join([f'<span class="chip">{s}</span>' for s in mdp["estados"]])
        st.markdown(f'<div style="margin-top:.5rem;">{chips}</div>', unsafe_allow_html=True)

with col_dec:
    decisiones_str = st.text_input(
        "Decisiones posibles",
        value=", ".join(mdp["decisiones"]) if mdp["decisiones"] else "",
        placeholder="d0, d1, d2, ...",
        help="Ingresa las decisiones posibles separadas por comas."
    )
    if decisiones_str.strip():
        nuevas_dec = [d.strip() for d in decisiones_str.split(",") if d.strip()]
        if nuevas_dec != mdp["decisiones"]:
            # Agregar nuevas decisiones
            for d in nuevas_dec:
                if d not in mdp["decisiones_data"]:
                    mdp["decisiones_data"][d] = {
                        "estados_afectados": [],
                        "costos": {},
                        "transiciones": {}
                    }
            # Eliminar decisiones que ya no estan
            for d in list(mdp["decisiones_data"].keys()):
                if d not in nuevas_dec:
                    del mdp["decisiones_data"][d]
            mdp["decisiones"] = nuevas_dec

    if mdp["decisiones"]:
        chips = " ".join([f'<span class="chip" style="background:rgba(245,168,0,.1);border-color:rgba(245,168,0,.4);color:#F5A800;">{d}</span>' for d in mdp["decisiones"]])
        st.markdown(f'<div style="margin-top:.5rem;">{chips}</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- SECCION 2: CONFIGURACION POR DECISION ----------
if not mdp["estados"] or not mdp["decisiones"]:
    st.markdown("""
    <div style="text-align:center;padding:3rem;color:#8FA0B8;">
        <div style="font-size:2rem;margin-bottom:.5rem;">⚙️</div>
        <div style="font-family:'Sora',sans-serif;">Ingresa estados y decisiones para continuar.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown("""
<div class="section-header">
    <div class="accent-bar"></div>
    <h3>2 · Configuracion por Decision</h3>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([f"  {d}  " for d in mdp["decisiones"]])

for tab, d in zip(tabs, mdp["decisiones"]):
    with tab:
        data = mdp["decisiones_data"][d]

        # --- Estados afectados ---
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:.75rem;color:#8FA0B8;
                    letter-spacing:.08em;margin-bottom:.75rem;">
            ESTADOS AFECTADOS POR <span style="color:#F5A800;">{d}</span>
        </div>
        """, unsafe_allow_html=True)

        afectados = st.multiselect(
            "Selecciona los estados en los que aplica esta decision",
            options=mdp["estados"],
            default=[s for s in data.get("estados_afectados", []) if s in mdp["estados"]],
            key=f"afect_{d}",
            label_visibility="collapsed"
        )
        data["estados_afectados"] = afectados

        if not afectados:
            st.info("Selecciona al menos un estado para continuar con esta decision.")
            continue

        st.markdown("<hr>", unsafe_allow_html=True)

        col_costos, col_trans = st.columns([1, 2])

        # --- Costos ---
        with col_costos:
            tipo_label = "Costo" if mdp["tipo"] == "costos" else "Recompensa"
            st.markdown(f"""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:.75rem;color:#8FA0B8;
                        letter-spacing:.08em;margin-bottom:.75rem;">
                {tipo_label.upper()}S C(s, {d})
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#0A0E1A;border:1px solid #1E2A3A;border-radius:8px;padding:.75rem;
                        margin-bottom:1rem;font-size:.78rem;color:#8FA0B8;font-family:'Sora',sans-serif;">
                Ingresa el {tipo_label.lower()} de estar en cada estado y aplicar la decision <b style="color:#F5A800;">{d}</b>.
            </div>
            """, unsafe_allow_html=True)

            for s in afectados:
                current = data["costos"].get(s, 0.0)
                val = st.number_input(
                    f"C({s}, {d})",
                    value=float(current),
                    step=0.01,
                    format="%.4f",
                    key=f"costo_{d}_{s}"
                )
                data["costos"][s] = val

        # --- Matriz de transicion ---
        with col_trans:
            st.markdown(f"""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:.75rem;color:#8FA0B8;
                        letter-spacing:.08em;margin-bottom:.75rem;">
                MATRIZ DE TRANSICION P(s'|s, {d})
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#0A0E1A;border:1px solid #1E2A3A;border-radius:8px;padding:.75rem;
                        margin-bottom:1rem;font-size:.78rem;color:#8FA0B8;font-family:'Sora',sans-serif;">
                Para cada estado origen <b style="color:#E8EAF0;">s</b>, ingresa las probabilidades de 
                transicion hacia cada estado destino <b style="color:#E8EAF0;">s'</b>.
                Cada fila debe sumar <b style="color:#10B981;">1.0</b>.
            </div>
            """, unsafe_allow_html=True)

            todos_estados = mdp["estados"]

            for s in afectados:
                if s not in data["transiciones"]:
                    data["transiciones"][s] = {}

                fila = data["transiciones"][s]

                st.markdown(f"""
                <div style="font-family:'IBM Plex Mono',monospace;font-size:.8rem;
                            color:#E8EAF0;margin:.75rem 0 .4rem 0;">
                    Desde <span style="color:#F5A800;">{s}</span> →
                </div>
                """, unsafe_allow_html=True)

                cols = st.columns(len(todos_estados))
                fila_sum = 0.0
                for col_i, s2 in zip(cols, todos_estados):
                    with col_i:
                        current_p = fila.get(s2, 0.0)
                        p = st.number_input(
                            f"→{s2}",
                            value=float(current_p),
                            min_value=0.0,
                            max_value=1.0,
                            step=0.01,
                            format="%.4f",
                            key=f"trans_{d}_{s}_{s2}"
                        )
                        fila[s2] = p
                        fila_sum += p

                diff = abs(fila_sum - 1.0)
                if diff < 1e-6:
                    st.markdown('<span class="badge-ok">Suma = 1.0000</span>', unsafe_allow_html=True)
                elif fila_sum == 0.0:
                    st.markdown('<span class="badge-warn">Sin ingresar</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="badge-err">Suma = {fila_sum:.4f} (debe ser 1.0)</span>', unsafe_allow_html=True)

# ---------- SECCION 3: GUARDAR / REINICIAR ----------
st.markdown("<hr>", unsafe_allow_html=True)

listo = mdp_completo()

col_save, col_reset, col_status = st.columns([2, 1, 3])

with col_save:
    if st.button("Guardar datos del sistema", type="primary", use_container_width=True):
        if listo:
            st.success("Datos guardados correctamente. Puedes ir al modulo de Visualizacion.")
        else:
            st.warning("El modelo tiene datos incompletos. Revisa que todas las filas de transicion sumen 1.0 y que cada estado afectado tenga un costo asignado.")

with col_reset:
    if st.button("Limpiar todo", use_container_width=True):
        reset_mdp()
        st.rerun()

with col_status:
    if listo:
        st.markdown('<div style="padding:.5rem 0;"><span class="badge-ok">Modelo completo y valido</span></div>', unsafe_allow_html=True)
    else:
        missing = []
        if not mdp["estados"]:
            missing.append("estados")
        if not mdp["decisiones"]:
            missing.append("decisiones")
        else:
            for d in mdp["decisiones"]:
                data = mdp["decisiones_data"].get(d, {})
                afectados = data.get("estados_afectados", [])
                if not afectados:
                    missing.append(f"estados de {d}")
                    continue
                for s in afectados:
                    if s not in data.get("costos", {}):
                        missing.append(f"costo({s},{d})")
                    probs = data.get("transiciones", {}).get(s, {})
                    total = sum(probs.values())
                    if abs(total - 1.0) > 1e-6:
                        missing.append(f"P(·|{s},{d})")
        if missing:
            st.markdown(f'<div style="padding:.5rem 0;font-size:.8rem;color:#8FA0B8;">Pendiente: {", ".join(missing[:4])}{"..." if len(missing)>4 else ""}</div>', unsafe_allow_html=True)
