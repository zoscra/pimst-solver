#!/bin/bash
# compare_two_versions.sh - Compare two git versions automatically

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar argumentos
if [ $# -ne 2 ]; then
    echo "Usage: $0 <version1> <version2>"
    echo "Example: $0 v0.21.0 v0.22.0"
    exit 1
fi

VERSION1=$1
VERSION2=$2
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

echo "======================================================================"
echo -e "${BLUE}📊 Comparando PIMST: $VERSION1 vs $VERSION2${NC}"
echo "======================================================================"
echo ""

# Verificar que las versiones existen
if ! git rev-parse "$VERSION1" >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: Versión $VERSION1 no encontrada${NC}"
    exit 1
fi

if ! git rev-parse "$VERSION2" >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: Versión $VERSION2 no encontrada${NC}"
    exit 1
fi

# Crear directorio temporal
TEMP_DIR="/tmp/pimst_comparison_$$"
mkdir -p $TEMP_DIR
echo -e "${BLUE}📁 Resultados temporales en: $TEMP_DIR${NC}"
echo ""

# Función para ejecutar benchmark en una versión
run_benchmark_for_version() {
    local version=$1
    local output_file=$2
    
    echo "======================================================================"
    echo -e "${BLUE}🔄 Ejecutando benchmark para $version...${NC}"
    echo "======================================================================"
    
    # Checkout versión
    git checkout "$version" 2>&1 | grep -v "^Note:"
    
    # Reinstalar
    echo "   Instalando PIMST $version..."
    pip install -e . > /dev/null 2>&1
    
    # Verificar instalación
    VERSION_INSTALLED=$(python -c "import pimst; print(pimst.__version__)" 2>/dev/null || echo "unknown")
    echo "   ✅ Versión instalada: $VERSION_INSTALLED"
    
    # Ejecutar benchmark
    echo "   Ejecutando benchmark..."
    START_TIME=$(date +%s)
    
    if python benchmark_comparison.py 2>&1 | tail -10; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        echo ""
        echo -e "   ${GREEN}✅ Benchmark completado en ${DURATION}s${NC}"
        
        # Copiar resultados
        if [ -f "benchmark_results.json" ]; then
            cp benchmark_results.json "$output_file"
            echo "   ✅ Resultados guardados"
        else
            echo -e "   ${RED}❌ No se encontró benchmark_results.json${NC}"
            return 1
        fi
    else
        echo -e "   ${RED}❌ Error ejecutando benchmark${NC}"
        return 1
    fi
    
    echo ""
}

# Ejecutar benchmarks
echo "🚀 Iniciando comparación..."
echo ""

# Benchmark versión 1
if ! run_benchmark_for_version "$VERSION1" "$TEMP_DIR/${VERSION1}_results.json"; then
    echo -e "${RED}❌ Error en versión $VERSION1${NC}"
    git checkout "$CURRENT_BRANCH" 2>/dev/null
    exit 1
fi

# Benchmark versión 2
if ! run_benchmark_for_version "$VERSION2" "$TEMP_DIR/${VERSION2}_results.json"; then
    echo -e "${RED}❌ Error en versión $VERSION2${NC}"
    git checkout "$CURRENT_BRANCH" 2>/dev/null
    exit 1
fi

# Volver a rama original
echo "======================================================================"
echo -e "${BLUE}🔄 Restaurando rama original: $CURRENT_BRANCH${NC}"
echo "======================================================================"
git checkout "$CURRENT_BRANCH" 2>&1 | grep -v "^Note:"
pip install -e . > /dev/null 2>&1
echo ""

# Comparar resultados
echo "======================================================================"
echo -e "${BLUE}📊 Comparando resultados...${NC}"
echo "======================================================================"
echo ""

if [ -f "$TEMP_DIR/${VERSION1}_results.json" ] && [ -f "$TEMP_DIR/${VERSION2}_results.json" ]; then
    python compare_versions.py \
        "$TEMP_DIR/${VERSION1}_results.json" \
        "$TEMP_DIR/${VERSION2}_results.json"
else
    echo -e "${RED}❌ No se pudieron comparar los resultados${NC}"
    exit 1
fi

# Guardar resultados permanentemente si se desea
echo ""
echo "======================================================================"
echo -e "${BLUE}💾 Guardar resultados permanentemente?${NC}"
echo "======================================================================"
read -p "¿Guardar en benchmark_history/? [y/N]: " save_results

if [[ $save_results =~ ^[Yy]$ ]]; then
    mkdir -p benchmark_history
    cp "$TEMP_DIR/${VERSION1}_results.json" "benchmark_history/${VERSION1}_results.json"
    cp "$TEMP_DIR/${VERSION2}_results.json" "benchmark_history/${VERSION2}_results.json"
    echo -e "${GREEN}✅ Resultados guardados en benchmark_history/${NC}"
else
    echo "Resultados no guardados (disponibles en $TEMP_DIR)"
fi

echo ""
echo "======================================================================"
echo -e "${GREEN}✅ COMPARACIÓN COMPLETADA${NC}"
echo "======================================================================"
echo ""
echo -e "${BLUE}📁 Archivos temporales:${NC}"
echo "   $TEMP_DIR/${VERSION1}_results.json"
echo "   $TEMP_DIR/${VERSION2}_results.json"
echo ""
echo -e "${BLUE}💡 Para limpiar archivos temporales:${NC}"
echo "   rm -rf $TEMP_DIR"
echo ""
