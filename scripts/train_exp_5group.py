import subprocess
import os
import time

DATA_YAML = r"E:\old\blackbridge_yolo_5group\data.yaml"
PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
RUN_NAME = "exp_5group_clinical_480"

print("=== Starting Experiment 1: 5-Group Clinical Hierarchy Training (480x480 Patch) ===")

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
    "dfl=2.0",
    "cls=0.5",
    "mixup=0.0",
    "mosaic=1.0",
    "flipud=0.5",
    "cos_lr=True"
]

start = time.time()
subprocess.run(cmd, check=True)
print(f"=== Experiment 1 Training Completed! Time: {(time.time()-start)/60:.2f} mins ===")
