# 🚀 Guía de Instalación - Nuevas Herramientas PIMST

Esta guía te ayudará a añadir todas las nuevas herramientas al repositorio de GitHub.

## 📦 Archivos Nuevos Creados

### Scripts de Gestión y Versionado
1. `CHANGELOG.md` - Historial de cambios del proyecto
2. `version_manager.py` - Gestor automático de versiones
3. `DEV_TOOLS_README.md` - Documentación de todas las herramientas

### Scripts de Benchmarking Mejorados
4. `compare_with_market.py` - Comparador completo con el mercado
5. `compare_versions.py` - Comparador de resultados entre versiones
6. `performance_tracker.py` - Rastreador de rendimiento histórico

### Scripts Bash
7. `benchmark_suite.sh` - Suite interactiva de benchmarks
8. `quick_test.sh` - Tests rápidos pre-commit
9. `compare_two_versions.sh` - Comparador automático entre versiones git
10. `compare_with_main.sh` - Comparador con rama main

### Documentación
11. `GIT_COMPARISON_GUIDE.md` - Guía completa de uso de git bash para comparaciones

---

## 🔧 Paso 1: Copiar Archivos al Repositorio

Desde tu terminal en Windows Git Bash:

```bash
# Navega a tu repositorio
cd /c/ruta/a/pimst-solver

# Copia los archivos (ajusta las rutas según sea necesario)
# Opción 1: Si los archivos están en la misma carpeta
cp CHANGELOG.md .
cp version_manager.py .
cp DEV_TOOLS_README.md .
cp compare_with_market.py .
cp compare_versions.py .
cp performance_tracker.py .
cp benchmark_suite.sh .
cp quick_test.sh .
cp compare_two_versions.sh .
cp compare_with_main.sh .
cp GIT_COMPARISON_GUIDE.md .

# Hacer scripts ejecutables
chmod +x *.sh
chmod +x *.py
```

---

## 🔧 Paso 2: Actualizar .gitignore

Añade estas líneas a tu `.gitignore`:

```bash
echo "
# Performance tracking
performance_history.db
performance_history.png
performance_by_size.png

# Benchmark results (mantener solo archivos importantes)
benchmark_results/session_*/
comparison_results/

# Experiments
experiments/

# Temporary files
/tmp/pimst_comparison/
*.pyc
__pycache__/
" >> .gitignore
```

---

## 🔧 Paso 3: Crear Estructura de Directorios

```bash
# Crear directorios necesarios
mkdir -p benchmark_results
mkdir -p benchmark_history
mkdir -p experiments
mkdir -p comparison_results

# Crear .gitkeep para mantener directorios en git
touch benchmark_results/.gitkeep
touch benchmark_history/.gitkeep
touch experiments/.gitkeep
touch comparison_results/.gitkeep
```

---

## 🔧 Paso 4: Actualizar README.md Principal

Añade estas secciones al README.md principal:

### Opción A: Añadir al final del README

```bash
cat >> README.md << 'EOF'

---

## 🛠️ Herramientas de Desarrollo

Este proyecto incluye un conjunto completo de herramientas para desarrollo, testing y benchmarking:

- 🧪 **quick_test.sh** - Tests rápidos pre-commit
- 🏃 **benchmark_suite.sh** - Suite interactiva de benchmarks
- 📊 **compare_with_market.py** - Comparación completa con otros solvers
- 🔍 **compare_versions.py** - Comparador de versiones
- 📈 **performance_tracker.py** - Rastreador de rendimiento histórico
- 📦 **version_manager.py** - Gestor de versiones

Ver [DEV_TOOLS_README.md](DEV_TOOLS_README.md) para documentación completa.

### Quick Start para Desarrolladores

```bash
# Tests rápidos
./quick_test.sh

# Benchmark completo
./benchmark_suite.sh

# Comparar con versión anterior
python compare_versions.py v0.21.0_results.json v0.22.0_results.json

# Rastrear rendimiento
python performance_tracker.py --add benchmark_results.json
python performance_tracker.py --plot
```

EOF
```

### Opción B: Crear sección específica

Edita manualmente `README.md` y añade en un lugar apropiado:

```markdown
## 🛠️ Development Tools

### Available Scripts

- **Testing**: `./quick_test.sh` - Run fast pre-commit tests
- **Benchmarking**: `./benchmark_suite.sh` - Interactive benchmark suite
- **Comparison**: `python compare_with_market.py` - Compare with market leaders
- **Tracking**: `python performance_tracker.py` - Track performance over time
- **Versioning**: `python version_manager.py --bump minor` - Manage versions

See [DEV_TOOLS_README.md](DEV_TOOLS_README.md) for complete documentation.
```

---

## 🔧 Paso 5: Configurar Git Hooks (Opcional)

Configurar hooks automáticos para tests:

```bash
# Crear hook pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "🔄 Ejecutando tests pre-commit..."

# Ejecutar tests rápidos
./quick_test.sh

# Si fallan, prevenir commit
if [ $? -ne 0 ]; then
    echo "❌ Tests fallaron. Commit cancelado."
    echo "Usa 'git commit --no-verify' para saltear tests."
    exit 1
fi

echo "✅ Tests pasaron. Continuando con commit..."
EOF

chmod +x .git/hooks/pre-commit

# Crear hook post-commit (opcional - para benchmark automático)
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash

echo "📊 Guardando estado del benchmark..."

# Solo si existen resultados recientes
if [ -f "benchmark_results.json" ]; then
    COMMIT_HASH=$(git rev-parse --short HEAD)
    mkdir -p benchmark_history
    cp benchmark_results.json benchmark_history/${COMMIT_HASH}_results.json
    echo "✅ Benchmark guardado: benchmark_history/${COMMIT_HASH}_results.json"
fi
EOF

chmod +x .git/hooks/post-commit
```

---

## 🔧 Paso 6: Verificar que Todo Funciona

```bash
# 1. Verificar Python scripts
python version_manager.py --show
python compare_versions.py --help
python performance_tracker.py --list

# 2. Verificar bash scripts
./quick_test.sh
./benchmark_suite.sh

# 3. Ejecutar un test completo
pytest tests/ -v

# 4. Ejecutar benchmark pequeño
python benchmark_comparison.py
```

---

## 🔧 Paso 7: Commit y Push

```bash
# Ver qué archivos se añadirán
git status

# Añadir todos los archivos nuevos
git add CHANGELOG.md
git add version_manager.py
git add DEV_TOOLS_README.md
git add GIT_COMPARISON_GUIDE.md
git add compare_with_market.py
git add compare_versions.py
git add performance_tracker.py
git add benchmark_suite.sh
git add quick_test.sh
git add compare_two_versions.sh
git add compare_with_main.sh
git add .gitignore
git add README.md  # Si lo modificaste

# Añadir directorios con .gitkeep
git add benchmark_results/.gitkeep
git add benchmark_history/.gitkeep
git add experiments/.gitkeep

# Commit
git commit -m "feat: Añadir suite completa de herramientas de desarrollo

- Añadido gestor de versiones automático
- Añadidos scripts de benchmarking mejorados
- Añadido comparador de versiones
- Añadido rastreador de rendimiento histórico
- Añadida documentación completa de herramientas
- Añadidos scripts bash para workflows comunes"

# Push
git push origin main
```

---

## 🔧 Paso 8: Crear Release Inicial (Opcional)

Si quieres crear una release con estas herramientas:

```bash
# Actualizar versión
python version_manager.py --bump minor

# Crear tag
git tag -a v0.23.0 -m "Release v0.23.0: Complete dev tools suite"

# Push con tags
git push origin main
git push origin v0.23.0
```

---

## 📊 Paso 9: Ejecutar Primera Comparación

```bash
# Ejecutar benchmark completo
./benchmark_suite.sh
# Selecciona opción 2 (Small Benchmark)

# Añadir al historial
python performance_tracker.py --add benchmark_results.json \
    --notes "Baseline v0.22.0 con nuevas herramientas"

# Generar gráficos
python performance_tracker.py --plot

# Ver reporte
python performance_tracker.py --report
```

---

## 🎯 Paso 10: Actualizar Documentación GitHub

### Crear Wiki Entries

En GitHub, ve a la pestaña "Wiki" y crea estas páginas:

1. **Development Workflow** - Copiar contenido de DEV_TOOLS_README.md
2. **Git Comparison Guide** - Copiar contenido de GIT_COMPARISON_GUIDE.md
3. **Benchmarking Guide** - Instrucciones de benchmarking
4. **Contributing** - Guía de contribución

### Actualizar Issues Template

Crea `.github/ISSUE_TEMPLATE/performance_regression.md`:

```markdown
---
name: Performance Regression
about: Report a performance regression in PIMST
title: '[PERF] '
labels: performance, regression
assignees: ''
---

**Version with regression**: 
<!-- e.g., v0.23.0 -->

**Previous good version**: 
<!-- e.g., v0.22.0 -->

**Instance affected**:
<!-- e.g., random-100, clustered-50 -->

**Performance difference**:
<!-- Paste output from compare_versions.py -->

**Reproduction steps**:
1. 
2. 
3. 

**Benchmark results**:
<!-- Attach benchmark_results.json -->

**Additional context**:
<!-- Any other context about the problem -->
```

---

## ✅ Checklist Final

Asegúrate de haber completado:

- [ ] Todos los archivos copiados al repositorio
- [ ] Scripts bash marcados como ejecutables (`chmod +x`)
- [ ] `.gitignore` actualizado
- [ ] Estructura de directorios creada
- [ ] README.md actualizado con nuevas herramientas
- [ ] Git hooks configurados (opcional)
- [ ] Todo verificado localmente
- [ ] Commit y push realizados
- [ ] Tag de versión creado (opcional)
- [ ] Wiki actualizado en GitHub (opcional)
- [ ] Issue templates creados (opcional)

---

## 🆘 Solución de Problemas

### "Permission denied" al ejecutar scripts

```bash
chmod +x *.sh
chmod +x *.py
```

### "Module not found" en Python scripts

```bash
pip install -e .
pip install matplotlib  # Para performance_tracker.py
```

### Scripts bash no funcionan en Windows

**Opción 1**: Usar Git Bash
```bash
# Descargar Git for Windows si no lo tienes
# https://git-scm.com/download/win
```

**Opción 2**: Usar WSL (Windows Subsystem for Linux)
```bash
# Instalar WSL
wsl --install

# Ejecutar scripts en WSL
wsl ./quick_test.sh
```

**Opción 3**: Ejecutar Python scripts directamente
```python
# En lugar de ./benchmark_suite.sh
python benchmark_comparison.py
python benchmark_large_scale.py
python compare_with_market.py
```

### Benchmarks muy lentos

```bash
# Usar versión rápida
python benchmark_comparison.py --max-size 50

# O editar datasets en el script
```

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa el archivo [DEV_TOOLS_README.md](DEV_TOOLS_README.md)
2. Revisa [GIT_COMPARISON_GUIDE.md](GIT_COMPARISON_GUIDE.md)
3. Abre un issue en GitHub
4. Contacta al maintainer

---

## 🎉 ¡Listo!

Ahora tienes un sistema completo de herramientas para:

✅ Gestionar versiones automáticamente
✅ Ejecutar benchmarks completos
✅ Comparar con otros solvers
✅ Rastrear rendimiento histórico
✅ Comparar versiones fácilmente
✅ Mantener calidad de código
✅ Documentar cambios apropiadamente

**¡Feliz desarrollo con PIMST! 🚀**
