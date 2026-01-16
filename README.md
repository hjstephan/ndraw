# Vector Network Designer Pro
Network Designer Pro ist eine leistungsstarke Desktop-Anwendung auf Basis von Python 3.12 und PyQt6, die speziell für das Entwerfen, Visualisieren und Exportieren von Netzwerk-Topologien entwickelt wurde. Die Anwendung kombiniert eine intuitive grafische Benutzeroberfläche mit präzisem Vektor-Export.

## Features
- Interaktives Zeichnen:
    - Linksklick: Erstellt neue Knoten auf dem Canvas.
    - Rechtsklick: Verbindet zwei Knoten mit einer gerichteten Kante.
    - Drag & Drop: Knoten können frei bewegt werden; Kanten passen sich in Echtzeit an.
- Direktes Labeling:
    - F2-Taste: Aktiviert die direkte Texteingabe im Knoten-Label (kein störender Dialog).
    - Automatisches Zentrieren der Labels nach der Bearbeitung.
- Validierung:
    - Integrierte Prüfung auf Zusammenhängigkeit (Connectivity Check) mittels Breitensuche (BFS) vor dem Speichern.
- Export & Import:
    - JSON: Speichert den vollständigen Status des Netzwerks zur späteren Bearbeitung.
    - SVG: Exportiert das Netzwerk als skalierbare Vektorgrafik (gecropped auf den Inhalt).

## Installation & Setup
Stelle sicher, dass du unter Ubuntu 24.04 (oder einem anderen Linux-System) Python 3.12 installiert hast.

1. Repository klonen:
```bash
git clone https://github.com/hjstephan/ndraw.git
cd ndraw
```

2. Virtuelle Umgebung erstellen:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt

# Falls keine requirements.txt vorhanden
pip install PyQt6 pytest pytest-qt pytest-cov
```

## Bedienung
```bash
Aktion                  Steuerung
---------------------------------------------------------------------------------
Knoten erstellen        Linksklick auf freien Bereich
Knoten verbinden        Rechtsklick auf Startknoten und Rechtsklick auf Zielknoten
Knoten verschieben      Linksklick halten und ziehen
Knoten umbenennen       Knoten selektieren und F2 drücken
Kante löschen           Kante selektieren und Del drücken
```

## Testing
Das Projekt nutzt pytest für Unit- und Integrationstests.

Tests ausführen:
```bash
pytest
```

Coverage-Bericht generieren:
```bash
pytest --cov=src --cov-report=html
```

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
```bash
[x] Knoten entfernen: Implementierung einer Löschfunktion (via Del-Taste).  
[x] Kanten entfernen: Auswahl und Entfernen einzelner Verbindungen.  
[x] Inline-Editing: Umbenennen via F2.  
[-] Testüberdeckung erhöhen: Ziel ist eine Coverage von > 80% (aktuell ~65%).  
[ ] Layout-Algorithmen: Implementierung von Force-Directed-Layouts zur automatischen Anordnung.  
```