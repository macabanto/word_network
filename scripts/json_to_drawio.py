import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import math
import random
import argparse

def create_drawio_xml(json_data):
    # Create the basic structure for the mxfile
    mxfile = ET.Element("mxfile")
    mxfile.set("host", "Electron")
    mxfile.set("agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) draw.io/26.2.2 Chrome/134.0.6998.178 Electron/35.1.2 Safari/537.36")
    mxfile.set("version", "26.2.2")
    
    diagram = ET.SubElement(mxfile, "diagram")
    diagram.set("name", "Page-1")
    diagram.set("id", "WceRunY-fH3GrYMkFwZS")
    
    graph_model = ET.SubElement(diagram, "mxGraphModel")
    graph_model.set("dx", "948")
    graph_model.set("dy", "732")
    graph_model.set("grid", "1")
    graph_model.set("gridSize", "10")
    graph_model.set("guides", "1")
    graph_model.set("tooltips", "1")
    graph_model.set("connect", "1")
    graph_model.set("arrows", "1")
    graph_model.set("fold", "1")
    graph_model.set("page", "1")
    graph_model.set("pageScale", "1")
    graph_model.set("pageWidth", "1500")
    graph_model.set("pageHeight", "1500")
    graph_model.set("math", "0")
    graph_model.set("shadow", "0")
    
    root = ET.SubElement(graph_model, "root")
    
    # Create default cells
    cell0 = ET.SubElement(root, "mxCell")
    cell0.set("id", "0")
    
    cell1 = ET.SubElement(root, "mxCell")
    cell1.set("id", "1")
    cell1.set("parent", "0")
    
    # Parse the JSON data
    data = json.loads(json_data)
    
    # Keep track of nodes we've already created
    created_nodes = set()
    
    # Calculate positions for nodes to avoid overlapping
    # We'll use a simple radial layout algorithm
    nodes_positions = position_nodes_radially(data)
    
    # Create nodes and connections
    for node_id, node_data in data.items():
        if node_id not in created_nodes:
            create_node(root, node_id, node_data, nodes_positions)
            created_nodes.add(node_id)
        
        # Create connections to synonyms
        for synonym_id in node_data.get("synonyms", []):
            # Only create edges for hexadecimal IDs (not text synonyms)
            if synonym_id.strip() and len(synonym_id) == 10 and all(c in "0123456789abcdef" for c in synonym_id):
                create_connection(root, node_id, synonym_id)
                
                # Add the synonym node if it's in our data but hasn't been created yet
                if synonym_id in data and synonym_id not in created_nodes:
                    create_node(root, synonym_id, data[synonym_id], nodes_positions)
                    created_nodes.add(synonym_id)
    
    # Convert the XML to a string with proper formatting
    rough_string = ET.tostring(mxfile, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def position_nodes_radially(data):
    """
    Position nodes in a radial layout to avoid overlapping.
    Central nodes with many connections are placed in the center.
    """
    # Count connections for each node
    connection_counts = {}
    for node_id, node_data in data.items():
        connection_counts[node_id] = len(node_data.get("synonyms", []))
        for synonym_id in node_data.get("synonyms", []):
            if len(synonym_id) == 10 and all(c in "0123456789abcdef" for c in synonym_id):
                connection_counts[synonym_id] = connection_counts.get(synonym_id, 0) + 1
    
    # Sort nodes by number of connections
    sorted_nodes = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)
    
    positions = {}
    center_x, center_y = 750, 750  # Center of the page
    
    # Place the most connected nodes in the center
    central_nodes = sorted_nodes[:5]  # Top 5 most connected nodes
    central_radius = 200
    for i, (node_id, _) in enumerate(central_nodes):
        angle = 2 * math.pi * i / len(central_nodes)
        if i == 0:  # Most connected node goes in the very center
            positions[node_id] = (center_x, center_y)
        else:
            x = center_x + central_radius * math.cos(angle)
            y = center_y + central_radius * math.sin(angle)
            positions[node_id] = (x, y)
    
    # Place the rest of the nodes in concentric circles
    remaining_nodes = sorted_nodes[5:]
    radius_increment = 150
    nodes_per_circle = 12
    
    for i, (node_id, _) in enumerate(remaining_nodes):
        circle_num = i // nodes_per_circle + 1
        pos_in_circle = i % nodes_per_circle
        
        radius = central_radius + circle_num * radius_increment
        angle = 2 * math.pi * pos_in_circle / nodes_per_circle
        # Add a small random offset to avoid perfect alignment
        angle_offset = random.uniform(-0.1, 0.1)
        
        x = center_x + radius * math.cos(angle + angle_offset)
        y = center_y + radius * math.sin(angle + angle_offset)
        
        positions[node_id] = (x, y)
    
    return positions

def create_node(parent, node_id, node_data, positions):
    """Create a node in the XML tree"""
    # Get position or use default
    x, y = positions.get(node_id, (300 + random.randint(-100, 100), 300 + random.randint(-100, 100)))
    
    # Set color based on term type
    term = node_data.get("term", "")
    if term == "term":
        fill_color = "#FF7F50"  # Coral
    elif term == "word":
        fill_color = "#6495ED"  # CornflowerBlue
    elif term == "name":
        fill_color = "#9ACD32"  # YellowGreen
    else:
        fill_color = "#D3D3D3"  # LightGray
    
    # Create the node
    cell = ET.SubElement(parent, "mxCell")
    cell.set("id", node_id)
    
    # Add term name to the label if available
    label = node_id
    if "term" in node_data and node_data["term"]:
        label += f"\n{node_data['term']}"
    if "part_of_speech" in node_data and node_data["part_of_speech"]:
        label += f" {node_data['part_of_speech']}"
    
    cell.set("value", label)
    cell.set("style", f"ellipse;whiteSpace=wrap;html=1;fillColor={fill_color};")
    cell.set("vertex", "1")
    cell.set("parent", "1")
    
    # Add geometry
    geometry = ET.SubElement(cell, "mxGeometry")
    geometry.set("x", str(int(x)))
    geometry.set("y", str(int(y)))
    geometry.set("width", "120")
    geometry.set("height", "80")
    geometry.set("as", "geometry")

def create_connection(parent, source_id, target_id):
    """Create a connection between two nodes"""
    # Create a unique ID for the edge
    edge_id = f"{source_id}_to_{target_id}"
    
    # Create the edge
    cell = ET.SubElement(parent, "mxCell")
    cell.set("id", edge_id)
    cell.set("value", "")
    cell.set("style", "endArrow=classic;html=1;rounded=0;")
    cell.set("edge", "1")
    cell.set("parent", "1")
    cell.set("source", source_id)
    cell.set("target", target_id)
    
    # Add geometry
    geometry = ET.SubElement(cell, "mxGeometry")
    geometry.set("width", "50")
    geometry.set("height", "50")
    geometry.set("relative", "1")
    geometry.set("as", "geometry")

def main():
    parser = argparse.ArgumentParser(description='Convert JSON data to draw.io XML format')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('output_file', help='Output XML file path')
    
    args = parser.parse_args()
    
    # Read the JSON data
    with open(args.input_file, 'r') as file:
        json_data = file.read()
    
    # Create the draw.io XML
    xml_output = create_drawio_xml(json_data)
    
    # Write the XML to file
    with open(args.output_file, 'w') as file:
        file.write(xml_output)
    
    print(f"Successfully converted {args.input_file} to draw.io XML format at {args.output_file}")

if __name__ == "__main__":
    main()