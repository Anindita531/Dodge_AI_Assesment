import pandas as pd
import sqlite3

conn = sqlite3.connect("data.db")
# Load joined data
query = """
SELECT 
    i.invoice_id,
    i.customer_id,
    ii.product_id,
    ii.delivery_id,
    p.payment_id
FROM invoices i
JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
LEFT JOIN payments p ON i.invoice_id = p.invoice_id
"""

df = pd.read_sql(query, conn)
nodes = set()
edges = []

for _, row in df.iterrows():
    
    # Nodes
    nodes.add(("customer_" + str(row.customer_id), "Customer"))
    nodes.add(("invoice_" + str(row.invoice_id), "Invoice"))
    nodes.add(("product_" + str(row.product_id), "Product"))
    
    if row.delivery_id:
        nodes.add(("delivery_" + str(row.delivery_id), "Delivery"))
    
    if row.payment_id:
        nodes.add(("payment_" + str(row.payment_id), "Payment"))
    
    # Edges
    edges.append(("customer_" + str(row.customer_id), "invoice_" + str(row.invoice_id), "PLACED"))
    edges.append(("invoice_" + str(row.invoice_id), "product_" + str(row.product_id), "CONTAINS"))
    
    if row.delivery_id:
        edges.append(("invoice_" + str(row.invoice_id), "delivery_" + str(row.delivery_id), "DELIVERED"))
    
    if row.payment_id:
        edges.append(("invoice_" + str(row.invoice_id), "payment_" + str(row.payment_id), "PAID"))

# Convert to JSON format
graph = {
    "nodes": [{"id": n[0], "label": n[0], "type": n[1]} for n in nodes],
    "edges": [{"source": e[0], "target": e[1], "label": e[2]} for e in edges]
}

print(len(graph["nodes"]), len(graph["edges"]))
import json

with open("graph.json", "w") as f:
    json.dump(graph, f, indent=2)

print("✅ graph.json created")