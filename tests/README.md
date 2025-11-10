# 🧪 Sistema de Testing - PIMST

## 📋 Descripción

Suite completa de tests para el proyecto PIMST, incluyendo:
- ✅ Tests unitarios del sistema SiNo
- ✅ Tests de algoritmos base
- ✅ Tests de integración
- ✅ Tests de performance
- ✅ Fixtures reutilizables

---

## 🚀 Uso Rápido

### Ejecutar Todos los Tests

```bash
# Usando el script
python run_tests.py

# O directamente con pytest
pytest tests/ -v
```

### Ejecutar Tests Específicos

```bash
# Solo tests del SiNo
python run_tests.py --sino

# Solo tests de algoritmos
python run_tests.py --algorithms

# Un archivo específico
pytest tests/test_sino_system.py -v

# Una clase específica
pytest tests/test_sino_system.py::TestSiNoBasics -v

# Un test específico
pytest tests/test_sino_system.py::TestSiNoBasics::test_simple_solve -v
```

### Tests con Coverage

```bash
# Con el script
python run_tests.py --coverage

# Directamente
pytest tests/ --cov=src/pimst --cov-report=html --cov-report=term
```

Luego abre `htmlcov/index.html` en tu navegador.

---

## 📂 Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidos
├── test_sino_system.py      # Tests del sistema SiNo
├── test_algorithms.py       # Tests de algoritmos base
└── test_basic.py           # Tests básicos existentes
```

---

## 🧩 Archivos de Test

### test_sino_system.py

Tests completos del sistema SiNo:

- **TestSiNoBasics**: Funcionalidad básica
- **TestDecisionTypes**: Tipos de decisión (SI/SINO/NO)
- **TestSmartSelector**: Selector inteligente
- **TestBatchProcessing**: Procesamiento por lotes
- **TestPerformance**: Benchmarks de rendimiento
- **TestEdgeCases**: Casos extremos
- **TestIntegration**: Tests de integración

**Total**: 50+ tests

### test_algorithms.py

Tests de algoritmos PIMST:

- **TestAlgorithmPerformance**: Rendimiento de algoritmos
- **TestGravityAlgorithms**: Algoritmos basados en gravedad
- **TestVersionComparison**: Comparación de versiones
- **TestCandidateLists**: Listas de candidatos
- **TestUtilities**: Funciones utilitarias
- **TestRandomInstances**: Instancias aleatorias
- **TestEdgeCases**: Casos especiales

**Total**: 40+ tests

### conftest.py

Fixtures reutilizables:

- Matrices de distancia (tiny, small, medium, large)
- Coordenadas (círculos, grids, random)
- Instancias TSP variadas
- Herramientas de performance
- Configuración pytest

---

## 🎯 Tipos de Tests

### Tests Unitarios

```python
@pytest.mark.unit
def test_simple_function():
    result = simple_function(input)
    assert result == expected
```

### Tests de Integración

```python
@pytest.mark.integration
def test_full_workflow():
    # Test de flujo completo
    solver = SiNoSolver()
    result = solver.solve(distances)
    assert result.cost > 0
```

### Tests Lentos

```python
@pytest.mark.slow
def test_large_instance():
    # Test que toma tiempo
    distances = np.random.rand(1000, 1000)
    result = solve(distances)
```

---

## 🔧 Configuración

### pytest.ini

```ini
[pytest]
addopts = -v --strict-markers --tb=short
markers =
    slow: tests lentos
    integration: tests de integración
    unit: tests unitarios
    performance: benchmarks
```

### Opciones de Línea de Comando

```bash
# Solo tests rápidos (omitir lentos)
pytest tests/ -m "not slow"

# Solo tests de integración
pytest tests/ -m integration

# Solo tests unitarios
pytest tests/ -m unit

# Parar en el primer fallo
pytest tests/ -x

# Verbose máximo
pytest tests/ -vv

# Mostrar output de prints
pytest tests/ -s

# Ejecutar en paralelo (requiere pytest-xdist)
pytest tests/ -n auto
```

---

## 📊 Coverage Report

### Generar Reporte

```bash
pytest tests/ --cov=src/pimst --cov-report=html
```

### Ver Reporte

```bash
# Abrir en navegador
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Interpretar Resultados

- **Verde**: Líneas cubiertas por tests
- **Rojo**: Líneas sin cobertura
- **Amarillo**: Branches parcialmente cubiertos

Objetivo: **>80% coverage**

---

## 🎨 Fixtures Disponibles

### Matrices de Distancia

```python
def test_with_fixtures(small_distances, medium_distances):
    # small_distances: 10x10 matriz
    # medium_distances: 50x50 matriz
    pass
```

Fixtures disponibles:
- `tiny_distances` (3x3)
- `small_distances` (10x10)
- `medium_distances` (50x50)
- `large_distances` (100x100)

### Coordenadas

```python
def test_with_coords(circle_coords_small, random_coords):
    # circle_coords_small: 20 puntos en círculo
    # random_coords: 30 puntos aleatorios
    pass
```

Fixtures disponibles:
- `circle_coords_small` (20 nodos)
- `circle_coords_medium` (50 nodos)
- `random_coords` (30 nodos)
- `grid_coords` (25 nodos en grid 5x5)

### Helpers

```python
def test_conversion(coords_to_dist):
    coords = np.array([[0,0], [1,0]])
    distances = coords_to_dist(coords)
    assert distances.shape == (2, 2)
```

---

## 🐛 Debugging Tests

### Con PDB

```bash
# Entrar en debugger al fallar
pytest tests/ --pdb

# Entrar en debugger al inicio
pytest tests/ --trace
```

### Con Print Statements

```bash
# Mostrar prints durante tests
pytest tests/ -s

# Mostrar prints solo de tests que fallan
pytest tests/ --tb=short
```

### Tests Individuales

```bash
# Ver más detalle de un test
pytest tests/test_sino_system.py::TestSiNoBasics::test_simple_solve -vv -s
```

---

## ✅ Best Practices

### 1. Nombrar Tests Descriptivamente

```python
# ❌ Mal
def test_1():
    pass

# ✅ Bien
def test_sino_solver_handles_small_instances():
    pass
```

### 2. Usar Fixtures para Datos Comunes

```python
# ❌ Mal
def test_a():
    data = create_data()
    # test...

def test_b():
    data = create_data()
    # test...

# ✅ Bien
@pytest.fixture
def data():
    return create_data()

def test_a(data):
    # test...

def test_b(data):
    # test...
```

### 3. Tests Independientes

```python
# ❌ Mal - tests dependen entre sí
global_state = None

def test_setup():
    global global_state
    global_state = initialize()

def test_use():
    # Depende de test_setup
    assert global_state is not None

# ✅ Bien - tests independientes
@pytest.fixture
def state():
    return initialize()

def test_use(state):
    assert state is not None
```

### 4. Assertions Claras

```python
# ❌ Mal
assert len(tour) == 50

# ✅ Bien
assert len(tour) == 50, f"Expected tour of length 50, got {len(tour)}"
```

---

## 📈 Agregar Nuevos Tests

### Plantilla de Test

```python
import pytest
import numpy as np
from pimst.improved.sino import SiNoSolver

class TestMiNuevaFeature:
    """Tests para mi nueva feature."""
    
    def test_funcionalidad_basica(self):
        """Test básico de la feature."""
        # Arrange
        solver = SiNoSolver()
        distances = np.random.rand(10, 10)
        
        # Act
        result = solver.solve(distances)
        
        # Assert
        assert result.cost > 0
        assert len(result.tour) == 10
    
    def test_caso_extremo(self):
        """Test de caso extremo."""
        # ...
    
    @pytest.mark.slow
    def test_performance(self):
        """Test de performance."""
        # ...
```

### Agregar al Suite

1. Crear archivo: `tests/test_mi_feature.py`
2. Escribir tests
3. Ejecutar: `pytest tests/test_mi_feature.py -v`
4. Commit y push

---

## 🔍 Continuous Integration

Los tests se ejecutan automáticamente en GitHub Actions:

### Workflow (`.github/workflows/tests.yml`)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=src/pimst
```

### Ver Resultados

1. Ve a tu repositorio en GitHub
2. Click en la pestaña "Actions"
3. Verás el estado de los tests

---

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Pytest Markers](https://docs.pytest.org/en/stable/example/markers.html)

---

## 🆘 Troubleshooting

### Tests no encuentran módulos

```bash
# Instalar en modo desarrollo
pip install -e .
```

### Fixtures no funcionan

```bash
# Verificar que conftest.py está en tests/
ls tests/conftest.py
```

### Coverage bajo

```bash
# Ver líneas sin cobertura
pytest tests/ --cov=src/pimst --cov-report=term-missing
```

---

## ✨ Contribuir

Para añadir tests:

1. Crea tu feature branch
2. Añade tests en `tests/`
3. Ejecuta `pytest tests/ -v`
4. Asegúrate de que todos pasen
5. Crea Pull Request

---

**¡Happy Testing! 🧪**
