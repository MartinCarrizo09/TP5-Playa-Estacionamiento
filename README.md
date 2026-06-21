# TP5 — Simulación: Playa de Estacionamiento (Grupo 13)

Simulación de **eventos discretos (DES)** de una playa de estacionamiento, con interfaz
gráfica en **PyQt5**. Trabajo Práctico 5 de Laboratorio de Simulación (4K3).

## Sistema simulado
- **N sectores** de estacionamiento (8 por defecto; parametrizable).
- Autos que llegan (exponencial, media 13′), estacionan 1–4 h y **pagan** en una zona de
  cobro (capacidad 1) antes de irse.
- **Tiempo de cobro** calculado por **integración numérica (Euler)** de
  `dD/dt = C + 0.2·T + t²` hasta el umbral (180 grande / 130 resto).
- Responde: **a)** recaudación, **b)** recaudación con 10 lugares, **c)** % de utilización.

## Archivos
| Archivo | Rol |
|---|---|
| `simulacion.py` | Motor DES (eventos, lógica, estadísticas). Sin UI. |
| `euler.py` | Integración numérica del tiempo de cobro. |
| `main.py` | Interfaz gráfica PyQt5 (vector de estado, auditoría Euler, filtros, copiar a Excel). |
| `test_completo.py` | Suite de pruebas del motor y la interfaz. |
| `docs/` | Punto A (md + pdf), documentación técnica (pdf) y generadores. |
| `casos_de_prueba.xlsx` | Plan de pruebas manual. |

## Cómo correr
```bash
pip install PyQt5
python main.py
```

## Tests
```bash
python test_completo.py
```
