import subprocess
import os
import time
import json

DATA_YAML = r"E:\old\blackbridge_yolo_5group\data.yaml"
PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"

# Define the trial configurations
trials = [
    {
        "name": "trial_dfl_2_5",
        "model": "yolo26m.pt",
        "imgsz": "480",
        "dfl": "2.5",
        "cls": "0.5",
        "batch": "16"
    },
    {
        "name": "trial_imgsz_512",
        "model": "yolo26m.pt",
        "imgsz": "512",
        "dfl": "2.0",
        "cls": "0.5",
        "batch": "12" # slightly smaller batch for larger image
    },
    {
        "name": "trial_model_yolo26l",
        "model": "yolo26l.pt",
        "imgsz": "480",
        "dfl": "2.0",
        "cls": "0.5",
        "batch": "12" # slightly smaller batch for larger model
    }
]

print("=== Starting Auto Trial-and-Error Optimizer ===")

history = []

for idx, config in enumerate(trials):
    print(f"\n[{idx+1}/{len(trials)}] Starting Trial: {config['name']}")
    start_time = time.time()
    
    cmd = [
        "yolo", "detect", "train",
        f"model={config['model']}",
        f"data={DATA_YAML}",
        "epochs=40",  # shorter epochs for fast trial
        f"imgsz={config['imgsz']}",
        f"batch={config['batch']}",
        "workers=4",
        "device=0",
        f"project={PROJECT_DIR}",
        f"name={config['name']}",
        "exist_ok=True",
        f"dfl={config['dfl']}",
        f"cls={config['cls']}",
        "mixup=0.0",
        "mosaic=1.0",
        "flipud=0.5",
        "cos_lr=True"
    ]
    
    try:
        # Run YOLO training
        subprocess.run(cmd, check=True)
        dur = time.time() - start_time
        print(f"[{config['name']}] Completed in {dur/60:.2f} mins.")
        
        # We assume the results will be printed or we can parse results.csv later
        # For this script, we just run them sequentially.
        
    except subprocess.CalledProcessError as e:
        print(f"[{config['name']}] FAILED: {e}")

print("\n=== Auto Trial-and-Error Optimizer Finished ===")
