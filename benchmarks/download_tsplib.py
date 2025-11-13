"""
Descargar instancias TSPLIB para benchmarks académicos
"""
import urllib.request
import os

# Instancias TSPLIB clásicas con soluciones óptimas conocidas
instances = {
    'eil51': 426,      # 51 ciudades, óptimo conocido
    'berlin52': 7542,
    'st70': 675,
    'eil76': 538,
    'pr76': 108159,
    'rat99': 1211,
    'kroA100': 21282,
    'kroB100': 22141,
    'kroC100': 20749,
    'kroD100': 21294,
    'kroE100': 22068,
    'rd100': 7910,
    'eil101': 629,
    'lin105': 14379,
    'pr107': 44303,
    'pr124': 59030,
    'bier127': 118282,
    'ch130': 6110,
    'pr136': 96772,
    'pr144': 58537,
    'ch150': 6528,
    'kroA150': 26524,
    'kroB150': 26130,
    'pr152': 73682,
    'u159': 42080,
    'rat195': 2323,
    'kroA200': 29368,
    'kroB200': 29437,
    'ts225': 126643,
    'pr226': 80369,
    'gil262': 2378,
    'pr264': 49135,
    'pr299': 48191,
}

base_url = 'http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/'

print("Descargando instancias TSPLIB...")
for name, optimal in instances.items():
    url = f"{base_url}{name}.tsp.gz"
    filename = f"benchmarks/tsplib/{name}.tsp.gz"
    
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"✅ {name}: óptimo = {optimal}")
    except:
        print(f"❌ Error descargando {name}")

print("\n✅ Descarga completada")
