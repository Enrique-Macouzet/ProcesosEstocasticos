"""
modulos/inicio.py
Pagina de inicio del MDP Solver. Muestra resumen del modelo y acceso a modulos.
"""

import streamlit as st
from guardado.sesion import get_mdp, mdp_completo

st.set_page_config(page_title="Inicio — MDP Solver", page_icon="🎓")

# ---------- ESTILOS (se heredan del CSS global de app.py, pero aseguramos algunos) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.main .block-container { padding-top: 2rem; max-width: 1100px; }
.unam-card { background:#111827; border:1px solid #1E2A3A; border-radius:12px; padding:1.5rem; margin-bottom:1rem; }
.badge-ok { display:inline-flex; align-items:center; gap:4px; background:rgba(16,185,129,.12); border:1px solid rgba(16,185,129,.3); color:#10B981; font-size:.75rem; font-family:'Sora',sans-serif; padding:2px 10px; border-radius:20px; }
.badge-warn { display:inline-flex; align-items:center; gap:4px; background:rgba(245,168,0,.12); border:1px solid rgba(245,168,0,.3); color:#F5A800; font-size:.75rem; font-family:'Sora',sans-serif; padding:2px 10px; border-radius:20px; }
hr { border-color:#1E2A3A; margin:1.5rem 0; }
</style>
""", unsafe_allow_html=True)

mdp = get_mdp()

# ---------- ENCABEZADO ----------
st.markdown("""
<div style="margin-bottom: 2rem;">
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem;
                color:#F5A800; letter-spacing:0.15em; margin-bottom:0.5rem;">
        PROCESOS MARKOVIANOS DE DECISIÓN
    </div>
    <h1 style="font-family:'Sora',sans-serif; font-weight:700; font-size:2.2rem;
               color:#E8EAF0; margin:0 0 0.5rem 0; line-height:1.2;">
        Herramienta MDP
    </h1>
    <p style="color:#8FA0B8; font-size:1rem; margin:0; max-width:600px;">
        Modelado y solución de Procesos Markovianos de Decisión.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------- RESUMEN DEL MODELO ----------
col1, col2, col3, col4 = st.columns(4)

with col1:
    n_estados = len(mdp["estados"])
    st.markdown(f"""
    <div class="unam-card" style="text-align:center;">
        <div style="font-size:2rem; font-weight:700; color:#F5A800;
                    font-family:'IBM Plex Mono',monospace;">{n_estados}</div>
        <div style="color:#8FA0B8; font-size:0.8rem; margin-top:4px;">Estados</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    n_dec = len(mdp["decisiones"])
    st.markdown(f"""
    <div class="unam-card" style="text-align:center;">
        <div style="font-size:2rem; font-weight:700; color:#003F8A;
                    font-family:'IBM Plex Mono',monospace;
                    -webkit-text-stroke: 1px #0056C7; color:#5B9BD5;">{n_dec}</div>
        <div style="color:#8FA0B8; font-size:0.8rem; margin-top:4px;">Decisiones</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    tipo = mdp.get("tipo", "costos").capitalize()
    st.markdown(f"""
    <div class="unam-card" style="text-align:center;">
        <div style="font-size:1.1rem; font-weight:600; color:#E8EAF0;
                    font-family:'Sora',sans-serif; margin-top:6px;">{tipo}</div>
        <div style="color:#8FA0B8; font-size:0.8rem; margin-top:4px;">Tipo de modelo</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    listo = mdp_completo()
    badge = '<span class="badge-ok">● Listo</span>' if listo else '<span class="badge-warn">● Incompleto</span>'
    st.markdown(f"""
    <div class="unam-card" style="text-align:center;">
        <div style="margin-top:8px;">{badge}</div>
        <div style="color:#8FA0B8; font-size:0.8rem; margin-top:6px;">Estado del modelo</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------- TARJETAS DE MODULOS ----------
st.markdown("### Modulos disponibles")
c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    <div class="unam-card" style="border-left: 3px solid #F5A800;">
        <div style="font-family:'Sora',sans-serif; font-weight:600; color:#E8EAF0; margin-bottom:6px;">
            Ingreso de Datos
        </div>
        <div style="color:#8FA0B8; font-size:0.85rem;">
            Define estados, decisiones, costos y matrices de transicion de tu MDP.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="unam-card" style="border-left: 3px solid #5B9BD5;">
        <div style="font-family:'Sora',sans-serif; font-weight:600; color:#E8EAF0; margin-bottom:6px;">
            Visualizacion de Datos
        </div>
        <div style="color:#8FA0B8; font-size:0.85rem;">
            Revisa el modelo ingresado: tablas de costos, matrices de transicion y grafo de la cadena.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:2rem; padding:1rem; background:#111827;
            border-radius:8px; border:1px solid #1E2A3A;">
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
                color:#8FA0B8; letter-spacing:0.05em;">
        Usa el menu lateral para navegar entre modulos.
        Los datos se conservan durante toda la sesion.
    </div>
</div>
""", unsafe_allow_html=True)
