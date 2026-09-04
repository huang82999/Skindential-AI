import subprocess
import os
import time

DATA_YAML = r"E:\old\blackbridge_yolo_micro\data.yaml"
PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
RUN_NAME = "micro_run_480_patch"

print("=== Starting Micro Model Training (480x480 Native Patches for Acne/Pores/Spots) ===")

cmd = [
    "yolo", "detect", "train",
    "model=yolo26m.pt",
    f"data={DATA_YAML}",
    "epochs=80",
    "imgsz=480",
    "batch=16",
    "workers=4",
    "device=0",
    f"project={PROJECT_DIR}",
    f"name={RUN_NAME}",
    "exist_ok=True",
    "cls=1.0",
    "mixup=0.0",
    "mosaic=1.0",
    "flipud=0.5",
    "cos_lr=True"
]

start = time.time()
subprocess.run(cmd, check=True)
print(f"=== Micro Model Training Completed! Time: {(time.time()-start)/60:.2f} mins ===")
