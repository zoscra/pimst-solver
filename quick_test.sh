#!/bin/bash
# quick_test.sh - Tests rápidos antes de commit

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "======================================================================"
echo -e "${BLUE}🧪 PIMST QUICK TEST SUITE${NC}"
echo "======================================================================"
echo ""

# Verificar entorno
echo -e "${BLUE}🔍 Verificando entorno...${NC}"

if ! python -c "import pimst" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PIMST no está instalado. Instalando...${NC}"
    pip install -e . > /dev/null 2>&1
fi

if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  pytest no está instalado. Instalando...${NC}"
    pip install pytest pytest-cov > /dev/null 2>&1
fi

echo -e "${GREEN}✅ Entorno verificado${NC}"
echo ""

# 1. Tests unitarios
echo "======================================================================"
echo -e "${BLUE}1️⃣  Tests Unitarios${NC}"
echo "======================================================================"
pytest tests/ -v --tb=short --durations=5

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Tests unitarios: PASSED${NC}"
    TESTS_PASSED=true
else
    echo -e "${RED}❌ Tests unitarios: FAILED${NC}"
    TESTS_PASSED=false
fi

echo ""

# 2. Coverage
echo "======================================================================"
echo -e "${BLUE}2️⃣  Code Coverage${NC}"
echo "======================================================================"
pytest --cov=pimst tests/ --cov-report=term-missing --cov-report=html --cov-fail-under=70 -q

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Coverage >70%: PASSED${NC}"
    COVERAGE_PASSED=true
else
    echo -e "${RED}❌ Coverage <70%: FAILED${NC}"
    COVERAGE_PASSED=false
fi

echo ""

# 3. Type checking (si está mypy)
if python -c "import mypy" 2>/dev/null; then
    echo "======================================================================"
    echo -e "${BLUE}3️⃣  Type Checking${NC}"
    echo "======================================================================"
    mypy src/pimst --ignore-missing-imports --no-strict-optional 2>&1 | head -20
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✅ Type checking: PASSED${NC}"
        MYPY_PASSED=true
    else
        echo -e "${YELLOW}⚠️  Type checking: WARNINGS${NC}"
        MYPY_PASSED=false
    fi
    echo ""
fi

# 4. Linting (si está flake8)
if python -c "import flake8" 2>/dev/null; then
    echo "======================================================================"
    echo -e "${BLUE}4️⃣  Code Linting${NC}"
    echo "======================================================================"
    flake8 src/pimst --count --max-line-length=100 --statistics 2>&1 | head -20
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✅ Linting: PASSED${NC}"
        LINT_PASSED=true
    else
        echo -e "${YELLOW}⚠️  Linting: WARNINGS${NC}"
        LINT_PASSED=false
    fi
    echo ""
fi

# 5. Benchmark rápido (solo instancias pequeñas)
echo "======================================================================"
echo -e "${BLUE}5️⃣  Quick Performance Test${NC}"
echo "======================================================================"

python -c "
import pimst
import time
import numpy as np

# Test básico
coords = [(np.random.rand()*100, np.random.rand()*100) for _ in range(30)]

start = time.time()
result = pimst.solve(coords, quality='fast')
elapsed = time.time() - start

print(f'✅ N=30: {result[\"length\"]:.2f} en {elapsed*1000:.1f}ms')

# Test mediano
coords = [(np.random.rand()*100, np.random.rand()*100) for _ in range(50)]

start = time.time()
result = pimst.solve(coords, quality='balanced')
elapsed = time.time() - start

print(f'✅ N=50: {result[\"length\"]:.2f} en {elapsed*1000:.1f}ms')

if elapsed < 0.1:
    print('✅ Performance: PASSED')
    exit(0)
else:
    print('⚠️  Performance: Más lento de lo esperado')
    exit(1)
"

if [ $? -eq 0 ]; then
    PERF_PASSED=true
else
    PERF_PASSED=false
fi

echo ""

# Resumen final
echo "======================================================================"
echo -e "${BLUE}📊 RESUMEN${NC}"
echo "======================================================================"
echo ""

if [ "$TESTS_PASSED" = true ]; then
    echo -e "✅ Tests Unitarios: ${GREEN}PASSED${NC}"
else
    echo -e "❌ Tests Unitarios: ${RED}FAILED${NC}"
fi

if [ "$COVERAGE_PASSED" = true ]; then
    echo -e "✅ Code Coverage: ${GREEN}PASSED${NC}"
else
    echo -e "❌ Code Coverage: ${RED}FAILED${NC}"
fi

if [ -n "$MYPY_PASSED" ]; then
    if [ "$MYPY_PASSED" = true ]; then
        echo -e "✅ Type Checking: ${GREEN}PASSED${NC}"
    else
        echo -e "⚠️  Type Checking: ${YELLOW}WARNINGS${NC}"
    fi
fi

if [ -n "$LINT_PASSED" ]; then
    if [ "$LINT_PASSED" = true ]; then
        echo -e "✅ Code Linting: ${GREEN}PASSED${NC}"
    else
        echo -e "⚠️  Code Linting: ${YELLOW}WARNINGS${NC}"
    fi
fi

if [ "$PERF_PASSED" = true ]; then
    echo -e "✅ Performance: ${GREEN}PASSED${NC}"
else
    echo -e "⚠️  Performance: ${YELLOW}SLOW${NC}"
fi

echo ""

# Decisión final
if [ "$TESTS_PASSED" = true ] && [ "$COVERAGE_PASSED" = true ] && [ "$PERF_PASSED" = true ]; then
    echo "======================================================================"
    echo -e "${GREEN}🎉 TODOS LOS CHECKS PASARON - LISTO PARA COMMIT${NC}"
    echo "======================================================================"
    echo ""
    echo "Próximos pasos:"
    echo "  git add ."
    echo "  git commit -m 'tu mensaje'"
    echo "  git push"
    exit 0
else
    echo "======================================================================"
    echo -e "${RED}⚠️  ALGUNOS CHECKS FALLARON - REVISA ANTES DE COMMIT${NC}"
    echo "======================================================================"
    echo ""
    echo "Recomendaciones:"
    if [ "$TESTS_PASSED" = false ]; then
        echo "  - Corrige los tests que fallaron"
    fi
    if [ "$COVERAGE_PASSED" = false ]; then
        echo "  - Aumenta cobertura de tests (objetivo: >70%)"
        echo "  - Ver reporte: open htmlcov/index.html"
    fi
    if [ "$PERF_PASSED" = false ]; then
        echo "  - Revisa por qué el rendimiento empeoró"
    fi
    exit 1
fi
