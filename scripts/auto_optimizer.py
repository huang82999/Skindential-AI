import subprocess
import os
import csv
import json
import time
import sys

# Force UTF-8 encoding for standard output on Windows to prevent CP950 encode errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Configurations
DATA_YAML = r"E:\old\blackbridge_yolo\data.yaml"
PROJECT_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
LOG_FILE = r"E:\old\optimization_history.json"

# Optimization Search Space & Parameter State
# Simple Hill-Climbing Auto-ML optimizer
def get_next_parameters(history):
    # Default initial parameters
    base_params = {
        "model": "yolo26l.pt",  # Switch to large model for maximum representation capacity
        "lr0": 0.01,
        "weight_decay": 0.0005,
        "box": 7.5,
        "cls": 0.5,
        "mixup": 0.15,
        "mosaic": 1.0,
        "epochs": 120
    }
    
    if not history:
        return base_params
        
    # Sort history by best mAP50
    sorted_history = sorted(history, key=lambda x: x.get("best_map50", 0), reverse=True)
    best_run = sorted_history[0]
    
    print(f"\n[Auto-Optimizer] Best run so far: {best_run['run_name']} with mAP50: {best_run['best_map50']:.5f}")
    
    # Clone the best parameters to mutate
    next_params = best_run["params"].copy()
    
    # Mutate parameters based on iteration index (hill climbing)
    num_runs = len(history)
    mutation_step = 0.8 if num_runs % 2 == 0 else 1.2
    
    # Cycle through variables to tune
    tune_var = ["lr0", "weight_decay", "box", "cls", "mixup"][num_runs % 5]
    
    if tune_var == "lr0":
        next_params["lr0"] = max(0.0001, min(0.05, next_params["lr0"] * mutation_step))
    elif tune_var == "weight_decay":
        next_params["weight_decay"] = max(0.0001, min(0.01, next_params["weight_decay"] * mutation_step))
    elif tune_var == "box":
        next_params["box"] = max(1.0, min(15.0, next_params["box"] * mutation_step))
    elif tune_var == "cls":
        next_params["cls"] = max(0.1, min(5.0, next_params["cls"] * mutation_step))
    elif tune_var == "mixup":
        next_params["mixup"] = max(0.0, min(0.5, next_params["mixup"] + (0.05 if mutation_step > 1 else -0.05)))
        
    return next_params

def load_history():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def extract_best_metrics(run_dir):
    results_csv = os.path.join(run_dir, "results.csv")
    if not os.path.exists(results_csv):
        return None
        
    best_map50 = 0.0
    best_precision = 0.0
    best_recall = 0.0
    
    try:
        with open(results_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Clean headers (strip spaces)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            for row in reader:
                map50 = float(row.get("metrics/mAP50(B)", 0.0))
                precision = float(row.get("metrics/precision(B)", 0.0))
                recall = float(row.get("metrics/recall(B)", 0.0))
                
                if map50 > best_map50:
                    best_map50 = map50
                    best_precision = precision
                    best_recall = recall
        return {
            "best_map50": best_map50,
            "precision": best_precision,
            "recall": best_recall
        }
    except Exception as e:
        print(f"Error reading metrics: {e}")
        return None

def auto_git_commit(run_name):
    try:
        print(f"[Auto-Optimizer] Staging files for {run_name}...")
        subprocess.run(["git", "add", f"blackbridge_yolo/yolo_runs/{run_name}/"], check=True)
        subprocess.run(["git", "commit", "-m", f"fit: auto-commit optimized weights and metrics for {run_name}"], check=True)
        print(f"[Auto-Optimizer] Pushing {run_name} to GitHub remote repository...")
        subprocess.run(["git", "push"], check=True)
        print(f"[Auto-Optimizer] Git push completed successfully!")
    except Exception as e:
        print(f"[Auto-Optimizer] Git operation failed: {e}")

def main():
    history = load_history()
    target_map50 = 0.95  # Ideal target
    
    print("=== Skindential AI Auto-ML Tuning Pipeline ===")
    
    # Run loops iteratively
    while True:
        params = get_next_parameters(history)
        run_idx = len(history) + 1
        run_name = f"auto_opt_run_{run_idx}"
        run_dir = os.path.join(PROJECT_DIR, run_name)
        
        # Clean up existing run directory to prevent YOLO auto-increment renaming (-2, -3)
        if os.path.exists(run_dir):
            import shutil
            try:
                shutil.rmtree(run_dir)
                print(f"[Auto-Optimizer] Cleaned up existing directory: {run_dir}")
            except Exception as e:
                print(f"[Auto-Optimizer] Warning: could not clean up {run_dir}: {e}")
        
        print(f"\n[Auto-Optimizer] Starting Run #{run_idx}: '{run_name}'")
        print(f"[Auto-Optimizer] Hyperparameters: {json.dumps(params, indent=2)}")
        
        cmd = [
            "yolo", "detect", "train",
            f"model={params['model']}",
            f"data={DATA_YAML}",
            f"epochs={params['epochs']}",
            f"imgsz=480",
            f"batch=4",
            f"workers=2",
            f"device=0",
            f"project={PROJECT_DIR}",
            f"name={run_name}",
            f"lr0={params['lr0']}",
            f"weight_decay={params['weight_decay']}",
            f"box={params['box']}",
            f"cls={params['cls']}",
            f"mixup={params['mixup']}",
            f"mosaic={params['mosaic']}",
            "exist_ok=True"
        ]
        
        start_time = time.time()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore", bufsize=1)
        
        # Stream logs in real-time
        for line in iter(process.stdout.readline, ""):
            print(line, end="")
            
        process.stdout.close()
        process.wait()
        
        duration = time.time() - start_time
        metrics = extract_best_metrics(run_dir)
        
        if metrics:
            print(f"\n[Auto-Optimizer] Run #{run_idx} Finished!")
            print(f"-> mAP50: {metrics['best_map50']:.5f}")
            print(f"-> Precision: {metrics['precision']:.5f}")
            print(f"-> Recall: {metrics['recall']:.5f}")
            
            # Save stats
            run_record = {
                "run_name": run_name,
                "duration_sec": duration,
                "params": params,
                "best_map50": metrics["best_map50"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            history.append(run_record)
            save_history(history)
            
            # Auto commit to Git LFS and push
            auto_git_commit(run_name)
            
            # Check target condition
            if metrics["best_map50"] >= target_map50:
                print(f"\n🎉 Goal achieved! Target mAP50 >= {target_map50} met.")
                break
        else:
            print(f"\n[Auto-Optimizer] Run #{run_idx} failed or did not generate results.")
            break
            
        # Short cooldown before next run
        time.sleep(10)

if __name__ == "__main__":
    main()
