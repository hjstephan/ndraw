# Vector Network Designer Pro

Vector Network Designer Pro ist eine leistungsstarke Desktop-Anwendung auf Basis von Python 3.12 und PyQt6, die speziell für das Entwerfen, Visualisieren und Exportieren von Netzwerk-Topologien entwickelt wurde. Die Anwendung kombiniert eine intuitive grafische Benutzeroberfläche mit präzisem Vektor-Export.

## Features

### Interaktives Zeichnen
- **Linksklick**: Erstellt neue Knoten auf dem Canvas.
- **Rechtsklick**: Verbindet zwei Knoten mit einer gerichteten Kante.
- **Drag & Drop**: Knoten können frei bewegt werden; Kanten passen sich in Echtzeit an.
- **Mausrad**: Zoom in/out mit flüssiger Skalierung (Strg + Mausrad für feinere Kontrolle).

### Selektion & Bearbeitung
- **Sichtbare Selektion**: Knoten werden hellblau hervorgehoben, Kanten in dickerer blauer Linie.
- **Mehrfachselektion**: Strg + Klick zum Hinzufügen zur Selektion.
- **Löschen**: Selektierte Knoten/Kanten mit **Entf-Taste** entfernen.
- **F2-Taste**: Aktiviert die direkte Texteingabe im Knoten-Label (kein störender Dialog).
- **Editing-Hervorhebung**: Während der Umbenennung wird der Knoten orange hervorgehoben.
- **Automatisches Zentrieren**: Labels werden nach der Bearbeitung automatisch zentriert.

### Zoom-Funktion
- **Mausrad-Zoom**: Sanftes Zoomen mit dem Mausrad
- **Zoom-Bereich**: 10% bis 1000% (10x Vergrößerung)
- **Intelligenter Fokus**: Zoom zentriert sich auf die Mausposition
- **Unbegrenzte Präzision**: Perfekt für große und kleine Netzwerke

### Design
- **Moderne Optik**: Weiße Knoten mit dunklem Text für optimale Lesbarkeit
- **Gerichtete Kanten**: Klare Pfeilspitzen zeigen die Richtung
- **Farbkodierung**: 
  - Normal: Weiß (#ffffff)
  - Selektiert: Hellblau (#e3f2fd)
  - Bearbeitung: Orange (#ff9500)

### Validierung
- Integrierte Prüfung auf Zusammenhängigkeit (Connectivity Check) mittels Breitensuche (BFS) vor dem Speichern.

### Export & Import
- **JSON**: Speichert den vollständigen Status des Netzwerks zur späteren Bearbeitung.
- **SVG**: Exportiert das Netzwerk als skalierbare Vektorgrafik (gecropped auf den Inhalt).

## Installation & Setup

Stelle sicher, dass du unter Ubuntu 24.04 (oder einem anderen Linux-System) Python 3.12 installiert hast.

### 1. Repository klonen
```bash
git clone https://github.com/hjstephan/ndraw.git
cd ndraw
```

### 2. Virtuelle Umgebung erstellen
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt

# Falls keine requirements.txt vorhanden
pip install PyQt6 pytest pytest-qt pytest-cov
```

### 4. Icon generieren (optional)
```bash
python3 generate_icon.py
```

## Bedienung

| Aktion | Steuerung |
|--------|-----------|
| Knoten erstellen | Linksklick auf freien Bereich |
| Knoten verbinden | Rechtsklick auf Startknoten → Rechtsklick auf Zielknoten |
| Knoten verschieben | Linksklick halten und ziehen |
| Knoten/Kante selektieren | Linksklick auf Element |
| Mehrfachselektion | Strg + Linksklick |
| Knoten umbenennen | Maus über Knoten bewegen + F2 drücken |
| Bearbeitung beenden | Enter drücken oder außerhalb des Labels klicken |
| Löschen | Element(e) selektieren + Entf-Taste |
| Zoom In | Mausrad nach oben |
| Zoom Out | Mausrad nach unten |

## Desktop-Integration (Ubuntu/Linux)

### Automatische Installation
```bash
# Icon kopieren
cp ndraw_icon.png ~/.local/share/icons/

# Desktop-Eintrag erstellen
cat > ~/.local/share/applications/ndraw.desktop << 'EOF'
[Desktop Entry]
Name=Network Designer Pro
Comment=Vector Network Design Tool
Exec=/pfad/zu/ndraw/venv/bin/python /pfad/zu/ndraw/src/ndraw.py
Icon=ndraw_icon
Terminal=false
Type=Application
Categories=Graphics;VectorGraphics;Development;
EOF

# Desktop-Datenbank aktualisieren
update-desktop-database ~/.local/share/applications/
```

**Hinweis**: Ersetze `/pfad/zu/ndraw/` mit dem tatsächlichen Pfad zu deinem ndraw-Verzeichnis.

## Testing

Das Projekt nutzt pytest für Unit- und Integrationstests mit einer Coverage von **>80%**.

### Tests ausführen
```bash
pytest
```

### Coverage-Bericht generieren
```bash
pytest --cov=src --cov-report=html
```

Der HTML-Report wird in `doc/coverage/` erstellt.

## Projektstruktur
```
├── doc/               # Dokumentation (Code Coverage Report, ...)
├── src/
│   └── ndraw.py       # Hauptanwendung (GUI & Logik)
├── tests/
│   └── test_ndraw.py  # Testsuite (Pytest & QtTest)
├── drw/               # Gezeichnete Netzwerke
│   ├── netw.json      
|   └── netw.svg
├── pyproject.toml     # Projektkonfiguration
├── pytest.ini         # Test-Konfiguration
└── README.md
```

## Milestones & Roadmap

- [x] Knoten entfernen: Implementierung einer Löschfunktion (via Entf-Taste)
- [x] Kanten entfernen: Auswahl und Entfernen einzelner Verbindungen
- [x] Inline-Editing: Umbenennen via F2
- [x] Sichtbare Selektion: Hervorhebung von Knoten und Kanten
- [x] Zoom-Funktion: Mausrad-Zoom mit intelligentem Fokus
- [x] Testüberdeckung erhöhen: Coverage von >80% erreicht
- [ ] Undo/Redo: History-Funktionalität für alle Operationen
- [ ] Layout-Algorithmen: Implementierung von Force-Directed-Layouts zur automatischen Anordnung
- [ ] Themes: Dark Mode & weitere Farbschemata
- [ ] Export-Formate: PDF, PNG Export

## Technische Details

- **Python Version**: 3.12+
- **GUI Framework**: PyQt6
- **Testing**: pytest, pytest-qt, pytest-cov
- **Grafik-Engine**: QGraphicsView/QGraphicsScene
- **Export-Formate**: JSON (Daten), SVG (Vektorgrafik)