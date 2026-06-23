"""Genera explicacion_euler_simulacion.pdf — recorrido del CÓDIGO de euler.py y simulacion.py."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, Preformatted, ListFlowable, ListItem)

OUT = "explicacion_euler_simulacion.pdf"
ACC = colors.HexColor("#264653")
HDR = colors.HexColor("#2a9d8f")
SOFT = colors.HexColor("#e8f3f1")
CODEBG = colors.HexColor("#1e1e2e")

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=1.8*cm, bottomMargin=1.8*cm,
                        title="Recorrido del código: euler.py y simulacion.py — TP5 Playa",
                        author="Grupo 13")
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

def M(t):  # nombre de código en monoespaciado
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
       Paragraph("Qué hace cada parte de los archivos del motor", h2),
       Paragraph("Playa de Estacionamiento — Grupo 13", sub),
       Paragraph("Archivos: <b>euler.py</b> y <b>simulacion.py</b>", sub),
       HRFlowable(width="100%", color=ACC, spaceBefore=10, spaceAfter=10)]
NB("Este documento recorre <b>el código real</b> de los dos archivos del motor, explicando "
   "qué hace cada función y cada bloque, en lenguaje claro. Los nombres en "
   + M("este color") + " son nombres reales que aparecen en el código.")

# ════════════════════ EULER.PY ════════════════════
el += [Paragraph("Parte 1 — euler.py", h1)]
P("Es un archivo cortito con una sola tarea: calcular cuánto tarda un auto en pagar. "
  "Tiene dos datos fijos arriba y una función principal.")

el += [Paragraph("Los datos fijos del archivo", h2)]
CODE('UMBRAL = {"Grande": 180, "Pequeño": 130, "Utilitario": 130}\nMAX_PASOS = 1_000_000')
P(M("UMBRAL")+" es una tabla que dice hasta qué número tiene que llegar el cálculo según el "
  "tipo de auto: 180 para los Grandes y 130 para el resto. "
  +M("MAX_PASOS")+" es un tope de seguridad (un millón) para cortar el cálculo si por algún "
  "parámetro raro nunca llegara a destino, y así evitar que el programa se quede pensando para siempre.")

el += [Paragraph("La función "+M("integrar(C, tipo, T, h)"), h2)]
P("Es el corazón del archivo. Recibe cuatro datos y devuelve el tiempo de cobro. Primero "
  "<b>revisa que los datos sean válidos</b> y, si no lo son, corta con un mensaje claro:")
CODE('if tipo not in UMBRAL:\n    raise ValueError("Tipo de auto desconocido...")\nif not h > 0:\n    raise ValueError("El paso h debe ser > 0...")\nif C < 0:\n    raise ValueError("C no puede ser negativo...")')
P("Después hace el cálculo. Arranca dos contadores en cero: "+M("D")+" (lo que se va acumulando) "
  "y "+M("t")+" (el tiempo). Y repite un paso una y otra vez <b>mientras "+M("D")+" no haya llegado al "
  "umbral</b>:")
CODE('D = 0.0; t = 0.0; tabla = []\nwhile D < umbral:\n    dD = C + 0.2 * T + t * t      # cuánto crece en este paso\n    tabla.append((t, D, dD))      # se anota la fila\n    D = D + h * dD                # se suma al acumulado\n    t = t + h                     # avanza el tiempo')
P("En cada vuelta: calcula "+M("dD")+" (cuánto crece ahora), <b>anota la fila</b> en "+M("tabla")+" "
  "para poder mostrarla después, le suma ese crecimiento a "+M("D")+" y adelanta "+M("t")+" un paso "+M("h")+". "
  "Un contador "+M("pasos")+" vigila que no se pase de "+M("MAX_PASOS")+".")
P("Cuando "+M("D")+" alcanza el umbral, el bucle termina, se agrega la fila final (el momento del corte) "
  "y la función devuelve tres cosas: "+M("t")+" (el tiempo de cobro en minutos), el "+M("umbral")+" usado "
  "y la "+M("tabla")+" completa con todos los pasos.")
NB("En resumen, "+M("integrar")+" \"llena un balde de a cucharadas\" hasta el borde y te dice "
   "cuántas cucharadas (tiempo) hicieron falta, guardando el registro de cada una.")

# ════════════════════ SIMULACION.PY ════════════════════
el += [Paragraph("Parte 2 — simulacion.py", h1)]
P("Es el archivo grande: el motor de la simulación. Lo recorremos por bloques, en el mismo "
  "orden en que están escritos.")

el += [Paragraph("Bloque 1 — Parámetros y estado", h2)]
P("Arriba de todo están los <b>parámetros</b> (los valores con los que se juega): "+M("N_LUGARES")+" "
  "(cuántos lugares), "+M("MEDIA_LLEGADA")+" (cada cuánto llega un auto), "+M("PRECIO")+", "
  +M("PROB_TIPO")+" y "+M("PROB_HORAS")+" (los porcentajes), y los datos de Euler "+M("T_EULER")+" y "+M("H_EULER")+".")
P("Más abajo están las <b>variables de estado</b>: la \"memoria viva\" de la simulación. Las principales:")
SP(2)
el.append(tabla(
    ["Variable", "Qué guarda"],
    [[M("lugares"), "La lista de los N lugares, cada uno con su estado (Libre/Ocupado) y qué auto tiene."],
     [M("autos"), "Todos los autos presentes en el sistema en este momento."],
     [M("zona_cobro")+" / "+M("cola_cobro"), "La caja (un auto por vez) y la fila de los que esperan pagar."],
     [M("eventos"), "La agenda de cosas por pasar, ordenada por hora (el \"heap\")."],
     [M("reloj"), "La hora simulada actual."],
     [M("recaudacion")+", "+M("acum_ocupacion"), "Acumuladores de plata y de ocupación para las estadísticas."],
     [M("contador_llegaron")+", "+M("contador_abandonos"), "Cuántos autos llegaron y cuántos se fueron por estar lleno."]],
    [5.2, 10.8]))

el += [Paragraph("Bloque 2 — "+M("validar_parametros()"), h2)]
P("Antes de simular, esta función revisa que <b>todo cierre</b> y, si encuentra problemas, los junta "
  "y corta con un mensaje. Por ejemplo: que los lugares sean al menos 1, que la media de llegadas sea "
  "mayor que 0, que los porcentajes sumen 100% y que los precios no sean negativos.")
NB("Es una red de seguridad: hace que el motor <b>falle rápido y explicando el motivo</b>, en lugar de "
   "colgarse o devolver números sin sentido si alguien carga datos imposibles.")

el += [Paragraph("Bloque 3 — Las variables aleatorias (los sorteos)", h2)]
P("Cuatro funciones traducen números al azar en decisiones:")
el.append(bullets([
    M("_take(...)")+": entrega el próximo número al azar. Puede usar una lista fija preparada "
    "(para comparar con Excel) o números realmente aleatorios.",
    M("gen_llegada()")+": convierte el azar en \"minutos hasta el próximo auto\" con una fórmula "
    "exponencial. Incluye un blindaje para que el número quede siempre entre 0 y 1 y la fórmula no falle.",
    M("gen_tipo()")+": recorre los porcentajes de tipo y devuelve Pequeño, Grande o Utilitario "
    "(la \"ruleta\" de tipos).",
    M("gen_horas()")+": igual, pero para decidir si el auto se queda 1, 2, 3 o 4 horas.",
]))

el += [Paragraph("Bloque 4 — La agenda de eventos", h2)]
P(M("push_evento(...)")+" anota un evento futuro en la agenda; "+M("siguiente_evento()")+" saca el "
  "más próximo; y "+M("tiempo_de(tipo)")+" busca cuándo es el próximo evento de cierto tipo (sirve para "
  "mostrar \"próxima llegada\" en la tabla). Por debajo usa un "+M("heap")+", que mantiene todo ordenado "
  "por hora automáticamente.")

el += [Paragraph("Bloque 5 — Ayudantes y la foto del estado", h2)]
P(M("lugar_libre()")+" busca el primer lugar disponible y "+M("ocupados()")+" cuenta cuántos hay ocupados. "
  "Después, "+M("guardar_fila(...)")+" es clave: cada vez que pasa algo, <b>saca una \"foto\" completa "
  "del sistema</b> (qué auto llegó, el estado de cada lugar, la cola, la plata acumulada, etc.) y la "
  "agrega a "+M("vector_estado")+". Esa lista de fotos es exactamente la tabla que se ve en pantalla.")

el += [Paragraph("Bloque 6 — Los procesadores de eventos", h2)]
P("Acá está la lógica principal: una función por cada tipo de evento.")
SP(2)
el.append(tabla(
    ["Función", "Qué hace cuando ocurre el evento"],
    [[M("procesar_llegada_auto()"),
      "Programa la próxima llegada; si hay lugar libre, ubica al auto, le sortea tipo y horas y "
      "calcula su importe; si está lleno, lo cuenta como abandono. Guarda la fila."],
     [M("_iniciar_cobro(aid, C)"),
      "Mete un auto en la caja: llama a "+M("euler.integrar")+" para saber cuánto tardará en pagar "
      "y programa su evento de fin de cobro."],
     [M("procesar_fin_estacionamiento(...)"),
      "Libera el lugar del auto. Si la caja está libre, lo manda a pagar; si está ocupada, lo pone "
      "en la cola."],
     [M("procesar_fin_cobro(aid)"),
      "El auto paga (suma a la recaudación) y se va. Si había alguien esperando, entra el primero "
      "de la cola."]],
    [5.4, 10.6]))

el += [Paragraph("Bloque 7 — El bucle principal "+M("simular(...)"), h2)]
P("Es el director de orquesta. Primero llama a "+M("validar_parametros()")+", programa la primera "
  "llegada, y después entra en un bucle que <b>repite hasta que se acabe el tiempo</b>:")
CODE('while iteracion < MAX_ITER and reloj < tiempo_max:\n    tiempo, _, tipo, eid = siguiente_evento()   # el más próximo\n    reloj = tiempo                               # adelanta el reloj\n    if   tipo == "llegada_auto":          procesar_llegada_auto()\n    elif tipo == "fin_estacionamiento":   procesar_fin_estacionamiento(eid)\n    elif tipo == "fin_cobro":             procesar_fin_cobro(eid)')
P("En cada vuelta saca el evento más próximo, mueve el reloj a esa hora y llama a la función que "
  "corresponde. El "+M("MAX_ITER")+" es otro tope de seguridad para que nunca quede en bucle infinito.")

el += [Paragraph("Bloque 8 — Resultados y reinicio", h2)]
P(M("estadisticas(...)")+" calcula al final los números que importan: recaudación, porcentaje de "
  "utilización y porcentaje de abandonos. Y "+M("resetear_estado()")+" deja todas las variables como al "
  "principio, para poder volver a simular desde cero sin reiniciar el programa.")

SP(4)
NB("Para llevarse: "+M("euler.py")+" calcula un solo número (el tiempo de cobro). "+M("simulacion.py")+" "
   "maneja todo lo demás: los parámetros, su validación, los sorteos, la agenda de eventos, la lógica de "
   "cada evento, el bucle del reloj y las estadísticas finales.")

doc.build(el)
print("PDF generado:", OUT)
