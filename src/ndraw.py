import sys
import json
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
                             QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox, 
                             QFileDialog, QInputDialog)
from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF, QFont

class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, node_id, label=None):
        super().__init__(-20, -20, 40, 40)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#ffffff")))  # Weißer Hintergrund
        self.setPen(QPen(QColor("#2c3e50"), 2))
        self.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges |
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)
        self.node_id = node_id
        self.lines = []
        self.is_editing = False
        
        # Label für den Knoten
        self.label_text = label if label is not None else str(node_id)
        self.label = QGraphicsTextItem(self.label_text, self)
        self.label.setDefaultTextColor(QColor("#2c3e50"))  # Dunkler Text für weißen Hintergrund
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.label.setFont(font)

        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction) 
        self.label.setTabChangesFocus(True) 
        self.update_label_position()

    def update_label_position(self):
        """Zentriert das Label im Knoten."""
        br = self.label.boundingRect()
        self.label.setPos(-br.width()/2, -br.height()/2)
    
    def set_label(self, text):
        """Setzt ein neues Label für den Knoten."""
        self.label_text = text
        self.label.setPlainText(text)
        self.update_label_position()
    
    def set_editing_mode(self, editing):
        """Setzt den Bearbeitungsmodus mit oranger Hervorhebung."""
        self.is_editing = editing
        if editing:
            self.setBrush(QBrush(QColor("#ff9500")))  # Orange Hintergrund beim Bearbeiten
            self.setPen(QPen(QColor("#ff6600"), 3))
        else:
            self.update_selection_style()
    
    def update_selection_style(self):
        """Aktualisiert den Stil basierend auf Selektionsstatus."""
        if self.is_editing:
            return  # Bearbeitungsmodus hat Vorrang
        
        if self.isSelected():
            self.setBrush(QBrush(QColor("#e3f2fd")))  # Hellblau wenn selektiert
            self.setPen(QPen(QColor("#2196f3"), 3))
        else:
            self.setBrush(QBrush(QColor("#ffffff")))  # Weiß normal
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
        """Aktualisiert den Stil basierend auf Selektionsstatus."""
        if self.isSelected():
            self.setPen(QPen(QColor("#2196f3"), 4))  # Dick und blau wenn selektiert
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
        
        # Pfeilspitze in gleicher Farbe wie Linie
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

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        # Finde den eigentlichen Node, falls auf Label geklickt wurde
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
        elif event.button() == Qt.MouseButton.MiddleButton:
            # Mittlere Maustaste: Label bearbeiten
            if isinstance(item, Node):
                self.edit_node_label(item)

    def edit_node_label(self, node):
        """Aktiviert den Text-Cursor direkt im Knoten-Label."""
        label = node.label
        node.set_editing_mode(True)
        
        # Aktiviere die Texteingabe
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        label.setFocus()
        
        # Cursor ans Ende setzen
        cursor = label.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        label.setTextCursor(cursor)

        # Wichtig: Wenn das Label den Fokus verliert, speichern wir den Text
        label.focusOutEvent = lambda event: self.finish_label_edit(node, event)
    
    def finish_label_edit(self, node, event):
        """Fixiert den Text und zentriert das Label neu."""
        # Standard-Verhalten für FocusOut aufrufen
        QGraphicsTextItem.focusOutEvent(node.label, event)
        
        # Bearbeitung sperren und neu zentrieren
        node.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        node.label_text = node.label.toPlainText()
        node.update_label_position()
        node.set_editing_mode(False)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F2:
            # Sucht das Item direkt unter dem Mauszeiger
            pos = self.mapFromGlobal(self.cursor().pos())
            item = self.itemAt(pos)
            
            if isinstance(item, QGraphicsTextItem) and isinstance(item.parentItem(), Node):
                item = item.parentItem()
            
            if isinstance(item, Node):
                self.edit_node_label(item)
        elif event.key() == Qt.Key.Key_Delete:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)
    
    def delete_selected_items(self):
        """Löscht alle selektierten Items (Knoten und Kanten)."""
        selected_items = self.scene.selectedItems()
        
        # Erst Kanten löschen
        for item in selected_items:
            if isinstance(item, DirectedEdge):
                self.remove_edge(item)
        
        # Dann Knoten löschen
        for item in selected_items:
            if isinstance(item, Node):
                self.remove_node(item)
    
    def remove_node(self, node):
        """Entfernt einen Knoten und alle verbundenen Kanten."""
        # Entferne alle Kanten, die mit diesem Knoten verbunden sind
        edges_to_remove = [edge for edge in self.edges if edge.source == node or edge.target == node]
        for edge in edges_to_remove:
            self.remove_edge(edge)
        
        # Entferne den Knoten
        self.scene.removeItem(node)
        if node in self.nodes:
            self.nodes.remove(node)
    
    def remove_edge(self, edge):
        """Entfernt eine Kante."""
        # Entferne Referenzen in den Knoten
        if edge in edge.source.lines:
            edge.source.lines.remove(edge)
        if edge in edge.target.lines:
            edge.target.lines.remove(edge)
        
        # Entferne die Kante aus der Scene und Liste
        self.scene.removeItem(edge)
        if edge in self.edges:
            self.edges.remove(edge)

    def add_new_node(self, x, y, node_id, label=None):
        node = Node(x, y, node_id, label)
        self.scene.addItem(node)
        self.nodes.append(node)
        return node

    def add_new_edge(self, source, target):
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
            node_map = {}
            for n_data in data["nodes"]:
                label = n_data.get("label", str(n_data["id"]))
                node = self.canvas.add_new_node(n_data["x"], n_data["y"], n_data["id"], label)
                node_map[n_data["id"]] = node
            for e_data in data["edges"]:
                self.canvas.add_new_edge(node_map[e_data["from"]], node_map[e_data["to"]])
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Datei konnte nicht geladen werden: {e}")

    def save_json(self):
        if not self.is_connected():
            QMessageBox.warning(self, "Validierung", "Netzwerk ist nicht zusammenhängend!")
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

    def export_svg(self):
        if not self.canvas.nodes: return
        if not self.is_connected():
            QMessageBox.warning(self, "Validierung", "Netzwerk ist nicht zusammenhängend.")
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
                
                # Kanten zeichnen
                for e in self.canvas.edges:
                    line = QLineF(e.source.pos(), e.target.pos())
                    l = line.length()
                    if l > 40:
                        p1, p2 = line.pointAt(20/l), line.pointAt(1-20/l)
                        f.write(f'  <line x1="{p1.x()}" y1="{p1.y()}" x2="{p2.x()}" y2="{p2.y()}" stroke="black" stroke-width="2" marker-end="url(#arrow)" />\n')
                
                # Knoten zeichnen
                for n in self.canvas.nodes:
                    f.write(f'  <circle cx="{n.pos().x()}" cy="{n.pos().y()}" r="20" fill="#ffffff" stroke="#2c3e50" stroke-width="2" />\n')
                    # Label als Text
                    f.write(f'  <text x="{n.pos().x()}" y="{n.pos().y()}" font-family="Arial" font-size="10" font-weight="bold" text-anchor="middle" fill="#2c3e50" dy=".35em">{n.label_text}</text>\n')
                
                f.write('</svg>')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())