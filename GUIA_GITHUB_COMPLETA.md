# 📘 GUÍA COMPLETA: Configurar PIMST en GitHub

Esta guía te llevará paso a paso desde cero hasta tener tu proyecto PIMST completamente configurado en GitHub con:
- ✅ Repositorio organizado
- ✅ Sistema SiNo integrado
- ✅ Tests funcionando
- ✅ GitHub Actions (CI/CD)
- ✅ Documentación profesional

---

## 📋 TABLA DE CONTENIDOS

1. [Preparación Inicial](#1-preparación-inicial)
2. [Crear Repositorio en GitHub](#2-crear-repositorio-en-github)
3. [Configurar Git Local](#3-configurar-git-local)
4. [Estructura del Proyecto](#4-estructura-del-proyecto)
5. [Commit y Push Inicial](#5-commit-y-push-inicial)
6. [Configurar GitHub Actions](#6-configurar-github-actions)
7. [Documentación](#7-documentación)
8. [Releases y Tags](#8-releases-y-tags)
9. [Colaboración](#9-colaboración)
10. [Mantenimiento](#10-mantenimiento)

---

## 1. Preparación Inicial

### 1.1 Verificar Git Instalado

```bash
git --version
```

Si no está instalado:
- **Windows**: Descarga de https://git-scm.com/
- **Mac**: `brew install git`
- **Linux**: `sudo apt-get install git`

### 1.2 Configurar Git (Primera vez)

```bash
# Configurar nombre y email
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@ejemplo.com"

# Verificar configuración
git config --list
```

### 1.3 Crear Cuenta en GitHub

Si no tienes cuenta: https://github.com/signup

---

## 2. Crear Repositorio en GitHub

### Opción A: Desde la Web (Recomendado para principiantes)

1. Ve a https://github.com/new
2. Configuración del repositorio:
   ```
   Repository name: pimst-solver
   Description: Physics-Inspired Multi-Start TSP Solver
   ✅ Public (o Private si prefieres)
   ✅ Add README file
   ✅ Add .gitignore: Python
   ✅ Choose a license: MIT License (recomendado)
   ```
3. Click en "Create repository"

### Opción B: Desde la Terminal

```bash
# Crear repositorio usando GitHub CLI
gh repo create pimst-solver --public --description "Physics-Inspired Multi-Start TSP Solver"
```

---

## 3. Configurar Git Local

### 3.1 Navegar a tu Proyecto

```bash
# Ve a la carpeta de tu proyecto
cd /ruta/a/pimst-solver-completo

# Verificar contenido
ls -la
```

### 3.2 Inicializar Git

```bash
# Inicializar repositorio Git
git init

# Configurar rama principal como 'main'
git branch -M main
```

### 3.3 Conectar con GitHub

```bash
# Agregar remote (sustituye con tu URL)
git remote add origin https://github.com/TU_USUARIO/pimst-solver.git

# Verificar remote
git remote -v
```

---

## 4. Estructura del Proyecto

Tu proyecto debe tener esta estructura:

```
pimst-solver/
├── .github/
│   └── workflows/
│       ├── tests.yml          # GitHub Actions para tests
│       └── release.yml        # GitHub Actions para releases
├── src/
│   └── pimst/
│       ├── __init__.py
│       ├── algorithms.py
│       ├── gravity.py
│       ├── utils.py
│       ├── solver.py
│       └── improved/
│           ├── __init__.py
│           └── sino/
│               ├── __init__.py
│               ├── types.py
│               ├── decision.py
│               ├── confidence.py
│               ├── explorer.py
│               ├── checkpoint.py
│               ├── api.py
│               └── selector.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_sino_system.py
│   ├── test_algorithms.py
│   └── test_basic.py
├── examples/
│   ├── basic_usage.py
│   └── sino_examples.py
├── docs/
│   ├── README.md
│   ├── INSTALLATION.md
│   └── API_REFERENCE.md
├── .gitignore
├── .gitattributes
├── README.md
├── LICENSE
├── setup.py
├── requirements.txt
├── pytest.ini
└── run_tests.py
```

### 4.1 Crear .gitignore

Ya debería existir, pero verifica que contenga:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# OS
.DS_Store
Thumbs.db

# Project specific
benchmark_results/
comparison_results/
performance_history.db
*.log
external_solvers/
```

### 4.2 Crear .gitattributes

```bash
cat > .gitattributes << 'EOF'
# Auto detect text files and perform LF normalization
* text=auto

# Python files
*.py text eol=lf
*.pyx text eol=lf

# Shell scripts
*.sh text eol=lf

# Documentation
*.md text
*.txt text

# Binary files
*.png binary
*.jpg binary
*.pdf binary
*.pickle binary
*.npy binary
EOF
```

---

## 5. Commit y Push Inicial

### 5.1 Verificar Estado

```bash
# Ver qué archivos hay
git status
```

### 5.2 Agregar Archivos

```bash
# Opción 1: Agregar todo
git add .

# Opción 2: Agregar selectivamente
git add src/ tests/ README.md setup.py requirements.txt

# Verificar qué se agregará
git status
```

### 5.3 Primer Commit

```bash
# Crear primer commit
git commit -m "Initial commit: PIMST Solver with SiNo system

- Core TSP algorithms (v14.x, v17.x)
- SiNo decision system integrated
- Comprehensive test suite
- Documentation and examples"

# Verificar commit
git log --oneline
```

### 5.4 Push a GitHub

```bash
# Primera vez (push y establecer upstream)
git push -u origin main

# Siguientes veces (simplemente)
git push
```

### 5.5 Verificar en GitHub

Ve a `https://github.com/TU_USUARIO/pimst-solver` y verifica que todo esté ahí.

---

## 6. Configurar GitHub Actions

### 6.1 Crear Workflow para Tests

```bash
# Crear directorio
mkdir -p .github/workflows

# Crear archivo de workflow
cat > .github/workflows/tests.yml << 'EOF'
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        python run_tests.py --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      if: matrix.python-version == '3.11'
EOF
```

### 6.2 Crear Workflow para Linting

```bash
cat > .github/workflows/lint.yml << 'EOF'
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        pip install flake8 black
    
    - name: Lint with flake8
      run: |
        flake8 src/ tests/ --max-line-length=100
    
    - name: Check formatting with black
      run: |
        black --check src/ tests/
EOF
```

### 6.3 Commit y Push Workflows

```bash
git add .github/
git commit -m "Add GitHub Actions workflows for CI/CD"
git push
```

Verifica en GitHub → pestaña "Actions" que los workflows se ejecuten.

---

## 7. Documentación

### 7.1 README.md Principal

Tu README debe tener:

```markdown
# PIMST Solver

Physics-Inspired Multi-Start TSP Solver with SiNo Decision System

[![Tests](https://github.com/TU_USUARIO/pimst-solver/workflows/Tests/badge.svg)](https://github.com/TU_USUARIO/pimst-solver/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Quick Start

\```python
from pimst.improved.sino import smart_solve
import numpy as np

# Create distance matrix
distances = np.random.rand(50, 50)

# Solve TSP
tour, cost = smart_solve(distances)
print(f"Tour cost: {cost:.2f}")
\```

## 📦 Installation

\```bash
pip install git+https://github.com/TU_USUARIO/pimst-solver.git
\```

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Examples](examples/)

## 🧪 Running Tests

\```bash
python run_tests.py
\```

## 📄 License

MIT License - see [LICENSE](LICENSE) file
```

### 7.2 Crear Documentación Adicional

```bash
mkdir -p docs

# docs/INSTALLATION.md
# docs/API_REFERENCE.md
# docs/CONTRIBUTING.md
```

### 7.3 Commit Documentación

```bash
git add README.md docs/
git commit -m "Add comprehensive documentation"
git push
```

---

## 8. Releases y Tags

### 8.1 Crear Primer Release

```bash
# Crear tag para v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0: Initial public release

Features:
- Core TSP algorithms
- SiNo decision system
- Comprehensive test suite
- Full documentation"

# Push tag
git push origin v1.0.0
```

### 8.2 Crear Release en GitHub

1. Ve a tu repositorio en GitHub
2. Click en "Releases" (lado derecho)
3. Click "Create a new release"
4. Selecciona el tag `v1.0.0`
5. Título: `v1.0.0 - Initial Release`
6. Descripción: Lista de features
7. Click "Publish release"

---

## 9. Colaboración

### 9.1 Ramas de Desarrollo

```bash
# Crear rama para nueva feature
git checkout -b feature/nueva-funcionalidad

# Trabajar en la rama
# ... hacer cambios ...

# Commit cambios
git add .
git commit -m "Add nueva funcionalidad"

# Push rama
git push -u origin feature/nueva-funcionalidad
```

### 9.2 Pull Requests

1. Ve a GitHub → tu repositorio
2. Verás un botón "Compare & pull request"
3. Describe tus cambios
4. Crea el Pull Request
5. Espera los checks de GitHub Actions
6. Merge cuando todo esté verde

---

## 10. Mantenimiento

### 10.1 Mantener Actualizado

```bash
# Actualizar desde GitHub
git pull origin main

# Ver cambios
git log --oneline --graph
```

### 10.2 Workflow Diario

```bash
# 1. Antes de empezar a trabajar
git pull origin main

# 2. Crear rama para tu trabajo
git checkout -b feature/mi-cambio

# 3. Hacer cambios y commits frecuentes
git add .
git commit -m "Descripción del cambio"

# 4. Push de tu rama
git push -u origin feature/mi-cambio

# 5. Crear Pull Request en GitHub

# 6. Después del merge, actualizar main
git checkout main
git pull origin main

# 7. Eliminar rama local
git branch -d feature/mi-cambio
```

### 10.3 Comandos Útiles

```bash
# Ver estado
git status

# Ver historial
git log --oneline --graph --all

# Ver diferencias
git diff

# Deshacer cambios no commiteados
git checkout -- archivo.py

# Ver ramas
git branch -a

# Cambiar de rama
git checkout nombre-rama

# Eliminar rama
git branch -d nombre-rama
```

---

## 🎯 CHECKLIST FINAL

Antes de considerar tu proyecto "listo":

- [ ] Repositorio creado en GitHub
- [ ] Git configurado localmente
- [ ] Código subido con primer commit
- [ ] README.md completo y profesional
- [ ] GitHub Actions configurado y funcionando
- [ ] Tests pasando en CI
- [ ] Documentación completa en /docs
- [ ] Primer release (v1.0.0) creado
- [ ] .gitignore configurado correctamente
- [ ] LICENSE file incluido
- [ ] requirements.txt actualizado

---

## 🆘 Solución de Problemas

### Error: "Permission denied (publickey)"

```bash
# Generar SSH key
ssh-keygen -t ed25519 -C "tu.email@ejemplo.com"

# Agregar a SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Agregar a GitHub: Settings → SSH and GPG keys → New SSH key
cat ~/.ssh/id_ed25519.pub
```

### Error: "remote origin already exists"

```bash
# Ver remote actual
git remote -v

# Cambiar URL
git remote set-url origin https://github.com/TU_USUARIO/pimst-solver.git
```

### Error: "Your branch is behind"

```bash
# Pull cambios primero
git pull origin main

# Luego push
git push origin main
```

---

## 📞 Recursos Adicionales

- [GitHub Docs](https://docs.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**¡Listo!** Tu proyecto PIMST ya está profesionalmente configurado en GitHub. 🎉
