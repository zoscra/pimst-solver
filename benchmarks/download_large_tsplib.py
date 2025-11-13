"""
Descargar instancias TSPLIB grandes (300-600 ciudades)
"""
import urllib.request
import gzip
import shutil
from pathlib import Path

# Instancias grandes
large_instances = {
    'a280': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/a280.tsp.gz',
    'pr299': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/pr299.tsp.gz',
    'lin318': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/lin318.tsp.gz',
    'rd400': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/rd400.tsp.gz',
    'fl417': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/fl417.tsp.gz',
    'pr439': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/pr439.tsp.gz',
    'pcb442': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/pcb442.tsp.gz',
    'd493': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/d493.tsp.gz',
    'u574': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/u574.tsp.gz',
    'rat575': 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/rat575.tsp.gz',
}

output_dir = Path('benchmarks/tsplib')
output_dir.mkdir(parents=True, exist_ok=True)

print("="*70)
print("  📥 DESCARGANDO INSTANCIAS GRANDES TSPLIB")
print("="*70)

for name, url in large_instances.items():
    output_file = output_dir / f"{name}.tsp.gz"
    
    if output_file.exists():
        print(f"✓ {name} ya existe")
        continue
    
    try:
        print(f"⬇️  Descargando {name}...", end=' ', flush=True)
        urllib.request.urlretrieve(url, output_file)
        print("✅")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*70)
print("  ✅ DESCARGA COMPLETADA")
print("="*70)
