# MDP Solver — UNAM FES Acatlán

Software para modelar y resolver Procesos Markovianos de Decisión.

## Estructura

```
mdp-solver/
├── .streamlit/
│   └── config.toml        # Tema UNAM (azul y oro)
├── pages/
│   ├── 01_ingreso.py      # Ingreso de datos
│   └── 02_mostrar.py      # Visualización del modelo
├── utils/
│   └── session.py         # Estado global de la sesión
├── app.py                 # Página principal
└── requirements.txt
```

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy en Streamlit Cloud

1. Sube este proyecto a un repositorio de GitHub.
2. Ve a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con tu cuenta de GitHub.
3. Selecciona el repositorio y apunta el archivo principal a `app.py`.
4. Haz clic en **Deploy**. La app estará disponible en una URL pública.

## Módulos

- **Ingreso de Datos**: Define estados, decisiones, costos y matrices de transición.
- **Visualización**: Tabla de costos, matrices de transición y grafo del MDP.
- *(Próximamente)* Enumeración Exhaustiva, Mejoramiento de Políticas, Aproximaciones Sucesivas, Programación Lineal, Mejoramiento con Descuento.
