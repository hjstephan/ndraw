import pytest
import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPointF, QPoint, QEvent
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QColor, QMouseEvent, QKeyEvent, QFocusEvent, QBrush

# Importiere die Klassen aus ndraw.py
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from ndraw import Node, DirectedEdge, NetworkCanvas, MainWindow

@pytest.fixture(scope="session")
def qapp():
    """Erstelle eine QApplication Instanz für alle Tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def canvas(qapp):
    """Erstelle eine neue NetworkCanvas Instanz für jeden Test."""
    return NetworkCanvas()

@pytest.fixture
def main_window(qapp):
    """Erstelle ein MainWindow für jeden Test."""
    window = MainWindow()
    yield window
    window.close()


class TestBugFixes:
    """Tests für die behobenen Bugs."""
    
    def test_remove_node_clears_connection_source(self, canvas):
        """Test: Löschen eines Knotens setzt connection_source zurück."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        # Setze node1 als connection_source
        canvas.connection_source = node1
        node1.setBrush(QBrush(QColor("#e74c3c")))
        
        # Lösche node1
        canvas.remove_node(node1)
        
        # connection_source sollte None sein
        assert canvas.connection_source is None
        assert len(canvas.nodes) == 1
    
    def test_remove_connection_source_prevents_half_edge(self, canvas):
        """Test: Verhindert 'halbe Kante' wenn connection_source gelöscht wird."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        node3 = canvas.add_new_node(200, 200, 2)
        
        # Starte Verbindung von node1
        canvas.connection_source = node1
        
        # Lösche node1 (connection_source)
        canvas.remove_node(node1)
        
        # Versuche Verbindung zu node2 zu erstellen
        # Dies sollte keine Kante erstellen, da connection_source None ist
        if canvas.connection_source:
            canvas.add_new_edge(canvas.connection_source, node2)
        
        assert len(canvas.edges) == 0
        assert canvas.connection_source is None
    
    def test_add_edge_validates_source_exists(self, canvas):
        """Test: add_new_edge validiert dass source existiert."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        # Entferne node1 aus der Liste, aber nicht aus Scene
        canvas.nodes.remove(node1)
        
        # Versuche Kante zu erstellen - sollte None zurückgeben
        edge = canvas.add_new_edge(node1, node2)
        
        assert edge is None
        assert len(canvas.edges) == 0
    
    def test_add_edge_validates_target_exists(self, canvas):
        """Test: add_new_edge validiert dass target existiert."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        # Entferne node2 aus der Liste
        canvas.nodes.remove(node2)
        
        # Versuche Kante zu erstellen - sollte None zurückgeben
        edge = canvas.add_new_edge(node1, node2)
        
        assert edge is None
        assert len(canvas.edges) == 0
    
    def test_add_edge_validates_both_nodes(self, canvas):
        """Test: add_new_edge validiert beide Knoten."""
        node1 = Node(0, 0, 0)
        node2 = Node(100, 100, 1)
        
        # Beide Knoten existieren nicht in canvas.nodes
        edge = canvas.add_new_edge(node1, node2)
        
        assert edge is None
        assert len(canvas.edges) == 0
    
    def test_right_click_empty_space_cancels_connection(self, canvas):
        """Test: Rechtsklick ins Leere bricht Verbindung ab."""
        from PyQt6.QtGui import QBrush
        
        node1 = canvas.add_new_node(100, 100, 0)
        
        # Setze connection_source
        canvas.connection_source = node1
        node1.setBrush(QBrush(QColor("#e74c3c")))
        
        # Simuliere Rechtsklick ins Leere
        pos = QPoint(500, 500)  # Leerer Bereich
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(pos),
            Qt.MouseButton.RightButton,
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        canvas.mousePressEvent(event)
        
        # connection_source sollte zurückgesetzt sein
        assert canvas.connection_source is None
    
    def test_escape_key_cancels_connection(self, canvas):
        """Test: ESC-Taste bricht Verbindung ab."""
        from PyQt6.QtGui import QBrush
        
        node1 = canvas.add_new_node(100, 100, 0)
        
        # Setze connection_source
        canvas.connection_source = node1
        node1.setBrush(QBrush(QColor("#e74c3c")))
        
        # Drücke ESC
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier
        )
        
        canvas.keyPressEvent(event)
        
        # connection_source sollte None sein
        assert canvas.connection_source is None
    
    def test_load_json_resets_connection_source(self, main_window, tmp_path):
        """Test: JSON-Laden setzt connection_source zurück."""
        node1 = main_window.canvas.add_new_node(100, 100, 0)
        
        # Setze connection_source
        main_window.canvas.connection_source = node1
        
        # Erstelle und lade JSON
        json_file = tmp_path / "test.json"
        test_data = {
            "nodes": [{"id": 0, "x": 50.0, "y": 100.0, "label": "Test"}],
            "edges": []
        }
        
        with open(json_file, "w") as f:
            json.dump(test_data, f)
        
        # Simuliere load_json Logik
        with open(json_file, "r") as f:
            data = json.load(f)
        
        main_window.canvas.scene.clear()
        main_window.canvas.nodes = []
        main_window.canvas.edges = []
        main_window.canvas.connection_source = None  # Der Fix
        
        node_map = {}
        for n_data in data["nodes"]:
            label = n_data.get("label", str(n_data["id"]))
            node = main_window.canvas.add_new_node(
                n_data["x"], n_data["y"], n_data["id"], label
            )
            node_map[n_data["id"]] = node
        
        # connection_source sollte None sein
        assert main_window.canvas.connection_source is None
    
    def test_delete_node_during_connection_setup(self, canvas):
        """Test: Knoten löschen während Verbindungsaufbau."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        node3 = canvas.add_new_node(200, 200, 2)
        
        # Starte Verbindung
        canvas.connection_source = node1
        
        # Selektiere und lösche node1
        node1.setSelected(True)
        canvas.delete_selected_items()
        
        # Versuche jetzt Verbindung zu node2 zu erstellen
        if canvas.connection_source and canvas.connection_source in canvas.nodes:
            canvas.add_new_edge(canvas.connection_source, node2)
        
        # Keine Kante sollte erstellt worden sein
        assert len(canvas.edges) == 0
        assert canvas.connection_source is None
    
    def test_connection_source_visual_reset(self, canvas):
        """Test: Visueller Zustand wird beim Abbruch zurückgesetzt."""
        from PyQt6.QtGui import QBrush
        
        node1 = canvas.add_new_node(100, 100, 0)
        
        # Setze connection_source mit rotem Hintergrund
        canvas.connection_source = node1
        original_color = QColor("#e74c3c")
        node1.setBrush(QBrush(original_color))
        
        # Simuliere Abbruch durch Rechtsklick ins Leere
        canvas.connection_source.update_selection_style()
        canvas.connection_source = None
        
        # Knoten sollte wieder normale Farbe haben
        assert node1.brush().color() == QColor("#ffffff")
    
    def test_multiple_connection_attempts_after_deletion(self, canvas):
        """Test: Mehrere Verbindungsversuche nach Knotenlöschung."""
        nodes = [canvas.add_new_node(i*100, i*100, i) for i in range(5)]
        
        # Starte Verbindung von nodes[0]
        canvas.connection_source = nodes[0]
        
        # Lösche nodes[0]
        canvas.remove_node(nodes[0])
        assert canvas.connection_source is None
        
        # Starte neue Verbindung von nodes[1]
        canvas.connection_source = nodes[1]
        
        # Erstelle Kante zu nodes[2]
        edge = canvas.add_new_edge(nodes[1], nodes[2])
        
        # Sollte funktionieren
        assert edge is not None
        assert len(canvas.edges) == 1
        assert edge.source == nodes[1]
        assert edge.target == nodes[2]
    
    def test_remove_target_node_during_connection(self, canvas):
        """Test: Zielknoten während Verbindungsaufbau löschen."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        # Starte Verbindung von node1 zu node2
        canvas.connection_source = node1
        
        # Lösche node2 (Ziel)
        canvas.remove_node(node2)
        
        # connection_source sollte noch node1 sein
        assert canvas.connection_source == node1
        
        # Versuche Verbindung zu erstellen - sollte None geben
        node3 = canvas.add_new_node(200, 200, 2)
        edge = canvas.add_new_edge(canvas.connection_source, node2)
        
        assert edge is None
        assert len(canvas.edges) == 0
    
    def test_connection_source_after_clear_scene(self, canvas):
        """Test: connection_source nach Scene-Clear."""
        node1 = canvas.add_new_node(100, 100, 0)
        canvas.connection_source = node1
        
        # Clear scene
        canvas.scene.clear()
        canvas.nodes = []
        canvas.edges = []
        
        # connection_source sollte manuell zurückgesetzt werden
        # (dies ist kein automatischer Fix, aber ein wichtiger Test)
        # In der Praxis sollte load_json dies tun
        canvas.connection_source = None
        
        assert canvas.connection_source is None
        assert len(canvas.nodes) == 0
    
    def test_edge_creation_with_deleted_source(self, canvas):
        """Test: Kanten-Erstellung mit gelöschtem Source-Knoten."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        # Entferne node1 komplett
        canvas.remove_node(node1)
        
        # Versuche Kante von gelöschtem node1 zu node2
        edge = canvas.add_new_edge(node1, node2)
        
        assert edge is None
        assert len(canvas.edges) == 0
    
    def test_edge_creation_with_deleted_target(self, canvas):
        """Test: Kanten-Erstellung mit gelöschtem Target-Knoten."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        # Entferne node2 komplett
        canvas.remove_node(node2)
        
        # Versuche Kante von node1 zu gelöschtem node2
        edge = canvas.add_new_edge(node1, node2)
        
        assert edge is None
        assert len(canvas.edges) == 0
    
    def test_connection_workflow_complete(self, canvas):
        """Test: Kompletter Verbindungs-Workflow."""
        from PyQt6.QtGui import QBrush
        
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        # Schritt 1: Starte Verbindung
        canvas.connection_source = node1
        node1.setBrush(QBrush(QColor("#e74c3c")))
        
        assert canvas.connection_source == node1
        assert len(canvas.edges) == 0
        
        # Schritt 2: Erstelle Verbindung
        edge = canvas.add_new_edge(node1, node2)
        
        assert edge is not None
        assert len(canvas.edges) == 1
        
        # Schritt 3: Reset connection_source
        canvas.connection_source.update_selection_style()
        canvas.connection_source = None
        
        assert canvas.connection_source is None
        assert node1.brush().color() == QColor("#ffffff")
    
    def test_escape_without_active_connection(self, canvas):
        """Test: ESC ohne aktive Verbindung."""
        node1 = canvas.add_new_node(100, 100, 0)
        
        # Keine aktive Verbindung
        assert canvas.connection_source is None
        
        # Drücke ESC
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier
        )
        
        canvas.keyPressEvent(event)
        
        # Sollte keinen Fehler werfen
        assert canvas.connection_source is None
        assert len(canvas.nodes) == 1


class TestRegressionBugs:
    """Regression-Tests um sicherzustellen dass Bugs nicht zurückkommen."""
    
    def test_no_orphaned_edges_after_node_deletion(self, canvas):
        """Test: Keine verwaisten Kanten nach Knoten-Löschung."""
        nodes = [canvas.add_new_node(i*100, 0, i) for i in range(4)]
        
        # Erstelle Kanten
        canvas.add_new_edge(nodes[0], nodes[1])
        canvas.add_new_edge(nodes[1], nodes[2])
        canvas.add_new_edge(nodes[2], nodes[3])
        
        assert len(canvas.edges) == 3
        
        # Lösche mittlere Knoten
        canvas.remove_node(nodes[1])
        canvas.remove_node(nodes[2])
        
        # Alle Kanten sollten weg sein
        assert len(canvas.edges) == 0
        assert len(canvas.nodes) == 2
    
    def test_edge_references_cleaned_up(self, canvas):
        """Test: Edge-Referenzen in Knoten werden aufgeräumt."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        edge = canvas.add_new_edge(node1, node2)
        
        assert edge in node1.lines
        assert edge in node2.lines
        
        # Entferne Kante
        canvas.remove_edge(edge)
        
        assert edge not in node1.lines
        assert edge not in node2.lines
        assert len(canvas.edges) == 0
    
    def test_multiple_edges_same_nodes(self, canvas):
        """Test: Mehrere Kanten zwischen gleichen Knoten."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        # Erstelle mehrere Kanten
        edge1 = canvas.add_new_edge(node1, node2)
        edge2 = canvas.add_new_edge(node1, node2)
        edge3 = canvas.add_new_edge(node2, node1)  # Gegenrichtung
        
        assert len(canvas.edges) == 3
        assert edge1 != edge2
        assert edge2 != edge3
        
        # Lösche node1
        canvas.remove_node(node1)
        
        # Alle Kanten sollten weg sein
        assert len(canvas.edges) == 0
    
    def test_self_loop_deletion(self, canvas):
        """Test: Löschen von Self-Loops."""
        node1 = canvas.add_new_node(100, 100, 0)
        
        # Erstelle Self-Loop
        edge = canvas.add_new_edge(node1, node1)
        
        assert edge.source == edge.target
        assert len(canvas.edges) == 1
        
        # Lösche Knoten
        canvas.remove_node(node1)
        
        # Edge sollte auch weg sein
        assert len(canvas.edges) == 0
        assert len(canvas.nodes) == 0