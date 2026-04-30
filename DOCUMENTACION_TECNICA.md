Documentación Técnica Completa – Herramienta MDP
Guía exhaustiva para el equipo de desarrollo
Índice

    Arquitectura general y flujo de datos

    Estructuras de datos en profundidad

    Módulo de Ingreso de Datos – lógica de captura y validación

    Módulo de Visualización – tablas y grafo interactivo

    Algoritmo: Enumeración Exhaustiva

    Algoritmo: Programación Lineal

    Algoritmo: Mejoramiento de Políticas (sin descuento)

    Algoritmo: Mejoramiento de Políticas con Descuento

    Algoritmo: Aproximaciones Sucesivas

    Módulo de Comparación de Métodos

    Módulo de Exportación a Excel

    Sistema de sesiones y persistencia

    Navegación, estilos y recursos visuales

    Resumen para exposición oral

1. Arquitectura general y flujo de datos
Organización del proyecto en capas
text

[ app.py ]  ────  Punto de entrada, estilos CSS, navegación
    │
    ├─[ guardado/sesion.py ]  ────  Memoria compartida (st.session_state)
    │
    ├─[ modulos/ ]  ────  Interfaces de usuario (Streamlit)
    │    ├── inicio.py
    │    ├── ingreso_datos.py
    │    ├── visualizacion.py
    │    ├── enumeracion_exhaustiva.py
    │    ├── programacion_lineal.py
    │    ├── mejoramiento_politicas.py
    │    ├── mejoramiento_politicas_descuento.py
    │    ├── aproximaciones_sucesivas.py
    │    ├── comparacion_metodos.py
    │    ├── exportar_excel.py
    │    └── agradecimientos.py
    │
    └─[ algoritmos/ ]  ────  Lógica matemática pura
         ├── exhaustiva.py
         ├── programacion_lineal.py
         ├── mejoramiento_politicas.py
         ├── mejoramiento_politicas_descuento.py
         └── aproximaciones_sucesivas.py

Principio de separación Frontend-Backend

    algoritmos/: Contiene funciones puras que reciben parámetros (listas, diccionarios) y devuelven resultados (diccionarios). No importan Streamlit. Se pueden probar con tests unitarios.

    modulos/: Son páginas de Streamlit que llaman a las funciones de algoritmos/ y muestran los resultados en la UI.

    guardado/sesion.py: Capa de persistencia. Centraliza el acceso a st.session_state.mdp para que todos los módulos compartan los mismos datos.

Flujo típico de un módulo

    Importa get_mdp() de guardado.sesion.

    Lee el modelo actual.

    El usuario interactúa (botones, sliders).

    Se llama a la función del backend en algoritmos/.

    Se muestran los resultados con Streamlit (st.write, st.dataframe, st.latex, etc.).

2. Estructuras de datos en profundidad
El diccionario mdp – detalle de cada nivel
python

mdp = {
    "estados": ["0", "1", "2", "3"],       # list[str]
    "decisiones": ["1", "2", "3"],         # list[str]
    "tipo": "costos",                      # "costos" o "ganancias"
    "decisiones_data": {                    # dict[str, dict]
        "1": {                              # clave = nombre de decisión
            "estados_afectados": ["0", "1"],
            "costos": {                     # dict[str, float]
                "0": 0.0,
                "1": 5.0
            },
            "transiciones": {               # dict[str, dict[str, float]]
                "0": {                      # desde estado "0"
                    "0": 0.5,               # P(0 → 0 | decisión 1)
                    "1": 0.5                # P(0 → 1 | decisión 1)
                },
                "1": {
                    "0": 0.8,
                    "1": 0.2
                }
            }
        },
        "2": { ... },
        "3": { ... }
    }
}

Por qué se eligió este diseño

    Nombres naturales: Los índices de estados y decisiones son strings, no números, para facilitar la depuración y la interacción con el usuario.

    Matriz de transición dispersa: Solo se almacenan las probabilidades ≠ 0. Esto ahorra memoria y evita bucles innecesarios.

    Separación por decisión: Cada decisión contiene su propia matriz de transición y sus costos, lo que permite acceder a todos los datos de una decisión sin recorrer todo el modelo.

    Costos por estado: costos[estado] es directo, sin necesidad de una tupla (estado, decision).

Mapeo a índices numéricos para álgebra lineal

Cuando un algoritmo necesita usar NumPy, se crea un mapeo temporal con un diccionario:
python

idx = {"0": 0, "1": 1, "2": 2, "3": 3}   # {nombre: posición}

Luego se construye una matriz densa de tamaño n×n:
python

P = np.zeros((n, n))
for s in estados:
    i = idx[s]
    d = politica[s]   # decisión asignada por la política
    for s2, prob in decisiones_data[d]["transiciones"][s].items():
        j = idx[s2]
        P[i, j] = prob

Esto se hace en cada evaluación de política, por lo que no se almacena permanentemente.
Representación de políticas

Una política determinista es un diccionario {estado: decision}:
python

{"0": "1", "1": "2", "2": "1", "3": "3"}

Para nombrarlas (R1, R2, …), se genera la lista completa de políticas mediante producto cartesiano y se asigna un número secuencial.
3. Módulo de Ingreso de Datos – lógica de captura y validación
3.1 Entrada de estados y decisiones

    Se usa st.text_input con un placeholder que muestra el formato esperado.

    Al cambiar el texto, se convierte a lista con split(",") y se eliminan espacios.

    Si se modifica la lista de estados, se recorre decisiones_data para eliminar referencias a estados que ya no existen.

3.2 Entrada de costos y probabilidades (aceptando fracciones)

Se crearon dos funciones auxiliares:

    evaluar_numero(texto, valor_actual, permitir_fraccion=True)
    Si el texto contiene "/", se divide en numerador y denominador y se calcula float(num)/float(den).
    Si no, se convierte directamente a float.
    Si la conversión falla, se retorna el valor actual y se muestra un warning.

    formatear_numero(valor)
    Usa Fraction(valor).limit_denominator(1000) para obtener una representación fraccionaria legible.
    Si el denominador es 1, retorna el numerador como entero; si no, retorna "num/den".
    Esto permite que los valores guardados se muestren como 1/3 en lugar de 0.3333.

3.3 Pestañas por decisión

    Se crea un st.tabs con una pestaña por decisión.

    Dentro de cada pestaña, un st.multiselect permite elegir los estados afectados.

    Para los costos: st.text_input con evaluar_numero.

    Para las probabilidades: se muestra una fila de encabezados con los nombres de los estados destino, y luego una fila de st.text_input para cada destino. La suma se calcula en tiempo real y se muestra con badges.

3.4 Validación de completitud

mdp_completo() en guardado/sesion.py verifica:

    estados y decisiones no vacías.

    Cada decisión tiene al menos un estado en estados_afectados.

    Cada estado afectado tiene una entrada en costos.

    Para cada estado afectado, la suma de probabilidades en transiciones[origen] es 1.0 (±1e-6).

4. Módulo de Visualización – tablas y grafo interactivo
4.1 Tablas

    Costos: Se construye un DataFrame con filas = estados, columnas = decisiones. Las celdas sin asignación muestran "—".

    Matriz de transición: Se selecciona una decisión con st.selectbox. Se construye un DataFrame con filas = estados origen, columnas = estados destino, y una columna extra "Σ" que suma cada fila. La columna Σ se colorea con verde o rojo según si suma 1.

4.2 Grafo con Cytoscape.js

    Se generan dos listas: nodes y edges.

    Cada nodo tiene un id igual al nombre del estado. Si el estado está afectado por la decisión, se le asigna la clase affected.

    Las aristas se generan solo para probabilidades > 0.

    Detección de pares bidireccionales:

        Se agrupan aristas por (origen, destino) en un diccionario.

        Si hay más de una arista entre el mismo par, la segunda se pinta de dorado (#F5A800).

        Si existe la arista opuesta (destino, origen), se comparan los nombres de los estados para asignar azul al primer par y dorado al segundo.

    El HTML y JavaScript se inyectan con st.components.v1.html. Cytoscape se carga desde CDN.

    Se usa el layout circle para distribuir los nodos uniformemente.

5. Algoritmo: Enumeración Exhaustiva
5.1 Generación de políticas (generar_politicas)

    Para cada estado, se recopilan las decisiones que lo afectan: opciones_por_estado[s] = [d1, d2, ...].

    Se calcula itertools.product(*opciones_por_estado.values()).

    Cada tupla resultante se convierte en diccionario con zip(estados, combo).

5.2 Evaluación de una política (evaluar_politica)

    Construcción de matriz P y vector c:
    python

P = [[0.0]*n for _ in range(n)]
c = [0.0]*n
for s in estados:
    i = idx[s]
    d = politica[s]
    c[i] = decisiones_data[d]["costos"][s]
    for s2, prob in decisiones_data[d]["transiciones"][s].items():
        j = idx[s2]
        P[i][j] = prob

    Sistema estacionario:

        Se forma A = I - P^T, pero con la última fila reemplazada por [1,1,...,1].

        b = [0,0,...,0,1].

        Se resuelve con np.linalg.solve(A, b). Si la matriz es singular, se captura LinAlgError y la política se marca como inválida.

        El resultado π se normaliza forzando no negatividad y división por la suma.

    Costo esperado: esperado = np.dot(pi, c).

    Gauss-Jordan para visualización: Se construye una matriz aumentada con Fraction para exactitud, y se aplica eliminación guardando cada paso.

5.3 Selección de la óptima

    Si tipo == "costos": min(resultados, key=lambda x: x["esperado"]).

    Si tipo == "ganancias": max(...).

6. Algoritmo: Programación Lineal
6.1 Construcción del modelo (construir_modelo_pl)

    Variables: Se crea una variable Y_{i,k} por cada par (estado, decisión) donde la decisión afecta al estado. Se asigna un índice secuencial.

    Función objetivo: Vector c donde c[idx] = costo (si es ganancias, se multiplica por -1).

    Restricciones:

        Una fila de normalización: [1,1,...,1].

        Para cada estado (excepto el último): Σ_k Y_{i,k} - Σ_{j,l} Y_{j,l} * P(i | j,l) = 0.

            La fila se construye recorriendo todas las variables Y_{j,l} y añadiendo -P(i|j,l) al coeficiente correspondiente, y +1 a las variables con origen i.

    Cotas: Y >= 0.

6.2 Resolución

    Se llama a linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs').

    Si no tiene éxito, se retorna un error.

6.3 Extracción de política

    Se calcula D_{i,k} = Y_{i,k} / Σ_k Y_{i,k}.

    Para cada estado, se elige la decisión con mayor D.

7. Algoritmo: Mejoramiento de Políticas (sin descuento)
7.1 Evaluación (evaluar_politica)

    Se construye la matriz A de tamaño n×(n+1) para incógnitas [g, V_0, ..., V_{n-1}].

    Ecuaciones: g + V_i - Σ_j P_{ij} V_j = C_ik.

    Se fija V_{n-1} = 0, eliminando su columna.

    Se resuelve el sistema cuadrado resultante.

    Se retorna g y diccionario V.

7.2 Mejora (mejorar_politica)

    Para cada estado i y cada decisión k:

        Q(i,k) = C_ik + Σ_j P_{ij}(k) * V_j.

    Se selecciona la decisión con menor Q (costos) o mayor Q (ganancias).

7.3 Iteración

    Se repite evaluación y mejora hasta que la política se estabiliza.

8. Algoritmo: Mejoramiento de Políticas con Descuento
8.1 Diferencia con el sin descuento

    Se introduce un factor α (0 ≤ α ≤ 1).

    Ecuación de evaluación: V_i = C_ik + α * Σ_j P_{ij} V_j.

    Esto forma el sistema (I - αP) V = c, que siempre tiene solución única si α < 1.

8.2 Implementación

    Se construye A = I - αP.

    Se resuelve con np.linalg.solve.

    La mejora usa Q(i,k) = C_ik + α * Σ_j P_{ij}(k) * V_j.

9. Algoritmo: Aproximaciones Sucesivas
9.1 Inicialización

    V_i^1 = min_k C_ik (o max_k para ganancias).

    La política se deriva de esas decisiones inmediatas.

9.2 Iteración

    Para n = 2, 3, ...:

        Para cada estado i y decisión k:

            temp = C_ik + α * Σ_j P_{ij}(k) * V_j^{n-1}.

        V_i^n = min_k(temp) (o max).

    Se calcula max_diff = max_i |V_i^n - V_i^{n-1}|.

    Se agrega la iteración a una lista.

9.3 Criterio de parada

    Si max_diff < epsilon, se termina.

    O si se alcanza max_iter.

10. Módulo de Comparación de Métodos
10.1 Ejecución de los 5 algoritmos

    Se llaman uno por uno, midiendo el tiempo con time.perf_counter().

    Se almacenan las políticas resultantes en un diccionario resultados.

    Para cada método, se guardan sus métricas nativas:

        EE y PL: costo esperado.

        MP sin descuento: g (costo promedio).

        MP con descuento y AS: valores V (no tienen un costo escalar único).

10.2 Análisis de coincidencia

    Se convierten las políticas a tuplas ordenadas para poder usar Counter.

    Se determina la política más frecuente (moda).

    Si todas son iguales, se muestra "Coincidencia Total". Si no, se listan las discrepancias.

10.3 Tabla comparativa

    Columnas: Método, Política, Costo/Ganancia nativo, Iteraciones, Tiempo, Coincide.

    Se construye un DataFrame y se muestra con st.dataframe.

10.4 Consistencia por estado

    Se analiza, para cada estado, si todos los métodos eligen la misma decisión.

    Se genera una tabla con ✅ o ❌.

11. Módulo de Exportación a Excel
11.1 Generación del libro

    Se usa openpyxl.Workbook().

    Se elimina la hoja por defecto.

    Para cada módulo seleccionado, se crea una hoja con create_sheet().

11.2 Contenido de cada hoja

    Ingreso de Datos: Listas de estados/decisiones, tabla de costos, matrices de transición.

    Enumeración Exhaustiva: Política óptima y tabla de todas las políticas evaluadas.

    Programación Lineal: Función objetivo, restricciones, variables Y, coeficientes D.

    Mejoramiento de Políticas: Iteraciones con política, g, V.

    Mejoramiento con Descuento: α, iteraciones con V y política.

    Aproximaciones Sucesivas: Parámetros, iteraciones con V y política.

    Comparación: Tabla resumen de los 5 métodos.

    Agradecimientos: Texto simple.

11.3 Descarga

    El libro se guarda en BytesIO() y se ofrece con st.download_button.

12. Sistema de sesiones y persistencia
12.1 Centralización en guardado/sesion.py

    init_session(): Si "mdp" no está en st.session_state, lo crea vacío.

    get_mdp(): Retorna st.session_state.mdp (llama a init_session por seguridad).

    reset_mdp(): Elimina st.session_state.mdp y reinicia.

    mdp_completo(): Verifica que el modelo tenga todos los datos requeridos.

12.2 Compartición entre módulos

Todos los módulos importan get_mdp y acceden al mismo diccionario. Streamlit garantiza que st.session_state persiste durante toda la sesión del navegador.
12.3 Parámetros guardados automáticamente

Algunos módulos almacenan configuraciones para que la Comparación de Métodos no tenga que pedirlas de nuevo:

    eps_as, max_iter_as, alpha_as (desde Aproximaciones Sucesivas).

    alpha_descuento (desde Mejoramiento con Descuento).

13. Navegación, estilos y recursos visuales
13.1 Sistema de navegación

    Se usa st.navigation con un diccionario de grupos.

    Cada grupo contiene una lista de st.Page con ruta al archivo y título.

13.2 CSS personalizado

    Definido en app.py mediante st.markdown("<style>...</style>", unsafe_allow_html=True).

    Paleta: fondos oscuros (#0D1321, #0A0E1A), dorado (#F5A800), azul UNAM (#003F8A).

    Tipografías: Sora (textos), IBM Plex Mono (código/datos).

    Componentes reutilizables: .unam-card, .section-header, .badge-ok/warn/err, .chip.

13.3 Emojis e iconos

Cada módulo tiene un emoji asignado (📥, 📊, 🔍, 📈, 🔄, 💲, 🔁, ⚖️, 📤, 🙏). Se usan en la barra lateral y en las tarjetas del panel principal.
14. Resumen para exposición oral

Si necesitan explicar el proyecto en pocos minutos, sigan esta estructura:

    Objetivo: Herramienta para modelar y resolver MDPs por 5 métodos diferentes.

    Entrada de datos: Interfaz que acepta fracciones y valida consistencia.

    Visualización: Tablas de costos y grafo interactivo por decisión.

    Enumeración Exhaustiva: Evalúa todas las políticas (producto cartesiano).

    Programación Lineal: Resuelve con scipy.optimize.linprog.

    Mejoramiento de Políticas: Iteración evaluación-mejora hasta convergencia.

    Descuento: Variante con factor α.

    Aproximaciones Sucesivas: Value Iteration con tolerancia.

    Comparación: Ejecuta los 5 métodos y muestra coincidencias.

    Exportación: Genera un Excel con todos los resultados.
