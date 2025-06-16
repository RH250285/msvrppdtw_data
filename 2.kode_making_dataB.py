import json
import random
import numpy as np

# PARAMETER
num_suppliers = 9
num_customers = 3
depot_id = 0
max_vehicles = 40

random.seed(42)
np.random.seed(42)

scenarios = {
    "B1": {"pairing_counts": [3]*3,
           "mode": "cluster", "vehicle_cap": 500,
           "tw_tight": False, "demand_scale": 1.0, "cluster_tightness": 10},
}

def get_supplier_xy(idx, mode, tightness=10):
    cx, cy = 20, 50
    return float(np.random.normal(cx, tightness)), float(np.random.normal(cy, tightness))

def get_customer_xy(idx, mode, tightness=10):
    cx, cy = 80, 50
    return float(np.random.normal(cx, tightness)), float(np.random.normal(cy, tightness))

for scenario_name, cfg in scenarios.items():
    counts = cfg["pairing_counts"]
    mode = cfg["mode"]
    cap = cfg["vehicle_cap"]
    scale = cfg.get("demand_scale", 1.0)
    tightness = cfg.get("cluster_tightness", 10)

    # --------- PAIRINGS ---------
    pairings = []
    supplier_ids = list(range(1, num_suppliers + 1))
    customer_ids = list(range(num_suppliers + 1, num_suppliers + 1 + num_customers))
    sid_ptr = 0
    for cid, n_pairs in zip(customer_ids, counts):
        for _ in range(n_pairs):
            pairings.append([int(supplier_ids[sid_ptr]), int(cid)])
            sid_ptr += 1
    # --------- END PAIRINGS ----------

    # ---- Depot node ----
    nodes = [{
        "id": depot_id,
        "x": 50.0, "y": 50.0,
        "demand": 0,
        "tw": [0, 10000],   # Lebar untuk fleksibilitas awal
        "service": 0
    }]

    # ---- Suppliers ----
    supplier_nodes = []
    for i in range(1, num_suppliers + 1):
        x, y = get_supplier_xy(i, mode, tightness)
        demand = -int(random.randint(5, 20) * scale)
        service = random.randint(1, 3)
        supplier_nodes.append({
            "id":      i,
            "x":       float(x),
            "y":       float(y),
            "demand":  demand,
            "tw":      [random.randint(0, 5000), 6000],  # masih longgar, untuk konstruksi realistis
            "service": service
        })
    nodes.extend(supplier_nodes)

    # ---- Customers ----
# ---- Customers ---- (TW disesuaikan dari latest TW supplier + travel)
    customer_nodes = []
    for idx, cid in enumerate(customer_ids, start=1):
        x, y = get_customer_xy(idx, mode, tightness)
        related_suppliers = [sid for sid, ccid in pairings if ccid == cid]
        total_demand = sum(-supplier_nodes[sid - 1]["demand"] for sid in related_suppliers)
        service = random.randint(1, 3)

        latest_supplier_time = 0
        for sid in related_suppliers:
            s = supplier_nodes[sid - 1]
            s_end = s["tw"][1]
            s_serv = s["service"]
            dist = np.hypot(x - s["x"], y - s["y"])
            latest_arrival = s_end + s_serv + dist
            latest_supplier_time = max(latest_supplier_time, latest_arrival)

        earliest_customer = int(np.ceil(latest_supplier_time))
        tw_start = earliest_customer
        tw_end = earliest_customer + 1000  # 1000 unit buffer

        customer_nodes.append({
            "id": int(cid),
            "x": float(x),
            "y": float(y),
            "demand": total_demand,
            "tw": [tw_start, tw_end],
            "service": service
        })

    nodes.extend(customer_nodes)

    coords = [(n["x"], n["y"]) for n in nodes]
    distance_matrix = [
        [round(np.hypot(coords[i][0] - coords[j][0],
                        coords[i][1] - coords[j][1]), 2)
         for j in range(len(nodes))]
        for i in range(len(nodes))
    ]

    output = {
        "depot_id":       depot_id,
        "depot_index":    depot_id,
        "vehicle_cap":    cap,
        "max_vehicles":   max_vehicles,
        "nodes":          nodes,
        "pairings":       pairings,
        "distance_matrix": distance_matrix,
    }

    print("Contoh pairing:", pairings[:5])
    filename = f"experimentB_{scenario_name}_msvrppdtw.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    print(f"File '{filename}' berhasil dibuat.")
