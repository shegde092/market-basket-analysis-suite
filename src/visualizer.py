import os
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

def generate_network_graphs(rules_df, static_png_path, interactive_html_path, min_confidence=0.6, min_lift=1.2):
    """
    Builds and saves a NetworkX directed graph representation of association rules.
    1. Pre-filters rules (min_confidence and min_lift) to avoid a chaotic 'hairball'.
    2. Maps nodes to products (size representing product support).
    3. Maps edges to rule associations (thickness/weight representing Lift).
    4. Generates a static PNG visualization.
    5. Generates a physics-enabled dynamic HTML graph via PyVis.
    """
    # Create output directories if they don't exist
    os.makedirs(os.path.dirname(static_png_path), exist_ok=True)
    os.makedirs(os.path.dirname(interactive_html_path), exist_ok=True)
    
    if rules_df.empty:
        print("No association rules available to visualize.")
        # Create blank files or return
        return False
        
    # ANTI-HAIRBALL FILTERING:
    # Filter rules to only show strong rules for a cleaner graph visualization
    strong_rules = rules_df[
        (rules_df['confidence'] >= min_confidence) & 
        (rules_df['lift'] >= min_lift)
    ].copy()
    
    # If the filtered rules dataframe is too small, relax the filter slightly so something shows up
    if len(strong_rules) < 5 and len(rules_df) >= 5:
        strong_rules = rules_df.head(25) # Just show the top 25 rules by lift
    elif len(strong_rules) > 100:
        strong_rules = strong_rules.head(100) # Cap at top 100 to prevent crash / massive hairball
        
    if strong_rules.empty:
        print("No strong rules met the visualizer thresholds. Graph not generated.")
        return False
        
    print(f"Creating network visual graph with {len(strong_rules)} rules...")

    # Build NetworkX Directed Graph
    G = nx.DiGraph()
    
    # Store item supports to scale node sizes
    item_support = {}
    
    # Add nodes and edges from filtered rules
    for _, row in strong_rules.iterrows():
        ant_str = row['antecedents_str']
        con_str = row['consequents_str']
        
        # Split multiple items in antecedent/consequent if they exist
        ants = [a.strip() for a in ant_str.split(',')]
        cons = [c.strip() for c in con_str.split(',')]
        
        # Capture support values for scaling node sizes
        for a in ants:
            # support of antecedent is a proxy for item support
            item_support[a] = max(item_support.get(a, 0.0), row['antecedent_support'])
        for c in cons:
            # support of consequent is a proxy for item support
            item_support[c] = max(item_support.get(c, 0.0), row['consequent_support'])
            
        # Draw edges between all combinations of antecedents and consequents
        for a in ants:
            for c in cons:
                # Add edge with metrics
                G.add_edge(
                    a, c, 
                    weight=float(row['lift']), 
                    support=float(row['support']),
                    confidence=float(row['confidence']),
                    lift=float(row['lift'])
                )
                
    # If no nodes got created
    if not G.nodes:
        return False
        
    # Set node attributes for support
    for node in G.nodes:
        G.nodes[node]['support'] = item_support.get(node, 0.01)

    # ------------------
    # STATIC GRAPH (PNG)
    # ------------------
    plt.figure(figsize=(12, 10), dpi=300)
    
    # Layout positions using spring layout
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Scale node sizes based on support (e.g. support * 5000 + 100)
    node_sizes = [G.nodes[node]['support'] * 8000 + 300 for node in G.nodes]
    
    # Scale edge widths based on Lift
    edge_widths = [G[u][v]['lift'] * 0.8 for u, v in G.edges]
    
    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, 
        node_size=node_sizes, 
        node_color='skyblue', 
        edgecolors='navy',
        alpha=0.85
    )
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos, 
        width=edge_widths, 
        edge_color='grey', 
        alpha=0.6, 
        arrowsize=15,
        arrowstyle='-|>'
    )
    
    # Draw labels
    nx.draw_networkx_labels(
        G, pos, 
        font_size=8, 
        font_family='sans-serif', 
        font_weight='bold'
    )
    
    plt.title("Market Basket Analysis - Product Association Clusters\n(Node Size: Support | Edge Thickness: Lift)", fontsize=14, fontweight='bold', pad=15)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(static_png_path, format="png", bbox_inches='tight')
    plt.close()
    
    # ----------------------
    # INTERACTIVE GRAPH (HTML)
    # ----------------------
    # Initialize PyVis network
    net = Network(
        height="650px", 
        width="100%", 
        directed=True, 
        bgcolor="#1e1e1e", 
        font_color="#ffffff",
        heading=""
    )
    
    # Custom physics parameters to organize clusters beautifully
    net.set_options("""
    var options = {
      "nodes": {
        "borderWidth": 2,
        "borderWidthSelected": 4,
        "font": {
          "size": 14,
          "face": "Tahoma"
        },
        "color": {
          "border": "#3b82f6",
          "background": "#1e293b",
          "highlight": {
            "border": "#60a5fa",
            "background": "#0f172a"
          }
        }
      },
      "edges": {
        "color": {
          "color": "#64748b",
          "highlight": "#3b82f6",
          "inherit": false
        },
        "smooth": {
          "type": "continuous",
          "forceDirection": "none"
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -60,
          "centralGravity": 0.015,
          "springLength": 120,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
          "enabled": true,
          "iterations": 100
        }
      }
    }
    """)
    
    # Add nodes to PyVis graph
    for node in G.nodes:
        support = G.nodes[node]['support']
        # Node size scaling
        size = float(support * 150 + 12)
        # Node label and detailed tooltip
        title = f"Product: {node}<br>Support: {support:.4f} ({support*100:.2f}%)"
        
        net.add_node(
            node, 
            label=node, 
            size=size, 
            title=title,
            color={"background": "#1e293b", "border": "#3b82f6"}
        )
        
    # Add edges to PyVis graph
    for u, v in G.edges:
        edge_data = G[u][v]
        lift = edge_data['lift']
        conf = edge_data['confidence']
        supp = edge_data['support']
        
        # Thickness representation
        width = float(max(1.0, lift * 1.5))
        title = f"Rule: {u} &rarr; {v}<br>Confidence: {conf:.4f} ({conf*100:.1f}%)<br>Lift: {lift:.2f}<br>Support: {supp:.4f}"
        
        net.add_edge(
            u, v, 
            width=width, 
            title=title,
            arrowStrikethrough=False
        )
        
    # Save the PyVis interactive graph
    net.save_graph(interactive_html_path)
    print(f"Interactive PyVis network saved successfully to {interactive_html_path}")
    return True
