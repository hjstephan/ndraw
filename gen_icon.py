#!/usr/bin/env python3
"""
Icon-Generator für Vector Network Designer Pro
Erstellt Icons in verschiedenen Größen für Desktop-Integration
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QPolygonF
from PyQt6.QtCore import Qt, QPointF
import sys

def create_icon(size=512):
    """Erstellt ein Icon in der angegebenen Größe."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Skalierungsfaktor für verschiedene Größen
    scale = size / 64.0
    
    # Hintergrund - abgerundetes Rechteck mit Gradient
    painter.setBrush(QBrush(QColor("#2c3e50")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(
        int(2 * scale), 
        int(2 * scale), 
        int(60 * scale), 
        int(60 * scale), 
        int(8 * scale), 
        int(8 * scale)
    )
    
    # Zeichne Netzwerk-Verbindungen (Kanten)
    painter.setPen(QPen(QColor("#3498db"), int(2.5 * scale)))
    
    # Knoten-Positionen (skaliert)
    nodes = [
        (20 * scale, 20 * scale),
        (44 * scale, 20 * scale),
        (32 * scale, 40 * scale)
    ]
    
    # Zeichne Verbindungslinien
    painter.drawLine(int(nodes[0][0]), int(nodes[0][1]), int(nodes[1][0]), int(nodes[1][1]))
    painter.drawLine(int(nodes[0][0]), int(nodes[0][1]), int(nodes[2][0]), int(nodes[2][1]))
    painter.drawLine(int(nodes[1][0]), int(nodes[1][1]), int(nodes[2][0]), int(nodes[2][1]))
    
    # Zeichne Pfeilspitzen für gerichtete Kanten
    arrow_size = 4 * scale
    
    # Pfeil von Node 0 zu Node 1
    draw_arrow(painter, nodes[0], nodes[1], arrow_size, QColor("#3498db"))
    
    # Pfeil von Node 0 zu Node 2
    draw_arrow(painter, nodes[0], nodes[2], arrow_size, QColor("#3498db"))
    
    # Pfeil von Node 1 zu Node 2
    draw_arrow(painter, nodes[1], nodes[2], arrow_size, QColor("#3498db"))
    
    # Zeichne Knoten (Kreise)
    node_radius = 6 * scale
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.setPen(QPen(QColor("#3498db"), int(2 * scale)))
    
    for x, y in nodes:
        painter.drawEllipse(
            int(x - node_radius), 
            int(y - node_radius), 
            int(2 * node_radius), 
            int(2 * node_radius)
        )
    
    painter.end()
    return pixmap

def draw_arrow(painter, start, end, size, color):
    """Zeichnet eine Pfeilspitze am Ende einer Linie."""
    import math
    
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    angle = math.atan2(dy, dx)
    
    # Pfeilspitze am Ende der Linie
    arrow_p1 = QPointF(
        end[0] - size * math.cos(angle - math.pi / 6),
        end[1] - size * math.sin(angle - math.pi / 6)
    )
    arrow_p2 = QPointF(
        end[0] - size * math.cos(angle + math.pi / 6),
        end[1] - size * math.sin(angle + math.pi / 6)
    )
    
    painter.setBrush(QBrush(color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPolygon(QPolygonF([QPointF(end[0], end[1]), arrow_p1, arrow_p2]))

def main():
    """Hauptfunktion zum Generieren der Icons."""
    app = QApplication(sys.argv)
    
    # Erstelle Icons in verschiedenen Größen
    sizes = {
        'ndraw_icon_16.png': 16,
        'ndraw_icon_32.png': 32,
        'ndraw_icon_48.png': 48,
        'ndraw_icon_64.png': 64,
        'ndraw_icon_128.png': 128,
        'ndraw_icon_256.png': 256,
        'ndraw_icon_512.png': 512,
        'ndraw_icon.png': 64  # Standard-Icon
    }
    
    for filename, size in sizes.items():
        icon = create_icon(size)
        if icon.save(filename):
            print(f"✓ {filename} erfolgreich erstellt ({size}x{size})")
        else:
            print(f"✗ Fehler beim Erstellen von {filename}")
    
    print("\n" + "="*50)
    print("Icon-Generierung abgeschlossen!")
    print("="*50)
    print("\nFür Ubuntu/Linux Desktop-Integration:")
    print("1. Kopiere ndraw_icon.png nach ~/.local/share/icons/")
    print("   cp ndraw_icon.png ~/.local/share/icons/")
    print("\n2. Erstelle eine .desktop Datei:")
    print("   nano ~/.local/share/applications/ndraw.desktop")
    print("\n3. Inhalt der .desktop Datei:")
    print("""
[Desktop Entry]
Name=Network Designer Pro
Comment=Vector Network Design Tool
Exec=/pfad/zu/ndraw/venv/bin/python /pfad/zu/ndraw/src/ndraw.py
Icon=ndraw_icon
Terminal=false
Type=Application
Categories=Graphics;VectorGraphics;Development;
    """)
    print("\n4. Desktop-Datenbank aktualisieren:")
    print("   update-desktop-database ~/.local/share/applications/")

if __name__ == "__main__":
    main()
