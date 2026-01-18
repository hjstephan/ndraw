import sys
import json
import math
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
                             QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox, 
                             QFileDialog, QInputDialog, QStatusBar)  # QStatusBar hinzufügen
from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF, QFont, QIcon, QPixmap

class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, node_id, label=None):
        super().__init__(-20, -20, 40, 40)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#ffffff")))
        self.setPen(QPen(QColor("#2c3e50"), 2))
        self.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges |
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
        self.node_id = node_id
        self.lines = []
        self.is_editing = False
        
        self.label_text = label if label is not None else str(node_id)
        self.label = QGraphicsTextItem(self.label_text, self)
        self.label.setDefaultTextColor(QColor("#2c3e50"))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.label.setFont(font)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction) 
        self.label.setTabChangesFocus(True) 
        self.update_label_position()

    def update_label_position(self):
        br = self.label.boundingRect()
        self.label.setPos(-br.width()/2, -br.height()/2)
    
    def set_label(self, text):
        self.label_text = text
        self.label.setPlainText(text)
        self.update_label_position()
    
    def set_editing_mode(self, editing):
        self.is_editing = editing
        if editing:
            self.setBrush(QBrush(QColor("#ff9500")))
            self.setPen(QPen(QColor("#ff6600"), 3))
        else:
            self.update_selection_style()
    
    def update_selection_style(self):
        if self.is_editing:
            return
        
        if self.isSelected():
            self.setBrush(QBrush(QColor("#e3f2fd")))
            self.setPen(QPen(QColor("#2196f3"), 3))
        else:
            self.setBrush(QBrush(QColor("#ffffff")))
            self.setPen(QPen(QColor("#2c3e50"), 2))

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.GraphicsItemChange.ItemPositionChange:
            for line in self.lines:
                line.update_position()
        elif change == QGraphicsEllipseItem.GraphicsItemChange.ItemSelectedChange:
            self.update_selection_style()
        return super().itemChange(change, value)

class DirectedEdge(QGraphicsLineItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable)
        self.arrow_size = 12
        self.node_radius = 20
        self.update_position()

    def update_position(self):
        raw_line = QLineF(self.source.pos(), self.target.pos())
        length = raw_line.length()
        if length > self.node_radius * 2:
            shorten_factor = self.node_radius / length
            p1 = raw_line.pointAt(shorten_factor)
            p2 = raw_line.pointAt(1.0 - shorten_factor)
            self.setLine(QLineF(p1, p2))
        else:
            self.setLine(QLineF(self.source.pos(), self.source.pos()))
    
    def update_selection_style(self):
        if self.isSelected():
            self.setPen(QPen(QColor("#2196f3"), 4))
        else:
            self.setPen(QPen(Qt.GlobalColor.black, 2))

    def itemChange(self, change, value):
        if change == QGraphicsLineItem.GraphicsItemChange.ItemSelectedChange:
            self.update_selection_style()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        line = self.line()
        if line.length() < 1: return
        painter.setPen(self.pen())
        painter.drawLine(line)
        angle = math.atan2(-line.dy(), line.dx())
        arrow_p1 = line.p2() - QPointF(math.cos(angle + math.pi/8) * self.arrow_size, -math.sin(angle + math.pi/8) * self.arrow_size)
        arrow_p2 = line.p2() - QPointF(math.cos(angle - math.pi/8) * self.arrow_size, -math.sin(angle - math.pi/8) * self.arrow_size)
        
        if self.isSelected():
            painter.setBrush(QBrush(QColor("#2196f3")))
        else:
            painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF([line.p2(), arrow_p1, arrow_p2]))

class NetworkCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(-5000, -5000, 10000, 10000)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.nodes = []
        self.edges = []
        self.connection_source = None
        
        self.zoom_factor = 1.0
        self.zoom_step = 1.15
        self.min_zoom = 0.1
        self.max_zoom = 10.0

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), Node):
            item = item.parentItem()
            
        if event.button() == Qt.MouseButton.LeftButton:
            if not item:
                pos = self.mapToScene(event.pos())
                self.add_new_node(pos.x(), pos.y(), len(self.nodes))
            else:
                super().mousePressEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            if isinstance(item, Node):
                if not self.connection_source:
                    self.connection_source = item
                    item.setBrush(QBrush(QColor("#e74c3c")))
                else:
                    if item != self.connection_source:
                        self.add_new_edge(self.connection_source, item)
                    self.connection_source.update_selection_style()
                    self.connection_source = None
            else:
                # BUGFIX: Rechtsklick außerhalb eines Knotens bricht Verbindung ab
                if self.connection_source:
                    self.connection_source.update_selection_style()
                    self.connection_source = None
        elif event.button() == Qt.MouseButton.MiddleButton:
            if isinstance(item, Node):
                self.edit_node_label(item)

    def edit_node_label(self, node):
        label = node.label
        node.set_editing_mode(True)
        
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        label.setFocus()
        
        cursor = label.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        label.setTextCursor(cursor)
        label.focusOutEvent = lambda event: self.finish_label_edit(node, event)
    
    def finish_label_edit(self, node, event):
        QGraphicsTextItem.focusOutEvent(node.label, event)
        
        node.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        node.label_text = node.label.toPlainText()
        node.update_label_position()
        node.set_editing_mode(False)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F2:
            pos = self.mapFromGlobal(self.cursor().pos())
            item = self.itemAt(pos)
            
            if isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), Node):
                item = item.parentItem()
            
            if isinstance(item, Node):
                self.edit_node_label(item)
        elif event.key() == Qt.Key.Key_Delete:
            self.delete_selected_items()
        elif event.key() == Qt.Key.Key_Escape:
            # BUGFIX: ESC bricht Verbindungsvorgang ab
            if self.connection_source:
                self.connection_source.update_selection_style()
                self.connection_source = None
        else:
            super().keyPressEvent(event)
    
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            zoom_change = self.zoom_step
        else:
            zoom_change = 1 / self.zoom_step
        
        new_zoom = self.zoom_factor * zoom_change
        
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        
        old_pos = self.mapToScene(event.position().toPoint())
        self.scale(zoom_change, zoom_change)
        self.zoom_factor = new_zoom
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
    
    def delete_selected_items(self):
        selected_items = self.scene.selectedItems()
        
        for item in selected_items:
            if isinstance(item, DirectedEdge):
                self.remove_edge(item)
        
        for item in selected_items:
            if isinstance(item, Node):
                self.remove_node(item)
    
    def remove_node(self, node):
        """BUGFIX: Prüfe ob Knoten als connection_source verwendet wird"""
        # Brich Verbindungsvorgang ab, falls dieser Knoten beteiligt ist
        if self.connection_source == node:
            self.connection_source = None
        
        # Entferne alle Kanten, die mit diesem Knoten verbunden sind
        edges_to_remove = [edge for edge in self.edges if edge.source == node or edge.target == node]
        for edge in edges_to_remove:
            self.remove_edge(edge)
        
        # Entferne den Knoten
        self.scene.removeItem(node)
        if node in self.nodes:
            self.nodes.remove(node)
    
    def remove_edge(self, edge):
        if edge in edge.source.lines:
            edge.source.lines.remove(edge)
        if edge in edge.target.lines:
            edge.target.lines.remove(edge)
        
        self.scene.removeItem(edge)
        if edge in self.edges:
            self.edges.remove(edge)

    def add_new_node(self, x, y, node_id, label=None):
        node = Node(x, y, node_id, label)
        self.scene.addItem(node)
        self.nodes.append(node)
        return node

    def add_new_edge(self, source, target):
        """BUGFIX: Validiere dass beide Knoten noch existieren"""
        if source not in self.nodes or target not in self.nodes:
            return None
            
        edge = DirectedEdge(source, target)
        self.scene.addItem(edge)
        self.edges.append(edge)
        source.lines.append(edge)
        target.lines.append(edge)
        return edge

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Network Designer Pro")
        self.resize(1000, 800)
        
        self.canvas = NetworkCanvas()
        
        # Statusleiste erstellen
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: palette(window);
                color: palette(text);
                border-top: 1px solid palette(mid);
                padding: 4px;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.show_status("Bereit", success=True)
        
        layout = QVBoxLayout()
        toolbar = QHBoxLayout()
        
        btn_load = QPushButton("JSON Laden")
        btn_load.clicked.connect(self.load_json)
        btn_save = QPushButton("JSON Speichern")
        btn_save.clicked.connect(self.save_json)
        btn_svg = QPushButton("SVG Export")
        btn_svg.clicked.connect(self.export_svg)
        
        toolbar.addWidget(btn_load)
        toolbar.addWidget(btn_save)
        toolbar.addWidget(btn_svg)
        
        layout.addLayout(toolbar)
        layout.addWidget(self.canvas)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def set_app_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QBrush(QColor("#2c3e50")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(2, 2, 60, 60, 8, 8)
        
        node_positions = [(20, 20), (44, 20), (32, 40)]
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#3498db"), 2))
        for x, y in node_positions:
            painter.drawEllipse(x-6, y-6, 12, 12)
        
        painter.setPen(QPen(QColor("#3498db"), 2))
        painter.drawLine(20, 20, 44, 20)
        painter.drawLine(20, 20, 32, 40)
        painter.drawLine(44, 20, 32, 40)
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.setWindowIcon(icon)
        
        try:
            pixmap.save("ndraw_icon.png")
        except:
            pass
    
    def show_status(self, message, success=True, duration=5000):
        """Zeigt eine Statusmeldung an."""
        if success:
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: palette(window);
                    color: #2e7d32;
                    border-top: 1px solid palette(mid);
                    padding: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: palette(window);
                    color: #c62828;
                    border-top: 1px solid palette(mid);
                    padding: 4px;
                    font-weight: bold;
                }
            """)
        self.status_bar.showMessage(message, duration)

    def is_connected(self):
        if not self.canvas.nodes: return True
        adj = {n: [] for n in self.canvas.nodes}
        for e in self.canvas.edges:
            adj[e.source].append(e.target)
            adj[e.target].append(e.source)
        visited = set()
        stack = [self.canvas.nodes[0]]
        while stack:
            n = stack.pop()
            if n not in visited:
                visited.add(n)
                stack.extend(adj[n])
        return len(visited) == len(self.canvas.nodes)

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "JSON Laden", "", "JSON Files (*.json)")
        if not path: return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.canvas.scene.clear()
            self.canvas.nodes = []
            self.canvas.edges = []
            # BUGFIX: Reset connection_source beim Laden
            self.canvas.connection_source = None
            
            node_map = {}
            for n_data in data["nodes"]:
                label = n_data.get("label", str(n_data["id"]))
                node = self.canvas.add_new_node(n_data["x"], n_data["y"], n_data["id"], label)
                node_map[n_data["id"]] = node
            for e_data in data["edges"]:
                self.canvas.add_new_edge(node_map[e_data["from"]], node_map[e_data["to"]])
            self.show_status(f"✓ Geladen: {Path(path).name}", success=True)
        except Exception as e:
            self.show_status(f"❌ Fehler beim Laden: {str(e)[:50]}", success=False, duration=8000)

    def save_json(self):
        if not self.is_connected():
            self.show_status("❌ Netzwerk nicht zusammenhängend", success=False, duration=6000)
            return
        path, _ = QFileDialog.getSaveFileName(self, "JSON Speichern", "", "JSON Files (*.json)")
        if path:
            data = {
                "nodes": [{"id": n.node_id, "x": n.pos().x(), "y": n.pos().y(), "label": n.label_text} 
                         for n in self.canvas.nodes],
                "edges": [{"from": e.source.node_id, "to": e.target.node_id} 
                         for e in self.canvas.edges]
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            self.show_status(f"✓ Gespeichert: {Path(path).name}", success=True)

    def export_svg(self):
        if not self.canvas.nodes: 
            self.show_status("❌ Kein Netzwerk vorhanden", success=False)
            return
        if not self.is_connected():
            self.show_status("❌ Netzwerk nicht zusammenhängend", success=False, duration=6000)
            return

        xs = [n.pos().x() for n in self.canvas.nodes]
        ys = [n.pos().y() for n in self.canvas.nodes]
        padding = 30
        min_x, max_x = min(xs) - padding, max(xs) + padding
        min_y, max_y = min(ys) - padding, max(ys) + padding
        width = max_x - min_x
        height = max_y - min_y

        path, _ = QFileDialog.getSaveFileName(self, "SVG Export", "", "SVG Files (*.svg)")
        if path:
            with open(path, "w") as f:
                f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{min_x} {min_y} {width} {height}">\n')
                f.write('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="black" /></marker></defs>\n')
                
                for e in self.canvas.edges:
                    line = QLineF(e.source.pos(), e.target.pos())
                    l = line.length()
                    if l > 40:
                        p1, p2 = line.pointAt(20/l), line.pointAt(1-20/l)
                        f.write(f'  <line x1="{p1.x()}" y1="{p1.y()}" x2="{p2.x()}" y2="{p2.y()}" stroke="black" stroke-width="2" marker-end="url(#arrow)" />\n')
                
                for n in self.canvas.nodes:
                    f.write(f'  <circle cx="{n.pos().x()}" cy="{n.pos().y()}" r="20" fill="#ffffff" stroke="#2c3e50" stroke-width="2" />\n')
                    f.write(f'  <text x="{n.pos().x()}" y="{n.pos().y()}" font-family="Arial" font-size="10" font-weight="bold" text-anchor="middle" fill="#2c3e50" dy=".35em">{n.label_text}</text>\n')
                
                f.write('</svg>')
            self.show_status(f"✓ SVG exportiert: {Path(path).name}", success=True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    icon_paths = [
        Path.home() / ".local/share/icons/ndraw_icon.png",
        Path(__file__).parent / "ndraw_icon.png",
        Path(__file__).parent.parent / "ndraw_icon.png",
        Path("ndraw_icon.png"),
    ]
    
    icon_loaded = False
    for icon_path in icon_paths:
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            icon_loaded = True
            break
    
    if not icon_loaded:
        print("Hinweis: Icon nicht gefunden. Bitte führe 'python3 generate_icon.py' aus.")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())