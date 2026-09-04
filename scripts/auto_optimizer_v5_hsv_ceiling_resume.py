import subprocess
import os
import time

PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
DATA_YAML = r"E:\old\blackbridge_yolo_5group\data.yaml"

print("=== Resuming Auto Trial-and-Error Optimizer V5 (HSV Ceiling) ===")
print("The previous run was paused before epoch 1 completed. Restarting from scratch.")

cmd = [
    "yolo", "detect", "train",
    "model=yolo26l.pt",
    f"data={DATA_YAML}",
    "epochs=100",  # Extended ceiling test
    "imgsz=480",
    "batch=12",
    "workers=4",
    "device=0",
    f"project={PROJECT_DIR}",
    "name=trial_hsv_ceiling_100ep",
    "exist_ok=True", # Overwrite the empty directory from the paused run
    "dfl=2.0",
    "cls=0.5",
    "mixup=0.0",
    "mosaic=1.0",
    "flipud=0.5",
    "cos_lr=True",
    "hsv_s=0.5",
    "hsv_v=0.5"
]

try:
    start_time = time.time()
    subprocess.run(cmd, check=True)
    dur = time.time() - start_time
    print(f"\n[trial_hsv_ceiling_100ep] Completed in {dur/60:.2f} mins.")
except subprocess.CalledProcessError as e:
    print(f"\n[trial_hsv_ceiling_100ep] FAILED: {e}")

print("\n=== Auto Trial-and-Error Optimizer V5 Resume Finished ===")
