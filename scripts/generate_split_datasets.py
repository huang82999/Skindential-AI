import os
import glob
from PIL import Image
import shutil

# Original Dataset
SRC_DIR = r"E:\old\blackbridge_yolo"
SRC_CLASSES_FILE = os.path.join(SRC_DIR, "classes.txt")

# Read classes
with open(SRC_CLASSES_FILE, "r", encoding="utf-8") as f:
    ALL_CLASSES = [line.strip() for line in f if line.strip()]

# Target Categories Split
MACRO_NAMES = ["抬頭紋", "法令紋", "皺眉紋", "魚尾紋", "細紋", "黑眼圈", "暗沈", "鬆弛", "輕微敏感發紅", "片狀紅斑"]
MICRO_NAMES = [name for name in ALL_CLASSES if name not in MACRO_NAMES]

# Index Mapping
MACRO_MAP = {ALL_CLASSES.index(name): idx for idx, name in enumerate(MACRO_NAMES)}
MICRO_MAP = {ALL_CLASSES.index(name): idx for idx, name in enumerate(MICRO_NAMES)}

# Target Directory Paths
MACRO_DIR = r"E:\old\blackbridge_yolo_macro"
MICRO_DIR = r"E:\old\blackbridge_yolo_micro"

# Slice configurations for Micro
PATCH_SIZE = 480
OVERLAP = 0.2
STRIDE = int(PATCH_SIZE * (1 - OVERLAP))  # 384 pixels

print(f"=== Class Splitting: {len(MACRO_NAMES)} Macro Classes, {len(MICRO_NAMES)} Micro Classes ===")

def setup_dirs(base_dir):
    for split in ["train", "val"]:
        os.makedirs(os.path.join(base_dir, "images", split), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "labels", split), exist_ok=True)

setup_dirs(MACRO_DIR)
setup_dirs(MICRO_DIR)

# Write classes files
with open(os.path.join(MACRO_DIR, "classes.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(MACRO_NAMES) + "\n")
with open(os.path.join(MICRO_DIR, "classes.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(MICRO_NAMES) + "\n")

def process_image(img_path, split):
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    src_lbl_dir = os.path.join(SRC_DIR, "labels", split)
    lbl_path = os.path.join(src_lbl_dir, base_name + ".txt")
    
    # 1. Parse Original Annotations
    macro_boxes = []
    micro_boxes = []
    
    img = Image.open(img_path)
    img_w, img_h = img.size
    
    if os.path.exists(lbl_path):
        with open(lbl_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    orig_cls = int(parts[0])
                    x_c, y_c, w, h = map(float, parts[1:5])
                    
                    if orig_cls in MACRO_MAP:
                        macro_boxes.append((MACRO_MAP[orig_cls], x_c, y_c, w, h))
                    elif orig_cls in MICRO_MAP:
                        # Convert to absolute xyxy for cropping overlap computation
                        x1 = (x_c - w / 2) * img_w
                        y1 = (y_c - h / 2) * img_h
                        x2 = (x_c + w / 2) * img_w
                        y2 = (y_c + h / 2) * img_h
                        micro_boxes.append((MICRO_MAP[orig_cls], x1, y1, x2, y2))
                        
    # --- Part A: Macro (Copy full image & write remapped macro annotations) ---
    if macro_boxes:
        macro_img_tgt = os.path.join(MACRO_DIR, "images", split, base_name + ".jpg")
        macro_lbl_tgt = os.path.join(MACRO_DIR, "labels", split, base_name + ".txt")
        shutil.copy(img_path, macro_img_tgt)
        with open(macro_lbl_tgt, "w", encoding="utf-8") as f:
            for cls_id, x_c, y_c, w, h in macro_boxes:
                f.write(f"{cls_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")
                
    # --- Part B: Micro (Crop to 480x480 patches & recompute coordinates) ---
    if micro_boxes:
        # Generate grid offsets
        x_offsets = []
        x = 0
        while x < img_w:
            x_offsets.append(x)
            if x + PATCH_SIZE >= img_w:
                break
            x += STRIDE
            
        y_offsets = []
        y = 0
        while y < img_h:
            y_offsets.append(y)
            if y + PATCH_SIZE >= img_h:
                break
            y += STRIDE
            
        patch_id = 0
        for py in y_offsets:
            for px in x_offsets:
                px1, py1 = px, py
                px2 = min(px + PATCH_SIZE, img_w)
                py2 = min(py + PATCH_SIZE, img_h)
                
                # Check patch boxes
                local_boxes = []
                for cls_id, bx1, by1, bx2, by2 in micro_boxes:
                    ix1 = max(px1, bx1)
                    iy1 = max(py1, by1)
                    ix2 = min(px2, bx2)
                    iy2 = min(py2, by2)
                    
                    if ix2 > ix1 and iy2 > iy1:
                        orig_area = (bx2 - bx1) * (by2 - by1)
                        inter_area = (ix2 - ix1) * (iy2 - iy1)
                        
                        if inter_area / (orig_area + 1e-6) >= 0.3:
                            lx1 = ix1 - px1
                            ly1 = iy1 - py1
                            lx2 = ix2 - px1
                            ly2 = iy2 - py1
                            
                            actual_pw = px2 - px1
                            actual_ph = py2 - py1
                            
                            lw = (lx2 - lx1) / actual_pw
                            lh = (ly2 - ly1) / actual_ph
                            lxc = (lx1 + lx2) / (2.0 * actual_pw)
                            lyc = (ly1 + ly2) / (2.0 * actual_ph)
                            local_boxes.append((cls_id, lxc, lyc, lw, lh))
                
                if local_boxes or (patch_id % 10 == 0):
                    patch_name = f"{base_name}_patch_{patch_id}"
                    out_img_path = os.path.join(MICRO_DIR, "images", split, patch_name + ".jpg")
                    out_lbl_path = os.path.join(MICRO_DIR, "labels", split, patch_name + ".txt")
                    
                    crop_patch = img.crop((px1, py1, px2, py2))
                    if crop_patch.size != (PATCH_SIZE, PATCH_SIZE):
                        crop_patch = crop_patch.resize((PATCH_SIZE, PATCH_SIZE), Image.Resampling.LANCZOS)
                    crop_patch.save(out_img_path, quality=95)
                    
                    with open(out_lbl_path, "w", encoding="utf-8") as f:
                        for cls_id, lxc, lyc, lw, lh in local_boxes:
                            f.write(f"{cls_id} {lxc:.6f} {lyc:.6f} {lw:.6f} {lh:.6f}\n")
                patch_id += 1
    img.close()

def generate_yaml(base_dir, split_name, class_names):
    yaml_content = f"""path: {base_dir}
train: images/train
val: images/val

names:
"""
    for idx, name in enumerate(class_names):
        yaml_content += f"  {idx}: {name}\n"
        
    with open(os.path.join(base_dir, "data.yaml"), "w", encoding="utf-8") as f:
        f.write(yaml_content)

# Process splits
for split in ["train", "val"]:
    src_img_dir = os.path.join(SRC_DIR, "images", split)
    img_files = glob.glob(os.path.join(src_img_dir, "*.jpg")) + glob.glob(os.path.join(src_img_dir, "*.png"))
    print(f"\nProcessing {split} split ({len(img_files)} images)...")
    for idx, img_path in enumerate(img_files):
        process_image(img_path, split)
        if (idx + 1) % 100 == 0 or (idx + 1) == len(img_files):
            print(f"Processed {idx+1}/{len(img_files)} images...")

# Generate YAMLs
generate_yaml(MACRO_DIR, "macro", MACRO_NAMES)
generate_yaml(MICRO_DIR, "micro", MICRO_NAMES)

print("\n=== Split Datasets Generation Completed successfully! ===")
print(f"Macro Dataset (Full Scale): {MACRO_DIR}")
print(f"Micro Dataset (480x480 Patches): {MICRO_DIR}")
