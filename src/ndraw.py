import sys
import json
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QVBoxLayout, 
                             QWidget, QPushButton, QHBoxLayout, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF

class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, node_id):
        # Radius ist 20 (Durchmesser 40)
        super().__init__(-20, -20, 40, 40)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#3498db")))
        self.setPen(QPen(QColor("#2c3e50"), 2))
        self.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.node_id = node_id
        self.lines = []

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.GraphicsItemChange.ItemPositionChange:
            for line in self.lines:
                line.update_position()
        return super().itemChange(change, value)

class DirectedEdge(QGraphicsLineItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.arrow_size = 12
        self.node_radius = 20
        self.update_position()

    def update_position(self):
        # Linie zwischen den Zentren berechnen
        raw_line = QLineF(self.source.pos(), self.target.pos())
        length = raw_line.length()

        # Linie kürzen, damit sie am Rand der Knoten startet/endet
        if length > self.node_radius * 2:
            shorten_factor = self.node_radius / length
            p1 = raw_line.pointAt(shorten_factor)
            p2 = raw_line.pointAt(1.0 - shorten_factor)
            self.setLine(QLineF(p1, p2))
        else:
            self.setLine(QLineF(self.source.pos(), self.source.pos()))

    def paint(self, painter, option, widget=None):
        line = self.line()
        if line.length() < 1:
            return

        # 1. Die sichtbare Linie zeichnen
        painter.setPen(self.pen())
        painter.drawLine(line)

        # 2. Winkel der Linie berechnen
        angle = math.atan2(-line.dy(), line.dx())

        # 3. Pfeilspitze direkt am Endpunkt (Knotenrand) berechnen
        arrow_p1 = line.p2() - QPointF(math.cos(angle + math.pi / 8) * self.arrow_size,
                                       -math.sin(angle + math.pi / 8) * self.arrow_size)
        arrow_p2 = line.p2() - QPointF(math.cos(angle - math.pi / 8) * self.arrow_size,
                                       -math.sin(angle - math.pi / 8) * self.arrow_size)

        # 4. Pfeilspitze schwarz füllen
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF([line.p2(), arrow_p1, arrow_p2]))

class NetworkCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 5000, 5000)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.nodes = []
        self.edges = []
        self.connection_source = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if event.button() == Qt.MouseButton.LeftButton:
            if not item:
                pos = self.mapToScene(event.pos())
                node = Node(pos.x(), pos.y(), len(self.nodes))
                self.scene.addItem(node)
                self.nodes.append(node)
            else:
                super().mousePressEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            if isinstance(item, Node):
                if not self.connection_source:
                    self.connection_source = item
                    item.setBrush(QBrush(QColor("#e74c3c"))) # Markierung
                else:
                    if item != self.connection_source:
                        edge = DirectedEdge(self.connection_source, item)
                        self.scene.addItem(edge)
                        self.edges.append(edge)
                        self.connection_source.lines.append(edge)
                        item.lines.append(edge)
                    self.connection_source.setBrush(QBrush(QColor("#3498db")))
                    self.connection_source = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Network Designer Pro")
        self.resize(1000, 800)
        self.canvas = NetworkCanvas()
        
        layout = QVBoxLayout()
        toolbar = QHBoxLayout()
        btn_json = QPushButton("JSON Speichern")
        btn_json.clicked.connect(self.save_json)
        btn_svg = QPushButton("SVG Export")
        btn_svg.clicked.connect(self.export_svg)
        
        toolbar.addWidget(btn_json)
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

    def save_json(self):
        if not self.is_connected():
            QMessageBox.warning(self, "Validierung", "Netzwerk ist nicht zusammenhängend!")
            return
        path, _ = QFileDialog.getSaveFileName(self, "JSON Speichern", "", "JSON Files (*.json)")
        if path:
            data = {
                "nodes": [{"id": n.node_id, "x": n.pos().x(), "y": n.pos().y()} for n in self.canvas.nodes],
                "edges": [{"from": e.source.node_id, "to": e.target.node_id} for e in self.canvas.edges]
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=4)

    def export_svg(self):
        if not self.is_connected():
            QMessageBox.warning(self, "Validierung", "Speichern nur bei zusammenhängendem Netzwerk möglich.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "SVG Export", "", "SVG Files (*.svg)")
        if path:
            with open(path, "w") as f:
                f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
                f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5000 5000">\n')
                # Marker Definition für SVG Pfeile am Rand
                f.write('<defs>\n')
                f.write('  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">\n')
                f.write('    <polygon points="0 0, 10 3.5, 0 7" fill="black" />\n')
                f.write('  </marker>\n')
                f.write('</defs>\n')
                
                for e in self.canvas.edges:
                    # Im SVG nutzen wir die Marker-Logik am Rand
                    line = QLineF(e.source.pos(), e.target.pos())
                    # Wir kürzen die Linie im SVG ebenfalls, damit der Marker am Rand sitzt
                    length = line.length()
                    if length > 40:
                        shorten = 20 / length
                        p1 = line.pointAt(shorten)
                        p2 = line.pointAt(1.0 - shorten)
                        f.write(f'  <line x1="{p1.x()}" y1="{p1.y()}" x2="{p2.x()}" y2="{p2.y()}" stroke="black" stroke-width="2" marker-end="url(#arrowhead)" />\n')
                
                for n in self.canvas.nodes:
                    f.write(f'  <circle cx="{n.pos().x()}" cy="{n.pos().y()}" r="20" fill="#3498db" stroke="#2c3e50" stroke-width="2" />\n')
                    f.write(f'  <text x="{n.pos().x()}" y="{n.pos().y()}" font-family="Arial" font-size="12" text-anchor="middle" fill="white" dy=".3em">{n.node_id}</text>\n')
                f.write('</svg>')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
