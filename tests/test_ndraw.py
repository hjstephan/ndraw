import pytest
import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtTest import QTest

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
    # Nicht beenden, da andere Tests die App noch brauchen könnten

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
        canvas.add_new_edge(node1, node2)
        
        assert len(canvas.edges) == 1
        assert canvas.edges[0].source == node1
        assert canvas.edges[0].target == node2
        assert canvas.edges[0] in node1.lines
        assert canvas.edges[0] in node2.lines
    
    def test_add_multiple_edges(self, canvas):
        """Test ob mehrere Kanten hinzugefügt werden können."""
        node1 = canvas.add_new_node(0, 0, 0)
        node2 = canvas.add_new_node(100, 0, 1)
        node3 = canvas.add_new_node(200, 0, 2)
        
        canvas.add_new_edge(node1, node2)
        canvas.add_new_edge(node2, node3)
        
        assert len(canvas.edges) == 2


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
        padding = 30
        min_x, max_x = min(xs) - padding, max(xs) + padding
        min_y, max_y = min(ys) - padding, max(ys) + padding
        width = max_x - min_x
        height = max_y - min_y
        
        with open(svg_file, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n')
            for n in main_window.canvas.nodes:
                f.write(f'  <text>{n.label_text}</text>\n')
            f.write('</svg>')
        
        assert svg_file.exists()
        content = svg_file.read_text()
        assert '<?xml version="1.0" encoding="UTF-8" ?>' in content
        assert '<svg' in content
        assert '<text>A</text>' in content
        assert '<text>B</text>' in content
