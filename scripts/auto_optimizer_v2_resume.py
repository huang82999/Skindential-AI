import subprocess
import os
import time

PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
DATA_YAML = r"E:\old\blackbridge_yolo_5group\data.yaml"

print("=== Resuming Auto Trial-and-Error Optimizer ===")

# 1. Resume trial_imgsz_512 (which stopped at epoch 32/40)
print("\n[1/2] Resuming Trial: trial_imgsz_512")
last_pt_path = os.path.join(PROJECT_DIR, "trial_imgsz_512", "weights", "last.pt")

if os.path.exists(last_pt_path):
    cmd_resume = [
        "yolo", "detect", "train", "resume",
        f"model={last_pt_path}"
    ]
    try:
        subprocess.run(cmd_resume, check=True)
        print("[trial_imgsz_512] Resume and completion successful.")
    except subprocess.CalledProcessError as e:
        print(f"[trial_imgsz_512] FAILED during resume: {e}")
else:
    print(f"Warning: Cannot find last.pt at {last_pt_path}. Skip resume.")

# 2. Run trial_model_yolo26l (Not yet started)
print("\n[2/2] Starting Trial: trial_model_yolo26l")
cmd_yolo26l = [
    "yolo", "detect", "train",
    "model=yolo26l.pt",
    f"data={DATA_YAML}",
    "epochs=40",
    "imgsz=480",
    "batch=12",
    "workers=4",
    "device=0",
    f"project={PROJECT_DIR}",
    "name=trial_model_yolo26l",
    "exist_ok=True",
    "dfl=2.0",
    "cls=0.5",
    "mixup=0.0",
    "mosaic=1.0",
    "flipud=0.5",
    "cos_lr=True"
]

try:
    subprocess.run(cmd_yolo26l, check=True)
    print("[trial_model_yolo26l] Completed.")
except subprocess.CalledProcessError as e:
    print(f"[trial_model_yolo26l] FAILED: {e}")

print("\n=== Auto Trial-and-Error Optimizer Finished ===")
