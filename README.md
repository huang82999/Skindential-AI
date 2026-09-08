# Skindential AI | 智能測膚 AI 系統

Skindential AI 是一個專為「邊緣運算 (Edge AI)」設計的高解析度臉部膚況檢測系統。
我們為了解決「原圖太大跑不動、縮圖太小看不清」的問題，設計了一套獨特的 **「雙路推論架構 (Dual-Path Inference)」**，將人臉特徵拆分為「宏觀」與「微觀」兩個模型來協同運作。

## 📂 專案資料夾結構

本專案將程式碼、自動化腳本與訓練日誌整理如下：

* **`/app` (前端與後端)**
  * 包含了 Web 視覺化介面 (`index.html`)、後端伺服器 (`server.py`)。
  * 以及用來打 API 推論的 Python 範例腳本 (`inference_template.py`)。
  
* **`/experiments` (訓練成果與日誌)**
  * *註：為符合 GitHub 容量限制，此處僅保留訓練 Log (`results.csv`) 與視覺化圖表，不包含原始圖片與 `.pt` 權重檔。*
  * `exp01_macro_path_640/`：負責看全臉的大面積特徵（如皺紋、黑眼圈）的宏觀模型基準。
  * `exp02_micro_path_5group_480_baseline/`：負責看微小瑕疵（痘痘、粉刺），並收斂為 5 大群組的微觀模型基準。
  * `exp03_micro_yolo26l_upgrade/`：將骨幹網路升級為大型 YOLO26L 的實驗紀錄。
  * `exp04_micro_yolo26l_hsv_best/`：**🏆 目前最強的微觀模型 (mAP50: 18.84%)**。我們加入了 HSV 光源與膚色干擾訓練，成功突破了準確率天花板。

* **`/scripts` (自動化腳本)**
  * 包含專案開發期間所寫的所有 Python 工具，例如自動裁切 480x480 切片的資料處理腳本，以及我們用來執行「無人值守自動試錯」的 `auto_optimizer` 系列腳本。

* **`/docs` (技術文件與報告)**
  * 包含高達 50 頁的 `Skindential_AI_Comprehensive_Whitepaper.docx` 技術白皮書。
  * 完整的自動化訓練歷程 JSON 日誌 (`research_log_phase5.json` 等)。

## 🚀 關於雙模型推論架構
本系統推論時會同時啟動兩支模型：
1. **宏觀模型 (10 類)**：直接吃 640x640 縮圖，負責抓取抬頭紋、法令紋等需要「看全臉幾何」的特徵。
2. **微觀模型 (5 類)**：將高清原圖切成多張 480x480 的小圖，專門抓取發炎痘痘、粉刺、色素痘印等「局部微小」瑕疵。
最後將兩邊的預測結果(Bounding Boxes)進行融合，輸出完整的臉部膚況檢測報告。
