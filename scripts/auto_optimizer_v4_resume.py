import subprocess
import os
import time
import json
import csv

PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
DATA_YAML = r"E:\old\blackbridge_yolo_5group\data.yaml"
LOG_FILE = r"E:\old\research_log_phase5.json"

print("=== Resuming Auto Trial-and-Error Optimizer V4 (Advanced Augmentation) ===")

results_log = []

def parse_results(name, desc, params, dur):
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
    
    results_log.append({
        "trial_name": name,
        "description": desc,
        "parameters": params,
        "duration_mins": round(dur/60, 2),
        "metrics": {
            "mAP50": round(best_map * 100, 2),
            "recall": round(best_r * 100, 2),
            "precision": round(best_p * 100, 2)
        }
    })
    return best_map

# 0. We already finished trial_yolo26l_rotation, let's just parse its results
parse_results("trial_yolo26l_rotation", "Adding 90-degree rotation. Skin lesions are rotation invariant.", {"model": "yolo26l.pt", "degrees": "90.0", "imgsz": "480", "batch": "12", "dfl": "2.0"}, 0)

# 1. Resume trial_yolo26l_hsv
print("\n[2/3] Resuming Trial: trial_yolo26l_hsv")
last_pt_path = os.path.join(PROJECT_DIR, "trial_yolo26l_hsv", "weights", "last.pt")
if os.path.exists(last_pt_path):
    cmd_resume = ["yolo", "detect", "train", "resume", f"model={last_pt_path}"]
    start_time = time.time()
    try:
        subprocess.run(cmd_resume, check=True)
        dur = time.time() - start_time
        print("[trial_yolo26l_hsv] Resume and completion successful.")
        parse_results("trial_yolo26l_hsv", "Adding HSV saturation/value augmentation.", {"model": "yolo26l.pt", "hsv_s": "0.5", "hsv_v": "0.5", "imgsz": "480", "batch": "12", "dfl": "2.0"}, dur)
    except subprocess.CalledProcessError as e:
        print(f"[trial_yolo26l_hsv] FAILED during resume: {e}")
else:
    print(f"Warning: Cannot find last.pt at {last_pt_path}. Skip resume.")

# 2. Run trial_yolo26l_no_mosaic
print("\n[3/3] Starting Trial: trial_yolo26l_no_mosaic")
cmd = [
    "yolo", "detect", "train",
    f"data={DATA_YAML}",
    "epochs=40", 
    "workers=4",
    "device=0",
    f"project={PROJECT_DIR}",
    "name=trial_yolo26l_no_mosaic",
    "exist_ok=True",
    "cls=0.5",
    "mixup=0.0",
    "cos_lr=True",
    "model=yolo26l.pt", "mosaic=0.0", "imgsz=480", "batch=12", "dfl=2.0"
]
start_time = time.time()
try:
    subprocess.run(cmd, check=True)
    dur = time.time() - start_time
    print("[trial_yolo26l_no_mosaic] Completed.")
    parse_results("trial_yolo26l_no_mosaic", "Disabling Mosaic.", {"model": "yolo26l.pt", "mosaic": "0.0", "imgsz": "480", "batch": "12", "dfl": "2.0"}, dur)
except subprocess.CalledProcessError as e:
    print(f"[trial_yolo26l_no_mosaic] FAILED: {e}")

# Save Log
with open(LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(results_log, f, indent=4, ensure_ascii=False)

print(f"\n=== Auto Trial-and-Error Optimizer V4 (Resume) Finished ===")
print(f"Log saved to {LOG_FILE}")
