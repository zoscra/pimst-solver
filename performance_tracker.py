#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Tracker - Track PIMST performance over time

This script maintains a database of benchmark results and generates
visualizations of performance trends.

Usage:
    python performance_tracker.py --add benchmark_results.json
    python performance_tracker.py --plot
    python performance_tracker.py --report
    python performance_tracker.py --compare v0.21.0 v0.22.0
"""

import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import subprocess


class PerformanceTracker:
    """Track and analyze PIMST performance over time."""
    
    def __init__(self, db_path: Path = Path("performance_history.db")):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS benchmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                version TEXT,
                commit_hash TEXT,
                branch TEXT,
                notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                benchmark_id INTEGER,
                instance_name TEXT,
                instance_size INTEGER,
                solver TEXT,
                tour_length REAL,
                execution_time REAL,
                algorithm TEXT,
                FOREIGN KEY (benchmark_id) REFERENCES benchmarks(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_git_info(self) -> Dict[str, str]:
        """Get current git information."""
        try:
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], 
                                            stderr=subprocess.DEVNULL).decode().strip()
            branch = subprocess.check_output(['git', 'branch', '--show-current'],
                                            stderr=subprocess.DEVNULL).decode().strip()
            
            # Get version from Python
            try:
                import pimst
                version = pimst.__version__
            except:
                version = "unknown"
            
            return {
                'version': version,
                'commit_hash': commit,
                'branch': branch
            }
        except:
            return {
                'version': 'unknown',
                'commit_hash': 'unknown',
                'branch': 'unknown'
            }
    
    def add_benchmark(self, results_file: Path, notes: Optional[str] = None):
        """Add benchmark results to database."""
        # Load results
        with open(results_file, encoding='utf-8') as f:
            results = json.load(f)
        
        # Get git info
        git_info = self.get_git_info()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert benchmark record
        cursor.execute("""
            INSERT INTO benchmarks (version, commit_hash, branch, notes)
            VALUES (?, ?, ?, ?)
        """, (git_info['version'], git_info['commit_hash'], 
              git_info['branch'], notes or ''))
        
        benchmark_id = cursor.lastrowid
        
        # Insert all results
        for instance_name, instance_data in results.items():
            n = instance_data['n']
            
            for solver_name, solver_data in instance_data['solvers'].items():
                cursor.execute("""
                    INSERT INTO results 
                    (benchmark_id, instance_name, instance_size, solver, 
                     tour_length, execution_time, algorithm)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (benchmark_id, instance_name, n, solver_name,
                      solver_data['length'], solver_data['time'],
                      solver_data.get('algorithm', 'unknown')))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Benchmark añadido al historial")
        print(f"   ID: {benchmark_id}")
        print(f"   Versión: {git_info['version']}")
        print(f"   Commit: {git_info['commit_hash'][:8]}")
        print(f"   Instancias: {len(results)}")
    
    def list_benchmarks(self):
        """List all benchmarks in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, version, commit_hash, branch, notes
            FROM benchmarks
            ORDER BY timestamp DESC
        """)
        
        benchmarks = cursor.fetchall()
        conn.close()
        
        if not benchmarks:
            print("📊 No hay benchmarks en el historial")
            return
        
        print("\n" + "=" * 80)
        print("📊 HISTORIAL DE BENCHMARKS")
        print("=" * 80)
        print(f"\n{'ID':<5} {'Fecha':<20} {'Versión':<12} {'Commit':<10} {'Rama':<15}")
        print("-" * 80)
        
        for bm in benchmarks:
            id, timestamp, version, commit, branch, notes = bm
            commit_short = commit[:8] if commit else 'N/A'
            print(f"{id:<5} {timestamp:<20} {version:<12} {commit_short:<10} {branch:<15}")
            if notes:
                print(f"      Notas: {notes}")
        
        print()
    
    def generate_report(self):
        """Generate performance report."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("\n" + "=" * 80)
        print("📈 REPORTE DE RENDIMIENTO")
        print("=" * 80)
        
        # Get latest benchmark
        cursor.execute("""
            SELECT id, timestamp, version, commit_hash
            FROM benchmarks
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        latest = cursor.fetchone()
        if not latest:
            print("\n❌ No hay datos disponibles")
            conn.close()
            return
        
        latest_id, timestamp, version, commit = latest
        
        print(f"\n📊 Última medición:")
        print(f"   Fecha: {timestamp}")
        print(f"   Versión: {version}")
        print(f"   Commit: {commit[:8]}")
        
        # Get statistics for latest benchmark
        cursor.execute("""
            SELECT 
                solver,
                COUNT(*) as instances,
                AVG(tour_length) as avg_length,
                AVG(execution_time) as avg_time,
                MIN(execution_time) as min_time,
                MAX(execution_time) as max_time
            FROM results
            WHERE benchmark_id = ?
            GROUP BY solver
        """, (latest_id,))
        
        stats = cursor.fetchall()
        
        print(f"\n📊 Estadísticas por solver:")
        print(f"\n{'Solver':<20} {'Instancias':<12} {'Tiempo Prom.':<15} {'Min':<10} {'Max':<10}")
        print("-" * 80)
        
        for stat in stats:
            solver, instances, avg_length, avg_time, min_time, max_time = stat
            time_str = f"{avg_time*1000:.1f}ms" if avg_time < 1 else f"{avg_time:.2f}s"
            min_str = f"{min_time*1000:.1f}ms" if min_time < 1 else f"{min_time:.2f}s"
            max_str = f"{max_time*1000:.1f}ms" if max_time < 1 else f"{max_time:.2f}s"
            print(f"{solver:<20} {instances:<12} {time_str:<15} {min_str:<10} {max_str:<10}")
        
        # Compare with previous benchmark if exists
        cursor.execute("""
            SELECT id, version
            FROM benchmarks
            WHERE id < ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (latest_id,))
        
        previous = cursor.fetchone()
        
        if previous:
            prev_id, prev_version = previous
            
            print(f"\n📊 Comparación con versión anterior ({prev_version}):")
            
            # Compare PIMST balanced
            cursor.execute("""
                SELECT 
                    r1.instance_name,
                    r1.tour_length as length1,
                    r2.tour_length as length2,
                    r1.execution_time as time1,
                    r2.execution_time as time2
                FROM results r1
                JOIN results r2 ON r1.instance_name = r2.instance_name
                WHERE r1.benchmark_id = ?
                  AND r2.benchmark_id = ?
                  AND r1.solver = 'pimst_balanced'
                  AND r2.solver = 'pimst_balanced'
            """, (latest_id, prev_id))
            
            comparisons = cursor.fetchall()
            
            if comparisons:
                import numpy as np
                
                quality_changes = []
                time_changes = []
                
                for comp in comparisons:
                    name, l1, l2, t1, t2 = comp
                    quality_change = ((l2 - l1) / l1) * 100
                    time_change = ((t2 - t1) / t1) * 100
                    quality_changes.append(quality_change)
                    time_changes.append(time_change)
                
                avg_quality = np.mean(quality_changes)
                avg_time = np.mean(time_changes)
                
                print(f"\n   Cambio en calidad:  {avg_quality:+.2f}%")
                print(f"   Cambio en tiempo:   {avg_time:+.1f}%")
                
                if avg_quality < -1:
                    print("   ✅ Mejora en calidad")
                elif avg_quality > 1:
                    print("   ⚠️  Regresión en calidad")
                else:
                    print("   ➡️  Calidad similar")
        
        conn.close()
    
    def plot_performance(self):
        """Generate performance plots."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("❌ matplotlib no está instalado")
            print("   Instalar con: pip install matplotlib")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all benchmarks with PIMST balanced results
        cursor.execute("""
            SELECT 
                b.id,
                b.timestamp,
                b.version,
                AVG(r.tour_length) as avg_length,
                AVG(r.execution_time) as avg_time
            FROM benchmarks b
            JOIN results r ON b.id = r.benchmark_id
            WHERE r.solver = 'pimst_balanced'
            GROUP BY b.id
            ORDER BY b.timestamp
        """)
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            print("❌ No hay suficientes datos para graficar")
            return
        
        ids = [d[0] for d in data]
        timestamps = [d[1] for d in data]
        versions = [d[2] for d in data]
        avg_lengths = [d[3] for d in data]
        avg_times = [d[4] for d in data]
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot execution time
        ax1.plot(range(len(timestamps)), [t*1000 for t in avg_times], 
                'b-o', linewidth=2, markersize=8)
        ax1.set_ylabel('Tiempo Promedio (ms)', fontsize=12)
        ax1.set_title('Evolución del Rendimiento de PIMST', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(len(timestamps)))
        ax1.set_xticklabels(versions, rotation=45, ha='right')
        
        # Plot tour length (quality)
        ax2.plot(range(len(timestamps)), avg_lengths, 
                'r-s', linewidth=2, markersize=8)
        ax2.set_ylabel('Longitud Promedio de Tour', fontsize=12)
        ax2.set_xlabel('Versión', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(len(timestamps)))
        ax2.set_xticklabels(versions, rotation=45, ha='right')
        
        plt.tight_layout()
        
        output_file = 'performance_history.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico guardado: {output_file}")
        
        # Also create a detailed plot for each instance size
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT instance_size
            FROM results
            WHERE solver = 'pimst_balanced'
            ORDER BY instance_size
        """)
        
        sizes = [s[0] for s in cursor.fetchall()]
        
        fig, axes = plt.subplots(len(sizes), 1, figsize=(12, 4*len(sizes)))
        if len(sizes) == 1:
            axes = [axes]
        
        for idx, size in enumerate(sizes):
            cursor.execute("""
                SELECT 
                    b.version,
                    AVG(r.execution_time) as avg_time
                FROM benchmarks b
                JOIN results r ON b.id = r.benchmark_id
                WHERE r.solver = 'pimst_balanced'
                  AND r.instance_size = ?
                GROUP BY b.id
                ORDER BY b.timestamp
            """, (size,))
            
            data = cursor.fetchall()
            versions_size = [d[0] for d in data]
            times_size = [d[1] for d in data]
            
            axes[idx].plot(range(len(versions_size)), [t*1000 for t in times_size],
                          'g-o', linewidth=2, markersize=8)
            axes[idx].set_ylabel('Tiempo (ms)', fontsize=10)
            axes[idx].set_title(f'N={size}', fontsize=12, fontweight='bold')
            axes[idx].grid(True, alpha=0.3)
            axes[idx].set_xticks(range(len(versions_size)))
            axes[idx].set_xticklabels(versions_size, rotation=45, ha='right')
        
        plt.tight_layout()
        output_file = 'performance_by_size.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico por tamaño guardado: {output_file}")
        
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Track PIMST performance over time"
    )
    
    parser.add_argument('--add', type=Path, 
                       help='Add benchmark results to history')
    parser.add_argument('--notes', type=str,
                       help='Notes about this benchmark')
    parser.add_argument('--list', action='store_true',
                       help='List all benchmarks in history')
    parser.add_argument('--report', action='store_true',
                       help='Generate performance report')
    parser.add_argument('--plot', action='store_true',
                       help='Generate performance plots')
    
    args = parser.parse_args()
    
    tracker = PerformanceTracker()
    
    if args.add:
        if not args.add.exists():
            print(f"❌ Error: Archivo no encontrado: {args.add}")
            return
        tracker.add_benchmark(args.add, args.notes)
    
    elif args.list:
        tracker.list_benchmarks()
    
    elif args.report:
        tracker.generate_report()
    
    elif args.plot:
        tracker.plot_performance()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
