from ultralytics import YOLO
import json
import cv2
import os

def run_inference(image_path, model_path, conf_threshold=0.15):
    """
    使用訓練好的 YOLO 模型進行推論 (Inference)
    """
    # 1. 載入模型 (Load Model)
    # 這裡指向我們目前表現最好的模型權重
    print(f"Loading model from: {model_path}")
    model = YOLO(model_path)
    
    # 2. 執行推論 (Predict)
    # imgsz=480 對應我們訓練時使用的尺寸
    # conf 是信心門檻，低於這個分數的預測框會被過濾掉
    print(f"Running inference on: {image_path}")
    results = model.predict(source=image_path, imgsz=480, conf=conf_threshold)
    
    # 3. 解析結果 (Parse Results)
    # 將預測結果轉換為 API 回傳常見的 JSON 格式
    api_response = {
        "status": "success",
        "image_file": os.path.basename(image_path),
        "detections": []
    }
    
    for result in results:
        # 獲取類別名稱對應表 (例如: 0: 發炎性痘痘, 1: 非發炎粉刺)
        names = result.names 
        
        # 遍歷每一個偵測到的病灶 (Bounding Box)
        for box in result.boxes:
            class_id = int(box.cls[0].item())       # 類別 ID
            class_name = names[class_id]            # 類別名稱
            confidence = float(box.conf[0].item())  # 信心分數
            
            # 取得邊界框座標 (x_min, y_min, x_max, y_max)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            
            # 加入到我們的回傳資料中
            api_response["detections"].append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": round(confidence, 3),
                "box": {
                    "x_min": int(x1),
                    "y_min": int(y1),
                    "x_max": int(x2),
                    "y_max": int(y2)
                }
            })
            
        # (選用) 將畫好框的圖片儲存下來，方便視覺檢查
        result.save(filename="inference_result_visual.jpg")
        print("Visual result saved to 'inference_result_visual.jpg'")
        
    return api_response


if __name__ == "__main__":
    # ⚠️ 請將這裡替換成您要測試的實際圖片路徑
    TEST_IMAGE = r"E:\old\blackbridge_yolo_5group\images\val\xxxx.jpg" 
    BEST_MODEL = r"E:\old\blackbridge_yolo\yolo_runs\trial_model_yolo26l\weights\best.pt"
    
    # 執行推論
    try:
        response_data = run_inference(TEST_IMAGE, BEST_MODEL)
        
        # 印出 JSON 格式的結果 (這就是未來 API 要吐給前端的資料結構)
        print("\n=== API JSON Response ===")
        print(json.dumps(response_data, indent=4, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error running inference: {e}")
