# data/txt_to_json.py
import json
from pathlib import Path

def parse_li_lim_file(txt_path, json_path, vehicle_cap=1000, max_vehicles=25):
    """
    Konversi file .txt benchmark Li & Lim menjadi JSON siap pakai
    untuk fungsi load_pairings(). Format output akan menyertakan:
      - "depot_id"
      - "vehicle_cap", "max_vehicles"
      - "nodes": semua node (dengan id, koordinat, demand, tw, service)
      - "pairings": list pasangan [pickup_id, delivery_id]
    """
    txt_path = Path(txt_path)
    lines = txt_path.read_text().splitlines()

    if len(lines) < 2:
        raise ValueError("❌ File terlalu pendek!")

    # 1. Parse node lines (skip first line)
    raw_nodes = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) < 9 or not parts[0].isdigit():
            continue
        raw_nodes.append({
            "id": int(parts[0]),
            "x": float(parts[1]),
            "y": float(parts[2]),
            "demand": int(parts[3]),
            "tw": [int(float(parts[4])), int(float(parts[5]))],
            "service": int(float(parts[6])),
            "pA": int(parts[7]),
            "pB": int(parts[8]),
        })

    # 2. Susun nodes list
    nodes = []
    for r in raw_nodes:
        nodes.append({
            "id": r["id"],
            "x": r["x"],
            "y": r["y"],
            "demand": r["demand"],
            "tw": r["tw"],
            "service": r["service"],
        })

    # 3. Susun pairings (ambil dari pickup)
    pairings = []
    for r in raw_nodes:
        if r["demand"] > 0:  # node ini pickup
            pairings.append([r["id"], r["pB"]])

    if not pairings:
        raise ValueError("❌ Tidak ada pasangan pickup–delivery yang valid!")

    # 4. Susun output JSON sesuai format standar
    out = {
        "depot_id": 0,
        "vehicle_cap": vehicle_cap,
        "max_vehicles": max_vehicles,
        "nodes": nodes,
        "pairings": pairings,
    }

    # 5. Tulis ke file JSON
    json_path = Path(json_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(out, indent=2))

    print(f"✅ JSON ditulis ke {json_path}")
    print(f"   Nodes: {len(nodes)}, Pairings: {len(pairings)}")

# Contoh pemanggilan langsung
if __name__ == "__main__":
    parse_li_lim_file("data/lrc205.txt", "data/lrc205_pairings.json")