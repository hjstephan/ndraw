import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QVBoxLayout, 
                             QWidget, QPushButton, QHBoxLayout, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush

class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, node_id):
        super().__init__(-20, -20, 40, 40)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#3498db")))
        self.setPen(QPen(QColor("#2980b9"), 2))
        self.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.node_id = node_id
        self.lines = []

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.GraphicsItemChange.ItemPositionChange:
            for line in self.lines:
                line.update_position()
        return super().itemChange(change, value)

class Edge(QGraphicsLineItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        self.setPen(QPen(QColor("#2c3e50"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        self.update_position()

    def update_position(self):
        self.setLine(self.source.pos().x(), self.source.pos().y(), 
                     self.target.pos().x(), self.target.pos().y())

class NetworkCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 2000, 2000)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing) # Das macht es flüssig!
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.nodes = []
        self.edges = []
        self.connection_source = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        
        if event.button() == Qt.MouseButton.LeftButton:
            if not item: # Klick auf leeren Bereich -> Knoten erstellen
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
                    item.setPen(QPen(Qt.GlobalColor.red, 3))
                else:
                    if item != self.connection_source:
                        edge = Edge(self.connection_source, item)
                        self.scene.addItem(edge)
                        self.edges.append(edge)
                        self.connection_source.lines.append(edge)
                        item.lines.append(edge)
                    
                    self.connection_source.setPen(QPen(QColor("#2980b9"), 2))
                    self.connection_source = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vektor Netzwerk Designer")
        self.resize(1000, 800)

        self.canvas = NetworkCanvas()
        
        # Layout & Buttons
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
            QMessageBox.warning(self, "Fehler", "Netzwerk nicht zusammenhängend!")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Speichern", "", "JSON Files (*.json)")
        if path:
            data = {
                "nodes": [{"id": n.node_id, "x": n.pos().x(), "y": n.pos().y()} for n in self.canvas.nodes],
                "edges": [[e.source.node_id, e.target.node_id] for e in self.canvas.edges]
            }
            with open(path, "w") as f:
                json.dump(data, f)

    def export_svg(self):
        # Für echtes SVG-Writing in PyQt gibt es QtSvg, 
        # hier nutzen wir zur Einfachheit wieder den manuellen Writer 
        # für maximale Kontrolle über die Skalierbarkeit.
        path, _ = QFileDialog.getSaveFileName(self, "Export", "", "SVG Files (*.svg)")
        if path:
            with open(path, "w") as f:
                f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
                f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000">\n')
                for e in self.canvas.edges:
                    f.write(f'<line x1="{e.source.pos().x()}" y1="{e.source.pos().y()}" x2="{e.target.pos().x()}" y2="{e.target.pos().y()}" stroke="black" stroke-width="2"/>\n')
                for n in self.canvas.nodes:
                    f.write(f'<circle cx="{n.pos().x()}" cy="{n.pos().y()}" r="20" fill="#3498db" />\n')
                f.write('</svg>')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
