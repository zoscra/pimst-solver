# Changelog

Todas las modificaciones notables de este proyecto serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.22.0] - 2025-11-05

### Añadido
- Sistema completo de benchmarking contra OR-Tools
- Benchmarks de gran escala (N=500-1000)
- Scripts de comparación automatizados
- Resultados validados: 6.67% gap promedio, 52,789x más rápido

### Mejorado
- Algoritmo gravity-guided con mejor normalización de masas
- Multi-start solver optimizado para instancias grandes
- Documentación completa en README

### Corregido
- Bug en cálculo de masas gravitacionales para grafos dispersos
- Mejora en estimación de complejidad temporal

## [0.21.0] - 2025-10-28

### Añadido
- Implementación de Lin-Kernighan Lite
- Multi-start strategy con 3/5/10 inicializaciones
- Sistema de selección adaptativa de algoritmos

### Mejorado
- Rendimiento en instancias N>100
- Uso de Numba JIT para acelerar cálculos

## [0.20.0] - 2025-10-20

### Añadido
- Primera versión pública
- Algoritmo gravity-guided innovador
- Nearest Neighbor clásico
- Tests básicos con pytest

### Características iniciales
- Soporte para coordenadas 2D
- API simple: `pimst.solve(coords)`
- Tres niveles de calidad: fast, balanced, optimal

## [Unreleased]

### Planeado
- Paralelización de multi-start
- Soporte para GPU (CUDA)
- Extensión a VRP (Vehicle Routing Problem)
- Integración con sistemas de mapas (Google Maps, OpenStreetMap)
- API REST para uso en producción
- Dashboard web interactivo

---

## Tipos de cambios
- **Añadido**: Para nuevas características
- **Mejorado**: Para mejoras en funcionalidades existentes
- **Obsoleto**: Para características que serán eliminadas
- **Eliminado**: Para características eliminadas
- **Corregido**: Para corrección de bugs
- **Seguridad**: Para vulnerabilidades de seguridad
