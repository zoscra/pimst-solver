#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare two versions of benchmark results

Usage:
    python compare_versions.py results_v1.json results_v2.json
    python compare_versions.py --dir benchmark_history/  # Compare all in directory
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List
import numpy as np


class VersionComparator:
    """Compare benchmark results between two versions."""
    
    def __init__(self, file1: Path, file2: Path):
        self.file1 = file1
        self.file2 = file2
        self.results1 = self.load_results(file1)
        self.results2 = self.load_results(file2)
    
    def load_results(self, filepath: Path) -> Dict:
        """Load benchmark results from JSON."""
        with open(filepath, encoding='utf-8') as f:
            return json.load(f)
    
    def get_version_name(self, filepath: Path) -> str:
        """Extract version name from filename."""
        stem = filepath.stem
        
        # Try to extract version from filename
        if 'v0' in stem or 'v1' in stem:
            import re
            match = re.search(r'v?\d+\.\d+\.\d+', stem)
            if match:
                return match.group(0)
        
        return stem
    
    def compare_instance(self, name: str) -> Dict:
        """Compare a specific instance between versions."""
        if name not in self.results1 or name not in self.results2:
            return None
        
        inst1 = self.results1[name]
        inst2 = self.results2[name]
        
        # Get PIMST balanced results
        solver_key = 'pimst_balanced'
        
        if solver_key not in inst1['solvers'] or solver_key not in inst2['solvers']:
            return None
        
        res1 = inst1['solvers'][solver_key]
        res2 = inst2['solvers'][solver_key]
        
        length1 = res1['length']
        length2 = res2['length']
        time1 = res1['time']
        time2 = res2['time']
        
        # Calculate differences
        length_change = ((length2 - length1) / length1) * 100
        time_change = ((time2 - time1) / time1) * 100
        
        return {
            'name': name,
            'n': inst1['n'],
            'length1': length1,
            'length2': length2,
            'length_change_pct': length_change,
            'time1': time1,
            'time2': time2,
            'time_change_pct': time_change,
            'improved': length2 < length1
        }
    
    def compare_all(self) -> List[Dict]:
        """Compare all common instances."""
        comparisons = []
        
        common_instances = set(self.results1.keys()) & set(self.results2.keys())
        
        for name in sorted(common_instances):
            comp = self.compare_instance(name)
            if comp:
                comparisons.append(comp)
        
        return comparisons
    
    def print_comparison(self):
        """Print detailed comparison."""
        version1 = self.get_version_name(self.file1)
        version2 = self.get_version_name(self.file2)
        
        print("\n" + "=" * 80)
        print(f"📊 COMPARACIÓN DE VERSIONES")
        print("=" * 80)
        print(f"\n📁 Versión 1: {version1}")
        print(f"📁 Versión 2: {version2}")
        print()
        
        comparisons = self.compare_all()
        
        if not comparisons:
            print("❌ No hay instancias comunes para comparar")
            return
        
        # Table header
        print(f"{'Instancia':<25} {'N':<5} {'Δ Calidad':<12} {'Δ Tiempo':<12} {'Estado':<10}")
        print("-" * 80)
        
        # Print each instance
        improvements = 0
        regressions = 0
        neutral = 0
        
        for comp in comparisons:
            name = comp['name']
            n = comp['n']
            length_change = comp['length_change_pct']
            time_change = comp['time_change_pct']
            
            # Format changes
            if abs(length_change) < 0.01:
                length_str = "~"
                status = "="
                neutral += 1
            elif length_change < 0:
                length_str = f"{length_change:.2f}%"
                status = "✅"
                improvements += 1
            else:
                length_str = f"+{length_change:.2f}%"
                status = "⚠️"
                regressions += 1
            
            time_str = f"{time_change:+.1f}%"
            
            print(f"{name:<25} {n:<5} {length_str:<12} {time_str:<12} {status:<10}")
        
        # Summary statistics
        print("\n" + "=" * 80)
        print("📈 RESUMEN ESTADÍSTICO")
        print("=" * 80)
        
        # Quality changes
        quality_changes = [c['length_change_pct'] for c in comparisons]
        time_changes = [c['time_change_pct'] for c in comparisons]
        
        print(f"\n🎯 Cambios en Calidad (menor es mejor):")
        print(f"   Promedio:     {np.mean(quality_changes):+.2f}%")
        print(f"   Mediana:      {np.median(quality_changes):+.2f}%")
        print(f"   Mejor:        {np.min(quality_changes):+.2f}%")
        print(f"   Peor:         {np.max(quality_changes):+.2f}%")
        print(f"   Desv. Est.:   {np.std(quality_changes):.2f}%")
        
        print(f"\n⏱️  Cambios en Tiempo (menor es mejor):")
        print(f"   Promedio:     {np.mean(time_changes):+.1f}%")
        print(f"   Mediana:      {np.median(time_changes):+.1f}%")
        print(f"   Mejor:        {np.min(time_changes):+.1f}%")
        print(f"   Peor:         {np.max(time_changes):+.1f}%")
        
        print(f"\n📊 Balance:")
        print(f"   Mejoras:      {improvements} instancias")
        print(f"   Regresiones:  {regressions} instancias")
        print(f"   Sin cambio:   {neutral} instancias")
        
        # Verdict
        print("\n" + "=" * 80)
        avg_quality = np.mean(quality_changes)
        avg_time = np.mean(time_changes)
        
        if avg_quality < -1:  # More than 1% improvement
            print("✅ VEREDICTO: MEJORA SIGNIFICATIVA EN CALIDAD")
        elif avg_quality > 1:  # More than 1% regression
            print("⚠️  VEREDICTO: REGRESIÓN EN CALIDAD")
        else:
            print("➡️  VEREDICTO: CALIDAD SIMILAR")
        
        if avg_time < -10:  # More than 10% faster
            print("⚡ VELOCIDAD: SIGNIFICATIVAMENTE MÁS RÁPIDO")
        elif avg_time > 10:  # More than 10% slower
            print("🐌 VELOCIDAD: SIGNIFICATIVAMENTE MÁS LENTO")
        else:
            print("➡️  VELOCIDAD: SIMILAR")
        
        print("=" * 80)
        
        # Recommendations
        print("\n💡 RECOMENDACIONES:")
        
        if improvements > regressions:
            print("  ✅ Los cambios mejoran el rendimiento general")
            print("  ✅ Recomendar merge/commit")
        elif regressions > improvements * 2:
            print("  ⚠️  Los cambios empeoran significativamente el rendimiento")
            print("  ⚠️  Revisar antes de merge")
        else:
            print("  ➡️  Cambios mixtos - revisar instancias específicas")
        
        if avg_time > 20:
            print("  ⚠️  El tiempo de ejecución aumentó significativamente")
            print("  ⚠️  Considerar optimizaciones")


def compare_directory(directory: Path):
    """Compare all result files in a directory."""
    json_files = sorted(directory.glob("*.json"))
    
    if len(json_files) < 2:
        print(f"❌ Se necesitan al menos 2 archivos JSON en {directory}")
        return
    
    print(f"\n📁 Encontrados {len(json_files)} archivos de resultados")
    print("\nArchivos:")
    for i, f in enumerate(json_files, 1):
        print(f"  {i}. {f.name}")
    
    print("\nComparando versiones consecutivas...\n")
    
    for i in range(len(json_files) - 1):
        file1 = json_files[i]
        file2 = json_files[i + 1]
        
        print(f"\n{'='*80}")
        print(f"Comparando: {file1.name} → {file2.name}")
        print(f"{'='*80}")
        
        try:
            comparator = VersionComparator(file1, file2)
            comparator.print_comparison()
        except Exception as e:
            print(f"❌ Error al comparar: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare benchmark results between versions"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('files', nargs='*', help='Two JSON files to compare')
    group.add_argument('--dir', type=Path, help='Directory with multiple result files')
    
    args = parser.parse_args()
    
    if args.dir:
        compare_directory(args.dir)
    else:
        if len(args.files) != 2:
            print("❌ Error: Se requieren exactamente 2 archivos para comparar")
            print("Uso: python compare_versions.py file1.json file2.json")
            sys.exit(1)
        
        file1 = Path(args.files[0])
        file2 = Path(args.files[1])
        
        if not file1.exists():
            print(f"❌ Error: No existe el archivo {file1}")
            sys.exit(1)
        
        if not file2.exists():
            print(f"❌ Error: No existe el archivo {file2}")
            sys.exit(1)
        
        comparator = VersionComparator(file1, file2)
        comparator.print_comparison()


if __name__ == '__main__':
    main()
