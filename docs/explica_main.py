"""Genera explicacion_main.pdf — recorrido del CÓDIGO de main.py (la interfaz gráfica)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, Preformatted, ListFlowable, ListItem)

OUT = "explicacion_main.pdf"
ACC = colors.HexColor("#264653")
HDR = colors.HexColor("#2a9d8f")
SOFT = colors.HexColor("#e8f3f1")
CODEBG = colors.HexColor("#1e1e2e")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=1.8*cm, bottomMargin=1.8*cm,
                        title="Recorrido del código: main.py — TP5 Playa", author="Grupo 13")
S = getSampleStyleSheet()
tit  = ParagraphStyle("tit", parent=S["Title"], fontSize=20, textColor=ACC, alignment=TA_CENTER)
sub  = ParagraphStyle("sub", parent=S["BodyText"], alignment=TA_CENTER, textColor=colors.HexColor("#555"), fontSize=11)
h1   = ParagraphStyle("h1", parent=S["Heading1"], fontSize=14.5, textColor=ACC, spaceBefore=13, spaceAfter=5)
h2   = ParagraphStyle("h2", parent=S["Heading2"], fontSize=11.5, textColor=HDR, spaceBefore=8, spaceAfter=3)
body = ParagraphStyle("body", parent=S["BodyText"], fontSize=9.8, leading=14, alignment=TA_JUSTIFY)
note = ParagraphStyle("note", parent=body, fontSize=9.3, leading=12.5, textColor=colors.HexColor("#333"),
                      backColor=SOFT, borderColor=HDR, borderWidth=0.6, borderPadding=7, spaceBefore=4, spaceAfter=4)
code = ParagraphStyle("code", parent=S["Code"], fontName="Courier", fontSize=8, leading=10.5,
                      textColor=colors.HexColor("#cdd6f4"), backColor=CODEBG,
                      borderPadding=7, spaceBefore=4, spaceAfter=6, leftIndent=2, firstLineIndent=0)
cell = ParagraphStyle("cell", parent=body, fontSize=8.8, leading=11.5, alignment=TA_JUSTIFY)
cellb= ParagraphStyle("cellb", parent=cell, textColor=colors.white)

el = []

def P(t): el.append(Paragraph(t, body))
def NB(t): el.append(Paragraph(t, note))
def SP(h=4): el.append(Spacer(1, h))
def CODE(t): el.append(Preformatted(t, code))

def M(t):
    return f'<font face="Courier" size="9" color="#1e66f5">{t}</font>'

def tabla(headers, rows, anchos):
    data = [[Paragraph(h, cellb) for h in headers]]
    for r in rows:
        data.append([Paragraph(c, cell) for c in r])
    t = Table(data, colWidths=[a * cm for a in anchos])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HDR),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef6f5")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t

def bullets(items):
    return ListFlowable([ListItem(Paragraph(t, body), leftIndent=10) for t in items],
                        bulletType="bullet", start="•", leftIndent=14, bulletColor=HDR)

# ── Portada ───────────────────────────────────────────────────────────────────
el += [Paragraph("Recorrido del código", tit),
       Paragraph("Qué hace cada parte de la interfaz gráfica", h2),
       Paragraph("Playa de Estacionamiento — Grupo 13", sub),
       Paragraph("Archivo: <b>main.py</b>", sub),
       HRFlowable(width="100%", color=ACC, spaceBefore=10, spaceAfter=10)]
NB("Este documento recorre <b>el código real</b> de "+M("main.py")+", la ventana del programa. "
   "Está hecha con una herramienta llamada <b>PyQt5</b> (una caja de piezas para armar ventanas: "
   "botones, tablas, pestañas). Los nombres en "+M("este color")+" son nombres reales del código.")

# ── 1 ─────────────────────────────────────────────────────────────────────────
el += [Paragraph("1. La idea general del archivo", h1)]
P("Este archivo <b>no hace cuentas</b>: las pide y las muestra. Importa el motor con "
  +M("import simulacion as sim")+" y se ocupa de tres cosas: <b>(1)</b> dibujar la ventana, "
  "<b>(2)</b> tomar lo que el usuario carga y mandárselo al motor, y <b>(3)</b> mostrar los "
  "resultados en tablas con colores. El programa arranca al final del archivo, en el bloque "
  +M("if __name__ == \"__main__\":")+", que crea la ventana y la muestra.")

# ── 2 ─────────────────────────────────────────────────────────────────────────
el += [Paragraph("2. Piezas de presentación (cómo se ven los datos)", h1)]

el += [Paragraph(M("fmt(v)")+" — dar formato a cada celda", h2)]
P("Función chiquita que decide cómo se ve cada valor: convierte "+M("None")+" en un guión, los "
  "verdadero/falso en \"Sí/No\", y recorta los decimales largos. Es puro maquillaje de los números.")

el += [Paragraph(M("construir_columnas(n)")+" — definir las columnas", h2)]
P("Arma la lista de todas las columnas de la tabla grande, agrupadas por tema (\"Llegada Auto\", "
  "\"Datos Auto\", \"Cobro\", un grupo por cada lugar, etc.). Para cada columna guarda un grupo, un "
  "título y una <b>instrucción de dónde sacar el dato</b> de cada fila. Como la playa puede tener "
  "8 o 10 lugares, las columnas se generan según "+M("n")+".")

el += [Paragraph(M("COLOR_ESTADO")+" — la paleta de estados", h2)]
P("Es una tabla que asocia cada estado con un color: por ejemplo Libre en verde, ocupado en naranja, "
  "playa llena en rojo. Después la tabla usa esto para pintar las celdas y comunicar de un vistazo.")

# ── 3 ─────────────────────────────────────────────────────────────────────────
el += [Paragraph("3. Las tablas en pantalla", h1)]
P("Una tabla en PyQt5 separa <b>los datos</b> de <b>cómo se dibujan</b>. Por eso hay varias clases:")
SP(2)
el.append(tabla(
    ["Clase", "Su rol"],
    [[M("TablaModel"),
      "Es el \"depósito de datos\" de la tabla. Sabe cuántas filas y columnas hay y, cuando la "
      "pantalla le pregunta por una celda, le entrega el valor ya formateado y su color."],
     [M("GroupedHeader"),
      "Dibuja el encabezado de <b>dos niveles</b>: arriba el nombre del grupo (con su color) y abajo "
      "el título de cada columna."],
     [M("SepDelegate"),
      "Dibuja una línea vertical al final de cada grupo de columnas, para separarlos visualmente."],
     [M("VectorView"),
      "Es la tabla en sí. Su truco principal: mantiene las <b>primeras 3 columnas congeladas</b> "
      "(número, reloj y evento) para que no se pierdan al desplazarse a la derecha, como en Excel."]],
    [4.6, 11.4]))
NB("Toda esta sección es solo <b>presentación</b>: no cambia ningún resultado, solo hace que la "
   "tabla —que es muy ancha— sea legible.")

# ── 4 ─────────────────────────────────────────────────────────────────────────
el += [Paragraph("4. "+M("SimWorker")+" — simular sin congelar la ventana", h1)]
P("Si el programa hiciera la simulación \"en el mismo lugar\" donde dibuja la ventana, la ventana se "
  "quedaría tildada hasta terminar. Para evitarlo, "+M("SimWorker")+" corre la simulación <b>en "
  "segundo plano</b> (un hilo aparte). Cuando termina, avisa con una señal:")
CODE('class SimWorker(QtCore.QThread):\n    terminado = QtCore.pyqtSignal(object, object, object)  # éxito\n    fallo     = QtCore.pyqtSignal(str)                     # hubo un error\n\n    def run(self):\n        try:\n            ...  # configura el motor y llama a sim.simular(...)\n            self.terminado.emit(filas, stats, ...)\n        except Exception as e:\n            self.fallo.emit(str(e))')
P("Tiene dos señales: "+M("terminado")+" (cuando todo salió bien, con los resultados) y "+M("fallo")+" "
  "(cuando el motor lanza un error). El "+M("try / except")+" <b>atrapa cualquier problema</b> y lo "
  "convierte en un aviso, para que la ventana muestre el motivo en vez de cerrarse de golpe.")

# ── 5 ─────────────────────────────────────────────────────────────────────────
el += [Paragraph("5. "+M("Main")+" — la ventana principal", h1)]
P("Es la clase central: arma la ventana entera y conecta los botones con las acciones.")

el += [Paragraph(M("_panel_parametros()")+" — las casillas de carga", h2)]
P("Crea todas las casillas donde se cargan los datos (lugares, media, precios, porcentajes, etc.) "
  "y los botones "+M("▶ Simular")+", "+M("Re-aplicar i/j")+" y "+M("Copiar a Excel")+". Cada casilla "
  "queda guardada en un diccionario "+M("self.inp")+" para poder leerla después.")

el += [Paragraph(M("_recoger_parametros()")+" y "+M("_num(...)")+" — validar lo que se carga", h2)]
P("Antes de simular, el programa <b>revisa que todo lo cargado tenga sentido</b>. "+M("_num(...)")+" "
  "lee una casilla, verifica que sea un número y que respete un mínimo (por ejemplo, los lugares no "
  "pueden ser menos de 1, ni la media ser 0). "+M("_recoger_parametros()")+" usa esa función en cada "
  "campo, junta todos los errores y además controla que los porcentajes sumen 100.")
NB("Si algo está mal, no simula: <b>devuelve la lista de errores</b> para mostrarlos. Así un dato "
   "imposible (una letra, un negativo, porcentajes que no suman) nunca rompe el programa.")

el += [Paragraph(M("on_simular()")+" — el botón de arranque", h2)]
P("Es lo que se ejecuta al apretar "+M("▶ Simular")+". Su lógica es directa:")
CODE('def on_simular(self):\n    params, errores = self._recoger_parametros()\n    if errores:\n        QMessageBox.warning(self, "Revisá los parámetros", ...)  # avisa y NO simula\n        return\n    ...\n    self.worker = SimWorker(params)\n    self.worker.terminado.connect(self.on_listo)\n    self.worker.fallo.connect(self.on_fallo)\n    self.worker.start()')
P("Primero valida. Si hay errores, muestra un cartel y corta. Si está todo bien, lanza el "
  +M("SimWorker")+" en segundo plano y le dice a quién avisar cuando termine: "+M("on_listo")+" si "
  "salió bien, "+M("on_fallo")+" si hubo un error.")

el += [Paragraph(M("on_listo(...)")+" y "+M("on_fallo(...)")+" — recibir el resultado", h2)]
P(M("on_listo")+" recibe las filas y las estadísticas, llena las tablas (incluida la de auditoría "
  "Euler) y muestra abajo la recaudación y el porcentaje de utilización. "+M("on_fallo")+" muestra un "
  "cartel rojo con el motivo del error y vuelve a habilitar el botón.")

el += [Paragraph("Acciones cómodas", h2)]
el.append(bullets([
    M("aplicar_filtro()")+": muestra solo un tramo de filas (desde cierta hora, o una cantidad máxima), "
    "porque una corrida puede generar muchísimas.",
    M("on_celda_click(...)")+": si se hace clic en el tiempo de cobro de un auto, salta al detalle de "
    "ese cálculo en la pestaña de Euler.",
    M("on_resumen_click(...)")+" / "+M("_ir_a_euler(...)")+": muestran, a la derecha, la tabla de pasos "
    "del cálculo del auto elegido.",
    M("on_copiar()")+": copia la tabla visible al portapapeles para pegarla en Excel.",
]))

# ── 6 ─────────────────────────────────────────────────────────────────────────
el += [Paragraph("6. En resumen", h1)]
el.append(tabla(
    ["Bloque del código", "Para qué está"],
    [["Piezas de presentación<br/>("+M("fmt")+", "+M("construir_columnas")+", "+M("COLOR_ESTADO")+")",
      "Definen cómo se ven los datos: formato, columnas y colores."],
     ["Clases de tabla<br/>("+M("TablaModel")+", "+M("VectorView")+"…)",
      "Muestran la tabla ancha de forma legible, con encabezados agrupados y columnas congeladas."],
     [M("SimWorker"),
      "Corre la simulación en segundo plano y avisa por señales si terminó o falló."],
     [M("Main")+" (la ventana)",
      "Arma la pantalla, <b>valida lo que se carga</b>, lanza la simulación y muestra los resultados."]],
    [6.0, 10.0]))
SP(4)
NB("Para llevarse: "+M("main.py")+" es la cara visible del programa. Su parte más importante para la "
   "robustez es "+M("_recoger_parametros()")+", que revisa los datos antes de simular, y el "
   +M("try/except")+" del "+M("SimWorker")+", que convierte cualquier error del motor en un aviso claro "
   "en vez de un cierre inesperado.")

doc.build(el)
print("PDF generado:", OUT)
