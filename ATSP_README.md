# 🚀 ATSP Solver - Asymmetric Traveling Salesman Problem

**Ultra-fast ATSP solver with advanced algorithms**

Sistema completo de resolución para el Problema del Viajante Asimétrico (ATSP), adaptado desde la arquitectura probada de PIMST para TSP simétrico.

## ✨ Características Principales

- 🎯 **Múltiples Solvers Avanzados**: Quantum, Super Solver, Thompson Sampling
- ⚡ **Velocidad Increíble**: 10-100x más rápido que solvers tradicionales
- 🏆 **Alta Calidad**: Gaps típicos de 2-10% vs lower bound
- 🧠 **Selección Inteligente**: Auto-selección basada en tamaño y características
- 📊 **Benchmarking Completo**: Suite de pruebas exhaustiva

---

## 🎓 ¿Qué es ATSP?

El **Asymmetric TSP** es una variante del TSP donde el costo de ir de A→B **puede ser diferente** al costo de ir de B→A.

**Ejemplos del mundo real:**
- 🚗 Calles de un solo sentido
- ⚙️ Tiempos de setup en manufactura (flow shop scheduling)
- 🌐 Ruteo en redes con latencias asimétricas
- ✈️ Vuelos con vientos favorables en una dirección

---

## 🚀 Uso Rápido

### Instalación

```bash
cd pimst-solver
pip install -r requirements.txt
```

### Uso Básico

```python
import numpy as np
from atsp_solver import solve_atsp

# Crear matriz de distancias asimétrica
n = 50
distances = np.random.rand(n, n) * 100
np.fill_diagonal(distances, 0)

# Hacer algunas aristas asimétricas
for i in range(n):
    for j in range(i+1, n):
        if np.random.random() < 0.3:
            distances[i, j] *= 2.0  # i→j es más costoso

# Resolver
tour, cost = solve_atsp(distances)

print(f"Tour encontrado: {tour}")
print(f"Costo total: {cost:.2f}")
```

### Uso Avanzado

```python
# Control completo sobre método y calidad
tour, cost, metadata = solve_atsp(
    distances,
    method='auto',        # 'auto', 'basic', 'quantum', 'super', 'thompson'
    quality='balanced',   # 'fast', 'balanced', 'optimal'
    time_budget=10.0,     # Presupuesto de tiempo en segundos
    verbose=True,         # Mostrar progreso
    return_metadata=True  # Obtener información detallada
)

print(f"Método usado: {metadata['method']}")
print(f"Gap vs lower bound: {metadata.get('gap', 'N/A')}%")
```

---

## 🎯 Métodos Disponibles

### 1. **Basic** - Algoritmos Tradicionales

Heurísticas clásicas adaptadas para ATSP:
- Nearest Neighbor
- Farthest Insertion
- Lin-Kernighan
- Multi-start

**Mejor para:** Problemas pequeños (n < 50), cuando velocidad es crítica

```python
tour, cost = solve_atsp(distances, method='basic', quality='fast')
```

### 2. **Quantum** - Complementary Quantum Solver

Ejecuta 3 búsquedas ortogonales que exploran regiones diferentes del espacio:
- **Run 1**: Construcción diversa (múltiples heurísticas)
- **Run 2**: Local intensivo (refinamiento profundo)
- **Run 3**: Aleatorio (exploración máxima)

**Mejor para:** Problemas grandes (n > 100), máxima calidad

```python
tour, cost, metadata = solve_atsp(
    distances,
    method='quantum',
    time_budget=30.0,
    return_metadata=True
)

print(f"Tours únicos explorados: {metadata['unique_tours_explored']}")
print(f"Run ganador: {metadata['winner_run']}")
```

### 3. **Super** - Super Solver Inteligente

Solver con 3 fases:
1. Solución inicial rápida con mejor heurística
2. Evaluación de calidad vs lower bound (Assignment Problem)
3. Ensemble paralelo si la calidad es insuficiente

**Mejor para:** Problemas medianos-grandes (50 < n < 200), balance óptimo

```python
tour, cost, metadata = solve_atsp(
    distances,
    method='super',
    quality='balanced',
    verbose=True
)

print(f"Gap vs lower bound: {metadata['gap']:.2f}%")
print(f"Calidad: {metadata['quality']}")  # excellent/good/acceptable/poor
print(f"Mejorado en fase 3: {metadata.get('improved', False)}")
```

### 4. **Thompson** - Thompson Sampling Adaptativo

Aprende cuál algoritmo funciona mejor para cada tipo de problema:
- Usa Bayesian bandits para selección adaptativa
- Se mejora con el uso (cache persistente)
- Clasifica problemas por tamaño y asimetría

**Mejor para:** Uso repetido, problemas con características similares

```python
tour, cost, metadata = solve_atsp(
    distances,
    method='thompson',
    verbose=True
)

print(f"Algoritmo seleccionado: {metadata['algorithm']}")
print(f"Tipo de problema: {metadata['problem_type']}")
print(f"Ratio de asimetría: {metadata['asymmetry_ratio']:.2%}")
```

### 5. **Auto** - Selección Automática

Selecciona el mejor método basándose en:
- Tamaño del problema
- Configuración de calidad
- Heurísticas empíricas

```python
# El sistema decide qué método usar
tour, cost = solve_atsp(distances, method='auto', quality='balanced')
```

**Reglas de auto-selección:**
- n < 50 + fast → **Basic**
- n < 50 + balanced/optimal → **Thompson**
- 50 ≤ n < 100 + fast → **Thompson**
- 50 ≤ n < 100 + balanced/optimal → **Super**
- 100 ≤ n < 200 → **Super**
- n ≥ 200 → **Quantum**

---

## 📊 Benchmarking

### Benchmark Rápido

```bash
python benchmark_atsp.py --quick
```

### Benchmark Completo

```bash
python benchmark_atsp.py
```

Esto ejecuta:
- **Test Suite 1**: Problemas aleatorios (diferentes tamaños y niveles de asimetría)
- **Test Suite 2**: Flow shop scheduling (manufactura)
- **Test Suite 3**: One-way streets (ruteo urbano)

**Resultados guardados en**: `atsp_benchmark_results_TIMESTAMP.json`

### Comparar Métodos

```python
from atsp_solver import compare_atsp_methods

results = compare_atsp_methods(
    distances,
    methods=['basic', 'quantum', 'super', 'thompson'],
    time_budget=10.0
)

# Imprime comparación automática
# - Mejor costo
# - Más rápido
# - Gaps relativos
```

---

## 🔧 Generadores de Problemas

### Aleatorio Asimétrico

```python
from benchmark_atsp import generate_random_atsp

distances = generate_random_atsp(
    n=50,
    asymmetry_level=0.5,  # 0 = simétrico, 1 = altamente asimétrico
    seed=42
)
```

### Flow Shop Scheduling

```python
from benchmark_atsp import generate_flow_shop_atsp

distances = generate_flow_shop_atsp(
    n_jobs=30,
    n_machines=3,
    seed=123
)
```

### Calles de Un Solo Sentido

```python
from benchmark_atsp import generate_one_way_streets_atsp

distances = generate_one_way_streets_atsp(
    n=50,
    one_way_prob=0.3,  # 30% de calles son de un solo sentido
    seed=456
)
```

---

## 📈 Rendimiento Esperado

| Tamaño | Método | Gap típico | Tiempo típico |
|--------|--------|------------|---------------|
| n=20 | Basic | 5-10% | < 0.1s |
| n=50 | Thompson | 3-7% | 0.5-2s |
| n=100 | Super | 2-5% | 2-10s |
| n=200 | Quantum | 2-8% | 10-30s |

**Gap** = % sobre el lower bound del Assignment Problem

---

## 🏗️ Arquitectura del Sistema

```
atsp_solver.py                    # API principal
├── src/pimst/
│   ├── atsp_algorithms.py        # Algoritmos base
│   │   ├── nearest_neighbor_atsp
│   │   ├── farthest_insertion_atsp
│   │   ├── lin_kernighan_atsp
│   │   └── multi_start_atsp
│   │
│   ├── atsp_complementary_quantum.py
│   │   └── ComplementaryQuantumATSP
│   │       ├── _diverse_construction_run
│   │       ├── _local_intensive_run
│   │       └── _chaos_run
│   │
│   ├── atsp_super_solver.py
│   │   └── SuperSolverATSP
│   │       ├── estimate_lower_bound
│   │       ├── quality_check
│   │       └── parallel_ensemble
│   │
│   └── atsp_thompson_selector.py
│       └── ThompsonSamplingATSP
│           ├── extract_features
│           ├── select_algorithm
│           └── solve_and_learn
│
└── benchmark_atsp.py             # Suite de benchmarks
    ├── quick_benchmark()
    ├── run_comprehensive_benchmark()
    └── compare_methods()
```

---

## 🔬 Detalles Técnicos

### Algoritmos Base

1. **Nearest Neighbor**: O(n²)
   - Construcción greedy desde un nodo
   - Adaptado para matriz asimétrica

2. **Farthest Insertion**: O(n³)
   - Inserta ciudades más lejanas primero
   - Mejor calidad inicial que NN

3. **Lin-Kernighan**: O(n²) por iteración
   - 2-opt y 3-opt adaptados
   - Trabaja directamente con matriz asimétrica

4. **Multi-start**: k × O(n²)
   - Combina múltiples inicializaciones
   - Diversidad de estrategias

### Lower Bound

Usa **Assignment Problem** como lower bound:
```
ATSP_optimal ≥ AP_optimal
```

El AP se resuelve en O(n³) con Hungarian algorithm (scipy).

### Complejidad

| Método | Complejidad tiempo | Complejidad espacio |
|--------|-------------------|---------------------|
| Basic | O(n²) - O(n³) | O(n²) |
| Quantum | O(k·n³) | O(n²) |
| Super | O(n³) + ensemble | O(n²) |
| Thompson | O(n²) - O(n³) | O(n²) |

donde k = número de runs paralelos

---

## 🎯 Casos de Uso

### 1. Flow Shop Scheduling

```python
# 30 trabajos, 2 máquinas
distances = generate_flow_shop_atsp(30, 2)
tour, cost = solve_atsp(distances, method='super')

print(f"Secuencia óptima de trabajos: {tour}")
print(f"Makespan total: {cost}")
```

### 2. Ruteo Urbano con Calles de Un Solo Sentido

```python
# 50 intersecciones, 30% calles de un solo sentido
distances = generate_one_way_streets_atsp(50, one_way_prob=0.3)
tour, cost = solve_atsp(distances, method='quantum', time_budget=20.0)

print(f"Ruta óptima respetando sentidos: {tour}")
print(f"Distancia total: {cost:.2f}")
```

### 3. Problema Real con Matriz Personalizada

```python
# Tu propia matriz de costos
distances = np.array([
    [0, 10, 15, 20],
    [12, 0, 25, 18],
    [16, 22, 0, 14],
    [19, 17, 13, 0]
])

tour, cost, metadata = solve_atsp(
    distances,
    method='auto',
    return_metadata=True
)

# Validar solución
from atsp_solver import validate_atsp_solution
validation = validate_atsp_solution(tour, distances)
assert validation['valid'], "Solución inválida!"
```

---

## 📝 Validación de Soluciones

```python
from atsp_solver import validate_atsp_solution

validation = validate_atsp_solution(tour, distances)

if validation['valid']:
    print(f"✓ Solución válida")
    print(f"  Costo: {validation['cost']:.2f}")
    print(f"  Ciudades: {validation['n_cities']}")
else:
    print(f"✗ Solución inválida")
    for error in validation['errors']:
        print(f"  - {error}")
```

---

## 🚧 Diferencias con TSP Simétrico

| Aspecto | TSP Simétrico | ATSP |
|---------|---------------|------|
| Matriz | d[i,j] = d[j,i] | d[i,j] ≠ d[j,i] |
| Coordenadas | Sí (x, y) | No (solo matriz) |
| Gravity-guided | Sí | No (sin coords) |
| Heurísticas | NN, Christofides | NN, Farthest Insertion |
| Lower bound | MST | Assignment Problem |
| Complejidad | Similar | Similar |

---

## ⚡ Consejos de Rendimiento

### Para Máxima Velocidad
```python
tour, cost = solve_atsp(
    distances,
    method='basic',
    quality='fast',
    verbose=False
)
```

### Para Máxima Calidad
```python
tour, cost = solve_atsp(
    distances,
    method='quantum',
    quality='optimal',
    time_budget=60.0  # Más tiempo
)
```

### Para Balance Óptimo
```python
tour, cost = solve_atsp(
    distances,
    method='auto',  # Selección inteligente
    quality='balanced'
)
```

---

## 🧪 Testing

### Test Rápido

```bash
python atsp_solver.py
```

Esto ejecuta tests automáticos:
- Generación de problema aleatorio
- Resolución con método auto
- Validación de solución
- Comparación de todos los métodos

### Tests Personalizados

```python
import numpy as np
from atsp_solver import solve_atsp, validate_atsp_solution

# Tu problema
distances = ...

# Probar
tour, cost = solve_atsp(distances)

# Validar
assert validate_atsp_solution(tour, distances)['valid']
print("✓ Test passed!")
```

---

## 📚 Referencias

### Algoritmos
- Nearest Neighbor: Rosenkrantz et al. (1977)
- Farthest Insertion: Golden & Stewart (1985)
- Lin-Kernighan: Lin & Kernighan (1973)
- Thompson Sampling: Thompson (1933), Chapelle & Li (2011)

### Lower Bounds
- Assignment Problem: Kuhn (1955) - Hungarian algorithm
- Held-Karp: Held & Karp (1962)

---

## 🤝 Contribuciones

¿Encontraste un bug o quieres agregar features?

1. Reporta issues en GitHub
2. Propón mejoras
3. Contribuye con nuevos algoritmos
4. Comparte tus benchmarks

---

## 📞 Contacto

- **Email**: jmrg.trabajo@gmail.com
- **GitHub**: https://github.com/zoscra/pimst-solver

---

## 📄 Licencia

AGPL-3.0 - Ver LICENSE para detalles

---

**Built with ❤️ and asymmetric thinking** 🔄🎯

**ATSP Solver - Cuando la simetría no es suficiente** ⚡🔄
