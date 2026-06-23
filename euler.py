"""
Integración numérica (Euler) del tiempo de cobro — TP5 Playa (Grupo 13).

EDO del enunciado:   dD/dt = C + 0.2*T + t^2
- Se integra desde D=0, t=0 hasta que D alcanza el umbral del tipo de auto.
- Umbral: 180 para autos Grandes, 130 para Pequeños y Utilitarios.
- C = autos esperando en la cola de cobro al iniciar ESTE cobro (sin contar al que entra).
- T = constante parametrizable.   h = paso de integración (1 unidad = 1 minuto).

Devuelve el tiempo de cobro EN MINUTOS (la simulación lo pasa a horas /60).
"""

# Umbrales de corte por tipo de auto
UMBRAL = {"Grande": 180, "Pequeño": 130, "Utilitario": 130}

# Tope de seguridad: cantidad máxima de pasos de integración antes de abortar.
# Evita un bucle infinito si los parámetros hacen que D nunca alcance el umbral.
MAX_PASOS = 1_000_000


def integrar(C, tipo, T, h):
    """
    Integra dD/dt = C + 0.2*T + t^2 hasta D >= umbral(tipo).

    Returns:
        t_min : tiempo de cobro en minutos (cantidad de pasos * h)
        umbral: el umbral usado (180/130)
        tabla : lista de filas (t, D, dD/dt) para mostrar/exportar
                (sin columnas t(i+1)/D(i+1) ni columna de paso h: la h es parámetro)

    Raises:
        ValueError: si el tipo es desconocido, h <= 0, C < 0, o si la integración
                    supera MAX_PASOS sin alcanzar el umbral (parámetros inválidos
                    que provocarían un bucle infinito).
    """
    if tipo not in UMBRAL:
        raise ValueError(f"Tipo de auto desconocido: {tipo!r}. "
                         f"Debe ser uno de {sorted(UMBRAL)}.")
    if not h > 0:
        raise ValueError(f"El paso de integración h debe ser > 0 (recibido: {h}). "
                         "Con h <= 0 la integración no avanzaría.")
    if C < 0:
        raise ValueError(f"C (autos en cola) no puede ser negativo (recibido: {C}).")

    umbral = UMBRAL[tipo]
    D = 0.0
    t = 0.0
    tabla = []
    pasos = 0
    while D < umbral:
        dD = C + 0.2 * T + t * t
        tabla.append((t, D, dD))   # t, acumuladora, derivada
        D = D + h * dD
        t = t + h
        pasos += 1
        if pasos > MAX_PASOS:
            raise ValueError(
                f"La integración superó {MAX_PASOS} pasos sin alcanzar el umbral "
                f"D={umbral} (C={C}, T={T}, h={h}). Revisá los parámetros: "
                "valores de T muy negativos o h demasiado chico pueden impedir el corte.")
    # fila final: D ya alcanzó/superó el umbral → punto de corte del cobro
    tabla.append((t, D, C + 0.2 * T + t * t))
    return t, umbral, tabla
