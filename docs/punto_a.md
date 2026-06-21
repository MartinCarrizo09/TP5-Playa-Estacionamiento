# TP5 — Punto A: Análisis y definiciones del sistema
## Playa de Estacionamiento (Grupo 13)

> Documento de análisis pedido por el punto A del TP5. Define objetos, eventos,
> colas y variables aleatorias del sistema, consistente con el aplicativo
> (`simulacion.py` + `euler.py`).

---

## 1. Identificación de objetos

### 1.1 Playa de estacionamiento (servidor de N lugares)
| Atributo | Valores posibles |
|---|---|
| Estado | `CLD` (con lugar disponible), `LL` (llena) |
| Capacidad (N) | parámetro (default 8; pregunta b: 10) |
| Lugares ocupados | 0 … N |

Cada **lugar** (1..N) es un sub-objeto:
| Atributo | Valores posibles |
|---|---|
| Estado | `Libre`, `OC` (ocupado) |
| Auto asignado | id de auto / — |
| Fin de estacionamiento | hora (h) / — |

### 1.2 Zona de cobro (servidor, capacidad 1)
| Atributo | Valores posibles |
|---|---|
| Estado | `Libre`, `Ocupado` |
| Auto en cobro | id de auto / — |

### 1.3 Auto (entidad temporal)
| Atributo | Valores posibles |
|---|---|
| **Estado** | `Estacionado`, `EsperandoCobro`, `EnCobro`, `Pagó` (o sigue de largo si la playa está llena) |
| **Tipo** | `Pequeño`, `Grande`, `Utilitario` |
| **Importe a pagar** | horas × precio según tipo |

> El auto guarda **solo** estado, tipo e importe. Las **horas** se usan al llegar
> para calcular el importe y programar el fin de estacionamiento, y no se guardan.
> El vínculo auto–lugar se modela en el objeto **Lugar** (`lugar → id de auto`),
> que usa menos columnas.
>
> El **tipo** se guarda porque la condición de corte de la integración del cobro
> (`D = 180` grande / `130` resto) se necesita al **finalizar el estacionamiento**,
> no solo al llegar.

### 1.4 Variables auxiliares (acumuladores / contadores)
- `reloj` (hora simulada, en horas)
- `recaudacion` (acumulador $)
- `acum_ocupacion` (∫ lugares_ocupados · dt → para el % de utilización)
- `contador_llegaron`, `contador_abandonos`
- longitud de la cola de cobro

---

## 2. Determinación de eventos

| Evento | Qué hace |
|---|---|
| **Llegada de auto** | Si hay lugar libre, ocupa y programa su fin de estacionamiento; si la playa está llena, sigue de largo (abandona, no vuelve). Programa la próxima llegada. |
| **Fin de estacionamiento** | El auto debe pagar. Si la zona de cobro está libre, libera su lugar y entra a cobrar (se integra el tiempo de cobro). Si está ocupada, espera en la cola de cobro ocupando su lugar. |
| **Fin de cobro** | El auto paga (suma a la recaudación) y abandona la playa. Libera la zona de cobro y entra el primero de la cola de cobro. |

---

## 3. Colas del sistema

| Cola | Características |
|---|---|
| **Cola de cobro** | FIFO. Autos que terminaron de estacionar y esperan la zona de cobro (capacidad 1). Al terminar de estacionar **liberan su lugar**, así que mientras esperan el cobro **ya no ocupan sector**. Sin tope explícito. |
| **Entrada (no hay cola)** | Si la playa está llena, el auto **sigue de largo y no vuelve** (no hay espera para entrar). |

---

## 4. Variables aleatorias y fórmulas de generación

| Variable | Distribución | Fórmula de generación |
|---|---|---|
| **Tiempo entre llegadas** | Exponencial negativa, media 13 min | `t = −media · ln(1 − RND)`, con `media = 13/60` h |
| **Tipo de auto** | Discreta (45/25/30 %, **parametrizable**) | `RND < 0.45` → Pequeño · `< 0.70` → Grande · `< 1` → Utilitario |
| **Horas de estacionamiento** | Discreta (50/30/15/5 %, **parametrizable**) | `RND < 0.50` → 1h · `< 0.80` → 2h · `< 0.95` → 3h · `< 1` → 4h |
| **Tiempo de cobro** | Parte continua (sin fórmula cerrada) | **Integración numérica (Euler)** de `dD/dt = C + 0.2·T + t²` hasta `D = umbral` (180 Grande / 130 resto). `C` = autos en la cola de cobro al iniciar el cobro (sin contar al que entra); `T`, `h` parámetros. |

> El valor de la variable por integración numérica (tiempo de cobro) se muestra en
> el vector de estado, y la tabla de la integración (columnas `t`, `D`, `dD/dt`) en
> la pestaña **Auditoría Euler** del aplicativo.

---

## 5. Preguntas a responder con la simulación

- **a) Recaudación** = Σ (horas × precio) de los autos que pagaron. Precios: Pequeño $500/h, Grande $1500/h, Utilitario $3000/h.
- **b) Recaudación con 10 lugares** = misma simulación con `N = 10` (lugares parametrizable).
- **c) % de utilización** = `acum_ocupacion / (N × tiempo_simulado) × 100` (solo sectores de estacionamiento).
