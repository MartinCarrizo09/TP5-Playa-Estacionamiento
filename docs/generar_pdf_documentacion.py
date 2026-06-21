"""Genera documentacion.pdf — explicación educativa del TP5 Playa (Grupo 13)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, ListFlowable, ListItem)

OUT = "documentacion.pdf"
ACC = colors.HexColor("#264653")
HDR = colors.HexColor("#2a9d8f")
COD = colors.HexColor("#1e1e2e")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title="TP5 Playa - Documentacion", author="Grupo 13")
S = getSampleStyleSheet()
tit = ParagraphStyle("tit", parent=S["Title"], fontSize=22, textColor=ACC, alignment=TA_CENTER)
sub = ParagraphStyle("sub", parent=S["BodyText"], alignment=TA_CENTER, textColor=colors.HexColor("#555"), fontSize=11)
h1 = ParagraphStyle("h1", parent=S["Heading1"], fontSize=15, textColor=ACC, spaceBefore=14, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=S["Heading2"], fontSize=12, textColor=HDR, spaceBefore=8, spaceAfter=3)
body = ParagraphStyle("body", parent=S["BodyText"], fontSize=10, leading=14, alignment=TA_JUSTIFY)
code = ParagraphStyle("code", parent=S["BodyText"], fontSize=8.5, leading=11, fontName="Courier",
                      textColor=colors.white, backColor=COD, leftIndent=6, borderPadding=5, spaceBefore=3, spaceAfter=3)
cell = ParagraphStyle("cell", parent=body, fontSize=9, leading=12, alignment=TA_JUSTIFY)
cellb = ParagraphStyle("cellb", parent=cell, textColor=colors.white)

el = []


def P(t):
    el.append(Paragraph(t, body))


def bullets(items):
    el.append(ListFlowable([ListItem(Paragraph(i, body), leftIndent=10) for i in items],
                           bulletType="bullet", start="•", leftIndent=12))


def tabla(headers, rows, anchos):
    data = [[Paragraph(h, cellb) for h in headers]]
    for r in rows:
        data.append([Paragraph(c, cell) for c in r])
    t = Table(data, colWidths=[a * cm for a in anchos])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HDR),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef6f5")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    el.append(t)


def dec(n, titulo, que, porque):
    el.append(Paragraph(f"{n}. {titulo}", h2))
    P(f"<b>Qué hicimos:</b> {que}")
    P(f"<b>Por qué:</b> {porque}")
    el.append(Spacer(1, 3))


# ── Portada ──
el += [Paragraph("Simulación — Playa de Estacionamiento", tit),
       Paragraph("Documentación técnica y educativa · TP5 · Grupo 13", sub),
       HRFlowable(width="100%", color=ACC, spaceBefore=8, spaceAfter=8),
       Paragraph("Este documento explica <b>qué hace el programa</b>, <b>cómo está armado</b>, "
                 "las <b>decisiones de diseño</b> que tomamos (con su porqué) y <b>para qué sirve "
                 "cada botón</b>. Está pensado para que cualquiera que lo lea entienda el simulador "
                 "de eventos discretos sin conocerlo de antes.", body)]

# ── 1. Qué simula ──
el += [Paragraph("1. ¿Qué simula el programa?", h1)]
P("Una <b>playa de estacionamiento</b> con N sectores (8 por defecto). Los autos llegan, "
  "estacionan un rato y al final <b>pagan en una zona de cobro</b> antes de irse. Es una "
  "<b>simulación de eventos discretos (DES)</b>: el reloj salta de evento en evento (no avanza "
  "segundo a segundo), y en cada salto se actualiza el estado del sistema en una fila del "
  "<b>vector de estado</b>.")
P("El objetivo del TP es responder: <b>a)</b> la recaudación, <b>b)</b> cuánto recaudaría con "
  "10 lugares, y <b>c)</b> el porcentaje de utilización de la playa.")

# ── 2. Arquitectura ──
el += [Paragraph("2. Arquitectura: tres archivos", h1)]
tabla(["Archivo", "Responsabilidad"],
      [["simulacion.py", "El <b>motor</b>: variables aleatorias, eventos, lógica de la playa, cola de "
        "cobro, estadísticas. No sabe nada de la interfaz."],
       ["euler.py", "La <b>integración numérica</b> (método de Euler) que calcula el tiempo de cobro. "
        "Separado a propósito (ver decisión 4)."],
       ["main.py", "La <b>interfaz gráfica</b> (PyQt5): parámetros, botones, tabla del vector de estado, "
        "pestaña de auditoría Euler, estadísticas."]], [3.2, 12.8])
P("La idea (buena práctica) es separar <b>lógica</b> de <b>interfaz</b>: el motor se puede probar y "
  "verificar solo, sin abrir ventanas.")

# ── 3. Cómo funciona el motor ──
el += [Paragraph("3. Cómo funciona el motor (DES)", h1)]
el += [Paragraph("Objetos", h2)]
bullets(["<b>Playa</b>: N lugares (Libre / Ocupado).",
         "<b>Zona de cobro</b>: capacidad 1 (Libre / Ocupado).",
         "<b>Auto</b>: con 3 atributos clave — <b>estado</b>, <b>importe a pagar</b> y <b>tipo</b> "
         "(Pequeño/Grande/Utilitario)."])
el += [Paragraph("Eventos", h2)]
bullets(["<b>Llegada de auto</b>: entra si hay lugar; si está lleno, sigue de largo y no vuelve.",
         "<b>Fin de estacionamiento</b>: va a cobrar (si la zona está libre) o espera en la cola de cobro.",
         "<b>Fin de cobro</b>: paga, se va y libera la zona de cobro para el siguiente."])
el += [Paragraph("El loop principal", h2)]
P("Hay una <b>cola de eventos</b> (un <i>heap</i>) ordenada por tiempo. El loop saca el próximo "
  "evento, mueve el reloj a ese instante, ejecuta lo que corresponde y guarda una fila. Repite hasta "
  "que se cumple una condición de corte.")

# ── 4. Decisiones de diseño ──
el += [Paragraph("4. Decisiones de diseño (el corazón del TP)", h1)]

dec(1, "El tiempo se mide en horas",
    "Todo el reloj y los tiempos están en horas (las llegadas, las duraciones de 1–4 h, etc.).",
    "Porque el estacionamiento se mide en horas y así coincide directo con nuestro Excel del TP.")

dec(2, "Llegadas con distribución exponencial",
    "El tiempo entre llegadas se genera con <font face='Courier'>t = −media · ln(1 − RND)</font>, "
    "con media = 13 min = 13/60 h.",
    "El enunciado da un 'índice entre llegadas de 13'. Elegimos exponencial negativa (lo habitual "
    "para llegadas aleatorias) y lo dejamos documentado.")

dec(3, "El RND se trunca a 2 decimales",
    "El número aleatorio se corta a 2 decimales (queda entre 0.00 y 0.99) antes de usarlo.",
    "Dos motivos: (1) que el RND que se muestra sea exactamente el que se usó, para poder recalcular "
    "la fila a mano (tabla auditable); (2) al quedar en [0.00, 0.99], nunca pasa que 1−RND = 0, "
    "evitando el error <font face='Courier'>log(0)</font>.")

dec(4, "El tiempo de cobro se calcula por integración numérica (Euler), en un archivo aparte",
    "El cobro no tiene una fórmula cerrada: se obtiene integrando "
    "<font face='Courier'>dD/dt = C + 0.2·T + t²</font> con el método de Euler, hasta que D llega al "
    "umbral. Esa lógica vive en <font face='Courier'>euler.py</font>.",
    "Es la 'parte continua' que pide el TP5. Lo separamos en su propio archivo para que se entienda y "
    "se pueda auditar por separado (la pestaña 'Auditoría Euler' muestra esa tabla).")

dec(5, "El umbral del cobro depende del tipo de auto (por eso el auto guarda su tipo)",
    "La integración corta cuando D = <b>180</b> (autos Grandes) o <b>130</b> (Pequeños y Utilitarios). "
    "Cada auto guarda su <b>tipo</b> desde que llega.",
    "El tipo se sortea al llegar, pero el cobro ocurre <b>después</b> (al terminar de estacionar). Si "
    "no guardáramos el tipo en el objeto auto, al cobrar no sabríamos qué umbral usar.")

dec(6, "C = autos en la cola de cobro, SIN contar al que entra",
    "Cuando un auto empieza a cobrar, <font face='Courier'>C</font> es la cantidad de autos que quedan "
    "esperando en la cola (los demás), no el que está cobrando. Ej.: si esperaban 3 y entra 1, C = 2.",
    "Es la lectura literal del enunciado ('autos esperando el cobro al inicio del mismo'): el que "
    "entra ya no espera. Lo verificamos contra nuestro Excel (caso real: 2 esperando, entra 1, C = 1).")

dec(7, "El auto libera su lugar apenas termina de estacionar (no queda 'bloqueado')",
    "Al ocurrir fin_estacionamiento, el auto deja libre su sector <b>de inmediato</b> y pasa a la "
    "zona/cola de pago. Si la zona de cobro esta ocupada, espera en la cola <b>sin ocupar ningun sector</b>.",
    "Si retuviera el lugar mientras espera el cobro, habria que inventar un estado 'bloqueado' y el % de "
    "utilizacion contaria tiempo en que el auto ya no esta estacionado. Liberandolo enseguida, la "
    "ocupacion mide solo autos realmente estacionados (pregunta c).")

dec(8, "El paso de Euler h se mantiene en 0.1 como mínimo",
    "El parámetro <font face='Courier'>h</font> es configurable, pero usamos 0.1.",
    "Con h = 0.1 la tabla de integración queda en ~80–115 filas (legible para mostrarla). El error "
    "frente al valor exacto es de apenas ~3 a 9 segundos por cobro: despreciable.")

dec(9, "La tabla de Euler muestra solo t, D y dD/dt",
    "Sacamos las columnas t(i+1) / D(i+1) y la columna de paso h por fila.",
    "Esas columnas eran redundantes (el i+1 es la fila siguiente) y la h es un parámetro fijo que va "
    "arriba, no repetido en cada fila. Queda más limpio y fácil de leer.")

dec(10, "RND sembrados que reproducen el Excel, con fallback a aleatorio",
    "Al principio el programa usa los mismos RND de nuestro Excel del TP; cuando se agotan, genera "
    "aleatorios. Se controla con <font face='Courier'>USAR_SEMILLA</font>.",
    "Sirve para <b>verificar</b>: la simulación da exactamente las mismas filas que la planilla hecha "
    "a mano. Una vez validado, se pasa a aleatorio para correr días enteros.")

dec(11, "La cantidad de filas (i) limita la simulación, no solo la vista",
    "Si pedís mostrar i filas desde la hora j, el motor <b>simula solo esa ventana</b> y se detiene; "
    "no simula un millón de filas para mostrar 20.",
    "Evita trabajo inútil y hace la app más rápida cuando solo querés inspeccionar un tramo. (Para "
    "estadísticas de un día completo, dejá i vacío y poné el tiempo máximo.)")

dec(12, "Tabla con 'modelo virtual' y columnas congeladas",
    "La tabla solo dibuja las celdas visibles (modelo virtual) y mantiene fijas las 3 primeras "
    "columnas (#, Reloj, Evento) al hacer scroll horizontal.",
    "Es un requisito de la cátedra: miles de filas sin que la pantalla 'parpadee', con los datos de "
    "referencia siempre a la vista. Además el scroll vertical de las columnas fijas va sincronizado "
    "con el resto.")

# ── 5. La interfaz ──
el += [Paragraph("5. La interfaz: parámetros y botones", h1)]
el += [Paragraph("Parámetros (todos editables)", h2)]
tabla(["Parámetro", "Qué controla"],
      [["Lugares (N)", "Cantidad de sectores de la playa (8; usar 10 para la pregunta b)."],
       ["Media llegada (min)", "Promedio de tiempo entre llegadas de autos (13')."],
       ["Tiempo máx (h)", "Hasta qué hora simular (X). Corta la simulación."],
       ["T (Euler)", "Constante T de la ecuación del cobro."],
       ["h (Euler)", "Paso de integración de Euler (0.1)."],
       ["Precio Pequeño / Grande / Utilitario", "Tarifa por hora de cada tipo de auto."],
       ["% Pequeño / Grande / Utilitario", "Probabilidad de cada tipo de auto (45 / 25 / 30)."],
       ["% 1h / 2h / 3h / 4h", "Probabilidad de cada duración de estacionamiento (50 / 30 / 15 / 5)."],
       ["Mostrar desde hora j", "Desde qué hora arranca la ventana que se muestra/simula."],
       ["Cant. filas i", "Cuántas filas mostrar (y hasta dónde simular). Vacío/0 = sin límite."]], [4.5, 11.5])
el += [Paragraph("Botones", h2)]
tabla(["Botón", "Qué hace"],
      [["▶ Simular", "Corre la simulación con los parámetros actuales (en un hilo aparte para que la "
        "ventana no se congele) y llena el vector de estado, la última fila y las estadísticas."],
       ["Re-aplicar i/j", "Vuelve a aplicar el filtro de visualización (mostrar i filas desde la hora j) "
        "sobre lo ya simulado, sin volver a simular."],
       ["Copiar a Excel", "Copia el vector de estado visible al portapapeles en formato tabulado, listo "
        "para pegar en Excel o Google Sheets."]], [3.2, 12.8])
el += [Paragraph("Pestañas y zonas", h2)]
bullets(["<b>Vector de Estado</b>: la tabla principal, fila por fila de la simulación. Debajo, la "
         "<b>última fila</b> (estado final del sistema).",
         "<b>Auditoría Euler</b>: la tabla de cada integración del cobro (columnas t, D, dD/dt), "
         "identificada por auto, tipo, C y umbral.",
         "<b>Barra inferior</b>: las estadísticas en vivo (recaudación, % utilización, % abandono, "
         "cantidad de filas e integraciones)."])

# ── 6. Cómo correrlo ──
el += [Paragraph("6. Cómo correrlo", h1)]
el.append(Paragraph("pip install PyQt5<br/>cd TP5-Playa<br/>python main.py", code))
P("Para verificar el motor sin interfaz se pueden importar <font face='Courier'>simulacion</font> y "
  "<font face='Courier'>euler</font> desde un script y leer <font face='Courier'>vector_estado</font> "
  "y <font face='Courier'>estadisticas()</font>.")

doc.build(el)
print("PDF generado:", OUT)
