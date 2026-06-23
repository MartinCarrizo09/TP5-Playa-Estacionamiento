"""
TP5 — Simulación Playa de Estacionamiento (Grupo 13)
Interfaz gráfica PyQt5. Motor en simulacion.py + euler.py.

Correr:  pip install PyQt5  &&  python main.py
"""
import sys 

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

import simulacion as sim


# ── Colores de estado (Catppuccin Mocha) ───────────────────────────────────────
COLOR_ESTADO = {
    "Libre": "#a6e3a1", 
    "OC": "#fab387", "AC": "#fab387",
    "CLD": "#a6e3a1", "LL": "#f38ba8",
    "Pequeño": "#89dceb", 
    "Grande": "#fab387", 
    "Utilitario": "#cba6f7",
    "Estacionado": "#a6e3a1", 
    "EsperandoCobro": "#f9e2af", 
    "EnCobro": "#f38ba8",
    "FueraDeSistema": "#c0c4cf",
}

# Tema CLARO (Catppuccin Latte) — superficies claras, sin blanco puro
WHITE = """
QWidget { background:#e6e9ef; color:#4c4f69; font-size:12px; }
QGroupBox { background:#eff1f5; border:1px solid #bcc0cc; border-radius:6px; margin-top:10px; }
QGroupBox::title { subcontrol-origin: margin; left:10px; padding:0 4px; color:#1e66f5; font-weight:bold; }
QLineEdit { background:#f4f5f8; border:1px solid #bcc0cc; border-radius:4px; padding:2px; color:#4c4f69; }
QTableView { background:#e9ecf2; alternate-background-color:#dfe3ea; gridline-color:transparent;
             color:#4c4f69; selection-background-color:#7287fd; selection-color:#ffffff;
             border:1px solid #bcc0cc; }
QTabWidget::pane { border:1px solid #bcc0cc; }
QTabBar::tab { background:#dce0e8; color:#4c4f69; padding:7px 24px; min-width:150px; margin-right:2px; }
QTabBar::tab:selected { background:#1e66f5; color:#ffffff; }
QSplitter::handle { background:#e6e9ef; }
QSplitter::handle:hover { background:#1e66f5; }
"""


def fmt(v): ##
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "Sí" if v else "No"
    if isinstance(v, float):
        return "0" if v == 0 else f"{v:.4f}".rstrip("0").rstrip(".")
    return str(v)


# ── Columnas del vector de estado ───────────────────────────────────────────────
def construir_columnas(n, auto_ids=()):
    cols = [
        ("", "#",          lambda r: r["num"]),
        ("", "Reloj (h)",  lambda r: r["reloj"]),
        ("", "Evento",     lambda r: r["evento"]),
        ("Llegada Auto", "RND",      lambda r: r["rnd_lleg"]),
        ("Llegada Auto", "T. entre", lambda r: r["t_entre"]),
        ("Llegada Auto", "Próx. Lleg.", lambda r: r["prox_lleg"]),
        ("Datos Auto", "RND tipo",  lambda r: r["rnd_tipo"]),
        ("Datos Auto", "Tipo",      lambda r: r["tipo"]),
        ("Datos Auto", "RND hs",    lambda r: r["rnd_horas"]),
        ("Datos Auto", "Horas",     lambda r: r["horas"]),
        ("Datos Auto", "Importe",   lambda r: r["importe"]),
    ]
    for i in range(n):
        cols.append(("Fin Estac.", f"L{i+1}", lambda r, i=i: r["fin_estac"][i])) 



    cols += [
        ("Cobro", "C",            lambda r: r["cobro_C"]),
        ("Cobro", "T. Cobro (h)", lambda r: r["t_cobro"]),
        ("Cobro", "Próx. FinCobro", lambda r: r["prox_cobro"]),
        ("Servidor Playa", "Estado",   lambda r: r["playa_est"]),
        ("Servidor Playa", "Ocupados", lambda r: r["ocupados"]),
        ("Servidor Cobro", "Estado", lambda r: r["cobro_est"]),
        ("Servidor Cobro", "Cola",   lambda r: r["cola"]),
    ]

    for i in range(n):
        cols.append((f"Lugar {i+1}", "Estado", lambda r, i=i: r["lug_est"][i]))
        cols.append((f"Lugar {i+1}", "Auto",   lambda r, i=i: r["lug_auto"][i]))


    cols += [
        ("Estadísticas", "AC Recaudación", lambda r: r["recaudacion"]),
        ("Estadísticas", "AC Ocupación",   lambda r: r["acum_ocup"]),
    ]

    # Objetos temporales: una columna-grupo por cada auto presente
    for aid in auto_ids:
        cols.append((f"Auto {aid}", "Estado",  lambda r, a=aid: r["autos"].get(a, (None, None, None))[0]))
        cols.append((f"Auto {aid}", "Tipo",    lambda r, a=aid: r["autos"].get(a, (None, None, None))[1]))
        cols.append((f"Auto {aid}", "Importe", lambda r, a=aid: r["autos"].get(a, (None, None, None))[2]))
    return cols


def autos_en(rows):
    """Ids de autos que aparecen en las filas dadas, en orden de aparición."""
    vistos, orden = set(), []
    for r in rows:
        for aid in r.get("autos", {}):
            if aid not in vistos:
                vistos.add(aid); orden.append(aid)
    return sorted(orden)


# ── Modelo virtual genérico ─────────────────────────────────────────────────────
class TablaModel(QtCore.QAbstractTableModel):
    def __init__(self, columnas):
        super().__init__()
        self._cols = columnas
        self._rows = []

    def set_filas(self, rows):
        self.beginResetModel(); self._rows = rows; self.endResetModel()

    def set_columnas(self, cols):
        self.beginResetModel(); self._cols = cols; self.endResetModel()

    def set_contenido(self, cols, rows):
        # cambia columnas y filas en un solo reset (evita estado inconsistente al variar N)
        self.beginResetModel(); self._cols = cols; self._rows = rows; self.endResetModel()

    def rowCount(self, p=QtCore.QModelIndex()):
        return len(self._rows)

    def columnCount(self, p=QtCore.QModelIndex()):
        return len(self._cols)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        raw = self._cols[index.column()][2](self._rows[index.row()])
        if role == Qt.DisplayRole:
            return fmt(raw)
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        if role == Qt.BackgroundRole and isinstance(raw, str) and raw in COLOR_ESTADO:
            return QtGui.QColor(COLOR_ESTADO[raw])
        if role == Qt.ForegroundRole:
            if isinstance(raw, str) and raw in COLOR_ESTADO:
                return QtGui.QColor("#1e1e2e")
            if isinstance(raw, str) and "abandona" in raw:
                return QtGui.QColor("#d20f39")
        return None

    def headerData(self, s, o, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and o == Qt.Horizontal:
            return self._cols[s][1]
        return None

    def grupos(self):
        tramos, ini = [], 0
        for i in range(1, len(self._cols) + 1):
            if i == len(self._cols) or self._cols[i][0] != self._cols[ini][0]:
                tramos.append((self._cols[ini][0], ini, i - 1)); ini = i
        return tramos


# ── Encabezado de dos niveles ───────────────────────────────────────────────────
class GroupedHeader(QtWidgets.QHeaderView):
    # Pasteles claros (Catppuccin Latte)
    COLORES = {
        "Llegada Auto": "#bcc8f5", 
        "Datos Auto": "#bce3c5", 
        "Fin Estac.": "#f5e6b0",
        "Cobro": "#f5c4cf", 
        "Servidor Playa": "#b3dde4", 
        "Servidor Cobro": "#dcc8ee",
        "Estadísticas": "#d2d6e0",
    }

    def __init__(self, model, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self._model = model
        self.setSectionsClickable(True)
        self.setFixedHeight(40)

    def _color(self, g):
        if g in self.COLORES:
            return self.COLORES[g]
        return "#ecd6b8" if g.startswith("Auto") else "#d2d6e0"

    def paintSection(self, painter, rect, idx):
        painter.save()
        h = rect.height()
        bajo = QtCore.QRect(rect.left(), h // 2, rect.width(), h - h // 2)
        painter.fillRect(bajo, QtGui.QColor("#d5d9e2"))
        painter.setPen(QtGui.QColor("#4c4f69"))
        painter.drawText(bajo, Qt.AlignCenter, self._model._cols[idx][1])
        for g, ini, fin in self._model.grupos():
            if ini <= idx <= fin:
                if g and idx == ini:
                    ancho = sum(self.sectionSize(c) for c in range(ini, fin + 1))
                    sup = QtCore.QRect(rect.left(), 0, ancho, h // 2)
                    painter.fillRect(sup, QtGui.QColor(self._color(g)))
                    painter.setPen(QtGui.QColor("#363a4e"))
                    f = painter.font(); f.setBold(True); painter.setFont(f)
                    painter.drawText(sup, Qt.AlignCenter, g)
                elif not g:
                    painter.fillRect(QtCore.QRect(rect.left(), 0, rect.width(), h // 2),
                                     QtGui.QColor("#e6e9ef"))
                break
        painter.setPen(QtGui.QColor("#bcc0cc"))
        painter.drawRect(rect)
        painter.restore()


# ── Delegate: línea vertical al final de cada grupo de columnas ──────────────────
class SepDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = model

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        col = index.column()
        ultima = self._model.columnCount() - 1
        for g, ini, fin in self._model.grupos():
            if col == fin and fin != ultima:
                painter.save()
                painter.setPen(QtGui.QColor("#9ca0b0"))
                x = option.rect.right()
                painter.drawLine(x, option.rect.top(), x, option.rect.bottom())
                painter.restore()
                break


# ── Vista con 3 columnas congeladas ─────────────────────────────────────────────
class VectorView(QtWidgets.QTableView):
    FROZEN = 3

    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setHorizontalHeader(GroupedHeader(model, self))
        self.setSelectionBehavior(self.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(22)
        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setItemDelegate(SepDelegate(model, self))
        for c, w in ((0, 46), (1, 92), (2, 190)):
            self.setColumnWidth(c, w)

        fz = QtWidgets.QTableView(self)
        fz.setModel(model)
        fz.setHorizontalHeader(GroupedHeader(model, fz))
        fz.setSelectionModel(self.selectionModel())
        fz.setSelectionBehavior(self.SelectRows)
        fz.setFocusPolicy(Qt.NoFocus)
        fz.setAlternatingRowColors(True)
        fz.verticalHeader().hide()
        fz.verticalHeader().setDefaultSectionSize(22)
        fz.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        fz.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        fz.setVerticalScrollMode(self.ScrollPerPixel)
        fz.setItemDelegate(SepDelegate(model, fz))
        fz.setStyleSheet("border:none;")
        self.frozen = fz
        self.viewport().stackUnder(fz)

        self.verticalScrollBar().valueChanged.connect(fz.verticalScrollBar().setValue)
        fz.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.horizontalHeader().sectionResized.connect(self._on_resize)
        model.modelReset.connect(self._setup_frozen)
        self._setup_frozen()

    def _setup_frozen(self):
        for c in range(self.model().columnCount()):
            self.frozen.setColumnHidden(c, c >= self.FROZEN)
        for c in range(self.FROZEN):
            self.frozen.setColumnWidth(c, self.columnWidth(c))
        self._geom()

    def _on_resize(self, idx, old, new):
        if idx < self.FROZEN:
            self.frozen.setColumnWidth(idx, new); self._geom()

    def _geom(self):
        ancho = sum(self.columnWidth(c) for c in range(self.FROZEN))
        self.frozen.setGeometry(self.frameWidth(), self.frameWidth(), ancho,
                                self.viewport().height() + self.horizontalHeader().height())

    def resizeEvent(self, e):
        super().resizeEvent(e); self._geom()

    def scrollTo(self, index, hint=QtWidgets.QAbstractItemView.EnsureVisible):
        if index.column() >= self.FROZEN:
            super().scrollTo(index, hint)


# ── Worker ──────────────────────────────────────────────────────────────────────
class SimWorker(QtCore.QThread):
    terminado = QtCore.pyqtSignal(object, object, object)
    fallo     = QtCore.pyqtSignal(str)            # avisa si la simulación lanza un error

    def __init__(self, params):
        super().__init__()
        self.p = params

    def run(self):
        try:
            p = self.p
            sim.N_LUGARES = p["n_lugares"]
            sim.MEDIA_LLEGADA = p["media"] / 60.0
            sim.T_EULER = p["T"]; sim.H_EULER = p["h"]
            sim.PRECIO = {"Pequeño": p["pp"], "Grande": p["pg"], "Utilitario": p["pu"]}
            sim.PROB_TIPO = p["prob_tipo"]
            sim.PROB_HORAS = p["prob_horas"]
            sim.resetear_estado()
            filas = sim.simular(p["tmax"])
            t_real = filas[-1]["reloj"] if filas else p["tmax"]
            stats = sim.estadisticas(t_real)
            self.terminado.emit(filas, stats, list(sim.tablas_euler))
        except Exception as e:                    # el motor valida y puede lanzar ValueError
            self.fallo.emit(str(e))


# ── Ventana principal ───────────────────────────────────────────────────────────
class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TP5 — Simulación: Playa de Estacionamiento (Grupo 13)")
        self.resize(1340, 800)
        self._todas = []
        self._N = 8
        self.euler_detalle = {}  
        self.euler_lbl = {}
        self.euler_fila_resumen = {}  

        central = QtWidgets.QWidget(); self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)
        v.addWidget(self._panel_parametros())

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.tabBar().setElideMode(Qt.ElideNone)
        self.tabs.setUsesScrollButtons(False)
        v.addWidget(self.tabs, 1)

        # Vector de estado
        self.modelo = TablaModel(construir_columnas(8))
        self.tabla = VectorView(self.modelo)
        self.tabla.clicked.connect(self.on_celda_click)
        self.tabs.addTab(self._tab_vector(), "Vector de Estado")

        # Auditoría Euler
        self.tabs.addTab(self._tab_euler(), "Auditoría Euler")

        self.lbl_stats = QtWidgets.QLabel("Listo para simular.")
        self.lbl_stats.setStyleSheet("font-size:14px;padding:6px;")
        self.lbl_stats.setAlignment(Qt.AlignCenter)
        v.addWidget(self.lbl_stats)

        # sin grilla interna: solo el borde de cada tabla
        for t in self.findChildren(QtWidgets.QTableView):
            t.setShowGrid(False)

    # ---- paneles ----
    def _panel_parametros(self):
        box = QtWidgets.QGroupBox("Parámetros")
        g = QtWidgets.QGridLayout(box)
        self.inp = {}

        def campo(col, fila, etiqueta, clave, valor):
            g.addWidget(QtWidgets.QLabel(etiqueta), fila, col * 2)
            e = QtWidgets.QLineEdit(str(valor)); e.setFixedWidth(64)
            g.addWidget(e, fila, col * 2 + 1); self.inp[clave] = e

        campo(0, 0, "Lugares (N)", "n_lugares", 8)
        campo(0, 1, "Media lleg. (min)", "media", 13)
        campo(0, 2, "Tiempo máx (h)", "tmax", 24)
        campo(0, 3, "T (Euler)", "T", 2)
        campo(1, 0, "h (Euler)", "h", 0.1)
        campo(1, 1, "Precio Pequeño", "pp", 500)
        campo(1, 2, "Precio Grande", "pg", 1500)
        campo(1, 3, "Precio Utilitario", "pu", 3000)
        campo(2, 0, "% Pequeño", "tpp", 45)
        campo(2, 1, "% Grande", "tpg", 25)
        campo(2, 2, "% Utilitario", "tpu", 30)
        campo(3, 0, "% 1 hora", "h1", 50)
        campo(3, 1, "% 2 horas", "h2", 30)
        campo(3, 2, "% 3 horas", "h3", 15)
        campo(3, 3, "% 4 horas", "h4", 5)
        campo(4, 0, "Mostrar desde hora j", "j", 0)
        campo(4, 1, "Cant. filas i", "i", 200)

        self.btn = QtWidgets.QPushButton("▶  Simular")
        self.btn.clicked.connect(self.on_simular)
        g.addWidget(self.btn, 4, 4, 1, 2)
        self.btn_filtro = QtWidgets.QPushButton("Re-aplicar i/j")
        self.btn_filtro.setObjectName("secundario")
        self.btn_filtro.clicked.connect(self.aplicar_filtro)
        g.addWidget(self.btn_filtro, 4, 6)
        self.btn_copiar = QtWidgets.QPushButton("Copiar a Excel")
        self.btn_copiar.setObjectName("secundario")
        self.btn_copiar.clicked.connect(self.on_copiar)
        g.addWidget(self.btn_copiar, 4, 7)
        return box

    def _tab_vector(self):
        w = QtWidgets.QWidget(); lay = QtWidgets.QVBoxLayout(w)
        lay.addWidget(self.tabla, 1)
        lay.addWidget(QtWidgets.QLabel("Última fila (estado final):"))
        self.modelo_ultima = TablaModel(construir_columnas(8))
        self.tabla_ultima = QtWidgets.QTableView()
        self.tabla_ultima.setModel(self.modelo_ultima)
        self.tabla_ultima.setHorizontalHeader(GroupedHeader(self.modelo_ultima, self.tabla_ultima))
        self.tabla_ultima.verticalHeader().hide()
        self.tabla_ultima.setItemDelegate(SepDelegate(self.modelo_ultima, self.tabla_ultima))
        self.tabla_ultima.setFixedHeight(90)
        lay.addWidget(self.tabla_ultima)
        return w

    def _tab_euler(self):
        w = QtWidgets.QWidget(); lay = QtWidgets.QVBoxLayout(w)
        lay.addWidget(QtWidgets.QLabel("Arrastrá la barra del medio para elegir el tamaño de cada tabla:"))
        split = QtWidgets.QSplitter(Qt.Horizontal)
        split.setChildrenCollapsible(False)
        split.setHandleWidth(5)

        # resumen (izquierda)
        pi = QtWidgets.QWidget(); izq = QtWidgets.QVBoxLayout(pi); izq.setContentsMargins(0, 0, 0, 0)
        izq.addWidget(QtWidgets.QLabel("Resumen de integraciones (clic = ir al detalle):"))
        self.modelo_resumen = TablaModel([
            ("", "ID Auto", lambda r: r["aid"]), ("", "Tipo", lambda r: r["tipo"]),
            ("", "D", lambda r: r["umbral"]), ("", "T", lambda r: r["T"]),
            ("", "C", lambda r: r["C"]),
            ("", "t vector (h)", lambda r: r["tvec"]),
        ])
        self.tabla_resumen = QtWidgets.QTableView()
        self.tabla_resumen.setModel(self.modelo_resumen)
        self.tabla_resumen.verticalHeader().hide()
        self.tabla_resumen.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tabla_resumen.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tabla_resumen.clicked.connect(self.on_resumen_click)
        izq.addWidget(self.tabla_resumen)
        split.addWidget(pi)

        # detalle (derecha)
        pd = QtWidgets.QWidget(); der = QtWidgets.QVBoxLayout(pd); der.setContentsMargins(0, 0, 0, 0)
        self.lbl_detalle = QtWidgets.QLabel("Detalle de la integración — (clic en un auto del resumen)")
        der.addWidget(self.lbl_detalle)
        self.modelo_euler = TablaModel([
            ("", "t", lambda r: r["t"]), ("", "D (acumuladora)", lambda r: r["D"]),
            ("", "dD/dt (derivada)", lambda r: r["dD"]),
        ])
        self.tabla_euler = QtWidgets.QTableView()
        self.tabla_euler.setModel(self.modelo_euler)
        self.tabla_euler.verticalHeader().hide()
        self.tabla_euler.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        der.addWidget(self.tabla_euler)
        split.addWidget(pd)

        split.setSizes([520, 900])   # tamaños iniciales (ajustables a mano)
        lay.addWidget(split, 1)
        return w

    # ---- acciones ----
    def _leer(self, clave, tipo):
        try:
            return tipo(self.inp[clave].text().replace(",", "."))
        except ValueError:
            return tipo(0)

    def _num(self, clave, tipo, nombre, errores, minimo=None, estricto=False):
        """Lee un campo y lo valida. Acumula mensajes en `errores`; devuelve None si falla."""
        txt = self.inp[clave].text().strip().replace(",", ".")
        try:
            v = tipo(txt)
        except (ValueError, TypeError):
            errores.append(f"«{nombre}»: «{txt}» no es un número válido.")
            return None
        if minimo is not None:
            if estricto and not v > minimo:
                errores.append(f"«{nombre}»: debe ser mayor que {minimo} (ingresado: {v}).")
                return None
            if not estricto and v < minimo:
                errores.append(f"«{nombre}»: no puede ser menor que {minimo} (ingresado: {v}).")
                return None
        return v

    def _recoger_parametros(self):
        """Lee y valida todos los campos. Devuelve (params, errores)."""
        e = []
        n     = self._num("n_lugares", int,   "Lugares (N)",        e, minimo=1)
        media = self._num("media",     float, "Media lleg. (min)",  e, minimo=0, estricto=True)
        tmax  = self._num("tmax",      float, "Tiempo máx (h)",     e, minimo=0, estricto=True)
        T     = self._num("T",         float, "T (Euler)",          e)
        h     = self._num("h",         float, "h (Euler)",          e, minimo=0, estricto=True)
        pp    = self._num("pp",        int,   "Precio Pequeño",     e, minimo=0)
        pg    = self._num("pg",        int,   "Precio Grande",      e, minimo=0)
        pu    = self._num("pu",        int,   "Precio Utilitario",  e, minimo=0)
        tpp   = self._num("tpp",       float, "% Pequeño",          e, minimo=0)
        tpg   = self._num("tpg",       float, "% Grande",           e, minimo=0)
        tpu   = self._num("tpu",       float, "% Utilitario",       e, minimo=0)
        h1    = self._num("h1",        float, "% 1 hora",           e, minimo=0)
        h2    = self._num("h2",        float, "% 2 horas",          e, minimo=0)
        h3    = self._num("h3",        float, "% 3 horas",          e, minimo=0)
        h4    = self._num("h4",        float, "% 4 horas",          e, minimo=0)
        j     = self._num("j",         float, "Mostrar desde hora", e, minimo=0)
        i     = self._num("i",         int,   "Cant. filas",        e, minimo=0)

        # sumas de porcentajes (solo si todos sus campos son válidos)
        if None not in (tpp, tpg, tpu) and abs((tpp + tpg + tpu) - 100) > 0.5:
            e.append(f"Los % de tipo de auto deben sumar 100 (suman {tpp + tpg + tpu:.0f}).")
        if None not in (h1, h2, h3, h4) and abs((h1 + h2 + h3 + h4) - 100) > 0.5:
            e.append(f"Los % de horas deben sumar 100 (suman {h1 + h2 + h3 + h4:.0f}).")

        if e:
            return None, e
        params = {
            "n_lugares": n, "media": media, "tmax": tmax, "T": T, "h": h,
            "pp": pp, "pg": pg, "pu": pu, "j": j, "i": i,
            "prob_tipo":  {"Pequeño": tpp / 100, "Grande": tpg / 100, "Utilitario": tpu / 100},
            "prob_horas": {1: h1 / 100, 2: h2 / 100, 3: h3 / 100, 4: h4 / 100},
        }
        return params, []

    def on_simular(self):
        params, errores = self._recoger_parametros()
        if errores:
            QtWidgets.QMessageBox.warning(
                self, "Revisá los parámetros",
                "No se puede simular por estos motivos:\n\n• " + "\n• ".join(errores))
            self.lbl_stats.setText("Corregí los parámetros marcados y volvé a simular.")
            return

        self._N = params["n_lugares"]
        self.btn.setEnabled(False)
        self.lbl_stats.setText("⏳ Simulando…")
        self.worker = SimWorker(params)
        self.worker.terminado.connect(self.on_listo)
        self.worker.fallo.connect(self.on_fallo)
        self.worker.start()

    def on_fallo(self, mensaje):
        QtWidgets.QMessageBox.critical(self, "No se pudo completar la simulación", mensaje)
        self.lbl_stats.setText("La simulación se detuvo por un error. Revisá los parámetros.")
        self.btn.setEnabled(True)

    def on_listo(self, filas, stats, tablas_euler):
        self._todas = filas
        self.aplicar_filtro()
        if filas:
            self.modelo_ultima.set_contenido(construir_columnas(self._N, autos_en([filas[-1]])), [filas[-1]])
        # auditoría Euler: resumen + detalle, con índice de salto
        self.euler_detalle, self.euler_lbl, self.euler_fila_resumen, filas_r = {}, {}, {}, []
        for aid, tipo, C, T, h, umbral, tabla in tablas_euler:
            self.euler_detalle[aid] = [{"it": k, "t": round(t, 4), "D": round(D, 4), "dD": round(dD, 4)}
                                       for k, (t, D, dD) in enumerate(tabla, 1)]
            tmin = round(tabla[-1][0], 4)
            self.euler_lbl[aid] = f"Cobro a{aid} ({tipo}, C={C}, umbral D={umbral}, t={tmin} min)"
            self.euler_fila_resumen[aid] = len(filas_r)   # posición de este auto en el resumen
            filas_r.append({"aid": aid, "tipo": tipo, "umbral": umbral, "T": T, "C": C,
                            "tmin": tmin, "tvec": round(tmin / 60, 4)})
        self.modelo_resumen.set_filas(filas_r)
        self.modelo_euler.set_filas([])   # detalle vacío hasta que elijas un auto
        self.lbl_detalle.setText("Detalle de la integración — (clic en un auto del resumen)")
        self.lbl_stats.setText(
            f"<b>Recaudación:</b> ${stats['recaudacion']:.0f}   |   "
            f"<b>% Utilización:</b> {stats['pct_utilizacion']:.2f}%   |   "
            f"Filas: {len(filas)}   |   Integraciones Euler: {len(tablas_euler)}")
        self.btn.setEnabled(True)

    def aplicar_filtro(self):
        if not self._todas:
            return
        j = self._leer("j", float); i = self._leer("i", int)
        vis = [f for f in self._todas if f["reloj"] >= j]
        if i > 0:
            vis = vis[:i]
        self.modelo.set_contenido(construir_columnas(self._N, autos_en(vis)), vis)

    def on_celda_click(self, index):
        # clic en la columna "T. Cobro (h)" → saltar a esa integración en Euler
        if self.modelo._cols[index.column()][1] != "T. Cobro (h)":
            return
        aid = self.modelo._rows[index.row()].get("cobro_auto")
        self._ir_a_euler(aid)

    def on_resumen_click(self, index):
        fila = self.modelo_resumen._rows[index.row()]
        self._ir_a_euler(fila["aid"])

    def _ir_a_euler(self, aid):
        if aid is None or aid not in self.euler_detalle:
            return
        # la tabla de detalle muestra SOLO la integración de este auto (dinámica)
        self.modelo_euler.set_filas(self.euler_detalle[aid])
        self.lbl_detalle.setText("Detalle de la integración — " + self.euler_lbl[aid])
        self.tabs.setCurrentIndex(1)
        last = self.modelo_euler.rowCount() - 1   # última fila = el cruce (t = tiempo de cobro)
        if last >= 0:
            self.tabla_euler.scrollTo(self.modelo_euler.index(last, 0),
                                      QtWidgets.QAbstractItemView.PositionAtCenter)
            self.tabla_euler.selectRow(last)
        # resaltar también la fila correspondiente en el resumen
        fr = self.euler_fila_resumen.get(aid)
        if fr is not None:
            self.tabla_resumen.selectRow(fr)
            self.tabla_resumen.scrollTo(self.modelo_resumen.index(fr, 0),
                                        QtWidgets.QAbstractItemView.PositionAtCenter)

    def on_copiar(self):
        cols = self.modelo._cols
        lineas = ["\t".join(c[1] for c in cols)]
        for r in self.modelo._rows:
            lineas.append("\t".join(fmt(c[2](r)) for c in cols))
        QtWidgets.QApplication.clipboard().setText("\n".join(lineas))
        self.lbl_stats.setText("Copiado al portapapeles (pegar en Excel).")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(WHITE)
    win = Main(); win.show()
    sys.exit(app.exec_())
