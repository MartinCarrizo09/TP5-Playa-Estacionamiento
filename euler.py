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


def integrar(C, tipo, T, h):
    """
    Integra dD/dt = C + 0.2*T + t^2 hasta D >= umbral(tipo).

    Returns:
        t_min : tiempo de cobro en minutos (cantidad de pasos * h)
        umbral: el umbral usado (180/130)
        tabla : lista de filas (t, D, dD/dt) para mostrar/exportar
                (sin columnas t(i+1)/D(i+1) ni columna de paso h: la h es parámetro)
    """
    umbral = UMBRAL[tipo]
    D = 0.0
    t = 0.0
    tabla = []
    while D < umbral:
        dD = C + 0.2 * T + t * t
        tabla.append((t, D, dD))   # t, acumuladora, derivada
        D = D + h * dD
        t = t + h
    # fila final: D ya alcanzó/superó el umbral → punto de corte del cobro
    tabla.append((t, D, C + 0.2 * T + t * t))
    return t, umbral, tabla
