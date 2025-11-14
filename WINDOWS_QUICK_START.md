# 🪟 Windows Quick Start - Ejecutar Benchmark AHORA

## ⚠️ Problema: Python no está en PATH

El error que viste significa que Git Bash no encuentra Python. Aquí está la solución:

---

## 🎯 Solución Rápida (Prueba Estos Comandos)

En Git Bash, prueba **uno por uno** hasta que funcione:

### Opción 1: Usar el launcher de Python (más común en Windows)

```bash
py --version
```

Si funciona, usa:
```bash
py -m pip install numpy numba scipy ortools
py benchmark_atsp_complete.py
```

### Opción 2: Usar python directamente

```bash
python --version
```

Si funciona, usa:
```bash
python -m pip install numpy numba scipy ortools
python benchmark_atsp_complete.py
```

### Opción 3: Usar python3

```bash
python3 --version
```

Si funciona, usa:
```bash
python3 -m pip install numpy numba scipy ortools
python3 benchmark_atsp_complete.py
```

---

## 📋 Si NINGUNO Funciona: Instalar Python

Si ningún comando anterior muestra la versión de Python, necesitas instalarlo:

### Método 1: Microsoft Store (MÁS FÁCIL)

1. Presiona `Win + S`
2. Busca "Microsoft Store"
3. En la Store, busca "Python 3.12" o "Python 3.11"
4. Click "Get" o "Instalar"
5. Espera a que termine
6. **Reinicia Git Bash**
7. Intenta `py --version`

### Método 2: python.org

1. Ve a: https://www.python.org/downloads/
2. Click en "Download Python 3.12.x" (botón grande amarillo)
3. **Ejecuta el instalador**
4. ⚠️ **IMPORTANTE**: Marca la casilla **"Add Python to PATH"**
5. Click "Install Now"
6. **Reinicia Git Bash**
7. Intenta `python --version`

---

## ✅ Una Vez que Python Funcione

### Paso 1: Verificar Python

```bash
# Prueba cuál funciona:
py --version
# o
python --version
```

Deberías ver algo como: `Python 3.11.x` o `Python 3.12.x`

### Paso 2: Instalar Dependencias

Usa el comando que funcionó arriba. Si fue `py`, usa:

```bash
py -m pip install numpy numba scipy ortools
```

Si fue `python`, usa:

```bash
python -m pip install numpy numba scipy ortools
```

**Tiempo:** ~2-5 minutos dependiendo de tu conexión.

### Paso 3: Ejecutar Benchmark

#### Quick Test (5 minutos):

```bash
# Si usas 'py':
py benchmark_atsp_complete.py --quick

# Si usas 'python':
python benchmark_atsp_complete.py --quick
```

#### Full Benchmark (60-90 minutos):

```bash
# Si usas 'py':
py benchmark_atsp_complete.py

# Si usas 'python':
python benchmark_atsp_complete.py
```

---

## 🔧 Troubleshooting

### Error: "pip no encontrado"

Si `pip install` falla, prueba:

```bash
py -m ensurepip --upgrade
# o
python -m ensurepip --upgrade
```

### Error: "numpy compilation failed"

En Windows, instala primero la versión pre-compilada:

```bash
py -m pip install --upgrade pip setuptools wheel
py -m pip install numpy numba scipy ortools
```

### Error: "Permission denied"

Ejecuta Git Bash como Administrador:
1. Click derecho en Git Bash
2. "Ejecutar como administrador"
3. Navega a la carpeta: `cd ~/pimst-solver`
4. Intenta de nuevo

### Python instalado pero no se encuentra

Reinicia completamente:
1. Cierra **todas** las ventanas de Git Bash
2. Abre una nueva ventana de Git Bash
3. Intenta `py --version` o `python --version`

---

## 📊 Comandos Completos de Referencia

### Si tienes 'py':

```bash
# 1. Verificar Python
py --version

# 2. Actualizar pip
py -m pip install --upgrade pip

# 3. Instalar dependencias
py -m pip install numpy numba scipy ortools

# 4. Verificar instalación
py -c "import numpy, numba, scipy; print('✅ Todo instalado')"

# 5. Quick test
py benchmark_atsp_complete.py --quick

# 6. Full benchmark
py benchmark_atsp_complete.py
```

### Si tienes 'python':

```bash
# 1. Verificar Python
python --version

# 2. Actualizar pip
python -m pip install --upgrade pip

# 3. Instalar dependencias
python -m pip install numpy numba scipy ortools

# 4. Verificar instalación
python -c "import numpy, numba, scipy; print('✅ Todo instalado')"

# 5. Quick test
python benchmark_atsp_complete.py --quick

# 6. Full benchmark
python benchmark_atsp_complete.py
```

---

## 🎯 Resumen Ultra-Rápido

```bash
# 1. Prueba si Python funciona
py --version

# 2. Si funciona, instala dependencias
py -m pip install numpy numba scipy ortools

# 3. Ejecuta benchmark
py benchmark_atsp_complete.py --quick
```

Si `py` no funciona, reemplaza `py` por `python` en todos los comandos.

---

## 🆘 Si Nada Funciona

Envíame la salida de estos comandos:

```bash
# En Git Bash, ejecuta:
echo "=== Checking Python ==="
which python python3 py

echo "=== Checking PATH ==="
echo $PATH

echo "=== Checking System ==="
uname -a
```

Y te ayudaré a diagnosticar el problema específico.

---

## ✅ Siguiente Paso

**Ejecuta esto AHORA en Git Bash:**

```bash
py --version
```

**Si ves la versión de Python**, continúa con:

```bash
py -m pip install numpy numba scipy ortools
py benchmark_atsp_complete.py --quick
```

**Si no ves nada**, instala Python desde Microsoft Store o python.org (ver arriba).

🚀 ¡Estás a solo unos comandos de tener los resultados completos!
