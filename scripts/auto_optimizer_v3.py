import subprocess
import os
import time

PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
DATA_YAML = r"E:\old\blackbridge_yolo_5group\data.yaml"

print("=== Starting Auto Trial-and-Error Optimizer V3 (Combined Strategy) ===")
print("Insights from V2:")
print("- DFL 2.5: mAP50 -> 18.13%")
print("- Imgsz 512: mAP50 -> 18.00%")
print("- YOLO26L: mAP50 -> 18.22%")
print("-> Strategy: Combine all three for 80 Epochs.")

cmd = [
    "yolo", "detect", "train",
    "model=yolo26l.pt",
    f"data={DATA_YAML}",
    "epochs=80",
    "imgsz=512",
    "batch=12", # Safe batch size for large model + 512 res
    "workers=4",
    "device=0",
    f"project={PROJECT_DIR}",
    "name=trial_combo_512_26l_dfl2_5",
    "exist_ok=True",
    "dfl=2.5",
    "cls=0.5",
    "mixup=0.0",
    "mosaic=1.0",
    "flipud=0.5",
    "cos_lr=True"
]

try:
    start_time = time.time()
    subprocess.run(cmd, check=True)
    dur = time.time() - start_time
    print(f"\n[trial_combo_512_26l_dfl2_5] Completed in {dur/60:.2f} mins.")
except subprocess.CalledProcessError as e:
    print(f"\n[trial_combo_512_26l_dfl2_5] FAILED: {e}")

print("\n=== Auto Trial-and-Error Optimizer V3 Finished ===")
