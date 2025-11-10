#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Encoding Script - Corrige problemas de encoding en Windows

Este script corrige automáticamente todos los archivos Python que tengan
problemas con encoding UTF-8 en Windows.

Uso:
    python fix_encoding_windows.py
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def fix_open_statements(content: str) -> Tuple[str, int]:
    """
    Corrige statements open() sin encoding='utf-8'.
    
    Returns:
        Tuple de (contenido_corregido, número_de_cambios)
    """
    changes = 0
    
    # Patrón 1: open(..., 'w') sin encoding
    pattern1 = r"open\(([^,)]+),\s*['\"]w['\"](?!\s*,\s*encoding)"
    replacement1 = r"open(\1, 'w', encoding='utf-8'"
    content, count1 = re.subn(pattern1, replacement1, content)
    changes += count1
    
    # Patrón 2: open(..., 'r') sin encoding (opcional pero recomendado)
    pattern2 = r"open\(([^,)]+),\s*['\"]r['\"](?!\s*,\s*encoding)"
    replacement2 = r"open(\1, 'r', encoding='utf-8'"
    content, count2 = re.subn(pattern2, replacement2, content)
    changes += count2
    
    # Patrón 3: open(...) sin modo ni encoding
    pattern3 = r"open\(([^,)]+)\)(?!\s*,)"
    replacement3 = r"open(\1, encoding='utf-8')"
    content, count3 = re.subn(pattern3, replacement3, content)
    changes += count3
    
    return content, changes


def fix_pathlib_methods(content: str) -> Tuple[str, int]:
    """
    Corrige métodos de pathlib sin encoding='utf-8'.
    
    Returns:
        Tuple de (contenido_corregido, número_de_cambios)
    """
    changes = 0
    
    # Patrón 1: .read_text() sin encoding
    pattern1 = r"\.read_text\(\)(?!\s*,\s*encoding)"
    replacement1 = r".read_text(encoding='utf-8')"
    content, count1 = re.subn(pattern1, replacement1, content)
    changes += count1
    
    # Patrón 2: .write_text(content) sin encoding
    # Más complejo porque puede tener contenido entre paréntesis
    pattern2 = r"\.write_text\(([^)]+)\)(?!\s*,\s*encoding)"
    
    def add_encoding(match):
        arg = match.group(1)
        # Verificar que no tenga ya encoding
        if 'encoding' not in arg:
            return f".write_text({arg}, encoding='utf-8')"
        return match.group(0)
    
    content, count2 = re.subn(pattern2, add_encoding, content)
    changes += count2
    
    return content, changes


def add_utf8_header(content: str) -> Tuple[str, bool]:
    """
    Añade header UTF-8 si no existe.
    
    Returns:
        Tuple de (contenido_con_header, si_se_añadió)
    """
    # Verificar si ya tiene header UTF-8
    if '# -*- coding: utf-8 -*-' in content[:100]:
        return content, False
    
    # Si tiene shebang, insertar después
    lines = content.split('\n')
    if lines[0].startswith('#!'):
        lines.insert(1, '# -*- coding: utf-8 -*-')
    else:
        lines.insert(0, '# -*- coding: utf-8 -*-')
    
    return '\n'.join(lines), True


def fix_file(filepath: Path, add_header: bool = True) -> Tuple[bool, int]:
    """
    Corrige un archivo Python.
    
    Args:
        filepath: Ruta al archivo
        add_header: Si añadir header UTF-8
        
    Returns:
        Tuple de (éxito, número_de_cambios)
    """
    try:
        # Leer contenido con UTF-8
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        total_changes = 0
        
        # Aplicar correcciones
        content, changes1 = fix_open_statements(content)
        total_changes += changes1
        
        content, changes2 = fix_pathlib_methods(content)
        total_changes += changes2
        
        if add_header:
            content, added = add_utf8_header(content)
            if added:
                total_changes += 1
        
        # Solo escribir si hubo cambios
        if content != original_content:
            filepath.write_text(content, encoding='utf-8')
            return True, total_changes
        
        return True, 0
        
    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False, 0


def main():
    """Función principal."""
    print("=" * 70)
    print("🔧 FIX DE ENCODING UTF-8 PARA WINDOWS")
    print("=" * 70)
    print()
    
    # Archivos a corregir
    files_to_fix = [
        'benchmark_comparison.py',
        'benchmark_large_scale.py',
        'version_manager.py',
        'compare_with_market.py',
        'compare_versions.py',
        'performance_tracker.py',
    ]
    
    print(f"📝 Archivos a revisar: {len(files_to_fix)}")
    print()
    
    fixed_count = 0
    total_changes = 0
    not_found = []
    
    for filename in files_to_fix:
        filepath = Path(filename)
        
        if not filepath.exists():
            not_found.append(filename)
            print(f"⚠️  {filename:<35} - No encontrado")
            continue
        
        success, changes = fix_file(filepath)
        
        if success:
            if changes > 0:
                print(f"✅ {filename:<35} - {changes} cambios aplicados")
                fixed_count += 1
                total_changes += changes
            else:
                print(f"✓  {filename:<35} - Ya estaba correcto")
        else:
            print(f"❌ {filename:<35} - Error al procesar")
    
    print()
    print("=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print(f"✅ Archivos corregidos:     {fixed_count}")
    print(f"📝 Total de cambios:        {total_changes}")
    print(f"⚠️  Archivos no encontrados: {len(not_found)}")
    
    if not_found:
        print(f"\nArchivos no encontrados:")
        for f in not_found:
            print(f"  - {f}")
    
    print()
    
    if fixed_count > 0:
        print("✅ CORRECCIONES APLICADAS EXITOSAMENTE")
        print()
        print("📋 Próximos pasos:")
        print("   1. Verificar que no haya errores de sintaxis:")
        print("      python -m py_compile benchmark_comparison.py")
        print()
        print("   2. Ejecutar benchmark nuevamente:")
        print("      python benchmark_comparison.py")
        print()
        print("   3. Si funciona correctamente, commit los cambios:")
        print("      git add .")
        print("      git commit -m 'fix: Corregir encoding UTF-8 para Windows'")
        print()
    else:
        print("ℹ️  No se necesitaron correcciones")
    
    print("=" * 70)


if __name__ == '__main__':
    main()
