import subprocess
import os
import time

DATA_YAML = r"E:\old\blackbridge_yolo_macro\data.yaml"
PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
RUN_NAME = "macro_run_640_full"

print("=== Starting Macro Model Training (640x640 Full Image for Wrinkles/Dark Circles) ===")

cmd = [
    "yolo", "detect", "train",
    "model=yolo26m.pt",
    f"data={DATA_YAML}",
    "epochs=80",
    "imgsz=640",
    "batch=16",
    "workers=4",
    "device=0",
    f"project={PROJECT_DIR}",
    f"name={RUN_NAME}",
    "exist_ok=True"
]

start = time.time()
subprocess.run(cmd, check=True)
print(f"=== Macro Model Training Completed! Time: {(time.time()-start)/60:.2f} mins ===")
