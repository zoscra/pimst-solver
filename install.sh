#!/bin/bash
# Script de Instalación Rápida para PIMST
# =========================================

set -e  # Exit on error

echo "================================================"
echo "   PIMST Solver - Instalación Rápida"
echo "================================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# 1. Verificar Python
echo "1. Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python encontrado: $PYTHON_VERSION"
else
    print_error "Python 3 no encontrado. Por favor instala Python 3.9+"
    exit 1
fi

# 2. Crear entorno virtual (opcional)
echo ""
echo "2. ¿Deseas crear un entorno virtual? (recomendado) [y/N]"
read -r CREATE_VENV

if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
    print_info "Creando entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate
    print_success "Entorno virtual creado y activado"
else
    print_warning "Continuando sin entorno virtual"
fi

# 3. Actualizar pip
echo ""
echo "3. Actualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip actualizado"

# 4. Instalar dependencias
echo ""
echo "4. Instalando dependencias..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    print_success "Dependencias instaladas desde requirements.txt"
else
    print_warning "requirements.txt no encontrado"
    print_info "Instalando dependencias básicas..."
    pip install numpy scipy > /dev/null 2>&1
fi

# 5. Instalar paquete en modo desarrollo
echo ""
echo "5. Instalando PIMST en modo desarrollo..."
pip install -e . > /dev/null 2>&1
print_success "PIMST instalado"

# 6. Instalar herramientas de testing
echo ""
echo "6. Instalando herramientas de testing..."
pip install pytest pytest-cov flake8 black > /dev/null 2>&1
print_success "Herramientas de testing instaladas"

# 7. Verificar instalación
echo ""
echo "7. Verificando instalación..."

# Test 1: Import básico
if python3 -c "import pimst" 2>/dev/null; then
    print_success "Import de pimst: OK"
else
    print_error "Import de pimst: FALLO"
    exit 1
fi

# Test 2: Import SiNo
if python3 -c "from pimst.improved.sino import smart_solve" 2>/dev/null; then
    print_success "Import de SiNo: OK"
else
    print_error "Import de SiNo: FALLO"
    exit 1
fi

# Test 3: Pytest disponible
if command -v pytest &> /dev/null; then
    print_success "pytest: OK"
else
    print_warning "pytest: NO DISPONIBLE"
fi

# 8. Ejecutar tests rápidos
echo ""
echo "8. ¿Ejecutar tests para verificar? [y/N]"
read -r RUN_TESTS

if [[ "$RUN_TESTS" =~ ^[Yy]$ ]]; then
    print_info "Ejecutando tests..."
    if pytest tests/test_sino_system.py::TestSiNoBasics -v; then
        print_success "Tests básicos: PASARON"
    else
        print_warning "Algunos tests fallaron, pero la instalación está completa"
    fi
fi

# 9. Resumen
echo ""
echo "================================================"
echo "   ✅ INSTALACIÓN COMPLETADA"
echo "================================================"
echo ""
print_info "Próximos pasos:"
echo ""
echo "  1. Probar el sistema:"
echo "     python -c 'from pimst.improved.sino import smart_solve; import numpy as np; d = np.random.rand(10,10); tour, cost = smart_solve(d); print(f\"Costo: {cost:.2f}\")'"
echo ""
echo "  2. Ejecutar tests:"
echo "     pytest tests/ -v"
echo ""
echo "  3. Ver documentación:"
echo "     cat GUIA_SINO_RAPIDA.md"
echo ""
echo "  4. Configurar GitHub:"
echo "     cat GUIA_GITHUB_COMPLETA.md"
echo ""
echo "================================================"

# Nota sobre entorno virtual
if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
    echo ""
    print_warning "Nota: Para usar PIMST en el futuro, activa el entorno virtual:"
    echo "      source venv/bin/activate"
fi

echo ""
print_success "¡Todo listo! 🎉"
