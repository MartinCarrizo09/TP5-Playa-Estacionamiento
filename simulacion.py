"""
TP5 — Simulación Playa de Estacionamiento (Grupo 13)

Paso 1: llegadas de autos, ocupación de los 8 lugares y fin de estacionamiento;
"""
import heapq
import math
import random

import euler

# ── Constantes / parámetros (los "valores en rojo" del enunciado) ──────────────
N_LUGARES       = 8            
MEDIA_LLEGADA   = 13 / 60       
MAX_ITER        = 99999          

# Cobro (parte continua, integrada por Euler en euler.py)
T_EULER         = 2              
H_EULER         = 0.1            

# Precios por hora según tipo de auto
PRECIO = {"Pequeño": 500, "Grande": 1500, "Utilitario": 3000}

# Probabilidades (parametrizables): tipo de auto y horas de estacionamiento
PROB_TIPO  = {"Pequeño": 0.45, "Grande": 0.25, "Utilitario": 0.30}
PROB_HORAS = {1: 0.50, 2: 0.30, 3: 0.15, 4: 0.05}

# ── RND sembrados TRUE = Mismos RND excel, FALSE = RND aleatorios ───────────────────
USAR_SEMILLA = False
RND_LLEGADA = [0.25, 0.34, 0.45, 0.75, 0.18, 0.8, 0.91, 0.15, 0.42, 0.88, 0.94, 0.98]
RND_TIPO    = [0.55, 0.21, 0.78, 0.78, 0.65, 0.56, 0.21, 0.44, 0.9, 0.59]
RND_HORAS   = [0.88, 0.65, 0.65, 0.05, 0.52, 0.81, 0.61, 0.15, 0.96, 0.42]

# ── Estado global ──────────────────────────────────────────────────────────────
lugares       = []
autos         = {}
zona_cobro    = {}               
cola_cobro    = []               
eventos       = []
reloj         = 0.0
iteracion     = 0
id_auto       = 0
_seq          = 0
_i_lleg = _i_tipo = _i_horas = 0
recaudacion   = 0.0
acum_ocupacion = 0.0             
contador_llegaron  = 0           
contador_abandonos = 0           
tablas_euler  = []               
vector_estado = []


# ── Validación de parámetros ────────────────────────────────────────────────────
def validar_parametros():
    """Revisa que los parámetros globales sean coherentes ANTES de simular.

    Lanza ValueError con un mensaje claro si algo no cierra. Así el motor falla
    rápido y explícito en vez de colgarse o devolver números sin sentido.
    """
    errores = []

    if not isinstance(N_LUGARES, int) or N_LUGARES < 1:
        errores.append(f"La cantidad de lugares debe ser un entero >= 1 (recibido: {N_LUGARES}).")
    if not MEDIA_LLEGADA > 0:
        errores.append("La media de llegadas debe ser > 0 (con 0 los autos llegarían "
                       "todos en el mismo instante y la simulación no avanzaría).")
    if not H_EULER > 0:
        errores.append(f"El paso h de Euler debe ser > 0 (recibido: {H_EULER}).")

    for tipo, p in PROB_TIPO.items():
        if p < 0:
            errores.append(f"La probabilidad de tipo {tipo!r} no puede ser negativa ({p}).")
    for h, p in PROB_HORAS.items():
        if p < 0:
            errores.append(f"La probabilidad de {h} hora(s) no puede ser negativa ({p}).")

    suma_tipo = sum(PROB_TIPO.values())
    if suma_tipo <= 0:
        errores.append("Las probabilidades de tipo de auto suman 0: ningún auto podría entrar.")
    elif abs(suma_tipo - 1.0) > 0.01:
        errores.append(f"Las probabilidades de tipo de auto deberían sumar 100% (suman {suma_tipo*100:.0f}%).")

    suma_horas = sum(PROB_HORAS.values())
    if suma_horas <= 0:
        errores.append("Las probabilidades de horas suman 0: ningún auto tendría duración.")
    elif abs(suma_horas - 1.0) > 0.01:
        errores.append(f"Las probabilidades de horas deberían sumar 100% (suman {suma_horas*100:.0f}%).")

    for tipo, precio in PRECIO.items():
        if precio < 0:
            errores.append(f"El precio de {tipo!r} no puede ser negativo ({precio}).")

    if errores:
        raise ValueError("Parámetros inválidos:\n- " + "\n- ".join(errores))


# ── Variables aleatorias ───────────────────────────────────────────────────────
def _take(seed_list, idx):
    """Devuelve (rnd, nuevo_idx). Usa la semilla si queda; si no, RND aleatorio."""
    if USAR_SEMILLA and idx < len(seed_list):
        return seed_list[idx], idx + 1
    # RND aleatorio truncado a 2 dec → queda en [0.00, 0.99], nunca 1.0 (evita log(0))
    return int(random.random() * 100) / 100, idx + 1


def gen_llegada():
    global _i_lleg
    rnd, _i_lleg = _take(RND_LLEGADA, _i_lleg)
    rnd = min(max(rnd, 0.0), 0.999999)       # blindaje: rnd en [0, 1) para que log(1-rnd) sea finito
    t = -MEDIA_LLEGADA * math.log(1 - rnd)   # exponencial negativa (en horas)
    return rnd, t


def gen_tipo():
    global _i_tipo
    rnd, _i_tipo = _take(RND_TIPO, _i_tipo)
    ac = 0.0
    for tipo in ("Pequeño", "Grande", "Utilitario"):
        ac += PROB_TIPO[tipo]
        if rnd < ac:
            return rnd, tipo
    return rnd, "Utilitario"


def gen_horas():
    global _i_horas
    rnd, _i_horas = _take(RND_HORAS, _i_horas)
    ac = 0.0
    for h in (1, 2, 3, 4):
        ac += PROB_HORAS[h]
        if rnd < ac:
            return rnd, h
    return rnd, 4


# ── Cola de eventos (heap) ──────────────────────────────────────────────────────
def push_evento(tiempo, tipo, eid=None):
    global _seq
    heapq.heappush(eventos, (tiempo, _seq, tipo, eid))
    _seq += 1


def siguiente_evento():
    return heapq.heappop(eventos)


def tiempo_de(tipo):
    ts = [e[0] for e in eventos if e[2] == tipo] ##ts es el tiempo del evento que se busca, si no hay eventos de ese tipo devuelve None
    return min(ts) if ts else None


# ── Helpers de lugares ──────────────────────────────────────────────────────────
def lugar_libre():
    for lg in lugares:
        if lg["estado"] == "Libre":
            return lg
    return None


def ocupados():
    return sum(1 for lg in lugares if lg["estado"] == "OC")


# ── Fila del vector de estado ───────────────────────────────────────────────────
def snapshot_autos():
    """Estado de cada auto presente en el sistema: id → (estado, tipo, importe)."""
    return {a["id"]: (a["estado"], a["tipo"], a["importe"]) for a in autos.values()}


def guardar_fila(evento_nombre, d):
    vector_estado.append({
        "num":   len(vector_estado),
        "reloj": reloj,
        "evento": evento_nombre,
        # llegada
        "rnd_lleg": d.get("rnd_lleg"), "t_entre": d.get("t_entre"),
        "prox_lleg": tiempo_de("llegada_auto"),
        # datos del auto que llega
        "rnd_tipo": d.get("rnd_tipo"), "tipo": d.get("tipo"),
        "rnd_horas": d.get("rnd_horas"), "horas": d.get("horas"),
        "importe": d.get("importe"),
        # fin de estacionamiento por lugar (1..N)
        "fin_estac": [lg["fin_estac"] for lg in lugares],
        # cobro
        "cobro_C":   d.get("cobro_C"),
        "t_cobro":   d.get("t_cobro"),
        "cobro_auto": d.get("cobro_auto"),   # auto que inició cobro en esta fila (para saltar a Euler)
        "prox_cobro": tiempo_de("fin_cobro"),
        # servidor playa
        "playa_est": "LL" if ocupados() >= N_LUGARES else "CLD",
        "ocupados": ocupados(),
        # servidor cobro
        "cobro_est": zona_cobro["estado"],
        "cola":      len(cola_cobro),
        # lugares
        "lug_est": [lg["estado"] for lg in lugares],
        "lug_auto": [lg["auto"] for lg in lugares],
        # estadísticas
        "recaudacion": recaudacion,
        "llegaron":   contador_llegaron,
        "abandonos":  contador_abandonos,
        "acum_ocup":  acum_ocupacion,
        # objetos temporales: snapshot de los autos presentes
        "autos": snapshot_autos(),
    })


# ── Procesadores de eventos ─────────────────────────────────────────────────────
def procesar_llegada_auto():
    global id_auto, contador_llegaron, contador_abandonos
    id_auto += 1
    d = {}

    # Programar la próxima llegada (siempre)
    rnd_e, t_e = gen_llegada()
    push_evento(reloj + t_e, "llegada_auto")
    d.update(rnd_lleg=rnd_e, t_entre=t_e)

    aid = id_auto
    contador_llegaron += 1
    abandona = False

    lg = lugar_libre()
    if lg:
        rnd_t, tipo = gen_tipo()
        rnd_h, horas = gen_horas()
        importe = horas * PRECIO[tipo]
        fin = reloj + horas

        lg["estado"]    = "OC"
        lg["auto"]      = aid
        lg["fin_estac"] = fin

        # el auto guarda solo estado, tipo e importe; el vínculo con el lugar
        # vive en el objeto Lugar (lg["auto"]). 'horas' se usa local y se descarta.
        autos[aid] = {"id": aid, "tipo": tipo, "importe": importe, "estado": "Estacionado"}

        push_evento(fin, "fin_estacionamiento", lg["id"])
        d.update(rnd_tipo=rnd_t, tipo=tipo, rnd_horas=rnd_h, horas=horas, importe=importe)
    else:
        # Playa llena → el auto se va. No se le genera tipo/horas (no hay stats por tipo),
        # pero igual se registra como objeto temporal en estado "FueraDeSistema".
        contador_abandonos += 1
        abandona = True
        autos[aid] = {"id": aid, "tipo": None, "importe": None, "estado": "FueraDeSistema"}

    nombre = f"llegada_auto_a{aid}" + (" (abandona)" if abandona else "")
    guardar_fila(nombre, d)
    if abandona:
        del autos[aid]   # se destruye tras registrar la fila (su columna muestra FS solo acá)


def _iniciar_cobro(aid, C):
    """Mete al auto `aid` en la zona de cobro: integra el tiempo de cobro por Euler
    con la C dada y programa el evento fin_cobro. (El lugar ya se liberó en
    fin_estacionamiento; el auto en cobro NO ocupa sector.)"""
    auto = autos[aid]

    t_min, umbral, tabla = euler.integrar(C, auto["tipo"], T_EULER, H_EULER)
    t_cobro = t_min / 60.0   # minutos → horas
    fin = reloj + t_cobro

    zona_cobro["estado"] = "AC"
    zona_cobro["auto"]   = aid
    auto["estado"]       = "EnCobro"

    tablas_euler.append((aid, auto["tipo"], C, T_EULER, H_EULER, umbral, tabla))
    push_evento(fin, "fin_cobro", aid)
    return {"cobro_C": C, "t_cobro": t_cobro, "cobro_auto": aid}


def procesar_fin_estacionamiento(lugar_id):
    lg = next(l for l in lugares if l["id"] == lugar_id)
    aid = lg["auto"]
    d = {}

    # Libera el lugar de inmediato: el auto pasa a la zona/cola de pago y deja de
    # ocupar sector (así la ocupación no cuenta tiempo "bloqueado" — pregunta c).
    lg["estado"]    = "Libre"
    lg["auto"]      = None
    lg["fin_estac"] = None

    if zona_cobro["estado"] == "Libre":
        # zona libre → pasa directo a cobrar (cola vacía → C = 0)
        d.update(_iniciar_cobro(aid, C=len(cola_cobro)))
    else:
        # zona ocupada → espera en la cola de pago (ya no ocupa lugar)
        autos[aid]["estado"] = "EsperandoCobro"
        cola_cobro.append(aid)

    guardar_fila(f"fin_estacionamiento({lugar_id})_a{aid}", d)


def procesar_fin_cobro(aid):
    global recaudacion

    # el auto paga y se destruye en el acto: EnCobro → destrucción
    recaudacion += autos[aid]["importe"]
    zona_cobro["estado"] = "Libre"
    zona_cobro["auto"]   = None
    del autos[aid]                   # destrucción directa, ANTES de guardar la fila

    d = {}
    if cola_cobro:
        # entra el primero de la cola; C = los que quedan esperando (cola - 1)
        sig = cola_cobro.pop(0)
        d.update(_iniciar_cobro(sig, C=len(cola_cobro)))

    guardar_fila(f"fin_cobro_a{aid}", d)


# ── Loop principal ──────────────────────────────────────────────────────────────
def simular(tiempo_max, hora_desde=0.0, max_filas=None):
    """Corre la simulación. Se detiene por lo que ocurra primero:
       - reloj >= tiempo_max (X),
       - MAX_ITER iteraciones,
       - max_filas filas visibles (con reloj >= hora_desde) ya generadas."""
    global reloj, iteracion, acum_ocupacion

    validar_parametros()                 # falla rápido y claro si algún parámetro no cierra
    if not tiempo_max > 0:
        raise ValueError(f"El tiempo máximo a simular debe ser > 0 (recibido: {tiempo_max}).")

    rnd_e, t_e = gen_llegada()
    push_evento(t_e, "llegada_auto")
    guardar_fila("Inicializacion", {"rnd_lleg": rnd_e, "t_entre": t_e})
    visibles = 1 if reloj >= hora_desde else 0
    if max_filas is not None and visibles >= max_filas:
        return vector_estado

    while iteracion < MAX_ITER and reloj < tiempo_max:
        if not eventos:
            break
        tiempo, _, tipo, eid = siguiente_evento()
        if tiempo > tiempo_max:
            break

        acum_ocupacion += ocupados() / N_LUGARES * (tiempo - reloj)
        reloj = tiempo

        if tipo == "llegada_auto":
            procesar_llegada_auto()
        elif tipo == "fin_estacionamiento":
            procesar_fin_estacionamiento(eid)
        elif tipo == "fin_cobro":
            procesar_fin_cobro(eid)

        iteracion += 1

        if reloj >= hora_desde:
            visibles += 1
            if max_filas is not None and visibles >= max_filas:
                break

    return vector_estado


def estadisticas(tiempo_max):
    pct_aband = (contador_abandonos / contador_llegaron * 100) if contador_llegaron else 0.0
    pct_util  = (acum_ocupacion / tiempo_max * 100) if tiempo_max else 0.0  
    return {
        "recaudacion": recaudacion,          # a) recaudación de la playa
        "pct_utilizacion": pct_util,         # c) % de utilización de los sectores
        "llegaron": contador_llegaron,
        "abandonos": contador_abandonos,
        "pct_abandono": pct_aband, 
        "lugares": N_LUGARES,               
    }


def resetear_estado():
    global lugares, autos, zona_cobro, cola_cobro, eventos, reloj, iteracion, id_auto, _seq
    global _i_lleg, _i_tipo, _i_horas, recaudacion, acum_ocupacion, vector_estado
    global contador_llegaron, contador_abandonos, tablas_euler

    lugares = [{"id": i, "estado": "Libre", "auto": None, "fin_estac": None}
               for i in range(1, N_LUGARES + 1)]
    autos = {}
    zona_cobro = {"estado": "Libre", "auto": None}
    cola_cobro = []
    eventos = []
    reloj = 0.0
    iteracion = 0
    id_auto = 0
    _seq = 0
    _i_lleg = _i_tipo = _i_horas = 0
    recaudacion = 0.0
    acum_ocupacion = 0.0
    contador_llegaron = 0
    contador_abandonos = 0
    tablas_euler = []
    vector_estado = []
