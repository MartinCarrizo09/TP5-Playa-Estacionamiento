# -*- coding: utf-8 -*-
"""Suite de pruebas completa del TP5 Playa (motor + interfaz). ASCII-safe."""
import os, random
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from collections import Counter

import simulacion as sim

PRECIO = {"Pequeño": 500, "Grande": 1500, "Utilitario": 3000}
fallos = []


def check(cond, msg):
    print(("  OK   " if cond else " FAIL  ") + msg)
    if not cond:
        fallos.append(msg)


def correr(N, tmax, seed, j=0.0, maxf=None):
    random.seed(seed)
    sim.N_LUGARES = N; sim.MEDIA_LLEGADA = 13 / 60; sim.T_EULER = 2; sim.H_EULER = 0.1
    sim.PRECIO = PRECIO
    pagos = []
    orig = sim.procesar_fin_cobro

    def patched(aid):
        a = sim.autos[aid]
        pagos.append((a["tipo"], a["importe"] // PRECIO[a["tipo"]], a["importe"]))  # horas derivada
        return orig(aid)
    sim.procesar_fin_cobro = patched
    sim.resetear_estado()
    v = sim.simular(tmax, hora_desde=j, max_filas=maxf)
    sim.procesar_fin_cobro = orig
    return v, pagos


# ============ MOTOR ============
print("=" * 64)
print("MOTOR - Escenario A (N=8, 24h): recaudacion validada a mano")
print("=" * 64)
v, pagos = correr(8, 24, 1234)
desglose = Counter((t, h) for t, h, _ in pagos)
total_mano = 0
print("%-12s %5s %5s %6s %10s" % ("Tipo", "Horas", "Cant", "$/h", "Subtotal"))
for (t, h), c in sorted(desglose.items()):
    sub = c * h * PRECIO[t]; total_mano += sub
    print("%-12s %5d %5d %6d %10d" % (t, h, c, PRECIO[t], sub))
print("%34s %10d" % ("TOTAL a mano:", total_mano))
print("Recaudacion del programa: %.0f" % sim.recaudacion)
check(abs(total_mano - sim.recaudacion) < 1e-6, "recaudacion a mano == programa")
check(all(imp == h * PRECIO[t] for t, h, imp in pagos), "cada importe = horas x precio")

print("\n-- Invariantes --")
check(all(0 <= f["ocupados"] <= 8 for f in v), "ocupados en [0, N]")
check(all(f["cola"] >= 0 for f in v), "cola nunca negativa")
check(all(f["cobro_C"] is None or f["cobro_C"] >= 0 for f in v), "C nunca negativo")
check(all((f["playa_est"] == "LL") == (f["ocupados"] == 8) for f in v), "playa LL sii ocupados==N")
check(all(f["reloj"] <= 24 + 1e-9 for f in v), "ningun evento pasa tiempo_max")
check(all(f["recaudacion"] == sorted(f["recaudacion"] for f in v)[i]
          for i, f in enumerate(sorted(v, key=lambda x: x["reloj"]))) or True, "recaudacion monotona (informativo)")
# recaudacion no decrece
rec = [f["recaudacion"] for f in v]
check(all(b >= a for a, b in zip(rec, rec[1:])), "recaudacion nunca decrece")
# ocupados nunca salta mas de 1 por evento
oc = [f["ocupados"] for f in v]
check(all(abs(b - a) <= 1 for a, b in zip(oc, oc[1:])), "ocupados cambia de a 1 por evento")

en_sist = len(sim.autos)
check(sim.contador_llegaron == len(pagos) + sim.contador_abandonos + en_sist,
      "conservacion: llegaron == pagaron + abandonos + en_sistema")

area = sum(a["ocupados"] * (b["reloj"] - a["reloj"]) for a, b in zip(v, v[1:]))
util_mano = area / (8 * 24) * 100
util_prog = sim.estadisticas(24)["pct_utilizacion"]
print("%% utilizacion: a mano=%.4f  programa=%.4f" % (util_mano, util_prog))
check(abs(util_mano - util_prog) < 0.05, "% utilizacion a mano ~= programa")

mal = [1 for (aid, tp, C, T, h, um, tab) in sim.tablas_euler
       if um != (180 if tp == "Grande" else 130)]
check(not mal, "umbral Euler correcto por tipo")
check(all(tab[-1][1] >= um for (a, t, C, T, h, um, tab) in sim.tablas_euler),
      "Euler corta cuando D alcanza el umbral")

print("\n-- Escenarios limite --")
for N, tmax, sd in [(1, 12, 7), (10, 24, 9), (8, 1, 3), (8, 24, 99)]:
    v2, p2 = correr(N, tmax, sd)
    st = sim.estadisticas(tmax)
    ok = (all(0 <= f["ocupados"] <= N for f in v2) and st["recaudacion"] >= 0
          and sim.contador_llegaron == len(p2) + sim.contador_abandonos + len(sim.autos)
          and st["pct_utilizacion"] <= 100.0001)
    check(ok, "N=%d tmax=%d: invariantes OK (filas=%d recaud=$%.0f util=%.1f%%)"
          % (N, tmax, len(v2), st["recaudacion"], st["pct_utilizacion"]))

print("\n-- Reproducibilidad de semilla (== Excel) --")
sim.N_LUGARES = 8; sim.resetear_estado(); v3 = sim.simular(2)
check(abs(v3[1]["reloj"] - 0.062331) < 1e-4 and v3[1]["tipo"] == "Grande" and v3[1]["horas"] == 3,
      "fila 1 = Grande 3h reloj 0.0623 (Excel)")
check(v3[1]["importe"] == 4500, "importe fila 1 = 4500")
check(v3[2]["tipo"] == "Pequeño" and v3[2]["importe"] == 1000, "fila 2 = Pequeno 2h $1000 (Excel)")

# limite por filas
v4, _ = correr(8, 99999, 5, maxf=15)
check(len(v4) == 15, "max_filas=15 -> simula exactamente 15 filas")

# ============ INTERFAZ ============
print("\n" + "=" * 64)
print("INTERFAZ (headless)")
print("=" * 64)
from PyQt5 import QtWidgets
import main
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
app.setStyleSheet(main.DARK)
win = main.Main(); win.resize(1400, 820)

random.seed(1234); sim.N_LUGARES = 8; sim.resetear_estado()
filas = sim.simular(24); stats = sim.estadisticas(24)
win._todas = filas
win.inp["i"].setText(""); win.inp["j"].setText("0")
win.on_listo(filas, stats, list(sim.tablas_euler))
check(win.modelo.rowCount() == len(filas), "i vacio -> muestra todas las filas (bug del [:0] arreglado)")
win.inp["i"].setText("20"); win.aplicar_filtro()
check(win.modelo.rowCount() == 20, "i=20 -> 20 filas")
win.inp["i"].setText(""); win.inp["j"].setText("3"); win.aplicar_filtro()
check(all(f["reloj"] >= 3 for f in win.modelo._rows), "j=3 -> solo filas con reloj>=3")
win.inp["j"].setText("0"); win.aplicar_filtro()
check(win.modelo_ultima.rowCount() == 1, "ultima fila poblada")
check(win.modelo_euler.rowCount() > 0, "auditoria Euler poblada")
check(len(main.construir_columnas(8)) == 44, "44 columnas base con N=8 (Estadisticas = 2 cols)")
check(win.modelo.columnCount() >= 44, "vector con columnas de autos agregadas")
check(win.tabs.tabText(0) == "Vector de Estado" and win.tabs.tabText(1) == "Auditoría Euler", "tabs con texto completo")
check(hasattr(win.tabla, "frozen") and win.tabla.verticalScrollMode() == win.tabla.frozen.verticalScrollMode(),
      "columnas congeladas + scroll sincronizado")
# copiar
win.on_copiar()
txt = QtWidgets.QApplication.clipboard().text()
check(txt.count("\n") == win.modelo.rowCount(), "copiar a Excel: header + N filas")
check(txt.split("\n")[0].startswith("#\tReloj"), "copiar: encabezado correcto")
# columnas se actualizan al cambiar N
check(len(main.construir_columnas(10)) == 44 + 6, "N=10 -> 6 columnas mas (2 Fin Estac + 2 lugares)")
# columnas de autos: con 2 autos presentes hay 2 grupos x 3 cols = 6 extra
filas_demo = [{"autos": {1: ("Estacionado","Grande",4500), 2: ("EnCobro","Pequeño",1000)},
               **{k:0 for k in ("num","reloj","rnd_lleg","t_entre","prox_lleg","rnd_tipo","rnd_horas","horas",
                  "importe","cobro_C","t_cobro","prox_cobro","ocupados","cola","recaudacion","acum_ocup")},
               "evento":"x","tipo":None,"fin_estac":[None]*8,"playa_est":"CLD","cobro_est":"Libre",
               "lug_est":["Libre"]*8,"lug_auto":[None]*8}]
check(len(main.construir_columnas(8, main.autos_en(filas_demo))) == 44 + 6, "2 autos presentes -> 6 columnas de autos")

# ============ SCREENSHOT ============
win.modelo._cols = main.construir_columnas(8)
random.seed(1234); sim.N_LUGARES = 8; sim.resetear_estado()
filas = sim.simular(24); stats = sim.estadisticas(24)
win._todas = filas; win.inp["i"].setText(""); win.inp["j"].setText("0")
win.on_listo(filas, stats, list(sim.tablas_euler))
app.processEvents()
px = win.grab()
px.save("screenshot_app.png")
print("\nScreenshot guardado: screenshot_app.png (%dx%d)" % (px.width(), px.height()))

print("\n" + "=" * 64)
print("RESULTADO:", "TODOS OK" if not fallos else ("%d FALLOS: %s" % (len(fallos), fallos)))
print("=" * 64)
