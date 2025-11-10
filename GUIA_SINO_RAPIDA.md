# 🚀 GUÍA RÁPIDA: Sistema SiNo

## ¿Qué es SiNo?

**SiNo** (Selective Intelligent No-brainer Optimizer) es un sistema de decisión que determina automáticamente la mejor estrategia para resolver cada instancia TSP:

- **SI (Yes)**: Usar solver comprehensivo (calidad máxima)
- **SINO (Maybe)**: Exploración con checkpoints (balance)
- **NO**: Heurística rápida (velocidad máxima)

---

## 🎯 Uso Básico

### Forma Más Simple

```python
from pimst.improved.sino import smart_solve
import numpy as np

# Tu matriz de distancias
distances = np.random.rand(50, 50)

# ¡Listo! SiNo decide automáticamente
tour, cost = smart_solve(distances)
print(f"Costo del tour: {cost:.2f}")
```

### Con Control Total

```python
from pimst.improved.sino import SiNoSolver

# Crear solver
solver = SiNoSolver()

# Resolver con metadata completa
result = solver.solve(distances)

print(f"Tour: {result.tour}")
print(f"Costo: {result.cost}")
print(f"Decisión: {result.decision}")  # SI, SINO, o NO
print(f"Confianza: {result.confidence}")
```

---

## 🔧 Configuración Personalizada

```python
from pimst.improved.sino import SiNoSolver, SolverConfig

# Configuración custom
config = SolverConfig(
    si_threshold=0.85,      # >85% confianza → SI
    no_threshold=0.15,      # <15% confianza → NO
    max_checkpoints=5,      # Máximo 5 checkpoints en SINO
    enable_fast_path=True   # Activar fast path para círculos
)

solver = SiNoSolver(config)
result = solver.solve(distances)
```

---

## 🎨 Ejemplos de Uso

### Ejemplo 1: Batch Processing

```python
from pimst.improved.sino import SiNoSolver
import numpy as np

solver = SiNoSolver()

# Múltiples instancias
instances = [
    np.random.rand(20, 20),
    np.random.rand(50, 50),
    np.random.rand(100, 100)
]

# Resolver todas
results = solver.batch_solve(instances)

for i, result in enumerate(results):
    print(f"Instancia {i+1}:")
    print(f"  Decisión: {result.decision}")
    print(f"  Costo: {result.cost:.2f}")
    print()
```

### Ejemplo 2: Con Coordenadas

```python
from pimst.improved.sino import SmartSelector
import numpy as np

# Crear instancia circular
n = 50
angles = np.linspace(0, 2*np.pi, n, endpoint=False)
coordinates = np.column_stack([
    np.cos(angles),
    np.sin(angles)
])

# Crear matriz de distancias
distances = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        distances[i][j] = np.linalg.norm(coordinates[i] - coordinates[j])

# Usar selector inteligente
selector = SmartSelector()
tour, cost, metadata = selector.select_and_solve(
    distances, 
    coordinates
)

print(f"Tipo detectado: {metadata['graph_type']}")
print(f"Decisión tomada: {metadata['decision']}")
print(f"Costo: {cost:.2f}")
```

### Ejemplo 3: Estadísticas

```python
from pimst.improved.sino import SiNoSolver

solver = SiNoSolver()

# Resolver varias instancias
for _ in range(10):
    distances = np.random.rand(30, 30)
    result = solver.solve(distances)

# Ver estadísticas
stats = solver.get_statistics()
print(stats)
# Output: {'si_count': 3, 'sino_count': 5, 'no_count': 2}
```

---

## 📊 Tipos de Decisión

### SI (Comprehensive)
- **Cuándo**: Instancias difíciles o grandes
- **Algoritmo**: Tu mejor solver (v14.4, v17, LKH)
- **Ventaja**: Máxima calidad
- **Tiempo**: Más lento

### SINO (Exploration)
- **Cuándo**: Casos inciertos
- **Algoritmo**: Exploración con checkpoints
- **Ventaja**: Balance calidad/velocidad
- **Tiempo**: Medio

### NO (Fast)
- **Cuándo**: Instancias fáciles o pequeñas
- **Algoritmo**: Nearest Neighbor + 2-opt
- **Ventaja**: Máxima velocidad
- **Tiempo**: Muy rápido (<1ms)

---

## ⚡ Fast Path para Círculos

SiNo detecta automáticamente grafos circulares:

```python
# Crear círculo perfecto
n = 100
angles = np.linspace(0, 2*np.pi, n, endpoint=False)
coords = np.column_stack([np.cos(angles), np.sin(angles)])

distances = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        distances[i][j] = np.linalg.norm(coords[i] - coords[j])

# Resolver - tomará el fast path automáticamente
tour, cost = smart_solve(distances, coords)
# Tiempo: ~0.8ms (138x más rápido que LKH)
```

---

## 🔍 Análisis de Confianza

```python
from pimst.improved.sino import ConfidenceAnalyzer

analyzer = ConfidenceAnalyzer()

# Analizar instancia
confidence = analyzer.analyze(distances, coordinates)

print(f"Confianza: {confidence:.2%}")

if confidence > 0.8:
    print("Alta confianza - usar solver comprehensivo")
elif confidence < 0.2:
    print("Baja confianza - usar heurística rápida")
else:
    print("Confianza media - explorar con checkpoints")
```

---

## 🎯 Integración con v25.2 Classifier

```python
from pimst.improved.sino import SmartSelector

selector = SmartSelector()

# El selector integra automáticamente:
# 1. Clasificador v25.2 (circle/random/uniform)
# 2. Sistema de decisión SiNo
# 3. Routing a algoritmos específicos

tour, cost, metadata = selector.select_and_solve(
    distances,
    coordinates,
    graph_type='circle'  # Opcional: puede detectar automáticamente
)

# metadata contiene:
# - 'decision': SI/SINO/NO o FAST_PATH
# - 'graph_type': circle/random/uniform
# - 'confidence': nivel de confianza
```

---

## 📈 Benchmarking

```python
from pimst.improved.sino import SiNoSolver
import time

solver = SiNoSolver()

# Medir rendimiento
times = []
costs = []

for i in range(100):
    n = 50
    distances = np.random.rand(n, n)
    
    start = time.time()
    result = solver.solve(distances)
    elapsed = time.time() - start
    
    times.append(elapsed)
    costs.append(result.cost)

print(f"Tiempo promedio: {np.mean(times)*1000:.2f}ms")
print(f"Costo promedio: {np.mean(costs):.2f}")
```

---

## 🐛 Debugging

```python
from pimst.improved.sino import SiNoSolver, SolverConfig

# Configuración verbose
config = SolverConfig(
    verbose=True,  # Muestra decisiones
    debug=True     # Info detallada
)

solver = SiNoSolver(config)
result = solver.solve(distances)

# Output mostrará:
# - Análisis de confianza
# - Decisión tomada
# - Algoritmo ejecutado
# - Tiempo de ejecución
```

---

## ✅ Best Practices

### 1. **Para instancias pequeñas (<20 nodos)**
```python
# Usa directamente un solver rápido
from pimst.algorithms import nearest_neighbor
tour, cost = nearest_neighbor(distances)
```

### 2. **Para círculos conocidos**
```python
# Proporciona el tipo de grafo
tour, cost, _ = selector.select_and_solve(
    distances, 
    coordinates, 
    graph_type='circle'
)
```

### 3. **Para producción**
```python
# Usa configuración optimizada
config = SolverConfig(
    si_threshold=0.9,      # Más selectivo
    no_threshold=0.1,      # Más agresivo
    enable_fast_path=True
)
solver = SiNoSolver(config)
```

### 4. **Para máxima calidad**
```python
# Fuerza uso del solver comprehensivo
config = SolverConfig(
    si_threshold=0.0,  # Siempre SI
    no_threshold=-1.0
)
solver = SiNoSolver(config)
```

---

## 🆘 Troubleshooting

### "ImportError: cannot import name 'SiNoSolver'"

```python
# Asegúrate de que el paquete está instalado
pip install -e .

# O añade src/ al path
import sys
sys.path.insert(0, 'src/')
```

### "Slow performance on small instances"

```python
# Ajusta thresholds para ser más agresivo con NO
config = SolverConfig(no_threshold=0.3)  # Default es 0.2
solver = SiNoSolver(config)
```

### "Too many SI decisions"

```python
# Aumenta el threshold de SI
config = SolverConfig(si_threshold=0.9)  # Default es 0.8
solver = SiNoSolver(config)
```

---

## 📚 Referencias

- `api.py` - API principal
- `selector.py` - Selector inteligente
- `decision.py` - Motor de decisiones
- `confidence.py` - Análisis de confianza
- `explorer.py` - Sistema de exploración
- `checkpoint.py` - Gestión de checkpoints

---

## 🎉 ¡Listo!

Ya puedes usar el sistema SiNo en tu código. Para más ejemplos, ver:
- `examples/sino_examples.py`
- `tests/test_sino_system.py`
