# Guía de Git Bash para Comparaciones y Benchmarking

Esta guía te ayudará a usar git bash para comparar versiones, ejecutar benchmarks y mantener un historial de rendimiento.

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Comparar Versiones](#comparar-versiones)
3. [Ejecutar Benchmarks](#ejecutar-benchmarks)
4. [Automatizar Comparaciones](#automatizar-comparaciones)
5. [Rastrear Rendimiento](#rastrear-rendimiento)
6. [Mejores Prácticas](#mejores-prácticas)

---

## 🔧 Configuración Inicial

### 1. Clonar el repositorio

```bash
# Clonar tu repositorio
git clone https://github.com/zoscra/pimst-solver.git
cd pimst-solver

# Verificar que estás en la rama correcta
git branch
```

### 2. Configurar entorno

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows Git Bash)
source venv/Scripts/activate

# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install -e .

# Instalar herramientas de benchmarking
pip install ortools python-tsp pytest pytest-benchmark
```

### 3. Verificar instalación

```bash
# Verificar versión de PIMST
python -c "import pimst; print(f'PIMST v{pimst.__version__}')"

# Ejecutar tests rápidos
pytest tests/ -v
```

---

## 🔍 Comparar Versiones

### Comparar código entre versiones

```bash
# Ver diferencias entre versión actual y anterior
git diff v0.21.0 v0.22.0

# Ver solo archivos modificados
git diff --name-only v0.21.0 v0.22.0

# Ver diferencias en un archivo específico
git diff v0.21.0 v0.22.0 -- src/pimst/algorithms.py

# Ver estadísticas de cambios
git diff --stat v0.21.0 v0.22.0
```

### Comparar rendimiento entre versiones

```bash
# Crear directorio para comparaciones
mkdir -p benchmark_history

# Ejecutar benchmark en versión actual
python benchmark_comparison.py
cp benchmark_results.json benchmark_history/v0.22.0_results.json

# Cambiar a versión anterior
git checkout v0.21.0

# Reinstalar esa versión
pip install -e .

# Ejecutar benchmark
python benchmark_comparison.py
cp benchmark_results.json benchmark_history/v0.21.0_results.json

# Volver a la versión actual
git checkout main
pip install -e .

# Comparar resultados
python compare_versions.py benchmark_history/v0.21.0_results.json benchmark_history/v0.22.0_results.json
```

### Script para comparar dos versiones automáticamente

Crea este script como `compare_two_versions.sh`:

```bash
#!/bin/bash
# Uso: ./compare_two_versions.sh v0.21.0 v0.22.0

VERSION1=$1
VERSION2=$2
CURRENT_BRANCH=$(git branch --show-current)

echo "======================================================================"
echo "Comparando PIMST: $VERSION1 vs $VERSION2"
echo "======================================================================"

# Crear directorio temporal
mkdir -p /tmp/pimst_comparison

# Benchmark versión 1
echo ""
echo "🔄 Ejecutando benchmark para $VERSION1..."
git checkout $VERSION1
pip install -e . > /dev/null 2>&1
python benchmark_comparison.py
cp benchmark_results.json /tmp/pimst_comparison/${VERSION1}_results.json

# Benchmark versión 2
echo ""
echo "🔄 Ejecutando benchmark para $VERSION2..."
git checkout $VERSION2
pip install -e . > /dev/null 2>&1
python benchmark_comparison.py
cp benchmark_results.json /tmp/pimst_comparison/${VERSION2}_results.json

# Volver a rama original
git checkout $CURRENT_BRANCH
pip install -e . > /dev/null 2>&1

# Comparar
echo ""
echo "📊 Comparando resultados..."
python compare_versions.py /tmp/pimst_comparison/${VERSION1}_results.json /tmp/pimst_comparison/${VERSION2}_results.json

echo ""
echo "✅ Comparación completada!"
echo "Resultados guardados en: /tmp/pimst_comparison/"
```

Haz el script ejecutable:

```bash
chmod +x compare_two_versions.sh
./compare_two_versions.sh v0.21.0 v0.22.0
```

---

## 🏃 Ejecutar Benchmarks

### Tests rápidos (antes de commit)

```bash
# Ejecutar solo tests unitarios
pytest tests/test_basic.py -v

# Ejecutar tests con coverage
pytest --cov=pimst tests/ --cov-report=html

# Ver reporte de coverage
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

### Benchmarks completos

```bash
# Benchmark contra OR-Tools (5-10 minutos)
python benchmark_comparison.py

# Benchmark de gran escala (20-40 minutos)
python benchmark_large_scale.py

# Comparación completa con el mercado (30-60 minutos)
python compare_with_market.py
```

### Benchmarks con diferentes configuraciones

```bash
# Solo instancias pequeñas (rápido)
python -c "
from benchmark_comparison import run_benchmarks, generate_datasets
datasets = {k: v for k, v in generate_datasets().items() if len(v) <= 30}
# Ejecutar solo en esas instancias
"

# Solo instancias específicas
python benchmark_comparison.py --instances "random-50,grid-100,circle-50"
```

---

## 🤖 Automatizar Comparaciones

### Script para ejecutar benchmark después de cada commit

Crea `.git/hooks/post-commit`:

```bash
#!/bin/bash

echo "🔄 Ejecutando benchmark automático..."

# Ejecutar benchmark rápido
python benchmark_comparison.py --quick

# Guardar resultado con hash del commit
COMMIT_HASH=$(git rev-parse --short HEAD)
cp benchmark_results.json benchmark_history/${COMMIT_HASH}_results.json

echo "✅ Benchmark guardado: benchmark_history/${COMMIT_HASH}_results.json"
```

Haz el hook ejecutable:

```bash
chmod +x .git/hooks/post-commit
```

### Script para comparar con rama main

Crea `compare_with_main.sh`:

```bash
#!/bin/bash
# Compara tu rama actual con main

CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "Ya estás en main"
    exit 0
fi

echo "======================================================================"
echo "Comparando $CURRENT_BRANCH con main"
echo "======================================================================"

# Benchmark rama actual
echo "🔄 Benchmark en $CURRENT_BRANCH..."
python benchmark_comparison.py
cp benchmark_results.json /tmp/current_branch_results.json

# Cambiar a main
git stash
git checkout main
pip install -e . > /dev/null 2>&1

# Benchmark main
echo "🔄 Benchmark en main..."
python benchmark_comparison.py
cp benchmark_results.json /tmp/main_results.json

# Volver a rama original
git checkout $CURRENT_BRANCH
git stash pop
pip install -e . > /dev/null 2>&1

# Comparar
echo "📊 Comparando resultados..."
python compare_versions.py /tmp/main_results.json /tmp/current_branch_results.json

echo ""
echo "✅ ¿Merece la pena hacer merge? Revisa los resultados arriba."
```

```bash
chmod +x compare_with_main.sh
./compare_with_main.sh
```

---

## 📈 Rastrear Rendimiento

### Crear base de datos de rendimiento histórico

```bash
# Crear directorio
mkdir -p performance_history

# Ejecutar y guardar con timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
python benchmark_comparison.py
cp benchmark_results.json performance_history/${TIMESTAMP}_results.json

# Agregar información de git
cat > performance_history/${TIMESTAMP}_info.txt << EOF
Commit: $(git rev-parse HEAD)
Fecha: $(date)
Rama: $(git branch --show-current)
Autor: $(git log -1 --pretty=format:'%an')
Mensaje: $(git log -1 --pretty=format:'%s')
EOF
```

### Script para generar gráfico de evolución

Crea `plot_performance_history.py`:

```python
import json
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# Leer todos los resultados históricos
history_dir = Path("performance_history")
results = []

for file in sorted(history_dir.glob("*_results.json")):
    with open(file) as f:
        data = json.load(f)
        timestamp = file.stem.split('_')[0]
        
        # Calcular gap promedio
        gaps = []
        for instance, result in data.items():
            if 'pimst_balanced' in result['solvers']:
                best = min(s['length'] for s in result['solvers'].values())
                pimst = result['solvers']['pimst_balanced']['length']
                gap = (pimst - best) / best * 100
                gaps.append(gap)
        
        results.append({
            'timestamp': timestamp,
            'avg_gap': np.mean(gaps),
            'median_gap': np.median(gaps)
        })

# Graficar
timestamps = [r['timestamp'] for r in results]
avg_gaps = [r['avg_gap'] for r in results]
median_gaps = [r['median_gap'] for r in results]

plt.figure(figsize=(12, 6))
plt.plot(timestamps, avg_gaps, 'b-o', label='Gap Promedio')
plt.plot(timestamps, median_gaps, 'r-s', label='Gap Mediana')
plt.xlabel('Versión / Timestamp')
plt.ylabel('Gap vs Óptimo (%)')
plt.title('Evolución de la Calidad de PIMST')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('performance_evolution.png')
print("✅ Gráfico guardado: performance_evolution.png")
```

```bash
python plot_performance_history.py
```

---

## 🎯 Mejores Prácticas

### 1. Antes de cada commit importante

```bash
# 1. Ejecutar tests
pytest tests/ -v

# 2. Ejecutar benchmark rápido
python benchmark_comparison.py --quick

# 3. Verificar que no empeoró
python compare_with_main.sh

# 4. Si todo está bien, commit
git add .
git commit -m "Mejora en algoritmo gravity-guided (+2% calidad)"
git push
```

### 2. Antes de cada release

```bash
# 1. Ejecutar suite completa de benchmarks
python benchmark_comparison.py
python benchmark_large_scale.py
python compare_with_market.py

# 2. Actualizar versión
python version_manager.py --bump minor

# 3. Actualizar documentación con resultados
# Copiar benchmark_results.json a docs/

# 4. Crear tag
git tag -a v0.23.0 -m "Release v0.23.0: Mejoras en multi-start"
git push origin v0.23.0
```

### 3. Mantener historial limpio

```bash
# Guardar benchmarks importantes
mkdir -p benchmark_archive
cp benchmark_results.json benchmark_archive/v0.22.0_$(date +%Y%m%d).json

# Limpiar resultados antiguos (> 30 días)
find benchmark_history/ -name "*.json" -mtime +30 -delete

# Comprimir archivos antiguos
tar -czf benchmark_archive_$(date +%Y%m).tar.gz benchmark_history/
```

### 4. Aliases útiles en Git Bash

Añade a tu `~/.bashrc` o `~/.bash_profile`:

```bash
# Aliases para PIMST
alias pimst-test='pytest tests/ -v'
alias pimst-bench='python benchmark_comparison.py'
alias pimst-bench-large='python benchmark_large_scale.py'
alias pimst-compare='python compare_with_market.py'
alias pimst-version='python version_manager.py --show'

# Función para benchmark rápido con timestamp
pimst-quick-bench() {
    python benchmark_comparison.py --quick
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp benchmark_results.json benchmark_history/${TIMESTAMP}_quick.json
    echo "✅ Resultado guardado: benchmark_history/${TIMESTAMP}_quick.json"
}
```

Recarga el archivo:

```bash
source ~/.bashrc
```

Ahora puedes usar:

```bash
pimst-test          # Ejecutar tests
pimst-bench         # Benchmark completo
pimst-quick-bench   # Benchmark rápido con guardado automático
pimst-version       # Ver versión actual
```

---

## 🔬 Comandos Avanzados

### Comparar rendimiento en diferentes máquinas

```bash
# En máquina 1
python benchmark_comparison.py
scp benchmark_results.json user@machine2:/tmp/machine1_results.json

# En máquina 2
python benchmark_comparison.py
python compare_versions.py /tmp/machine1_results.json benchmark_results.json
```

### Bisect para encontrar commit que introdujo regresión

```bash
# Si sabes que v0.20.0 era bueno y v0.22.0 es malo
git bisect start
git bisect bad v0.22.0
git bisect good v0.20.0

# Git irá a un commit intermedio
# Ejecuta benchmark
python benchmark_comparison.py --quick

# Si el resultado es bueno
git bisect good

# Si el resultado es malo
git bisect bad

# Repite hasta encontrar el commit culpable
# Cuando termines
git bisect reset
```

### Crear reporte de benchmark en Markdown

```bash
# Ejecutar benchmark y generar reporte
python benchmark_comparison.py
python generate_markdown_report.py benchmark_results.json > BENCHMARK_REPORT.md

# Agregar al README
cat BENCHMARK_REPORT.md >> README.md

# Commit
git add README.md BENCHMARK_REPORT.md
git commit -m "docs: Actualizar resultados de benchmark"
```

---

## 📊 Ejemplo de Workflow Completo

```bash
# 1. Crear nueva rama para feature
git checkout -b feature/improve-gravity-algorithm

# 2. Hacer cambios
# ... editar src/pimst/gravity.py ...

# 3. Verificar que funciona
pytest tests/ -v

# 4. Benchmark rápido
python benchmark_comparison.py --quick

# 5. Si mejora, benchmark completo
python benchmark_comparison.py

# 6. Comparar con main
./compare_with_main.sh

# 7. Si todo está bien, commit
git add src/pimst/gravity.py
git commit -m "feat: Mejorar normalización de masas gravitacionales"

# 8. Guardar resultado del benchmark
COMMIT_HASH=$(git rev-parse --short HEAD)
cp benchmark_results.json benchmark_history/${COMMIT_HASH}_results.json

# 9. Push
git push origin feature/improve-gravity-algorithm

# 10. Crear Pull Request en GitHub
# Incluir benchmark_results.json en la descripción del PR
```

---

## 🚀 Recursos Adicionales

- [Documentación de Git](https://git-scm.com/doc)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions para CI/CD](https://docs.github.com/en/actions)

---

## ❓ Troubleshooting

### Problema: Los benchmarks tardan demasiado

**Solución:**
```bash
# Usar solo instancias pequeñas
python benchmark_comparison.py --max-size 50

# O crear versión rápida personalizada
python -c "
import benchmark_comparison
datasets = generate_datasets()
small_datasets = {k: v for k, v in datasets.items() if len(v) <= 30}
results = run_benchmarks(small_datasets)
"
```

### Problema: Diferencias entre máquinas

**Solución:** Normaliza por tiempo de referencia:
```bash
# Ejecutar benchmark de referencia
python benchmark_reference.py

# Usar factor de normalización en comparaciones
python compare_versions.py --normalize
```

### Problema: Git hooks no se ejecutan

**Solución:**
```bash
# Verificar permisos
chmod +x .git/hooks/post-commit

# Verificar que el hook está en el lugar correcto
ls -la .git/hooks/

# Probar manualmente
.git/hooks/post-commit
```

---

**¡Con estas herramientas tienes todo lo necesario para mantener un control riguroso de la evolución de PIMST!** 🚀
