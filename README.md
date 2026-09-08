# Skindential AI | 智能測膚 AI 系統

Skindential AI 是一個專為「邊緣運算 (Edge AI)」設計的高解析度臉部膚況檢測系統。
採用獨特的 **「雙路推論架構 (Dual-Path Inference)」**，將人臉特徵拆分為「宏觀」與「微觀」兩個模型來協同運作。

## 📂 專案結構

* **`/app`**：包含前端 Web 介面 (`index.html`)、後端伺服器 (`server.py`) 以及推論腳本。
* **`/scripts`**：資料處理與自動化訓練 (Auto-ML) 的 Python 腳本。
* **`/experiments`**：所有已完賽的訓練日誌 (`results.csv`)、超參數設定 (`args.yaml`) 與視覺化圖表 (`*.png`)。*(已排除過大的影像與權重檔)*

---

## 🚀 系統啟動方式

本專案自帶輕量化的本地後端與前端網頁。

### 步驟 1：啟動後端伺服器
請確認已安裝 Python 環境與相關依賴 (如 FastAPI, Uvicorn, Ultralytics)，並執行啟動腳本：
```bash
cd app
# 在 Windows 環境下可以直接點擊 start.bat 啟動
start.bat

# 或者手動執行 Python 伺服器
python server.py
```

### 步驟 2：開啟前端網頁
後端啟動後，直接使用網頁瀏覽器打開以下檔案即可使用系統：
👉 `app/index.html`

---

## 📊 歷次訓練成效排行榜 (mAP50)

以下列出專案開發期間所有**完整完賽**的模型訓練紀錄（依準確率排序）：

| 排名 | 實驗名稱 (Experiment Name) | 最高 mAP50 | 最佳 Epoch | 說明 / 備註 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `trial_yolo26l_hsv` | **18.84%** | 40 | 詳見 `/experiments/trial_yolo26l_hsv` |
| 2 | `trial_yolo26l_rotation` | **18.19%** | 40 | 詳見 `/experiments/trial_yolo26l_rotation` |
| 3 | `trial_yolo26l_no_mosaic` | **18.18%** | 40 | 詳見 `/experiments/trial_yolo26l_no_mosaic` |
| 4 | `trial_dfl_2_5` | **18.13%** | 34 | 詳見 `/experiments/trial_dfl_2_5` |
| 5 | `trial_imgsz_512` | **18.0%** | 40 | 詳見 `/experiments/trial_imgsz_512` |
| 6 | `trial_combo_512_26l_dfl2_5` | **17.84%** | 46 | 詳見 `/experiments/trial_combo_512_26l_dfl2_5` |
| 7 | `exp_5group_clinical_480` | **17.47%** | 40 | 詳見 `/experiments/exp_5group_clinical_480` |
| 8 | `blackbridge_yolo26n` | **9.2%** | 42 | 詳見 `/experiments/blackbridge_yolo26n` |
| 9 | `macro_run_640_full` | **7.75%** | 19 | 詳見 `/experiments/macro_run_640_full` |
| 10 | `single_run_480_patch_native` | **6.52%** | 47 | 詳見 `/experiments/single_run_480_patch_native` |
| 11 | `blackbridge_yolo11m_1920_fine_tune` | **6.21%** | 14 | 詳見 `/experiments/blackbridge_yolo11m_1920_fine_tune` |
| 12 | `blackbridge_yolo11m_1920_b2` | **6.15%** | 46 | 詳見 `/experiments/blackbridge_yolo11m_1920_b2` |
| 13 | `micro_run_480_patch` | **6.03%** | 48 | 詳見 `/experiments/micro_run_480_patch` |
| 14 | `single_run_480_patch_optimized` | **6.02%** | 51 | 詳見 `/experiments/single_run_480_patch_optimized` |
| 15 | `blackbridge_yolo11m_1920_clean` | **5.66%** | 38 | 詳見 `/experiments/blackbridge_yolo11m_1920_clean` |
| 16 | `blackbridge_yolo26m_1920` | **5.61%** | 93 | 詳見 `/experiments/blackbridge_yolo26m_1920` |
| 17 | `auto_opt_run_1-3` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_1-3` |
| 18 | `auto_opt_run_1` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_1` |
| 19 | `auto_opt_run_6` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_6` |
| 20 | `auto_opt_run_11` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_11` |
| 21 | `auto_opt_run_16` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_16` |
| 22 | `auto_opt_run_21` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_21` |
| 23 | `auto_opt_run_26` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_26` |
| 24 | `auto_opt_run_31` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_31` |
| 25 | `auto_opt_run_36` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_36` |
| 26 | `auto_opt_run_41` | **5.61%** | 67 | 詳見 `/experiments/auto_opt_run_41` |
| 27 | `auto_opt_run_2` | **5.56%** | 60 | 詳見 `/experiments/auto_opt_run_2` |
| 28 | `auto_opt_run_12` | **5.56%** | 60 | 詳見 `/experiments/auto_opt_run_12` |
| 29 | `auto_opt_run_22` | **5.56%** | 60 | 詳見 `/experiments/auto_opt_run_22` |
| 30 | `auto_opt_run_32` | **5.56%** | 60 | 詳見 `/experiments/auto_opt_run_32` |
| 31 | `auto_opt_run_42` | **5.56%** | 60 | 詳見 `/experiments/auto_opt_run_42` |
| 32 | `auto_opt_run_5` | **5.47%** | 66 | 詳見 `/experiments/auto_opt_run_5` |
| 33 | `auto_opt_run_8` | **5.47%** | 60 | 詳見 `/experiments/auto_opt_run_8` |
| 34 | `auto_opt_run_15` | **5.47%** | 66 | 詳見 `/experiments/auto_opt_run_15` |
| 35 | `auto_opt_run_18` | **5.47%** | 60 | 詳見 `/experiments/auto_opt_run_18` |
| 36 | `auto_opt_run_25` | **5.47%** | 66 | 詳見 `/experiments/auto_opt_run_25` |
| 37 | `auto_opt_run_28` | **5.47%** | 60 | 詳見 `/experiments/auto_opt_run_28` |
| 38 | `auto_opt_run_35` | **5.47%** | 66 | 詳見 `/experiments/auto_opt_run_35` |
| 39 | `auto_opt_run_38` | **5.47%** | 60 | 詳見 `/experiments/auto_opt_run_38` |
| 40 | `auto_opt_run_4` | **5.41%** | 65 | 詳見 `/experiments/auto_opt_run_4` |
| 41 | `auto_opt_run_14` | **5.41%** | 65 | 詳見 `/experiments/auto_opt_run_14` |
| 42 | `auto_opt_run_24` | **5.41%** | 65 | 詳見 `/experiments/auto_opt_run_24` |
| 43 | `auto_opt_run_34` | **5.41%** | 65 | 詳見 `/experiments/auto_opt_run_34` |
| 44 | `auto_opt_run_44` | **5.41%** | 65 | 詳見 `/experiments/auto_opt_run_44` |
| 45 | `auto_opt_run_7` | **5.4%** | 64 | 詳見 `/experiments/auto_opt_run_7` |
| 46 | `auto_opt_run_17` | **5.4%** | 64 | 詳見 `/experiments/auto_opt_run_17` |
| 47 | `auto_opt_run_27` | **5.4%** | 64 | 詳見 `/experiments/auto_opt_run_27` |
| 48 | `auto_opt_run_37` | **5.4%** | 64 | 詳見 `/experiments/auto_opt_run_37` |
| 49 | `auto_opt_run_9` | **5.37%** | 23 | 詳見 `/experiments/auto_opt_run_9` |
| 50 | `auto_opt_run_19` | **5.37%** | 23 | 詳見 `/experiments/auto_opt_run_19` |
| 51 | `auto_opt_run_29` | **5.37%** | 23 | 詳見 `/experiments/auto_opt_run_29` |
| 52 | `auto_opt_run_39` | **5.37%** | 23 | 詳見 `/experiments/auto_opt_run_39` |
| 53 | `auto_opt_run_10` | **5.31%** | 58 | 詳見 `/experiments/auto_opt_run_10` |
| 54 | `auto_opt_run_20` | **5.31%** | 58 | 詳見 `/experiments/auto_opt_run_20` |
| 55 | `auto_opt_run_30` | **5.31%** | 58 | 詳見 `/experiments/auto_opt_run_30` |
| 56 | `auto_opt_run_40` | **5.31%** | 58 | 詳見 `/experiments/auto_opt_run_40` |
| 57 | `auto_opt_run_3` | **5.05%** | 32 | 詳見 `/experiments/auto_opt_run_3` |
| 58 | `auto_opt_run_13` | **5.05%** | 32 | 詳見 `/experiments/auto_opt_run_13` |
| 59 | `auto_opt_run_23` | **5.05%** | 32 | 詳見 `/experiments/auto_opt_run_23` |
| 60 | `auto_opt_run_33` | **5.05%** | 32 | 詳見 `/experiments/auto_opt_run_33` |
| 61 | `auto_opt_run_43` | **5.05%** | 32 | 詳見 `/experiments/auto_opt_run_43` |
| 62 | `blackbridge_yolo11m` | **4.75%** | 44 | 詳見 `/experiments/blackbridge_yolo11m` |
| 63 | `single_run_480_edge` | **4.38%** | 59 | 詳見 `/experiments/single_run_480_edge` |
| 64 | `blackbridge_yolo26n-2` | **2.14%** | 45 | 詳見 `/experiments/blackbridge_yolo26n-2` |
| 65 | `auto_opt_run_45` | **1.76%** | 3 | 詳見 `/experiments/auto_opt_run_45` |

*(註：為保持 GitHub 輕量化，`experiments/` 目錄內僅保留訓練曲線圖、混淆矩陣與 CSV Log 數據。)*
