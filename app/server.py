import os
from flask import Flask, request, jsonify, send_from_directory
from ultralytics import YOLO
from PIL import Image
import io

app = Flask(__name__, static_folder=".")

YOLO_RUNS_DIR = r"E:\old\blackbridge_yolo\yolo_runs"
BASE_DIR = r"E:\old"

# Cache loaded models to avoid loading overhead on every request
loaded_models = {}

def get_yolo_model(model_path):
    if model_path not in loaded_models:
        try:
            loaded_models[model_path] = YOLO(model_path)
            print(f"Loaded model: {model_path}")
        except Exception as e:
            print(f"Error loading model {model_path}: {e}")
            return None
    return loaded_models[model_path]

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(BASE_DIR, path)

@app.route("/api/models", methods=["GET"])
def list_models():
    import torch
    models = []
    # Search for all best.pt and last.pt files in runs dir
    if os.path.exists(YOLO_RUNS_DIR):
        for root, dirs, files in os.walk(YOLO_RUNS_DIR):
            for file in files:
                if file.endswith(".pt"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, YOLO_RUNS_DIR)
                    # Extract classes using torch load (extremely fast and memory efficient)
                    try:
                        ckpt = torch.load(full_path, map_location='cpu', weights_only=False)
                        model_obj = ckpt.get('ema') or ckpt.get('model')
                        model_classes = list(model_obj.names.values()) if model_obj else []
                    except Exception as e:
                        print(f"Error loading classes for {full_path}: {e}")
                        model_classes = []
                    
                    models.append({
                        "name": rel_path,
                        "path": full_path,
                        "classes": model_classes
                    })
    # Also add standard pre-trained models for testing
    for path, name in [("yolo11n.pt", "yolo11n.pt (預訓練模型)"), ("yolo11m.pt", "yolo11m.pt (預訓練模型)")]:
        try:
            model = get_yolo_model(path)
            model_classes = list(model.names.values()) if model else []
        except Exception as e:
            model_classes = []
        models.append({
            "name": name,
            "path": path,
            "classes": model_classes
        })
    
    return jsonify(models)

def sahi_predict(model, img, slice_size=480, overlap=0.2, conf_thresh=0.01, iou_thresh=0.45):
    import numpy as np
    import torch
    from torchvision.ops import nms
    
    img_w, img_h = img.size
    
    # Calculate slice coordinates with overlapping
    stride = int(slice_size * (1 - overlap))
    
    x_offsets = []
    y_offsets = []
    
    x = 0
    while x < img_w:
        x_offsets.append(x)
        if x + slice_size >= img_w:
            break
        x += stride
        
    y = 0
    while y < img_h:
        y_offsets.append(y)
        if y + slice_size >= img_h:
            break
        y += stride

    all_boxes = []
    all_scores = []
    all_classes = []
    
    for y_off in y_offsets:
        for x_off in x_offsets:
            x_min = x_off
            y_min = y_off
            x_max = min(x_off + slice_size, img_w)
            y_max = min(y_off + slice_size, img_h)
            
            # Crop the local image slice
            crop_img = img.crop((x_min, y_min, x_max, y_max))
            
            # Run inference locally on the slice (imgsz=480 for edge optimization)
            results = model(crop_img, imgsz=480, conf=conf_thresh, verbose=False)
            if not results:
                continue
                
            result = results[0]
            boxes = result.boxes
            if len(boxes) == 0:
                continue
                
            xyxy = boxes.xyxy.cpu().numpy()
            scores = boxes.conf.cpu().numpy()
            classes = boxes.cls.cpu().numpy()
            
            for i in range(len(xyxy)):
                # Map relative slice coordinates back to global original coordinates
                gx_min = xyxy[i][0] + x_off
                gy_min = xyxy[i][1] + y_off
                gx_max = xyxy[i][2] + x_off
                gy_max = xyxy[i][3] + y_off
                
                all_boxes.append([gx_min, gy_min, gx_max, gy_max])
                all_scores.append(scores[i])
                all_classes.append(classes[i])
                
    if not all_boxes:
        return []
        
    # Convert to tensors for fast GPU/CPU NMS
    boxes_t = torch.tensor(all_boxes, dtype=torch.float32)
    scores_t = torch.tensor(all_scores, dtype=torch.float32)
    
    # Run Non-Maximum Suppression (NMS) to merge overlapping duplicate detections
    keep_indices = nms(boxes_t, scores_t, iou_threshold=iou_thresh)
    
    final_rois = []
    names = model.names
    for idx in keep_indices:
        idx = int(idx)
        box = all_boxes[idx]
        cls_id = int(all_classes[idx])
        conf = float(all_scores[idx])
        cls_name = names.get(cls_id, "未知")
        
        # Convert back to relative center-based coords
        cx = (box[0] + box[2]) / 2 / img_w
        cy = (box[1] + box[3]) / 2 / img_h
        w = (box[2] - box[0]) / img_w
        h = (box[3] - box[1]) / img_h
        
        final_rois.append({
            "cls": cls_name,
            "cx": float(cx),
            "cy": float(cy),
            "w": float(w),
            "h": float(h),
            "conf": conf
        })
        
    return final_rois

@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
        
    img_file = request.files["image"]
    model_path = request.form.get("model_path", "yolo11m.pt")
    iou_threshold = float(request.form.get("iou_threshold", 0.7))
    use_sahi = request.form.get("use_sahi", "false").lower() == "true"
    
    # Load model
    model = get_yolo_model(model_path)
    if model is None:
        return jsonify({"error": f"Failed to load model: {model_path}"}), 500
        
    try:
        # Read image
        img_bytes = img_file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img_w, img_h = img.size
        
        if use_sahi:
            # Perform Slicing Aided Hyper Inference (SAHI)
            print(f"Performing SAHI inference using: {model_path}")
            rois = sahi_predict(model, img, slice_size=640, overlap=0.2, conf_thresh=0.01, iou_thresh=iou_threshold)
        else:
            # Run standard whole-image inference
            print(f"Performing standard inference using: {model_path}")
            results = model(img, imgsz=1920, conf=0.01, iou=iou_threshold, agnostic_nms=True)
            
            # Parse results
            rois = []
            if len(results) > 0:
                result = results[0]
                boxes = result.boxes
                names = model.names
                
                for box in boxes:
                    xywh = box.xywh[0].cpu().numpy()
                    cls_id = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    cls_name = names.get(cls_id, "未知")
                    
                    rois.append({
                        "cls": cls_name,
                        "cx": float(xywh[0] / img_w),
                        "cy": float(xywh[1] / img_h),
                        "w": float(xywh[2] / img_w),
                        "h": float(xywh[3] / img_h),
                        "conf": conf
                    })
                
        return jsonify({
            "rois": rois,
            "width": img_w,
            "height": img_h
        })
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
