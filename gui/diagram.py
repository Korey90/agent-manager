"""DiagramPanel — dependency & workflow visualization for agents."""
from __future__ import annotations
import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QPainter, QPen, QPainterPath, QWheelEvent,
)
from PyQt6.QtWidgets import (
    QButtonGroup, QFrame, QGraphicsPathItem, QGraphicsScene,
    QGraphicsTextItem, QGraphicsView, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
    QSplitter, QVBoxLayout, QWidget,
)


# ── Zoomable view ─────────────────────────────────────────────────────────────

class _ZoomView(QGraphicsView):
    """QGraphicsView with Ctrl+Wheel zoom and middle-button pan."""
    _ZOOM_STEP = 1.15
    _ZOOM_MIN  = 0.1
    _ZOOM_MAX  = 8.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1.0
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    # zoom with mouse wheel (no modifier needed)
    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        if delta == 0:
            super().wheelEvent(event)
            return
        factor = self._ZOOM_STEP if delta > 0 else 1.0 / self._ZOOM_STEP
        new_zoom = self._zoom * factor
        if self._ZOOM_MIN <= new_zoom <= self._ZOOM_MAX:
            self._zoom = new_zoom
            self.scale(factor, factor)

    def zoom_in(self):
        factor = self._ZOOM_STEP
        if self._zoom * factor <= self._ZOOM_MAX:
            self._zoom *= factor
            self.scale(factor, factor)

    def zoom_out(self):
        factor = 1.0 / self._ZOOM_STEP
        if self._zoom * factor >= self._ZOOM_MIN:
            self._zoom *= factor
            self.scale(factor, factor)

    def zoom_reset(self):
        self.resetTransform()
        self._zoom = 1.0
        if self.scene():
            self.fitInView(self.scene().sceneRect(),
                           Qt.AspectRatioMode.KeepAspectRatio)

# ── Color palette ─────────────────────────────────────────────────────────────
_P = {
    "agent":       ("#0063B1", "#DDEEFF"),
    "skill":       ("#107C10", "#DFF0D8"),
    "hook_pre":    ("#C55A00", "#FFF0E0"),
    "hook_post":   ("#881798", "#F4E6FF"),
    "instruction": ("#006B6B", "#D6F5F5"),
}
_NW, _NH = 210, 44
_ROW_H = 90          # row pitch when subtitle is shown
_HGAP, _VGAP = 310, 95


# ── Low-level drawing primitives ──────────────────────────────────────────────

def _trunc(s: str, n: int = 55) -> str:
    """Truncate string to n chars, appending ellipsis if needed."""
    s = (s or "").strip()
    return (s[:n] + "\u2026") if len(s) > n else s


def _node(scene: QGraphicsScene, label: str, kind: str,
          cx: float, cy: float, w: float = _NW, h: float | None = None,
          subtitle: str = "") -> dict:
    """Rounded-rectangle node; subtitle shown below name in smaller italic text."""
    border, fill = _P.get(kind, ("#555", "#EEE"))

    name_font = QFont("Segoe UI", 10 if kind == "agent" else 9)
    if kind == "agent":
        name_font.setBold(True)

    ti = QGraphicsTextItem(label)
    ti.setFont(name_font)
    ti.setTextWidth(w - 16)
    name_h = ti.boundingRect().height()

    sub_h = 0.0
    si = None
    if subtitle:
        sub_font = QFont("Segoe UI", 8)
        sub_font.setItalic(True)
        si = QGraphicsTextItem(subtitle)
        si.setFont(sub_font)
        si.setTextWidth(w - 16)
        sub_h = si.boundingRect().height()

    if h is None:
        h = max(_NH, int(name_h + sub_h + 14))

    path = QPainterPath()
    path.addRoundedRect(cx - w / 2, cy - h / 2, w, h, 10, 10)
    pi = QGraphicsPathItem(path)
    pi.setPen(QPen(QColor(border), 3 if kind == "agent" else 2))
    pi.setBrush(QBrush(QColor(fill)))
    scene.addItem(pi)

    total_text_h = name_h + sub_h
    text_top = cy - total_text_h / 2

    ti.setDefaultTextColor(QColor("#111"))
    ti.setPos(cx - w / 2 + 8, text_top)
    scene.addItem(ti)

    if si:
        si.setDefaultTextColor(QColor("#555"))
        si.setPos(cx - w / 2 + 8, text_top + name_h)
        scene.addItem(si)

    return dict(cx=cx, cy=cy, w=w, h=h)


def _oval(scene: QGraphicsScene, label: str, cx: float, cy: float) -> dict:
    w, h = 110, 36
    path = QPainterPath()
    path.addEllipse(cx - w / 2, cy - h / 2, w, h)
    pi = QGraphicsPathItem(path)
    pi.setPen(QPen(QColor("#444"), 2))
    pi.setBrush(QBrush(QColor("#F0F0F0")))
    scene.addItem(pi)
    ti = QGraphicsTextItem(label)
    ti.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    ti.setDefaultTextColor(QColor("#333"))
    bw = ti.boundingRect().width()
    bh = ti.boundingRect().height()
    ti.setPos(cx - bw / 2, cy - bh / 2)
    scene.addItem(ti)
    return dict(cx=cx, cy=cy, w=w, h=h)


def _arrow(scene: QGraphicsScene, a: dict, b: dict, color: str = "#888"):
    """Straight arrow (with filled arrowhead) from bottom of a to top of b."""
    x1, y1 = a["cx"], a["cy"] + a["h"] / 2
    x2, y2 = b["cx"], b["cy"] - b["h"] / 2
    scene.addLine(x1, y1, x2, y2, QPen(QColor(color), 1.8))
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 10
    p1 = QPointF(x2 - L * math.cos(ang - 0.4), y2 - L * math.sin(ang - 0.4))
    p2 = QPointF(x2 - L * math.cos(ang + 0.4), y2 - L * math.sin(ang + 0.4))
    ap = QPainterPath()
    ap.moveTo(x2, y2); ap.lineTo(p1); ap.lineTo(p2); ap.closeSubpath()
    scene.addPath(ap, QPen(Qt.PenStyle.NoPen), QBrush(QColor(color)))


def _arrow_h(scene: QGraphicsScene, a: dict, b: dict, color: str = "#888"):
    """L-shaped elbow arrow: exits a's left/right edge, arrives at b's opposite edge."""
    if b["cx"] < a["cx"]:
        x1 = a["cx"] - a["w"] / 2
        x2 = b["cx"] + b["w"] / 2
        dx = -1
    else:
        x1 = a["cx"] + a["w"] / 2
        x2 = b["cx"] - b["w"] / 2
        dx = 1
    y1, y2 = a["cy"], b["cy"]
    mx = (x1 + x2) / 2

    path = QPainterPath()
    path.moveTo(x1, y1)
    path.lineTo(mx, y1)
    path.lineTo(mx, y2)
    path.lineTo(x2, y2)
    pi = QGraphicsPathItem(path)
    pi.setPen(QPen(QColor(color), 1.8))
    scene.addItem(pi)

    L = 10
    p1 = QPointF(x2 - dx * L * math.cos(0.4), y2 - L * math.sin(0.4))
    p2 = QPointF(x2 - dx * L * math.cos(0.4), y2 + L * math.sin(0.4))
    ap = QPainterPath()
    ap.moveTo(x2, y2); ap.lineTo(p1); ap.lineTo(p2); ap.closeSubpath()
    scene.addPath(ap, QPen(Qt.PenStyle.NoPen), QBrush(QColor(color)))


def _dashed_arrow(scene: QGraphicsScene, a: dict, b: dict, color: str = "#006B6B"):
    """Vertical dashed arrow with arrowhead — agent → instruction (below)."""
    x1, y1 = a["cx"], a["cy"] + a["h"] / 2
    x2, y2 = b["cx"], b["cy"] - b["h"] / 2
    ang = math.atan2(y2 - y1, x2 - x1)
    pen = QPen(QColor(color), 1.5, Qt.PenStyle.DashLine)
    scene.addLine(x1, y1, x2, y2, pen)
    L = 10
    p1 = QPointF(x2 - L * math.cos(ang - 0.4), y2 - L * math.sin(ang - 0.4))
    p2 = QPointF(x2 - L * math.cos(ang + 0.4), y2 - L * math.sin(ang + 0.4))
    ap = QPainterPath()
    ap.moveTo(x2, y2); ap.lineTo(p1); ap.lineTo(p2); ap.closeSubpath()
    scene.addPath(ap, QPen(Qt.PenStyle.NoPen), QBrush(QColor(color)))


def _dashed_arrow_h(scene: QGraphicsScene, a: dict, b: dict, color: str = "#006B6B"):
    """Horizontal dashed L-arrow with arrowhead — agent → instruction (side)."""
    if b["cx"] < a["cx"]:
        x1 = a["cx"] - a["w"] / 2
        x2 = b["cx"] + b["w"] / 2
        dx = -1
    else:
        x1 = a["cx"] + a["w"] / 2
        x2 = b["cx"] - b["w"] / 2
        dx = 1
    y1, y2 = a["cy"], b["cy"]
    mx = (x1 + x2) / 2

    path = QPainterPath()
    path.moveTo(x1, y1)
    path.lineTo(mx, y1)
    path.lineTo(mx, y2)
    path.lineTo(x2, y2)
    pi = QGraphicsPathItem(path)
    pi.setPen(QPen(QColor(color), 1.5, Qt.PenStyle.DashLine))
    scene.addItem(pi)

    L = 10
    p1 = QPointF(x2 - dx * L * math.cos(0.4), y2 - L * math.sin(0.4))
    p2 = QPointF(x2 - dx * L * math.cos(0.4), y2 + L * math.sin(0.4))
    ap = QPainterPath()
    ap.moveTo(x2, y2); ap.lineTo(p1); ap.lineTo(p2); ap.closeSubpath()
    scene.addPath(ap, QPen(Qt.PenStyle.NoPen), QBrush(QColor(color)))


def _xs(n: int, gap: float = _HGAP) -> list[float]:
    """Return n x-positions centered around 0."""
    if n == 1:
        return [0.0]
    total = (n - 1) * gap
    return [-total / 2 + i * gap for i in range(n)]


def _ev(hook) -> str:
    ev = getattr(hook, "event", None)
    if ev is None:
        return ""
    return ev.value if hasattr(ev, "value") else str(ev)


# ── Dependency diagram ────────────────────────────────────────────────────────

def build_dependency(agent, skills: list, hooks: list,
                     instructions: list = ()) -> QGraphicsScene:
    """Star diagram: agent centre, skills left column (L-arrows), hooks right column."""
    scene = QGraphicsScene()

    ag_sub = _trunc(agent.role or agent.description, 65)
    ag = _node(scene, agent.name, "agent", 0, 0, w=270, subtitle=ag_sub)

    pre      = [h for h in hooks if _ev(h) in ("pre_run", "on_skill_call", "on_error")]
    post     = [h for h in hooks if h not in pre]
    all_hooks = pre + post

    # Skills — left column, rows centred vertically on agent
    for i, s in enumerate(skills):
        cy  = (i - (len(skills) - 1) / 2) * _ROW_H
        sub = _trunc(s.when_to_use or s.description, 55)
        sn  = _node(scene, s.name, "skill", -_HGAP, cy, subtitle=sub)
        _arrow_h(scene, ag, sn, "#107C10")

    # Hooks — right column
    for i, h in enumerate(all_hooks):
        kind = "hook_pre" if h in pre else "hook_post"
        cy   = (i - (len(all_hooks) - 1) / 2) * _ROW_H
        sub  = _trunc(h.trigger or _ev(h).replace("_", " "), 55)
        hn   = _node(scene, h.name, kind, _HGAP, cy, subtitle=sub)
        _arrow_h(scene, ag, hn, "#C55A00" if kind == "hook_pre" else "#881798")

    # Instructions — bottom row with dashed vertical arrows
    if instructions:
        max_col = max(len(skills), len(all_hooks), 1)
        iy = max_col * _ROW_H / 2 + ag["h"] / 2 + _VGAP
        first_n = None
        for instr, cx in zip(instructions, _xs(len(instructions), gap=235)):
            inst_n = _node(scene, instr.name, "instruction", cx, iy, w=210)
            _dashed_arrow(scene, ag, inst_n)
            if first_n is None:
                first_n = inst_n
        lbl = scene.addText("\u2015 context / instructions")
        lbl.setFont(QFont("Segoe UI", 7))
        lbl.setDefaultTextColor(QColor("#006B6B"))
        lbl_y = iy - (first_n["h"] / 2) - 18  # always above actual node top
        lbl.setPos(-85, lbl_y)

    if not skills and not hooks and not instructions:
        ti = scene.addText("Brak przypisanych skilli, hooków i instrukcji.")
        ti.setFont(QFont("Segoe UI", 10))
        ti.setPos(-170, 70)

    return scene


# ── Workflow diagram ──────────────────────────────────────────────────────────

def build_workflow(agent, skills: list, hooks: list,
                   instructions: list = ()) -> QGraphicsScene:
    """Top-to-bottom flow: start → pre hooks → agent → skills → post hooks → end."""
    scene = QGraphicsScene()

    pre   = [h for h in hooks if _ev(h) == "pre_run"]
    post  = [h for h in hooks if _ev(h) in ("post_run", "on_response")]
    err   = [h for h in hooks if _ev(h) == "on_error"]
    other = [h for h in hooks if h not in pre and h not in post and h not in err]

    y = 0
    start = _oval(scene, "START", 0, y)
    y += _VGAP
    prev_row = [start]

    # ── pre-run hooks ────────────────────────────────────────────────────────
    if pre:
        row = []
        for h, cx in zip(pre, _xs(len(pre), 240)):
            sub = _trunc(h.trigger or _ev(h).replace("_", " "), 45)
            hn = _node(scene, h.name, "hook_pre", cx, y, subtitle=sub)
            for pn in prev_row:
                _arrow(scene, pn, hn, "#C55A00")
            row.append(hn)
        prev_row = row
        y += _VGAP + 15

    # ── agent ────────────────────────────────────────────────────────────────
    ag_sub = _trunc(agent.role or agent.description, 70)
    ag = _node(scene, agent.name, "agent", 0, y, w=290, subtitle=ag_sub)
    for pn in prev_row:
        _arrow(scene, pn, ag, "#0063B1")

    # instructions: sidebar on the left, dashed horizontal L-arrows
    if instructions:
        ix = -(290 / 2 + _HGAP * 0.6)
        for i, instr in enumerate(instructions):
            inst_n = _node(scene, instr.name, "instruction",
                           ix, y + i * _ROW_H, w=210)
            _dashed_arrow_h(scene, ag, inst_n)
        cap = scene.addText("context")
        cap.setFont(QFont("Segoe UI", 7))
        cap.setDefaultTextColor(QColor("#006B6B"))
        cap.setPos(ix - 28, y - 20)

    # on_error hooks: right side, L-shaped
    if err:
        ex = ag["cx"] + ag["w"] / 2 + 80
        for i, h in enumerate(err):
            sub = _trunc(h.trigger or "on error", 45)
            hn  = _node(scene, h.name, "hook_pre", ex, y + i * _ROW_H, subtitle=sub)
            _arrow_h(scene, ag, hn, "#C55A00")

    y += _VGAP + 20

    # ── skills ───────────────────────────────────────────────────────────────
    if skills:
        skill_nodes = []
        for s, cx in zip(skills, _xs(len(skills), 240)):
            sub = _trunc(s.when_to_use or s.description, 50)
            sn  = _node(scene, s.name, "skill", cx, y, subtitle=sub)
            _arrow(scene, ag, sn, "#107C10")
            skill_nodes.append(sn)
        prev_row = skill_nodes
        y += _VGAP + 15
    else:
        prev_row = [ag]

    # ── post-run hooks ───────────────────────────────────────────────────────
    if post:
        post_nodes = []
        for h, cx in zip(post, _xs(len(post), 240)):
            sub = _trunc(h.trigger or _ev(h).replace("_", " "), 45)
            hn  = _node(scene, h.name, "hook_post", cx, y, subtitle=sub)
            for pn in prev_row:
                _arrow(scene, pn, hn, "#881798")
            post_nodes.append(hn)
        prev_row = post_nodes
        y += _VGAP + 15

    # ── other hooks (on_skill_call etc.) ─────────────────────────────────────
    if other:
        other_nodes = []
        for h, cx in zip(other, _xs(len(other), 240)):
            sub = _trunc(h.trigger or _ev(h).replace("_", " "), 45)
            hn  = _node(scene, h.name, "hook_pre", cx, y, subtitle=sub)
            for pn in prev_row:
                _arrow(scene, pn, hn, "#C55A00")
            other_nodes.append(hn)
        prev_row = other_nodes
        y += _VGAP + 15

    end = _oval(scene, "END", 0, y)
    for pn in prev_row:
        _arrow(scene, pn, end, "#444")

    return scene


# ── DiagramPanel widget ───────────────────────────────────────────────────────

class DiagramPanel(QWidget):
    """Tab with agent list on the left and diagram on the right."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_id: str | None = None
        self._mode = "deps"
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: agent list ──────────────────────────────────────────────
        left = QWidget()
        left.setMinimumWidth(180)
        left.setMaximumWidth(260)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(4, 4, 4, 4)
        hdr = QLabel("Agenci")
        hdr.setStyleSheet("font-weight: bold; color: #555; padding: 2px 0;")
        lv.addWidget(hdr)
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_select)
        lv.addWidget(self.list_widget)
        splitter.addWidget(left)

        # ── Right: toolbar + view ─────────────────────────────────────────
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(6, 6, 6, 6)
        rv.setSpacing(4)

        # Toggle buttons
        tb = QHBoxLayout()
        self.btn_deps = QPushButton("🔗  Zależności")
        self.btn_flow = QPushButton("▶  Workflow")
        for btn in (self.btn_deps, self.btn_flow):
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.setStyleSheet(
                "QPushButton { border:1px solid #ccc; padding:2px 18px;"
                "  background:#f5f5f5; border-radius:3px; }"
                "QPushButton:checked { background:#0063B1; color:white;"
                "  border-color:#0063B1; }"
            )
        self.btn_deps.setChecked(True)
        bg = QButtonGroup(self)
        bg.addButton(self.btn_deps)
        bg.addButton(self.btn_flow)
        bg.setExclusive(True)
        self.btn_deps.toggled.connect(
            lambda checked: checked and self._set_mode("deps"))
        self.btn_flow.toggled.connect(
            lambda checked: checked and self._set_mode("workflow"))

        tb.addStretch()
        tb.addWidget(self.btn_deps)
        tb.addWidget(self.btn_flow)
        tb.addStretch()
        rv.addLayout(tb)

        # Info banner
        info = QLabel(
            "<b>Diagram</b> wizualizuje powiązania agenta ze skillami i hookami. "
            "<i>Zależności</i> — widok gwiazdowy (agent w centrum). "
            "<i>Workflow</i> — przepływ: START → pre-hooki → agent → skille → post-hooki → END. "
            "Kółko myszy = zoom &nbsp;·&nbsp; przeciągnij = przesunięcie."
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        info.setStyleSheet(
            "background:#E8F4FD; border-left:4px solid #6CB4E4;"
            " border-radius:3px; padding:5px 10px;"
            " color:#333; font-size:11px;"
        )
        rv.addWidget(info)

        # Inline legend
        leg = QHBoxLayout()
        leg.setSpacing(10)
        for kind, lbl in [
            ("agent",       "Agent"),
            ("skill",       "Skill"),
            ("hook_pre",    "Hook pre/err"),
            ("hook_post",   "Hook post/resp"),
            ("instruction", "Instruction"),
        ]:
            border, fill = _P[kind]
            box = QLabel()
            box.setFixedSize(14, 14)
            box.setStyleSheet(
                f"background:{fill};border:2px solid {border};border-radius:3px;")
            leg.addWidget(box)
            lbl_w = QLabel(lbl)
            lbl_w.setStyleSheet("color:#555; font-size:11px;")
            leg.addWidget(lbl_w)
        leg.addStretch()
        rv.addLayout(leg)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        rv.addWidget(sep)

        # Zoom toolbar
        zoom_row = QHBoxLayout()
        zoom_row.setSpacing(4)
        for icon, tip, slot_name in [
            ("＋", "Powiększ  (kółko myszy)",  "zoom_in"),
            ("−", "Pomniejsz (kółko myszy)",  "zoom_out"),
            ("⊙", "Resetuj zoom",              "zoom_reset"),
        ]:
            btn = QPushButton(icon)
            btn.setFixedSize(28, 28)
            btn.setToolTip(tip)
            btn.setStyleSheet(
                "QPushButton { border:1px solid #ccc; background:#f5f5f5;"
                "  border-radius:3px; font-size:14px; }"
                "QPushButton:hover { background:#e0e0e0; }"
            )
            btn.clicked.connect(lambda _, s=slot_name: getattr(self.view, s)())
            zoom_row.addWidget(btn)
        zoom_row.addStretch()
        zoom_row.addWidget(QLabel(
            '<span style="color:#999;font-size:10px;">'
            'kółko = zoom · przeciągnij = przesuń</span>'))
        rv.addLayout(zoom_row)

        # Graphics view
        self.view = _ZoomView()
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setStyleSheet(
            "background:white; border:1px solid #ddd; border-radius:4px;")
        rv.addWidget(self.view)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        root.addWidget(splitter)

    # ── data ─────────────────────────────────────────────────────────────────

    def refresh(self):
        prev = self._current_id
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        try:
            from gui.state import get_registry
            for agent in get_registry().agents.list():
                item = QListWidgetItem(agent.name)
                item.setData(Qt.ItemDataRole.UserRole, agent.id)
                self.list_widget.addItem(item)
        except Exception:
            pass
        self.list_widget.blockSignals(False)
        if prev:
            for i in range(self.list_widget.count()):
                if self.list_widget.item(i).data(Qt.ItemDataRole.UserRole) == prev:
                    self.list_widget.setCurrentRow(i)
                    return
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_select(self, row: int):
        if row < 0:
            self._current_id = None
            self.view.setScene(QGraphicsScene())
            return
        self._current_id = self.list_widget.item(row).data(Qt.ItemDataRole.UserRole)
        self._render()

    def _set_mode(self, mode: str):
        self._mode = mode
        self._render()

    def _render(self):
        if not self._current_id:
            return
        from gui.state import get_registry
        reg = get_registry()
        agent = reg.agents.get(self._current_id)
        if not agent:
            return
        skills       = [s for sid in agent.skill_ids       if (s := reg.skills.get(sid))]
        hooks        = [h for hid in agent.hook_ids        if (h := reg.hooks.get(hid))]
        instructions = [n for iid in agent.instruction_ids if (n := reg.instructions.get(iid))]
        try:
            scene = (build_dependency(agent, skills, hooks, instructions)
                     if self._mode == "deps"
                     else build_workflow(agent, skills, hooks, instructions))
            self.view.setScene(scene)
            r = scene.itemsBoundingRect()
            if not r.isEmpty():
                r.adjust(-50, -50, 50, 50)
                self.view.fitInView(r, Qt.AspectRatioMode.KeepAspectRatio)
        except Exception as exc:
            err_scene = QGraphicsScene()
            err_scene.addText(f"Błąd renderowania: {exc}")
            self.view.setScene(err_scene)
