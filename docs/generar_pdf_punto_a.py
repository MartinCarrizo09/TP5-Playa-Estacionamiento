"""Genera punto_a.pdf a partir del análisis del Punto A (TP5 Playa, Grupo 13)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, KeepTogether)

OUT = "punto_a.pdf"
ACC = colors.HexColor("#264653")
HDR = colors.HexColor("#2a9d8f")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm,
                        title="TP5 Punto A - Playa de Estacionamiento", author="Grupo 13")
S = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=S["Heading1"], fontSize=15, textColor=ACC, spaceBefore=12, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=S["Heading2"], fontSize=12, textColor=HDR, spaceBefore=8, spaceAfter=4)
body = ParagraphStyle("body", parent=S["BodyText"], fontSize=9.5, leading=13)
cell = ParagraphStyle("cell", parent=body, fontSize=8.5, leading=11)
cellb = ParagraphStyle("cellb", parent=cell, textColor=colors.white)
tit = ParagraphStyle("tit", parent=S["Title"], fontSize=20, textColor=ACC, alignment=TA_CENTER)
sub = ParagraphStyle("sub", parent=body, alignment=TA_CENTER, textColor=colors.HexColor("#555"))

el = []

def tabla(headers, rows, anchos):
    data = [[Paragraph(h, cellb) for h in headers]]
    for r in rows:
        data.append([Paragraph(c, cell) for c in r])
    t = Table(data, colWidths=[a * cm for a in anchos])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HDR),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef6f5")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t

# Portada
el += [Paragraph("TP5 — Punto A", tit),
       Paragraph("Análisis y definiciones del sistema", h2),
       Paragraph("Playa de Estacionamiento — Grupo 13", sub),
       HRFlowable(width="100%", color=ACC, spaceBefore=8, spaceAfter=10)]

# 1. Objetos
el += [Paragraph("1. Identificación de objetos", h1)]
el += [Paragraph("1.1 Playa de estacionamiento (servidor de N lugares)", h2),
       tabla(["Atributo", "Valores posibles"],
             [["Estado", "CLD (con lugar disponible), LL (llena)"],
              ["Capacidad (N)", "parámetro (default 8; pregunta b: 10)"],
              ["Lugares ocupados", "0 … N"]], [4, 12])]
el += [Spacer(1, 4), Paragraph("Cada lugar (1..N):", body),
       tabla(["Atributo", "Valores posibles"],
             [["Estado", "Libre, OC (ocupado)"],
              ["Auto asignado", "id de auto / —"],
              ["Fin de estacionamiento", "hora (h) / —"]], [4, 12])]
el += [Spacer(1, 4), Paragraph("1.2 Zona de cobro (servidor, capacidad 1)", h2),
       tabla(["Atributo", "Valores posibles"],
             [["Estado", "Libre, Ocupado"], ["Auto en cobro", "id de auto / —"]], [4, 12])]
el += [Spacer(1, 4), Paragraph("1.3 Auto (entidad temporal)", h2),
       tabla(["Atributo", "Valores posibles"],
             [["Estado", "Estacionado, EsperandoCobro, EnCobro, Pagó (o sigue de largo si la playa está llena)"],
              ["Tipo", "Pequeño, Grande, Utilitario"],
              ["Importe a pagar", "horas × precio según tipo"]], [4, 12])]
el += [Spacer(1, 3),
       Paragraph("El auto guarda <b>solo</b> estado, tipo e importe. Las horas se usan al llegar para "
                 "calcular el importe y programar el fin de estacionamiento, y no se guardan. El vínculo "
                 "auto–lugar se modela en el objeto <b>Lugar</b> (lugar → id de auto), que usa menos columnas.", body)]
el += [Spacer(1, 3),
       Paragraph("El <b>tipo</b> se guarda en el objeto porque la condición de corte de la "
                 "integración del cobro (D = 180 grande / 130 resto) se necesita al finalizar el "
                 "estacionamiento, no solo al llegar.", body)]
el += [Spacer(1, 4), Paragraph("1.4 Variables auxiliares (acumuladores / contadores)", h2),
       Paragraph("reloj (hora simulada), recaudación, acum_ocupación (∫ lugares_ocupados·dt), "
                 "contador_llegaron, contador_abandonos, longitud de la cola de cobro.", body)]

# 2. Eventos
el += [Paragraph("2. Determinación de eventos", h1),
       tabla(["Evento", "Qué hace"],
             [["Llegada de auto", "Si hay lugar libre, ocupa y programa su fin de estacionamiento; "
               "si la playa está llena, sigue de largo (abandona, no vuelve). Programa la próxima llegada."],
              ["Fin de estacionamiento", "El auto debe pagar. Si la zona de cobro está libre, libera su "
               "lugar y entra a cobrar (se integra el tiempo de cobro). Si está ocupada, espera en la "
               "cola de cobro ocupando su lugar."],
              ["Fin de cobro", "El auto paga (suma a la recaudación) y abandona la playa. Libera la zona "
               "de cobro y entra el primero de la cola de cobro."]], [4, 12])]

# 3. Colas
el += [Paragraph("3. Colas del sistema", h1),
       tabla(["Cola", "Características"],
             [["Cola de cobro", "FIFO. Autos que terminaron de estacionar y esperan la zona de cobro "
               "(capacidad 1). Al terminar de estacionar liberan su lugar, así que mientras esperan el "
               "cobro ya NO ocupan sector. Sin tope explícito."],
              ["Entrada (no hay cola)", "Si la playa está llena, el auto sigue de largo y no vuelve."]],
             [4, 12])]

# 4. Variables aleatorias
el += [Paragraph("4. Variables aleatorias y fórmulas de generación", h1),
       tabla(["Variable", "Distribución", "Fórmula de generación"],
             [["Tiempo entre llegadas", "Exponencial neg., media 13 min",
               "t = −media · ln(1 − RND), con media = 13/60 h"],
              ["Tipo de auto", "Discreta (45/25/30 %, parametrizable)",
               "RND por probabilidad acumulada: &lt; 0.45 → Pequeño · &lt; 0.70 → Grande · &lt; 1 → Utilitario"],
              ["Horas de estacionamiento", "Discreta (50/30/15/5 %, parametrizable)",
               "RND por prob. acumulada: &lt; 0.50 → 1h · &lt; 0.80 → 2h · &lt; 0.95 → 3h · &lt; 1 → 4h"],
              ["Tiempo de cobro", "Parte continua (sin fórmula cerrada)",
               "Integración numérica (Euler) de dD/dt = C + 0.2·T + t² hasta D = umbral "
               "(180 Grande / 130 resto). C = autos en cola de cobro al iniciar el cobro "
               "(sin contar al que entra); T, h parámetros."]], [3.5, 4, 8.5])]

# 5. Preguntas
el += [Paragraph("5. Preguntas a responder con la simulación", h1),
       Paragraph("<b>a) Recaudación</b> = Σ (horas × precio) de los autos que pagaron. "
                 "Precios: Pequeño $500/h, Grande $1500/h, Utilitario $3000/h.", body),
       Paragraph("<b>b) Recaudación con 10 lugares</b> = misma simulación con N = 10.", body),
       Paragraph("<b>c) % de utilización</b> = acum_ocupación / (N × tiempo_simulado) × 100 "
                 "(solo sectores de estacionamiento).", body)]

doc.build(el)
print("PDF generado:", OUT)
