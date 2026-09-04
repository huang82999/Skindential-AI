# Skindential AI

Skindential AI is an Edge AI-powered facial skin lesion detection system. It utilizes a Dual-Path Inference architecture (Macro + Micro) to detect both global facial features (wrinkles, dark circles) and microscopic lesions (acne, pores) from high-resolution images.

## Repository Structure

* `/app`: Frontend UI (`index.html`) and Backend API Server (`server.py`).
* `/experiments`: Training logs, learning curves, confusion matrices, and precision-recall charts for key iterations.
    * `exp01_macro_path_640`: Macro features baseline.
    * `exp02_micro_path_5group_480_baseline`: 5-Group micro lesion baseline.
    * `exp03_micro_yolo26l_upgrade`: Upgraded Large model.
    * `exp04_micro_yolo26l_hsv_best`: The current absolute best model (18.84% mAP50) using HSV augmentation.
* `/scripts`: Python automation scripts used for dataset generation and Auto-ML trial-and-error hyperparameter tuning.
* `/docs`: Project whitepapers, generated reports, and detailed JSON trial logs.

## Note
Due to file size limits, this repository does not include the raw image datasets or the `.pt` model weights. Only training logs and code are provided.
