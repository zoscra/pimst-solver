#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version Manager - Herramienta para gestionar versiones del proyecto PIMST

Uso:
    python version_manager.py --show          # Mostrar versión actual
    python version_manager.py --bump patch    # Incrementar versión patch (0.22.0 -> 0.22.1)
    python version_manager.py --bump minor    # Incrementar versión minor (0.22.0 -> 0.23.0)
    python version_manager.py --bump major    # Incrementar versión major (0.22.0 -> 1.0.0)
    python version_manager.py --set 1.0.0     # Establecer versión específica
"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime


class VersionManager:
    """Gestiona versiones en múltiples archivos del proyecto."""
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root
        self.files_to_update = [
            "src/pimst/__init__.py",
            "setup.py",
            "README.md",
        ]
    
    def get_current_version(self) -> str:
        """Obtiene la versión actual del proyecto."""
        init_file = self.project_root / "src/pimst/__init__.py"
        
        if not init_file.exists():
            return "0.0.0"
        
        content = init_file.read_text(encoding='utf-8')
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        
        if match:
            return match.group(1)
        
        return "0.0.0"
    
    def parse_version(self, version: str) -> tuple:
        """Parse version string to tuple (major, minor, patch)."""
        parts = version.split('.')
        return tuple(int(p) for p in parts)
    
    def bump_version(self, bump_type: str) -> str:
        """Incrementa la versión según el tipo."""
        current = self.get_current_version()
        major, minor, patch = self.parse_version(current)
        
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Tipo de bump inválido: {bump_type}")
        
        return f"{major}.{minor}.{patch}"
    
    def update_version_in_file(self, filepath: Path, old_version: str, new_version: str):
        """Actualiza la versión en un archivo específico."""
        if not filepath.exists():
            print(f"⚠️  Archivo no encontrado: {filepath}")
            return
        
        content = filepath.read_text(encoding='utf-8')
        
        # Patrones para diferentes archivos
        patterns = [
            (r'__version__\s*=\s*["\']([^"\']+)["\']', f'__version__ = "{new_version}"'),
            (r'version\s*=\s*["\']([^"\']+)["\']', f'version="{new_version}"'),
            (r'\*\*[0-9]+\.[0-9]+\.[0-9]+\*\*', f'**{new_version}**'),
        ]
        
        updated = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                updated = True
        
        if updated:
            filepath.write_text(content, encoding='utf-8')
            print(f"✅ Actualizado: {filepath}")
        else:
            print(f"⚠️  No se encontró patrón de versión en: {filepath}")
    
    def update_changelog(self, new_version: str):
        """Actualiza CHANGELOG.md con la nueva versión."""
        changelog = self.project_root / "CHANGELOG.md"
        
        if not changelog.exists():
            print("⚠️  CHANGELOG.md no encontrado")
            return
        
        content = changelog.read_text(encoding='utf-8')
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Buscar sección [Unreleased]
        unreleased_section = re.search(
            r'## \[Unreleased\](.*?)(?=## \[|\Z)', 
            content, 
            re.DOTALL
        )
        
        if unreleased_section:
            unreleased_content = unreleased_section.group(1).strip()
            
            # Crear nueva entrada de versión
            new_entry = f"\n## [{new_version}] - {today}\n\n{unreleased_content}\n"
            
            # Insertar después de [Unreleased]
            content = content.replace(
                unreleased_section.group(0),
                f"## [Unreleased]\n\n### Planeado\n- Próximas características\n{new_entry}"
            )
            
            changelog.write_text(content, encoding='utf-8')
            print(f"✅ CHANGELOG.md actualizado con versión {new_version}")
        else:
            print("⚠️  No se encontró sección [Unreleased] en CHANGELOG.md")
    
    def set_version(self, new_version: str):
        """Establece una nueva versión en todos los archivos."""
        old_version = self.get_current_version()
        
        print(f"\n🔄 Actualizando versión: {old_version} → {new_version}")
        print("=" * 60)
        
        # Actualizar archivos
        for filepath in self.files_to_update:
            full_path = self.project_root / filepath
            self.update_version_in_file(full_path, old_version, new_version)
        
        # Actualizar CHANGELOG
        self.update_changelog(new_version)
        
        print("=" * 60)
        print(f"✅ Versión actualizada exitosamente a {new_version}\n")
        print("📝 Próximos pasos:")
        print("   1. Revisar cambios: git diff")
        print("   2. Commitear: git add . && git commit -m 'Bump version to {}'".format(new_version))
        print("   3. Crear tag: git tag v{}".format(new_version))
        print("   4. Push: git push && git push --tags")


def main():
    parser = argparse.ArgumentParser(
        description="Gestionar versiones del proyecto PIMST"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--show', action='store_true', help='Mostrar versión actual')
    group.add_argument('--bump', choices=['major', 'minor', 'patch'], 
                      help='Incrementar versión')
    group.add_argument('--set', metavar='VERSION', help='Establecer versión específica')
    
    args = parser.parse_args()
    
    manager = VersionManager()
    
    if args.show:
        version = manager.get_current_version()
        print(f"Versión actual: {version}")
    
    elif args.bump:
        new_version = manager.bump_version(args.bump)
        manager.set_version(new_version)
    
    elif args.set:
        # Validar formato de versión
        if not re.match(r'^\d+\.\d+\.\d+$', args.set):
            print("❌ Error: La versión debe tener formato X.Y.Z (ej: 1.0.0)")
            sys.exit(1)
        manager.set_version(args.set)


if __name__ == '__main__':
    main()
