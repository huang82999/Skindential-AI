import subprocess
import os
import time
import json
import csv

PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
DATA_YAML = r"E:\old\blackbridge_yolo_5group\data.yaml"
LOG_FILE = r"E:\old\research_log_phase5.json"

print("=== Starting Auto Trial-and-Error Optimizer V4 (Advanced Augmentation) ===")
print("Baseline: yolo26l.pt (mAP50: 18.22%)")

trials = [
    {
        "name": "trial_yolo26l_rotation",
        "desc": "Adding 90-degree rotation. Skin lesions are rotation invariant.",
        "params": {"model": "yolo26l.pt", "degrees": "90.0", "imgsz": "480", "batch": "12", "dfl": "2.0"}
    },
    {
        "name": "trial_yolo26l_hsv",
        "desc": "Adding HSV saturation/value augmentation to simulate lighting/skin tone variations.",
        "params": {"model": "yolo26l.pt", "hsv_s": "0.5", "hsv_v": "0.5", "imgsz": "480", "batch": "12", "dfl": "2.0"}
    },
    {
        "name": "trial_yolo26l_no_mosaic",
        "desc": "Disabling Mosaic. Mosaic can cut small lesions at borders. Testing pure native patches.",
        "params": {"model": "yolo26l.pt", "mosaic": "0.0", "imgsz": "480", "batch": "12", "dfl": "2.0"}
    }
]

results_log = []

for idx, t in enumerate(trials):
    name = t["name"]
    print(f"\n[{idx+1}/{len(trials)}] Starting Trial: {name}")
    
    cmd = [
        "yolo", "detect", "train",
        f"data={DATA_YAML}",
        "epochs=40", # Fast trial
        "workers=4",
        "device=0",
        f"project={PROJECT_DIR}",
        f"name={name}",
        "exist_ok=True",
        "cls=0.5",
        "mixup=0.0",
        "cos_lr=True"
    ]
    
    # Inject dynamic params
    for k, v in t["params"].items():
        cmd.append(f"{k}={v}")
        
    start_time = time.time()
    try:
        subprocess.run(cmd, check=True)
        dur = time.time() - start_time
        
        # Parse result
        csv_path = os.path.join(PROJECT_DIR, name, "results.csv")
        best_map = 0
        best_r = 0
        best_p = 0
        if os.path.exists(csv_path):
            with open(csv_path, "r") as f:
                reader = list(csv.reader(f))
                if len(reader) > 1:
                    header = [h.strip() for h in reader[0]]
                    for row in reader[1:]:
                        vals = [v.strip() for v in row]
                        try:
                            m = float(vals[header.index("metrics/mAP50(B)")])
                            if m > best_map:
                                best_map = m
                                best_r = float(vals[header.index("metrics/recall(B)")])
                                best_p = float(vals[header.index("metrics/precision(B)")])
                        except: pass
                        
        print(f"[{name}] Completed in {dur/60:.2f} mins. Best mAP50: {best_map*100:.2f}%")
        
        results_log.append({
            "trial_name": name,
            "description": t["desc"],
            "parameters": t["params"],
            "duration_mins": round(dur/60, 2),
            "metrics": {
                "mAP50": round(best_map * 100, 2),
                "recall": round(best_r * 100, 2),
                "precision": round(best_p * 100, 2)
            }
        })
        
    except subprocess.CalledProcessError as e:
        print(f"[{name}] FAILED: {e}")

# Save to log file
with open(LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(results_log, f, indent=4, ensure_ascii=False)

print(f"\n=== Auto Trial-and-Error Optimizer V4 Finished ===")
print(f"Log saved to {LOG_FILE}")
