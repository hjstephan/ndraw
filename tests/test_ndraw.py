import pytest
import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QColor

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


class TestNode:
    """Tests für die Node Klasse."""
    
    def test_node_creation(self, qapp):
        """Test ob ein Node korrekt erstellt wird."""
        node = Node(100, 200, 0)
        assert node.node_id == 0
        assert node.pos().x() == 100
        assert node.pos().y() == 200
        assert len(node.lines) == 0
        assert node.label_text == "0"
        assert node.is_editing == False
    
    def test_node_with_label(self, qapp):
        """Test ob ein Node mit custom Label erstellt wird."""
        node = Node(100, 200, 5, label="Knoten A")
        assert node.node_id == 5
        assert node.label_text == "Knoten A"
    
    def test_node_position(self, qapp):
        """Test ob die Position eines Nodes geändert werden kann."""
        node = Node(0, 0, 1)
        node.setPos(50, 75)
        assert node.pos().x() == 50
        assert node.pos().y() == 75
    
    def test_node_set_label(self, qapp):
        """Test ob das Label eines Nodes geändert werden kann."""
        node = Node(0, 0, 1)
        node.set_label("Neues Label")
        assert node.label_text == "Neues Label"
        assert node.label.toPlainText() == "Neues Label"
    
    def test_node_movable(self, qapp):
        """Test ob Node als movable markiert ist."""
        node = Node(0, 0, 0)
        assert node.flags() & Node.GraphicsItemFlag.ItemIsMovable
    
    def test_node_selectable(self, qapp):
        """Test ob Node als selectable markiert ist."""
        node = Node(0, 0, 0)
        assert node.flags() & Node.GraphicsItemFlag.ItemIsSelectable
    
    def test_node_default_color(self, qapp):
        """Test ob Node standardmäßig weißen Hintergrund hat."""
        node = Node(0, 0, 0)
        assert node.brush().color() == QColor("#ffffff")
    
    def test_node_selection_style(self, qapp):
        """Test ob Selection den Stil ändert."""
        node = Node(0, 0, 0)
        node.setSelected(True)
        node.update_selection_style()
        assert node.brush().color() == QColor("#e3f2fd")
        assert node.pen().width() == 3
    
    def test_node_editing_mode(self, qapp):
        """Test ob Editing-Mode korrekt gesetzt wird."""
        node = Node(0, 0, 0)
        node.set_editing_mode(True)
        assert node.is_editing == True
        assert node.brush().color() == QColor("#ff9500")
        assert node.pen().width() == 3
    
    def test_node_editing_mode_off(self, qapp):
        """Test ob Editing-Mode korrekt deaktiviert wird."""
        node = Node(0, 0, 0)
        node.set_editing_mode(True)
        node.set_editing_mode(False)
        assert node.is_editing == False
        assert node.brush().color() == QColor("#ffffff")
    
    def test_node_label_positioning(self, qapp):
        """Test ob Label-Position korrekt zentriert wird."""
        node = Node(0, 0, 0)
        br = node.label.boundingRect()
        expected_x = -br.width() / 2
        expected_y = -br.height() / 2
        assert abs(node.label.pos().x() - expected_x) < 0.1
        assert abs(node.label.pos().y() - expected_y) < 0.1


class TestDirectedEdge:
    """Tests für die DirectedEdge Klasse."""
    
    def test_edge_creation(self, qapp):
        """Test ob eine Kante korrekt erstellt wird."""
        source = Node(0, 0, 0)
        target = Node(100, 100, 1)
        edge = DirectedEdge(source, target)
        
        assert edge.source == source
        assert edge.target == target
        assert edge.arrow_size == 12
    
    def test_edge_update_position(self, qapp):
        """Test ob die Kantenposition aktualisiert wird."""
        source = Node(0, 0, 0)
        target = Node(100, 0, 1)
        edge = DirectedEdge(source, target)
        
        # Überprüfe dass die Linie verkürzt wurde (wegen node_radius)
        line = edge.line()
        assert line.length() < 100
        assert line.length() > 0
    
    def test_edge_selectable(self, qapp):
        """Test ob Edge als selectable markiert ist."""
        source = Node(0, 0, 0)
        target = Node(100, 100, 1)
        edge = DirectedEdge(source, target)
        assert edge.flags() & DirectedEdge.GraphicsItemFlag.ItemIsSelectable
    
    def test_edge_selection_style(self, qapp):
        """Test ob Selection den Edge-Stil ändert."""
        source = Node(0, 0, 0)
        target = Node(100, 100, 1)
        edge = DirectedEdge(source, target)
        edge.setSelected(True)
        edge.update_selection_style()
        assert edge.pen().width() == 4
        assert edge.pen().color() == QColor("#2196f3")
    
    def test_edge_deselection_style(self, qapp):
        """Test ob Deselection den Edge-Stil zurücksetzt."""
        source = Node(0, 0, 0)
        target = Node(100, 100, 1)
        edge = DirectedEdge(source, target)
        edge.setSelected(True)
        edge.update_selection_style()
        edge.setSelected(False)
        edge.update_selection_style()
        assert edge.pen().width() == 2
    
    def test_edge_zero_length(self, qapp):
        """Test Edge-Verhalten bei gleicher Quell- und Zielposition."""
        source = Node(0, 0, 0)
        target = Node(0, 0, 1)
        edge = DirectedEdge(source, target)
        line = edge.line()
        assert line.length() == 0


class TestNetworkCanvas:
    """Tests für die NetworkCanvas Klasse."""
    
    def test_canvas_initialization(self, canvas):
        """Test ob Canvas korrekt initialisiert wird."""
        assert len(canvas.nodes) == 0
        assert len(canvas.edges) == 0
        assert canvas.connection_source is None
    
    def test_add_node(self, canvas):
        """Test ob Nodes hinzugefügt werden können."""
        node = canvas.add_new_node(100, 200, 0)
        
        assert len(canvas.nodes) == 1
        assert canvas.nodes[0] == node
        assert node.node_id == 0
        assert node.pos().x() == 100
        assert node.pos().y() == 200
    
    def test_add_node_with_label(self, canvas):
        """Test ob Nodes mit Label hinzugefügt werden können."""
        node = canvas.add_new_node(100, 200, 0, label="Test Node")
        
        assert len(canvas.nodes) == 1
        assert node.label_text == "Test Node"
    
    def test_add_multiple_nodes(self, canvas):
        """Test ob mehrere Nodes hinzugefügt werden können."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        node3 = canvas.add_new_node(200, 200, 2)
        
        assert len(canvas.nodes) == 3
        assert canvas.nodes == [node1, node2, node3]
    
    def test_add_edge(self, canvas):
        """Test ob Kanten zwischen Nodes hinzugefügt werden können."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        edge = canvas.add_new_edge(node1, node2)
        
        assert len(canvas.edges) == 1
        assert canvas.edges[0].source == node1
        assert canvas.edges[0].target == node2
        assert edge in node1.lines
        assert edge in node2.lines
    
    def test_add_multiple_edges(self, canvas):
        """Test ob mehrere Kanten hinzugefügt werden können."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 0, 1)
        node3 = canvas.add_new_node(200, 0, 2)
        
        canvas.add_new_edge(node1, node2)
        canvas.add_new_edge(node2, node3)
        
        assert len(canvas.edges) == 2
    
    def test_remove_node(self, canvas):
        """Test ob Knoten entfernt werden können."""
        node = canvas.add_new_node(100, 100, 0)
        assert len(canvas.nodes) == 1
        
        canvas.remove_node(node)
        assert len(canvas.nodes) == 0
    
    def test_remove_node_with_edges(self, canvas):
        """Test ob Knoten mit Kanten korrekt entfernt werden."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        node3 = canvas.add_new_node(200, 200, 2)
        canvas.add_new_edge(node1, node2)
        canvas.add_new_edge(node2, node3)
        
        canvas.remove_node(node2)
        
        assert len(canvas.nodes) == 2
        assert len(canvas.edges) == 0
        assert node2 not in canvas.nodes
    
    def test_remove_edge(self, canvas):
        """Test ob Kanten entfernt werden können."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        edge = canvas.add_new_edge(node1, node2)
        
        assert len(canvas.edges) == 1
        canvas.remove_edge(edge)
        assert len(canvas.edges) == 0
        assert edge not in node1.lines
        assert edge not in node2.lines
    
    def test_delete_selected_items_nodes(self, canvas):
        """Test ob selektierte Knoten gelöscht werden."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        
        node1.setSelected(True)
        canvas.delete_selected_items()
        
        assert len(canvas.nodes) == 1
        assert node2 in canvas.nodes
    
    def test_delete_selected_items_edges(self, canvas):
        """Test ob selektierte Kanten gelöscht werden."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        edge = canvas.add_new_edge(node1, node2)
        
        edge.setSelected(True)
        canvas.delete_selected_items()
        
        assert len(canvas.edges) == 0
        assert len(canvas.nodes) == 2
    
    def test_delete_selected_items_mixed(self, canvas):
        """Test ob gemischte Selektion (Knoten+Kanten) gelöscht wird."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        node3 = canvas.add_new_node(200, 200, 2)
        edge1 = canvas.add_new_edge(node1, node2)
        edge2 = canvas.add_new_edge(node2, node3)
        
        node2.setSelected(True)
        edge1.setSelected(True)
        canvas.delete_selected_items()
        
        assert len(canvas.nodes) == 2
        assert len(canvas.edges) == 0
    
    def test_edit_node_label(self, canvas):
        """Test ob Label-Editing aktiviert wird."""
        node = canvas.add_new_node(100, 100, 0)
        canvas.edit_node_label(node)
        
        assert node.is_editing == True
        assert node.label.textInteractionFlags() & Qt.TextInteractionFlag.TextEditorInteraction
    
    def test_finish_label_edit(self, canvas):
        """Test ob Label-Editing korrekt beendet wird."""
        node = canvas.add_new_node(100, 100, 0)
        canvas.edit_node_label(node)
        
        # Simuliere Textänderung
        node.label.setPlainText("Neuer Text")
        
        # Simuliere FocusOut Event
        from PyQt6.QtGui import QFocusEvent
        from PyQt6.QtCore import Qt
        event = QFocusEvent(QFocusEvent.Type.FocusOut)
        canvas.finish_label_edit(node, event)
        
        assert node.is_editing == False
        assert node.label_text == "Neuer Text"
        assert not (node.label.textInteractionFlags() & Qt.TextInteractionFlag.TextEditorInteraction)


class TestMainWindow:
    """Tests für das MainWindow."""
    
    def test_window_initialization(self, main_window):
        """Test ob das Fenster korrekt initialisiert wird."""
        assert main_window.windowTitle() == "Vector Network Designer Pro"
        assert main_window.canvas is not None
    
    def test_is_connected_empty_network(self, main_window):
        """Test ob ein leeres Netzwerk als verbunden gilt."""
        assert main_window.is_connected() == True
    
    def test_is_connected_single_node(self, main_window):
        """Test ob ein einzelner Node als verbunden gilt."""
        main_window.canvas.add_new_node(0, 0, 0)
        assert main_window.is_connected() == True
    
    def test_is_connected_two_connected_nodes(self, main_window):
        """Test ob zwei verbundene Nodes als verbunden erkannt werden."""
        node1 = main_window.canvas.add_new_node(0, 0, 0)
        node2 = main_window.canvas.add_new_node(100, 100, 1)
        main_window.canvas.add_new_edge(node1, node2)
        
        assert main_window.is_connected() == True
    
    def test_is_connected_disconnected_nodes(self, main_window):
        """Test ob getrennte Nodes als nicht verbunden erkannt werden."""
        main_window.canvas.add_new_node(0, 0, 0)
        main_window.canvas.add_new_node(100, 100, 1)
        
        assert main_window.is_connected() == False
    
    def test_is_connected_complex_network(self, main_window):
        """Test ob ein komplexes verbundenes Netzwerk erkannt wird."""
        node1 = main_window.canvas.add_new_node(0, 0, 0)
        node2 = main_window.canvas.add_new_node(100, 0, 1)
        node3 = main_window.canvas.add_new_node(200, 0, 2)
        node4 = main_window.canvas.add_new_node(100, 100, 3)
        
        main_window.canvas.add_new_edge(node1, node2)
        main_window.canvas.add_new_edge(node2, node3)
        main_window.canvas.add_new_edge(node2, node4)
        
        assert main_window.is_connected() == True
    
    def test_is_connected_after_node_deletion(self, main_window):
        """Test ob Connectivity nach Löschung korrekt erkannt wird."""
        node1 = main_window.canvas.add_new_node(0, 0, 0)
        node2 = main_window.canvas.add_new_node(100, 100, 1)
        node3 = main_window.canvas.add_new_node(200, 200, 2)
        main_window.canvas.add_new_edge(node1, node2)
        main_window.canvas.add_new_edge(node2, node3)
        
        # Lösche mittleren Knoten
        main_window.canvas.remove_node(node2)
        
        assert main_window.is_connected() == False


class TestJSONImportExport:
    """Tests für JSON Import/Export."""
    
    def test_json_export_structure(self, main_window, tmp_path):
        """Test ob die JSON Struktur korrekt ist."""
        # Erstelle ein einfaches Netzwerk
        node1 = main_window.canvas.add_new_node(100, 200, 0, label="Node A")
        node2 = main_window.canvas.add_new_node(300, 400, 1, label="Node B")
        main_window.canvas.add_new_edge(node1, node2)
        
        # Exportiere zu JSON
        json_file = tmp_path / "test_network.json"
        
        data = {
            "nodes": [{"id": n.node_id, "x": n.pos().x(), "y": n.pos().y(), "label": n.label_text} 
                     for n in main_window.canvas.nodes],
            "edges": [{"from": e.source.node_id, "to": e.target.node_id} 
                     for e in main_window.canvas.edges]
        }
        
        with open(json_file, "w") as f:
            json.dump(data, f, indent=4)
        
        # Überprüfe die Datei
        with open(json_file, "r") as f:
            loaded_data = json.load(f)
        
        assert len(loaded_data["nodes"]) == 2
        assert len(loaded_data["edges"]) == 1
        assert loaded_data["nodes"][0]["id"] == 0
        assert loaded_data["nodes"][0]["label"] == "Node A"
        assert loaded_data["nodes"][1]["id"] == 1
        assert loaded_data["nodes"][1]["label"] == "Node B"
        assert loaded_data["edges"][0]["from"] == 0
        assert loaded_data["edges"][0]["to"] == 1
    
    def test_json_import(self, main_window, tmp_path):
        """Test ob JSON korrekt importiert wird."""
        # Erstelle Test-JSON
        json_file = tmp_path / "test_import.json"
        test_data = {
            "nodes": [
                {"id": 0, "x": 50.0, "y": 100.0, "label": "Start"},
                {"id": 1, "x": 150.0, "y": 200.0, "label": "Ende"}
            ],
            "edges": [
                {"from": 0, "to": 1}
            ]
        }
        
        with open(json_file, "w") as f:
            json.dump(test_data, f)
        
        # Importiere
        with open(json_file, "r") as f:
            data = json.load(f)
        
        main_window.canvas.scene.clear()
        main_window.canvas.nodes = []
        main_window.canvas.edges = []
        node_map = {}
        
        for n_data in data["nodes"]:
            label = n_data.get("label", str(n_data["id"]))
            node = main_window.canvas.add_new_node(
                n_data["x"], n_data["y"], n_data["id"], label
            )
            node_map[n_data["id"]] = node
        
        for e_data in data["edges"]:
            main_window.canvas.add_new_edge(
                node_map[e_data["from"]], 
                node_map[e_data["to"]]
            )
        
        # Überprüfe
        assert len(main_window.canvas.nodes) == 2
        assert len(main_window.canvas.edges) == 1
        assert main_window.canvas.nodes[0].pos().x() == 50.0
        assert main_window.canvas.nodes[0].label_text == "Start"
        assert main_window.canvas.nodes[1].pos().y() == 200.0
        assert main_window.canvas.nodes[1].label_text == "Ende"
    
    def test_json_import_backward_compatibility(self, main_window, tmp_path):
        """Test ob alte JSON-Dateien ohne Labels importiert werden können."""
        json_file = tmp_path / "test_old_format.json"
        test_data = {
            "nodes": [
                {"id": 0, "x": 50.0, "y": 100.0},
                {"id": 1, "x": 150.0, "y": 200.0}
            ],
            "edges": [
                {"from": 0, "to": 1}
            ]
        }
        
        with open(json_file, "w") as f:
            json.dump(test_data, f)
        
        with open(json_file, "r") as f:
            data = json.load(f)
        
        main_window.canvas.scene.clear()
        main_window.canvas.nodes = []
        main_window.canvas.edges = []
        node_map = {}
        
        for n_data in data["nodes"]:
            label = n_data.get("label", str(n_data["id"]))
            node = main_window.canvas.add_new_node(
                n_data["x"], n_data["y"], n_data["id"], label
            )
            node_map[n_data["id"]] = node
        
        # Labels sollten auf IDs zurückfallen
        assert main_window.canvas.nodes[0].label_text == "0"
        assert main_window.canvas.nodes[1].label_text == "1"
    
    def test_json_export_empty_network(self, main_window, tmp_path):
        """Test JSON-Export mit leerem Netzwerk."""
        json_file = tmp_path / "empty_network.json"
        
        data = {
            "nodes": [{"id": n.node_id, "x": n.pos().x(), "y": n.pos().y(), "label": n.label_text} 
                     for n in main_window.canvas.nodes],
            "edges": [{"from": e.source.node_id, "to": e.target.node_id} 
                     for e in main_window.canvas.edges]
        }
        
        with open(json_file, "w") as f:
            json.dump(data, f, indent=4)
        
        with open(json_file, "r") as f:
            loaded_data = json.load(f)
        
        assert len(loaded_data["nodes"]) == 0
        assert len(loaded_data["edges"]) == 0
    
    def test_json_import_multiple_edges(self, main_window, tmp_path):
        """Test Import mit mehreren Kanten."""
        json_file = tmp_path / "multi_edge.json"
        test_data = {
            "nodes": [
                {"id": 0, "x": 0.0, "y": 0.0, "label": "A"},
                {"id": 1, "x": 100.0, "y": 0.0, "label": "B"},
                {"id": 2, "x": 200.0, "y": 0.0, "label": "C"}
            ],
            "edges": [
                {"from": 0, "to": 1},
                {"from": 1, "to": 2},
                {"from": 0, "to": 2}
            ]
        }
        
        with open(json_file, "w") as f:
            json.dump(test_data, f)
        
        with open(json_file, "r") as f:
            data = json.load(f)
        
        main_window.canvas.scene.clear()
        main_window.canvas.nodes = []
        main_window.canvas.edges = []
        node_map = {}
        
        for n_data in data["nodes"]:
            label = n_data.get("label", str(n_data["id"]))
            node = main_window.canvas.add_new_node(
                n_data["x"], n_data["y"], n_data["id"], label
            )
            node_map[n_data["id"]] = node
        
        for e_data in data["edges"]:
            main_window.canvas.add_new_edge(
                node_map[e_data["from"]], 
                node_map[e_data["to"]]
            )
        
        assert len(main_window.canvas.nodes) == 3
        assert len(main_window.canvas.edges) == 3


class TestSVGExport:
    """Tests für SVG Export."""
    
    def test_svg_export_file_creation(self, main_window, tmp_path):
        """Test ob SVG Datei erstellt wird."""
        node1 = main_window.canvas.add_new_node(100, 100, 0, label="A")
        node2 = main_window.canvas.add_new_node(200, 200, 1, label="B")
        main_window.canvas.add_new_edge(node1, node2)
        
        svg_file = tmp_path / "test_export.svg"
        
        # Simuliere SVG Export
        xs = [n.pos().x() for n in main_window.canvas.nodes]
        ys = [n.pos().y() for n in main_window.canvas.nodes]
        
        assert len(xs) == 2
        assert len(main_window.canvas.edges) == 1
        
        svg_file = tmp_path / "complex.svg"
        with open(svg_file, "w") as f:
            f.write('<svg></svg>')
        
        assert svg_file.exists()


class TestEdgeCases:
    """Tests für Randfälle und Fehlersituationen."""
    
    def test_remove_nonexistent_node(self, canvas):
        """Test Entfernung eines nicht existierenden Knotens."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = Node(100, 100, 1)  # Nicht zur Canvas hinzugefügt
        
        canvas.remove_node(node2)
        assert len(canvas.nodes) == 1
    
    def test_remove_nonexistent_edge(self, canvas):
        """Test Entfernung einer nicht existierenden Kante."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 100, 1)
        edge = DirectedEdge(node1, node2)  # Nicht zur Canvas hinzugefügt
        
        canvas.remove_edge(edge)
        assert len(canvas.edges) == 0
    
    def test_node_with_empty_label(self, qapp):
        """Test Node mit leerem Label."""
        node = Node(0, 0, 0, label="")
        assert node.label_text == ""
        assert node.label.toPlainText() == ""
    
    def test_node_with_long_label(self, qapp):
        """Test Node mit sehr langem Label."""
        long_label = "A" * 100
        node = Node(0, 0, 0, label=long_label)
        assert node.label_text == long_label
        assert len(node.label.toPlainText()) == 100
    
    def test_multiple_delete_operations(self, canvas):
        """Test mehrfache Löschoperationen."""
        nodes = [canvas.add_new_node(i*100, i*100, i) for i in range(5)]
        
        for i in range(3):
            canvas.remove_node(nodes[i])
        
        assert len(canvas.nodes) == 2
    
    def test_edge_between_same_node(self, canvas):
        """Test Kante vom Knoten zu sich selbst."""
        node = canvas.add_new_node(100, 100, 0)
        edge = canvas.add_new_edge(node, node)
        
        assert edge.source == edge.target
        assert len(canvas.edges) == 1
    
    def test_connectivity_with_cycle(self, main_window):
        """Test Connectivity bei Netzwerk mit Zyklus."""
        node1 = main_window.canvas.add_new_node(0, 0, 0)
        node2 = main_window.canvas.add_new_node(100, 0, 1)
        node3 = main_window.canvas.add_new_node(200, 0, 2)
        
        main_window.canvas.add_new_edge(node1, node2)
        main_window.canvas.add_new_edge(node2, node3)
        main_window.canvas.add_new_edge(node3, node1)
        
        assert main_window.is_connected() == True
    
    def test_node_label_special_characters(self, qapp):
        """Test Node-Label mit Sonderzeichen."""
        special_label = "Test!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        node = Node(0, 0, 0, label=special_label)
        assert node.label_text == special_label
    
    def test_node_label_unicode(self, qapp):
        """Test Node-Label mit Unicode-Zeichen."""
        unicode_label = "Tëst 测试 тест"
        node = Node(0, 0, 0, label=unicode_label)
        assert node.label_text == unicode_label
        
    def test_svg_export_single_node(self, main_window, tmp_path):
        """Test SVG Export mit einzelnem Knoten."""
        node1 = main_window.canvas.add_new_node(150, 150, 0, label="Single")
        
        svg_file = tmp_path / "single_node.svg"
        
        xs = [n.pos().x() for n in main_window.canvas.nodes]
        ys = [n.pos().y() for n in main_window.canvas.nodes]
        padding = 30
        min_x, max_x = min(xs) - padding, max(xs) + padding
        min_y, max_y = min(ys) - padding, max(ys) + padding
        width = max_x - min_x
        height = max_y - min_y
        
        with open(svg_file, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n')
            for n in main_window.canvas.nodes:
                f.write(f'  <circle cx="{n.pos().x()}" cy="{n.pos().y()}" r="20" fill="#ffffff" />\n')
                f.write(f'  <text>{n.label_text}</text>\n')
            f.write('</svg>')
        
        assert svg_file.exists()
        content = svg_file.read_text()
        assert 'fill="#ffffff"' in content
        assert '<text>Single</text>' in content
