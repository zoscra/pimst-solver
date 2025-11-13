# 🏆 ATSP Complete Benchmark Guide

Guía completa para ejecutar benchmarks comparativos entre PIMST-ATSP, LKH-3 y OR-Tools.

---

## 📋 Requisitos

### Obligatorios
- ✅ Python 3.8+
- ✅ numpy, numba, scipy
- ✅ ATSP solvers (incluidos en este repo)

### Opcionales (para comparación completa)
- 📦 **OR-Tools** - Google optimization library
- 🔧 **LKH-3** - State-of-the-art TSP/ATSP solver

---

## 🚀 Instalación Rápida

### Paso 1: Instalar Dependencias

```bash
# Instalar dependencias Python + OR-Tools
python install_benchmark_deps.py
```

Este script:
- ✓ Verifica numpy/numba/scipy
- ✓ Instala OR-Tools automáticamente
- ✓ Verifica si LKH-3 está disponible
- ✓ Imprime instrucciones de instalación de LKH

### Paso 2: (Opcional) Instalar LKH-3

**Windows:**
```bash
# Descargar desde: http://akira.ruc.dk/~keld/research/LKH-3/
# Extraer LKH.exe
# Colocar en este directorio o agregar al PATH
```

**Linux/Mac:**
```bash
# Opción A: Precompilado
wget http://akira.ruc.dk/~keld/research/LKH-3/LKH-3.0.8.tgz
tar xzf LKH-3.0.8.tgz
cd LKH-3.0.8
make
sudo mv LKH /usr/local/bin/

# Opción B: Desde GitHub
git clone https://github.com/mastqe/LKH
cd LKH
make
sudo mv LKH /usr/local/bin/
```

**Verificar instalación:**
```bash
LKH --version
# o
./LKH --version
```

---

## 🧪 Ejecutar Benchmarks

### Test Rápido (5-10 minutos)

```bash
python benchmark_atsp_complete.py --quick
```

Esto ejecuta:
- 1 problema de n=30
- Todos los solvers disponibles
- Comparación rápida

**Salida esperada:**
```
======================================================================
  PROBLEM: test_30_random (n=30, type=random)
======================================================================
  📊 Assignment Lower Bound: 234.56

  Testing PIMST-Basic...
    ✓ Cost: 256.78, Gap: 9.48%, Time: 0.123s
  Testing PIMST-Super...
    ✓ Cost: 248.92, Gap: 6.13%, Time: 0.456s
  Testing PIMST-Quantum...
    ✓ Cost: 245.67, Gap: 4.74%, Time: 2.345s
  Testing OR-Tools...
    ✓ Cost: 242.34, Gap: 3.32%, Time: 5.678s
  Testing LKH-3...
    ✓ Cost: 238.90, Gap: 1.85%, Time: 3.456s

  🏆 Best quality: LKH-3 (cost: 238.90, gap: 1.85%)
  ⚡ Fastest: PIMST-Basic (time: 0.123s)
```

### Benchmark Completo (30-60 minutos)

```bash
python benchmark_atsp_complete.py
```

Esto ejecuta:
- 13 configuraciones de problemas
- Tamaños: 20, 30, 50, 75, 100 ciudades
- Tipos: random, flow_shop, one_way, structured
- Todos los solvers
- Análisis completo

**Genera:**
- 📊 `atsp_complete_benchmark_TIMESTAMP.json` - Resultados detallados
- 📄 `atsp_benchmark_report_TIMESTAMP.md` - Reporte markdown

---

## 📊 Configuración del Benchmark

### Problemas Incluidos

| Size | Type | Time Limit | Description |
|------|------|------------|-------------|
| 20-100 | random | 10-60s | Matrices asimétricas aleatorias |
| 30-75 | flow_shop | 15-45s | Scheduling con setup times |
| 30-75 | one_way | 15-45s | Ruteo con calles de un sentido |
| 30-50 | structured | 15-30s | Patrones geométricos asimétricos |

### Solvers Comparados

| Solver | Method | Speed | Expected Gap |
|--------|--------|-------|--------------|
| **PIMST-Basic** | NN + Farthest Insertion + LK | ⚡⚡⚡ Ultra-fast | 5-10% |
| **PIMST-Super** | 3-phase intelligent | ⚡⚡ Fast | 2-5% |
| **PIMST-Quantum** | 3 orthogonal runs | ⚡ Moderate | 2-8% |
| **OR-Tools** | Guided Local Search | 🐌 Slow | 1-3% |
| **LKH-3** | Advanced Lin-Kernighan | 🐌 Slow | <2% |

---

## 📈 Interpretar Resultados

### Métricas

- **Cost**: Costo total del tour encontrado
- **Gap**: % sobre el lower bound (Assignment Problem)
- **Time**: Tiempo de ejecución en segundos
- **Wins**: Número de problemas donde obtuvo el mejor costo

### Lower Bound

El benchmark usa el **Assignment Problem** como lower bound:
```
ATSP_optimal_cost ≥ Assignment_Problem_cost
```

Un gap bajo indica mayor calidad.

### Ejemplo de Salida

```json
{
  "summary": {
    "PIMST-Super": {
      "avg_gap": 3.45,
      "avg_time": 2.134,
      "wins": 3,
      "problems_solved": 13
    },
    "LKH-3": {
      "avg_gap": 1.23,
      "avg_time": 15.678,
      "wins": 10,
      "problems_solved": 13
    }
  }
}
```

**Interpretación:**
- LKH-3 tiene mejor calidad (gap 1.23% vs 3.45%)
- PIMST-Super es **7.3x más rápido** (2.1s vs 15.7s)
- LKH-3 gana en 10/13 problemas en calidad
- PIMST es competitivo con speedup significativo

---

## 🎯 Casos de Uso

### Caso 1: Validar Calidad

**Objetivo:** ¿Es PIMST competitivo en calidad?

```bash
python benchmark_atsp_complete.py
```

**Esperar:**
- PIMST-Quantum: gap 2-5% vs LKH
- PIMST-Super: gap 3-7% vs LKH
- PIMST-Basic: gap 5-10% vs LKH

**Criterio de éxito:** Gap promedio < 10%

### Caso 2: Validar Velocidad

**Objetivo:** ¿Es PIMST más rápido?

```bash
python benchmark_atsp_complete.py
```

**Esperar:**
- PIMST-Basic: 10-100x más rápido que LKH
- PIMST-Super: 5-20x más rápido que LKH
- PIMST-Quantum: 2-10x más rápido que LKH

**Criterio de éxito:** Speedup > 5x en promedio

### Caso 3: Comparar con OR-Tools

**Objetivo:** ¿Es PIMST mejor que OR-Tools?

```bash
python benchmark_atsp_complete.py
```

**Esperar:**
- Calidad similar o mejor
- 5-50x más rápido

---

## 🔧 Personalizar Benchmark

### Agregar Problemas

Edita `benchmark_atsp_complete.py`:

```python
test_cases = [
    # (size, problem_type, time_limit)
    (50, 'random', 30),
    (100, 'flow_shop', 60),
    # Agregar más aquí
]
```

### Tipos de Problemas Disponibles

```python
'random'      # Aleatorio con 40% asimetría
'flow_shop'   # Flow shop scheduling
'one_way'     # Calles de un solo sentido
'structured'  # Patrones geométricos
```

### Ajustar Time Limits

```python
# Para problemas más grandes
(200, 'random', 120),  # 2 minutos
(300, 'random', 300),  # 5 minutos
```

---

## 🐛 Troubleshooting

### Error: "OR-Tools not installed"

```bash
pip install ortools
```

### Error: "LKH not found"

El benchmark continuará sin LKH. Para instalarlo:
```bash
# Ver sección "Instalar LKH-3" arriba
```

### Error: "scipy not found"

```bash
pip install scipy
```

### Benchmark muy lento

**Opción 1:** Reduce time limits
```python
(50, 'random', 10)  # Instead of 30
```

**Opción 2:** Reduce problemas
```python
test_cases = test_cases[:5]  # Solo primeros 5
```

**Opción 3:** Usa --quick
```bash
python benchmark_atsp_complete.py --quick
```

### Memory errors con n > 200

ATSP requiere O(n²) memoria. Para n=500:
- Memoria: ~2 GB
- Para n=1000: ~8 GB

Reduce tamaños si tienes poco RAM.

---

## 📊 Resultados Esperados

### Small Problems (n ≤ 50)

| Solver | Gap | Time | Speedup vs LKH |
|--------|-----|------|----------------|
| PIMST-Basic | 8% | 0.1s | **100x** |
| PIMST-Super | 4% | 0.5s | **40x** |
| PIMST-Quantum | 3% | 2s | **10x** |
| OR-Tools | 2% | 10s | 2x |
| LKH-3 | 1% | 20s | 1x (baseline) |

### Medium Problems (50 < n ≤ 100)

| Solver | Gap | Time | Speedup vs LKH |
|--------|-----|------|----------------|
| PIMST-Basic | 10% | 2s | **30x** |
| PIMST-Super | 5% | 5s | **12x** |
| PIMST-Quantum | 4% | 15s | **4x** |
| OR-Tools | 3% | 45s | 1.3x |
| LKH-3 | 2% | 60s | 1x (baseline) |

### Large Problems (n > 100)

| Solver | Gap | Time | Speedup vs LKH |
|--------|-----|------|----------------|
| PIMST-Super | 6% | 30s | **10x** |
| PIMST-Quantum | 5% | 60s | **5x** |
| OR-Tools | 4% | 200s | 1.5x |
| LKH-3 | 2% | 300s | 1x (baseline) |

**Nota:** PIMST-Basic no recomendado para n > 100

---

## 📝 Citar Resultados

Si usas estos benchmarks en tu investigación:

```bibtex
@software{pimst_atsp_2025,
  title={PIMST-ATSP: Ultra-Fast Asymmetric TSP Solver},
  author={José Manuel Reguera Gutiérrez},
  year={2025},
  url={https://github.com/zoscra/pimst-solver}
}
```

---

## 🎓 Metodología

### Lower Bound

Usa Assignment Problem (AP):
```
minimize: Σ c[i,σ(i)]
subject to: σ is a permutation
```

Resuelto con Hungarian algorithm en O(n³).

**Propiedad:** `ATSP_opt ≥ AP_opt`

### Gap Calculation

```python
gap = (tour_cost - lower_bound) / lower_bound * 100
```

### Time Measurement

- **Wall time**: Tiempo total incluyendo I/O
- **Excludes**: Tiempo de generación de problema
- **Includes**: Tiempo de escritura de archivos (LKH)

---

## 📞 Soporte

**Problemas con el benchmark:**
- Email: jmrg.trabajo@gmail.com
- GitHub Issues: https://github.com/zoscra/pimst-solver/issues

**Problemas con LKH:**
- Website: http://akira.ruc.dk/~keld/research/LKH-3/

**Problemas con OR-Tools:**
- Docs: https://developers.google.com/optimization

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Instalar deps
python install_benchmark_deps.py

# 2. Test rápido (5 min)
python benchmark_atsp_complete.py --quick

# 3. Benchmark completo (30-60 min)
python benchmark_atsp_complete.py

# 4. Ver resultados
cat atsp_benchmark_report_*.md
```

**¡Listo!** 🎉

---

**Built for speed and science** ⚡🔬
