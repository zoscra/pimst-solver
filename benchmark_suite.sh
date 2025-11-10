#!/bin/bash
# benchmark_suite.sh - Suite completa de benchmarks para PIMST

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo "======================================================================"
echo -e "${BLUE}🚀 PIMST BENCHMARK SUITE${NC}"
echo "======================================================================"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "setup.py" ]; then
    echo -e "${RED}❌ Error: No estás en el directorio raíz del proyecto${NC}"
    echo "Por favor ejecuta este script desde el directorio pimst-solver/"
    exit 1
fi

# Verificar que PIMST está instalado
if ! python -c "import pimst" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PIMST no está instalado. Instalando...${NC}"
    pip install -e . > /dev/null 2>&1
    echo -e "${GREEN}✅ PIMST instalado${NC}"
fi

# Crear directorio para resultados
RESULTS_DIR="benchmark_results"
mkdir -p $RESULTS_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_DIR="$RESULTS_DIR/session_$TIMESTAMP"
mkdir -p $SESSION_DIR

echo -e "${BLUE}📁 Resultados se guardarán en: $SESSION_DIR${NC}"
echo ""

# Guardar información de la versión actual
echo "======================================================================"
echo -e "${BLUE}📊 INFORMACIÓN DE LA VERSIÓN${NC}"
echo "======================================================================"
COMMIT_HASH=$(git rev-parse HEAD 2>/dev/null || echo "N/A")
COMMIT_SHORT=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
BRANCH=$(git branch --show-current 2>/dev/null || echo "N/A")
VERSION=$(python -c "import pimst; print(pimst.__version__)" 2>/dev/null || echo "N/A")

echo "Versión PIMST: $VERSION"
echo "Commit: $COMMIT_SHORT ($COMMIT_HASH)"
echo "Rama: $BRANCH"
echo "Fecha: $(date)"
echo "Usuario: $(whoami)"
echo "Máquina: $(hostname)"

# Guardar info en archivo
cat > $SESSION_DIR/session_info.txt << EOF
PIMST Benchmark Session
=======================
Versión: $VERSION
Commit: $COMMIT_HASH
Rama: $BRANCH
Fecha: $(date)
Usuario: $(whoami)
Máquina: $(hostname)
Python: $(python --version)
EOF

echo ""

# Función para ejecutar benchmark con manejo de errores
run_benchmark() {
    local name=$1
    local script=$2
    local output=$3
    
    echo "======================================================================"
    echo -e "${BLUE}🔄 Ejecutando: $name${NC}"
    echo "======================================================================"
    echo ""
    
    START_TIME=$(date +%s)
    
    if python $script 2>&1 | tee $SESSION_DIR/$output.log; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        echo ""
        echo -e "${GREEN}✅ $name completado en ${DURATION}s${NC}"
        
        # Copiar resultado si existe
        if [ -f "benchmark_results.json" ]; then
            cp benchmark_results.json $SESSION_DIR/$output.json
        fi
        if [ -f "large_benchmark_results.json" ]; then
            cp large_benchmark_results.json $SESSION_DIR/$output.json
        fi
        
        return 0
    else
        echo ""
        echo -e "${RED}❌ Error en $name${NC}"
        return 1
    fi
}

# Menu de opciones
echo "======================================================================"
echo -e "${BLUE}📋 OPCIONES DE BENCHMARK${NC}"
echo "======================================================================"
echo ""
echo "1) Quick Test       - Tests unitarios rápidos (1 min)"
echo "2) Small Benchmark  - Instancias N≤100 vs OR-Tools (5-10 min)"
echo "3) Large Benchmark  - Instancias N=200-1000 (20-40 min)"
echo "4) Market Compare   - Comparación completa con el mercado (30-60 min)"
echo "5) Full Suite       - Todo lo anterior (60-120 min)"
echo "6) Custom           - Seleccionar benchmarks específicos"
echo ""
echo "0) Salir"
echo ""

read -p "Selecciona una opción [0-6]: " option

case $option in
    1)
        echo ""
        echo -e "${BLUE}🧪 Ejecutando tests unitarios...${NC}"
        pytest tests/ -v --tb=short 2>&1 | tee $SESSION_DIR/tests.log
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            echo -e "${GREEN}✅ Todos los tests pasaron${NC}"
        else
            echo -e "${RED}❌ Algunos tests fallaron${NC}"
        fi
        ;;
    
    2)
        run_benchmark "Small Benchmark (N≤100)" "benchmark_comparison.py" "small_benchmark"
        ;;
    
    3)
        run_benchmark "Large Benchmark (N=200-1000)" "benchmark_large_scale.py" "large_benchmark"
        ;;
    
    4)
        run_benchmark "Market Comparison" "compare_with_market.py" "market_comparison"
        ;;
    
    5)
        echo ""
        echo -e "${YELLOW}⚠️  Suite completa: esto tomará 60-120 minutos${NC}"
        read -p "¿Continuar? [y/N]: " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo ""
            echo -e "${BLUE}🚀 Iniciando suite completa...${NC}"
            
            # Tests
            echo ""
            pytest tests/ -v --tb=short 2>&1 | tee $SESSION_DIR/tests.log
            
            # Small benchmark
            run_benchmark "Small Benchmark" "benchmark_comparison.py" "small_benchmark"
            
            # Large benchmark
            run_benchmark "Large Benchmark" "benchmark_large_scale.py" "large_benchmark"
            
            # Market comparison
            run_benchmark "Market Comparison" "compare_with_market.py" "market_comparison"
            
            echo ""
            echo -e "${GREEN}✅ Suite completa terminada${NC}"
        else
            echo "Cancelado"
            exit 0
        fi
        ;;
    
    6)
        echo ""
        echo -e "${BLUE}Benchmarks disponibles:${NC}"
        echo "  t) Tests unitarios"
        echo "  s) Small benchmark"
        echo "  l) Large benchmark"
        echo "  m) Market comparison"
        echo ""
        read -p "Selecciona benchmarks a ejecutar (ej: ts para tests + small): " custom
        
        if [[ $custom == *"t"* ]]; then
            pytest tests/ -v 2>&1 | tee $SESSION_DIR/tests.log
        fi
        if [[ $custom == *"s"* ]]; then
            run_benchmark "Small Benchmark" "benchmark_comparison.py" "small_benchmark"
        fi
        if [[ $custom == *"l"* ]]; then
            run_benchmark "Large Benchmark" "benchmark_large_scale.py" "large_benchmark"
        fi
        if [[ $custom == *"m"* ]]; then
            run_benchmark "Market Comparison" "compare_with_market.py" "market_comparison"
        fi
        ;;
    
    0)
        echo "Saliendo..."
        exit 0
        ;;
    
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

# Generar reporte resumen
echo ""
echo "======================================================================"
echo -e "${BLUE}📊 GENERANDO REPORTE RESUMEN${NC}"
echo "======================================================================"

REPORT_FILE="$SESSION_DIR/SUMMARY_REPORT.md"

cat > $REPORT_FILE << EOF
# Reporte de Benchmark - PIMST

**Fecha:** $(date)
**Versión:** $VERSION
**Commit:** $COMMIT_SHORT
**Rama:** $BRANCH

---

## Configuración

- **Usuario:** $(whoami)
- **Máquina:** $(hostname)
- **Python:** $(python --version)
- **Sistema:** $(uname -s)

---

## Resultados

EOF

# Añadir resultados si existen
if [ -f "$SESSION_DIR/small_benchmark.json" ]; then
    echo "### Small Benchmark (N≤100)" >> $REPORT_FILE
    echo "" >> $REPORT_FILE
    echo "✅ Completado. Ver \`small_benchmark.json\` para detalles." >> $REPORT_FILE
    echo "" >> $REPORT_FILE
fi

if [ -f "$SESSION_DIR/large_benchmark.json" ]; then
    echo "### Large Benchmark (N=200-1000)" >> $REPORT_FILE
    echo "" >> $REPORT_FILE
    echo "✅ Completado. Ver \`large_benchmark.json\` para detalles." >> $REPORT_FILE
    echo "" >> $REPORT_FILE
fi

if [ -f "$SESSION_DIR/market_comparison.json" ]; then
    echo "### Market Comparison" >> $REPORT_FILE
    echo "" >> $REPORT_FILE
    echo "✅ Completado. Ver \`market_comparison.json\` para detalles." >> $REPORT_FILE
    echo "" >> $REPORT_FILE
fi

cat >> $REPORT_FILE << EOF

---

## Archivos Generados

EOF

ls -lh $SESSION_DIR >> $REPORT_FILE

echo ""
echo -e "${GREEN}✅ Reporte generado: $REPORT_FILE${NC}"

# Resumen final
echo ""
echo "======================================================================"
echo -e "${GREEN}🎉 BENCHMARK COMPLETADO${NC}"
echo "======================================================================"
echo ""
echo -e "${BLUE}📁 Resultados guardados en:${NC} $SESSION_DIR"
echo ""
echo -e "${BLUE}Archivos generados:${NC}"
ls -lh $SESSION_DIR | tail -n +2
echo ""
echo -e "${YELLOW}💡 Próximos pasos:${NC}"
echo "  1. Revisar resultados en $SESSION_DIR"
echo "  2. Comparar con versiones anteriores:"
echo "     python compare_versions.py $SESSION_DIR/small_benchmark.json benchmark_results/previous.json"
echo "  3. Actualizar README.md con resultados destacados"
echo "  4. Commit resultados si son significativos:"
echo "     git add $SESSION_DIR"
echo "     git commit -m 'docs: Resultados de benchmark v$VERSION'"
echo ""

# Abrir directorio (opcional)
read -p "¿Abrir carpeta de resultados? [y/N]: " open_folder
if [[ $open_folder =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        explorer.exe $SESSION_DIR
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        open $SESSION_DIR
    else
        xdg-open $SESSION_DIR 2>/dev/null || echo "Abre manualmente: $SESSION_DIR"
    fi
fi

echo ""
echo "✨ ¡Gracias por usar PIMST Benchmark Suite!"
