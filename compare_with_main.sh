#!/bin/bash
# compare_with_main.sh - Compare current branch with main

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# Verificar que no estamos en main
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo -e "${YELLOW}⚠️  Ya estás en la rama main${NC}"
    echo "No hay nada que comparar."
    exit 0
fi

if [ "$CURRENT_BRANCH" = "unknown" ]; then
    echo -e "${RED}❌ No se pudo determinar la rama actual${NC}"
    exit 1
fi

echo "======================================================================"
echo -e "${BLUE}📊 Comparando $CURRENT_BRANCH con main${NC}"
echo "======================================================================"
echo ""

# Verificar que hay cambios no guardados
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  Hay cambios no guardados${NC}"
    echo ""
    read -p "¿Hacer stash de los cambios? [Y/n]: " do_stash
    
    if [[ ! $do_stash =~ ^[Nn]$ ]]; then
        git stash push -m "Temporal para comparación con main"
        STASHED=true
        echo -e "${GREEN}✅ Cambios guardados temporalmente${NC}"
    else
        echo -e "${YELLOW}⚠️  Continuando sin hacer stash...${NC}"
        STASHED=false
    fi
    echo ""
fi

# Crear directorio temporal
TEMP_DIR="/tmp/pimst_main_comparison_$$"
mkdir -p $TEMP_DIR

# Benchmark en rama actual
echo "======================================================================"
echo -e "${BLUE}1️⃣  Ejecutando benchmark en $CURRENT_BRANCH...${NC}"
echo "======================================================================"
echo ""

START_TIME=$(date +%s)

if python benchmark_comparison.py 2>&1 | tail -10; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo ""
    echo -e "${GREEN}✅ Benchmark completado en ${DURATION}s${NC}"
    
    if [ -f "benchmark_results.json" ]; then
        cp benchmark_results.json "$TEMP_DIR/current_branch_results.json"
        echo -e "${GREEN}✅ Resultados guardados${NC}"
    else
        echo -e "${RED}❌ No se encontró benchmark_results.json${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Error ejecutando benchmark${NC}"
    exit 1
fi

echo ""

# Cambiar a main
echo "======================================================================"
echo -e "${BLUE}2️⃣  Cambiando a main...${NC}"
echo "======================================================================"

git checkout main 2>&1 | grep -v "^Note:"
pip install -e . > /dev/null 2>&1

VERSION_MAIN=$(python -c "import pimst; print(pimst.__version__)" 2>/dev/null || echo "unknown")
echo -e "${GREEN}✅ En main (versión $VERSION_MAIN)${NC}"
echo ""

# Benchmark en main
echo "======================================================================"
echo -e "${BLUE}3️⃣  Ejecutando benchmark en main...${NC}"
echo "======================================================================"
echo ""

START_TIME=$(date +%s)

if python benchmark_comparison.py 2>&1 | tail -10; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo ""
    echo -e "${GREEN}✅ Benchmark completado en ${DURATION}s${NC}"
    
    if [ -f "benchmark_results.json" ]; then
        cp benchmark_results.json "$TEMP_DIR/main_results.json"
        echo -e "${GREEN}✅ Resultados guardados${NC}"
    else
        echo -e "${RED}❌ No se encontró benchmark_results.json${NC}"
        git checkout "$CURRENT_BRANCH" 2>/dev/null
        exit 1
    fi
else
    echo -e "${RED}❌ Error ejecutando benchmark${NC}"
    git checkout "$CURRENT_BRANCH" 2>/dev/null
    exit 1
fi

echo ""

# Volver a rama original
echo "======================================================================"
echo -e "${BLUE}4️⃣  Restaurando rama $CURRENT_BRANCH...${NC}"
echo "======================================================================"

git checkout "$CURRENT_BRANCH" 2>&1 | grep -v "^Note:"
pip install -e . > /dev/null 2>&1

if [ "$STASHED" = true ]; then
    echo "   Restaurando cambios guardados..."
    git stash pop > /dev/null 2>&1
    echo -e "   ${GREEN}✅ Cambios restaurados${NC}"
fi

echo -e "${GREEN}✅ De vuelta en $CURRENT_BRANCH${NC}"
echo ""

# Comparar resultados
echo "======================================================================"
echo -e "${BLUE}📊 COMPARANDO RESULTADOS${NC}"
echo "======================================================================"
echo ""

python compare_versions.py \
    "$TEMP_DIR/main_results.json" \
    "$TEMP_DIR/current_branch_results.json"

# Guardar resultados si se desea
echo ""
echo "======================================================================"
echo -e "${BLUE}💾 OPCIONES${NC}"
echo "======================================================================"
echo ""
echo "1. Guardar resultados en benchmark_history/"
echo "2. Limpiar archivos temporales"
echo "3. Ambos"
echo "4. Ninguno (mantener en $TEMP_DIR)"
echo ""

read -p "Selecciona opción [1-4]: " option

case $option in
    1)
        mkdir -p benchmark_history
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        cp "$TEMP_DIR/main_results.json" "benchmark_history/main_${TIMESTAMP}.json"
        cp "$TEMP_DIR/current_branch_results.json" "benchmark_history/${CURRENT_BRANCH}_${TIMESTAMP}.json"
        echo -e "${GREEN}✅ Resultados guardados en benchmark_history/${NC}"
        ;;
    2)
        rm -rf $TEMP_DIR
        echo -e "${GREEN}✅ Archivos temporales eliminados${NC}"
        ;;
    3)
        mkdir -p benchmark_history
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        cp "$TEMP_DIR/main_results.json" "benchmark_history/main_${TIMESTAMP}.json"
        cp "$TEMP_DIR/current_branch_results.json" "benchmark_history/${CURRENT_BRANCH}_${TIMESTAMP}.json"
        rm -rf $TEMP_DIR
        echo -e "${GREEN}✅ Resultados guardados y archivos temporales eliminados${NC}"
        ;;
    4)
        echo "Archivos mantenidos en: $TEMP_DIR"
        ;;
    *)
        echo "Opción inválida. Archivos mantenidos en: $TEMP_DIR"
        ;;
esac

# Veredicto final
echo ""
echo "======================================================================"
echo -e "${BLUE}💡 RECOMENDACIÓN${NC}"
echo "======================================================================"
echo ""

# Leer el JSON para determinar si mejoró
if command -v jq &> /dev/null; then
    # Si jq está disponible, hacer análisis más detallado
    echo "Análisis automático no disponible (requiere jq)"
else
    echo "💡 Revisa los resultados de la comparación arriba para decidir:"
fi

echo ""
echo "✅ Si tu rama mejora el rendimiento → Procede con el merge"
echo "⚠️  Si hay regresiones menores → Evalúa si vale la pena"
echo "❌ Si hay regresiones significativas → Revisa antes de merge"
echo ""
echo "Comandos útiles:"
echo "  git diff main                 # Ver cambios de código"
echo "  git log main..HEAD            # Ver commits de tu rama"
echo "  git merge main                # Integrar cambios de main"
echo "  git push origin $CURRENT_BRANCH  # Push de tu rama"
echo ""

echo "======================================================================"
echo -e "${GREEN}✅ COMPARACIÓN COMPLETADA${NC}"
echo "======================================================================"
