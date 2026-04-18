LÓGICA INTERNA DE LA HERRAMIENTA MDP

Este documento explica cómo se implementaron internamente las estructuras de datos
y los algoritmos matemáticos para modelar y resolver Procesos Markovianos de
Decisión (MDP). Está dirigido a quien desee comprender la mecánica detrás de la
aplicación, sin necesidad de leer el código fuente línea por línea.


1. ALMACENAMIENTO DEL MODELO MDP

El modelo completo se guarda en un diccionario de Python con la siguiente
estructura:

mdp = {
    "estados": ["s0", "s1", ...],               # lista de nombres
    "decisiones": ["d1", "d2", ...],            # lista de nombres
    "tipo": "costos" | "ganancias",             # objetivo
    "decisiones_data": {
        "d1": {
            "estados_afectados": ["s0", "s1"],  # estados donde aplica d1
            "costos": {"s0": 10.0, "s1": 5.0},  # costo/ganancia por estado
            "transiciones": {                   # matriz de transición para d1
                "s0": {"s0": 0.5, "s1": 0.5},
                "s1": {"s0": 0.8, "s1": 0.2}
            }
        },
        ...
    }
}

Esta estructura permite acceder rápidamente a los datos de cualquier decisión y
estado, y es fácil de serializar. La validación de completitud comprueba que:
- Existan estados y decisiones.
- Toda decisión tenga al menos un estado afectado.
- Cada estado afectado tenga un costo/ganancia definido.
- Las probabilidades desde cada estado afectado sumen 1.0 (con tolerancia 1e-6).


2. GENERACIÓN DE POLÍTICAS DETERMINISTAS

Una política determinista es una regla que asigna exactamente una decisión a cada
estado. Se generan mediante el producto cartesiano de las opciones disponibles
por estado.

Para cada estado, se recopilan las decisiones que lo afectan. Luego se calcula
itertools.product(*lista_de_opciones). Cada combinación se convierte en un
diccionario {estado: decisión} y se almacena en una lista. El número total de
políticas es el producto del número de opciones en cada estado.

Ejemplo: 2 estados, s0 con opciones {d1, d2} y s1 con opciones {d1}. Se generan
2 políticas: {s0:d1, s1:d1} y {s0:d2, s1:d1}.


3. EVALUACIÓN DE UNA POLÍTICA

Dada una política π (mapeo estado→decisión), se evalúa en tres pasos:

3.1 Construcción de la matriz de transición P y vector de costos c
    - Se crea una matriz cuadrada P de tamaño n×n (n = número de estados).
    - Para cada estado i, se toma la decisión d = política[i] y se copian las
      probabilidades de transición desde i hacia todos los destinos j.
    - Simultáneamente se llena el vector c[i] con el costo/ganancia de aplicar
      la decisión d en el estado i.

3.2 Cálculo de probabilidades estacionarias
    Las probabilidades estacionarias π (vector fila de tamaño n) deben cumplir:
        π = π · P
        Σ π_i = 1

    Esto es un sistema lineal homogéneo. Se transforma a:
        (I - Pᵀ) π = 0
    junto con la ecuación de normalización Σ π_i = 1.

    Como el sistema original tiene rango n-1, se descarta una ecuación de
    balance (la última) y se añade la normalización, obteniendo un sistema
    cuadrado de n ecuaciones.

    En la práctica, construimos la matriz A (n×n) donde las primeras n-1 filas
    corresponden a (I - Pᵀ) y la última fila es [1,1,...,1]. El vector b es
    [0,0,...,0,1]. Resolvemos A·π = b usando numpy.linalg.solve. Si la matriz
    es singular (determinante cercano a cero), se captura el error y la política
    se marca como "sin solución".

3.3 Cálculo del valor esperado
    Con el vector π y el vector de costos/ganancias c, el valor esperado es:
        E = Σ (π_i · c_i)   para i = 0..n-1

    Si el modelo es de costos, buscamos minimizar E; si es de ganancias,
    maximizar.


4. RESOLUCIÓN MANUAL CON GAUSS-JORDAN (OPCIONAL)

Para mostrar los pasos intermedios en la interfaz, se implementó una versión
manual del método de Gauss‑Jordan usando fracciones (para evitar errores de
redondeo). El procedimiento es:

- Convertir la matriz A aumentada a fracciones (Fraction).
- Para cada columna pivote:
    a. Buscar la fila con el mayor valor absoluto en esa columna (pivoteo parcial).
    b. Intercambiar filas si es necesario.
    c. Dividir toda la fila del pivote por el valor del pivote.
    d. Eliminar los elementos de las demás filas en esa columna restando
       múltiplos de la fila pivote.
- Al finalizar, la columna de términos independientes contiene la solución π.

Cada operación se guarda junto con una copia de la matriz, permitiendo luego
renderizar los pasos en la UI.


5. MANEJO DE FRACCIONES EN LA ENTRADA DE DATOS

Los campos numéricos aceptan expresiones como "1/3" o "0.5". Una función auxiliar
detecta la presencia del carácter '/' y divide los operandos; de lo contrario
convierte a float. Al guardar, el valor se almacena como float, pero al mostrar
valores existentes se usa Fraction para representarlos como fracción exacta
(ej. 0.3333 -> 1/3) si el denominador es pequeño.


6. DETECCIÓN DE ARISTAS BIDIRECCIONALES EN EL GRAFO

Para el grafo interactivo se construye una lista de aristas con Cytoscape.js.
Antes de renderizar, se agrupan las aristas por par ordenado (origen, destino).
- Si hay más de una arista entre el mismo par, se asigna color azul a la primera
  y dorado a la segunda.
- Si existe la arista opuesta (A→B y B→A), se asigna azul a una dirección y
  dorado a la otra, según el orden lexicográfico de los nombres de los estados.

Esto permite distinguir visualmente la dirección en pares bidireccionales.


7. ANÁLISIS COMPARATIVO DE POLÍTICAS

Después de evaluar todas las políticas seleccionadas, se genera una tabla con:
- Nombre de la política.
- Decisiones que toma.
- Valor esperado.
- Diferencia absoluta y porcentual respecto a la política óptima.

Se ordenan de mejor a peor (menor costo o mayor ganancia). Además se grafican
las barras horizontales y se extraen estadísticas como la subóptima más cercana
y la más alejada.


Con estos fundamentos se puede entender el funcionamiento interno de la
herramienta, facilitando su mantenimiento, extensión o uso académico.
