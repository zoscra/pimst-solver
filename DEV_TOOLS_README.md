# 🛠️ Herramientas de Desarrollo PIMST

Este documento describe todas las herramientas disponibles para el desarrollo, testing y benchmarking de PIMST.

## 📋 Tabla de Contenidos

- [Scripts de Testing](#scripts-de-testing)
- [Scripts de Benchmarking](#scripts-de-benchmarking)
- [Scripts de Comparación](#scripts-de-comparación)
- [Gestión de Versiones](#gestión-de-versiones)
- [Rastreo de Rendimiento](#rastreo-de-rendimiento)
- [Workflows Recomendados](#workflows-recomendados)

---

## 🧪 Scripts de Testing

### `quick_test.sh` - Tests Rápidos Pre-Commit

**Propósito**: Ejecutar tests rápidos antes de hacer commit para asegurar calidad.

**Uso**:
```bash
./quick_test.sh
```

**Qué hace**:
- ✅ Tests unitarios con pytest
- ✅ Code coverage (>70% requerido)
- ✅ Type checking con mypy (si está instalado)
- ✅ Linting con flake8 (si está instalado)
- ✅ Test de rendimiento rápido (N=30, N=50)

**Tiempo**: ~1-2 minutos

**Cuándo usar**: Antes de cada commit importante

---

## 🏃 Scripts de Benchmarking

### `benchmark_suite.sh` - Suite Completa de Benchmarks

**Propósito**: Ejecutar benchmarks completos con menú interactivo.

**Uso**:
```bash
./benchmark_suite.sh
```

**Opciones disponibles**:
1. **Quick Test** (1 min) - Tests unitarios rápidos
2. **Small Benchmark** (5-10 min) - Instancias N≤100 vs OR-Tools
3. **Large Benchmark** (20-40 min) - Instancias N=200-1000
4. **Market Compare** (30-60 min) - Comparación completa con el mercado
5. **Full Suite** (60-120 min) - Todos los benchmarks
6. **Custom** - Selección personalizada

**Output**: Crea carpeta `benchmark_results/session_TIMESTAMP/` con todos los resultados.

**Características**:
- 📊 Menú interactivo
- 📁 Organización automática de resultados
- 📝 Logs detallados de cada ejecución
- 📈 Generación de reporte resumen
- 🎨 Colores en terminal para mejor visualización

---

### `benchmark_comparison.py` - Benchmark vs OR-Tools

**Propósito**: Comparación detallada con Google OR-Tools en instancias pequeñas/medianas.

**Uso**:
```bash
python benchmark_comparison.py
```

**Qué hace**:
- Genera 11 datasets diversos (random, clustered, grid, circle)
- Compara PIMST (fast, balanced, optimal) vs OR-Tools
- Calcula gaps, speedups y estadísticas
- Guarda resultados en JSON y genera BENCHMARK_SUMMARY.md

**Output**:
- `benchmark_results.json` - Resultados detallados
- `BENCHMARK_SUMMARY.md` - Resumen en Markdown

**Tiempo**: 5-10 minutos

---

### `benchmark_large_scale.py` - Benchmark de Gran Escala

**Propósito**: Testing en instancias grandes (N=200-1000).

**Uso**:
```bash
python benchmark_large_scale.py
```

**Qué hace**:
- Genera instancias de 200, 500 y 1000 ciudades
- Prueba diferentes tipos (random, clustered, grid, circle)
- Analiza escalabilidad y complejidad temporal
- Compara con resultados publicados de LKH

**Output**:
- `large_benchmark_results.json`

**Tiempo**: 20-40 minutos

---

### `compare_with_market.py` - Comparación Completa con el Mercado

**Propósito**: Comparar PIMST con TODOS los solvers disponibles.

**Uso**:
```bash
python compare_with_market.py
```

**Qué compara**:
- Google OR-Tools (siempre)
- Python-TSP exact y SA (si está instalado)
- LKH-3 (si está compilado)

**Qué hace**:
- Detecta automáticamente solvers disponibles
- Ejecuta comparación completa
- Genera estadísticas detalladas
- Guarda resultados timestamped

**Output**:
- `comparison_results/market_comparison_TIMESTAMP.json`

**Tiempo**: 30-60 minutos

---

## 🔍 Scripts de Comparación

### `compare_versions.py` - Comparar Dos Versiones

**Propósito**: Comparar resultados de benchmark entre dos versiones.

**Uso básico**:
```bash
# Comparar dos archivos
python compare_versions.py v0.21.0_results.json v0.22.0_results.json

# Comparar todos los archivos en un directorio
python compare_versions.py --dir benchmark_history/
```

**Qué hace**:
- Calcula cambios en calidad (gap %)
- Calcula cambios en tiempo de ejecución
- Genera estadísticas (promedio, mediana, min, max)
- Provee veredicto automático (mejora/regresión/similar)
- Da recomendaciones sobre si hacer merge

**Output**: Tabla comparativa en terminal

**Ejemplo de output**:
```
Instancia              N     Δ Calidad    Δ Tiempo     Estado
-----------------------------------------------------------
random-50             50     -2.15%       +5.2%        ✅
grid-100             100      ~           -10.1%       =
```

---

### `compare_two_versions.sh` - Comparar Versiones Git

**Propósito**: Comparar automáticamente dos tags/commits de git.

**Uso**:
```bash
./compare_two_versions.sh v0.21.0 v0.22.0
```

**Qué hace**:
1. Checkout de versión 1
2. Instala y ejecuta benchmark
3. Guarda resultados
4. Checkout de versión 2
5. Instala y ejecuta benchmark
6. Compara ambos resultados
7. Restaura rama original

**Tiempo**: 10-20 minutos

---

### `compare_with_main.sh` - Comparar con Main

**Propósito**: Comparar tu rama actual con main antes de hacer merge.

**Uso**:
```bash
./compare_with_main.sh
```

**Qué hace**:
1. Ejecuta benchmark en tu rama actual
2. Cambia temporalmente a main
3. Ejecuta benchmark en main
4. Compara resultados
5. Vuelve a tu rama

**Tiempo**: 10-20 minutos

**Cuándo usar**: Antes de abrir Pull Request

---

## 📦 Gestión de Versiones

### `version_manager.py` - Gestor de Versiones

**Propósito**: Actualizar versión del proyecto automáticamente en todos los archivos.

**Uso**:
```bash
# Ver versión actual
python version_manager.py --show

# Incrementar patch (0.22.0 → 0.22.1)
python version_manager.py --bump patch

# Incrementar minor (0.22.0 → 0.23.0)
python version_manager.py --bump minor

# Incrementar major (0.22.0 → 1.0.0)
python version_manager.py --bump major

# Establecer versión específica
python version_manager.py --set 1.0.0
```

**Qué actualiza**:
- `src/pimst/__init__.py`
- `setup.py`
- `README.md`
- `CHANGELOG.md` (crea nueva entrada)

**Output**: Comandos git sugeridos para commit y tag

---

### `CHANGELOG.md` - Historial de Cambios

**Propósito**: Documentar todos los cambios del proyecto.

**Formato**: [Keep a Changelog](https://keepachangelog.com/)

**Categorías**:
- **Añadido**: Nuevas características
- **Mejorado**: Mejoras en funcionalidades existentes
- **Corregido**: Corrección de bugs
- **Obsoleto**: Características que serán eliminadas
- **Eliminado**: Características eliminadas
- **Seguridad**: Vulnerabilidades corregidas

**Cuándo actualizar**: Con cada cambio significativo

---

## 📈 Rastreo de Rendimiento

### `performance_tracker.py` - Rastreador de Rendimiento

**Propósito**: Mantener historial de rendimiento a lo largo del tiempo.

**Uso**:
```bash
# Añadir benchmark al historial
python performance_tracker.py --add benchmark_results.json --notes "Mejora en gravity-guided"

# Listar todos los benchmarks
python performance_tracker.py --list

# Generar reporte
python performance_tracker.py --report

# Generar gráficos
python performance_tracker.py --plot
```

**Qué hace**:
- Almacena resultados en SQLite (`performance_history.db`)
- Asocia resultados con commit hash y versión
- Genera gráficos de evolución temporal
- Compara automáticamente con versión anterior

**Output**:
- `performance_history.db` - Base de datos SQLite
- `performance_history.png` - Gráfico de evolución
- `performance_by_size.png` - Gráfico por tamaño de instancia

---

## 🚀 Workflows Recomendados

### 1. Workflow Diario (Desarrollo)

```bash
# Antes de empezar a trabajar
git pull origin main

# Después de hacer cambios
./quick_test.sh

# Si los tests pasan
git add .
git commit -m "feat: tu mensaje"
git push
```

---

### 2. Workflow Pre-Commit (Cambios Importantes)

```bash
# 1. Tests rápidos
./quick_test.sh

# 2. Si pasan, benchmark rápido
python benchmark_comparison.py --quick

# 3. Comparar con main
./compare_with_main.sh

# 4. Si todo está bien, commit
git add .
git commit -m "feat: descripción del cambio"

# 5. Añadir al historial
python performance_tracker.py --add benchmark_results.json --notes "Descripción"

# 6. Push
git push
```

---

### 3. Workflow Pre-Release

```bash
# 1. Tests completos
pytest tests/ -v --cov=pimst

# 2. Benchmarks completos
./benchmark_suite.sh
# Seleccionar opción 5 (Full Suite)

# 3. Actualizar versión
python version_manager.py --bump minor

# 4. Actualizar CHANGELOG manualmente
nano CHANGELOG.md

# 5. Añadir al historial
python performance_tracker.py --add benchmark_results.json --notes "Release v0.23.0"

# 6. Generar gráficos
python performance_tracker.py --plot

# 7. Actualizar README con resultados

# 8. Commit todo
git add .
git commit -m "chore: Release v0.23.0"

# 9. Crear tag
git tag -a v0.23.0 -m "Release v0.23.0: Descripción"

# 10. Push con tags
git push origin main
git push origin v0.23.0
```

---

### 4. Workflow de Investigación (Probar Nueva Idea)

```bash
# 1. Crear rama
git checkout -b experiment/new-algorithm

# 2. Implementar cambios
# ... editar código ...

# 3. Tests básicos
./quick_test.sh

# 4. Benchmark
python benchmark_comparison.py

# 5. Comparar con main
./compare_with_main.sh

# 6. Si mejora, guardar resultados
COMMIT=$(git rev-parse --short HEAD)
cp benchmark_results.json experiments/${COMMIT}_new_algorithm.json

# 7. Si no mejora, descartar o seguir iterando
git checkout main
git branch -D experiment/new-algorithm
```

---

### 5. Workflow de Paper (Preparar Publicación)

```bash
# 1. Suite completa de benchmarks
./benchmark_suite.sh
# Seleccionar opción 5

# 2. Comparación con mercado
python compare_with_market.py

# 3. Generar todos los gráficos
python performance_tracker.py --plot

# 4. Copiar resultados a paper/
mkdir -p paper/results
cp benchmark_results/*.json paper/results/
cp *.png paper/figures/

# 5. Generar tablas en LaTeX
python generate_latex_tables.py

# 6. Crear release en GitHub con resultados
git tag -a paper-v1.0 -m "Versión para paper"
git push --tags
```

---

## 🎯 Alias Útiles

Añade estos alias a tu `~/.bashrc` o `~/.bash_profile`:

```bash
# PIMST Development Aliases
alias ptest='./quick_test.sh'
alias pbench='./benchmark_suite.sh'
alias pcompare='./compare_with_main.sh'
alias pversion='python version_tracker.py --show'
alias ptrack='python performance_tracker.py'

# Quick benchmark function
pbench-quick() {
    python benchmark_comparison.py
    python performance_tracker.py --add benchmark_results.json --notes "$1"
    echo "✅ Benchmark guardado en historial"
}

# Compare two versions function
pcompare-versions() {
    ./compare_two_versions.sh $1 $2
}
```

Uso:
```bash
ptest                              # Tests rápidos
pbench                             # Benchmark suite
pcompare                           # Comparar con main
pbench-quick "Mi nota"            # Benchmark + guardar en historial
pcompare-versions v0.21.0 v0.22.0 # Comparar dos versiones
```

---

## 📊 Estructura de Archivos Recomendada

```
pimst-solver/
├── benchmark_results/           # Resultados organizados por sesión
│   ├── session_20251105_143022/
│   │   ├── session_info.txt
│   │   ├── small_benchmark.json
│   │   ├── large_benchmark.json
│   │   └── SUMMARY_REPORT.md
│   └── session_20251106_091533/
│       └── ...
├── benchmark_history/           # Resultados históricos para comparación
│   ├── v0.21.0_results.json
│   ├── v0.22.0_results.json
│   └── abc123f_experiment.json
├── experiments/                 # Experimentos y tests de nuevas ideas
│   ├── gravity_v2_results.json
│   └── multistart_comparison.json
├── performance_history.db       # Base de datos de rendimiento
├── performance_history.png      # Gráficos de evolución
└── paper/                       # Materiales para publicación
    ├── results/
    ├── figures/
    └── tables/
```

---

## 🐛 Troubleshooting

### Problema: Scripts bash no se ejecutan

**Solución**:
```bash
chmod +x *.sh
```

### Problema: Import error en Python scripts

**Solución**:
```bash
pip install -e .
```

### Problema: Benchmarks muy lentos

**Solución**: Usar versión quick o reducir instancias:
```bash
python benchmark_comparison.py --max-size 50
```

### Problema: Git hooks no funcionan

**Solución**:
```bash
chmod +x .git/hooks/*
```

---

## 📚 Documentación Adicional

- [GIT_COMPARISON_GUIDE.md](GIT_COMPARISON_GUIDE.md) - Guía completa de uso de git bash
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía de contribución
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios

---

## 🤝 Contribuir

¿Tienes ideas para mejorar las herramientas de desarrollo? 

1. Crea un issue describiendo tu propuesta
2. Fork el repositorio
3. Implementa tu mejora
4. Abre un Pull Request

---

**¡Feliz desarrollo con PIMST! 🚀**
