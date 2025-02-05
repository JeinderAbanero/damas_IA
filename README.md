# 🎮 Damas con Q-Learning

Un juego de damas implementado en Python que utiliza Q-Learning para crear un agente de IA que aprende y mejora con cada partida.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-yellow.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 🌟 Características

- **Aprendizaje por Refuerzo**: Implementación de Q-Learning para el aprendizaje autónomo
- **Interfaz Gráfica**: Visualización del juego usando Pygame
- **Modos de Juego**: 
  - Entrenamiento IA vs IA
  - Jugador vs IA entrenada
- **Estadísticas en Tiempo Real**: Seguimiento del rendimiento del agente
- **Sistema de Recompensas Optimizado**: Incentiva jugadas agresivas y decisivas

## 🎯 Rendimiento del Agente

Con la configuración actual, el agente logra:
- **Tasa de Victoria**: ~60%
- **Tasa de Empate**: ~5%
- **Movimientos Promedio por Partida**: ~24

## 🛠️ Configuración

### Requisitos
```bash
python >= 3.8
pygame >= 2.0.0
numpy >= 1.19.0
```

### Instalación

1. Clona el repositorio:
```bash
git clone git@github.com:JeinderAbanero/damas_IA.git
cd damas_IA
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 🎮 Uso

### Entrenar el Agente
```bash
python damas.py
```
Selecciona "Sí" cuando se te pregunte por el entrenamiento.

### Jugar contra la IA
```bash
python damas.py
```
Selecciona "No" para usar un agente previamente entrenado.

## 🧠 Parámetros de Q-Learning

El agente puede configurarse con diferentes parámetros para ajustar su comportamiento:

### Configuración Actual (Conservadora)
```python
alpha = 0.1    # Tasa de aprendizaje
gamma = 0.9    # Factor de descuento
epsilon = 0.2  # Tasa de exploración
```

### Configuraciones Alternativas

#### Agresiva
```python
alpha = 0.3    # Aprendizaje más rápido
gamma = 0.99   # Mayor énfasis en recompensas futuras
epsilon = 0.4  # Alta exploración
```

#### Equilibrada
```python
alpha = 0.2    # Balance aprendizaje-estabilidad
gamma = 0.95   # Balance recompensas inmediatas-futuras
epsilon = 0.25 # Exploración moderada
```

## 📊 Sistema de Recompensas

El agente recibe recompensas por:
- **Victoria**: +200 puntos
- **Captura de Pieza**: +50 puntos
- **Coronación**: +20 puntos
- **Control del Centro**: +15 puntos
- **Capturas Consecutivas**: +30 puntos adicionales

Y penalizaciones por:
- **Derrota**: -200 puntos
- **Inactividad**: -10 puntos por turno
- **Tendencia al Empate**: -15 puntos por turno

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para cambios importantes:

1. Haz fork del repositorio
2. Crea una nueva rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -am 'Añade nueva mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request



## 👤 Autor

**Jeinder Abanero**
- GitHub: [@JeinderAbanero](https://github.com/JeinderAbanero)

