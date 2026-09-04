import os
import glob
from PIL import Image
import shutil

# Directories
SRC_DIR = r"E:\old\blackbridge_yolo"
SRC_CLASSES_FILE = os.path.join(SRC_DIR, "classes.txt")
TGT_DIR = r"E:\old\blackbridge_yolo_5group"

# Read original 59 classes
with open(SRC_CLASSES_FILE, "r", encoding="utf-8") as f:
    ALL_CLASSES = [line.strip() for line in f if line.strip()]

# 5 Core Clinical Groups Mapping
CLASS_GROUP_MAP_BY_NAME = {
    # Group 0: 發炎性痘痘 (Inflammatory Acne)
    "丘疹": 0, "囊腫": 0, "毛囊炎": 0, "水泡": 0, "皰疹": 0, "紅腫": 0, "膿皰": 0, "膿胞": 0, "痘痘": 0,
    # Group 1: 非發炎粉刺 (Comedones)
    "栗粒腫": 1, "閉合性粉刺": 1, "閉鎖性粉刺": 1, "開放性粉刺": 1, "皮脂腺囊腫": 1, "皮脂腺增生": 1,
    # Group 2: 色素與痘印 (Pigmentation & Marks)
    "太田母斑": 2, "日曬斑": 2, "痘印": 2, "痣": 2, "老人斑": 2, "肝斑": 2, "胎記": 2,
    "脂溢性角化斑(老人斑)": 2, "脂漏性角化斑": 2, "色素斑": 2, "色素沉澱": 2, "雀斑": 2, "顴骨母斑": 2,
    # Group 3: 凹痘坑與疤痕 (Scars & Pits)
    "傷疤": 3, "凹洞": 3, "水痘疤": 3, "痘坑": 3, "痘疤": 3, "結痂": 3, "蟹足腫": 3, "皮膚損傷": 3,
    # Group 4: 血管與紅斑 (Vascular & Redness)
    "小紅疹": 4, "微血管擴張": 4, "淡紅色小圓點": 4, "滲組織液": 4, "老人血管瘤": 4, "脂漏性皮膚炎": 4, "脫屑": 4, "脫皮": 4, "表皮囊腫": 4, "垂疣": 4, "扁平疣": 4
}

GROUP_NAMES = [
    "發炎性痘痘",
    "非發炎粉刺",
    "色素與痘印",
    "凹痘坑與疤痕",
    "血管與紅斑"
]

# Map original class index -> 5 group index
INDEX_TO_GROUP = {}
for idx, name in enumerate(ALL_CLASSES):
    if name in CLASS_GROUP_MAP_BY_NAME:
        INDEX_TO_GROUP[idx] = CLASS_GROUP_MAP_BY_NAME[name]

# Crop settings
PATCH_SIZE = 480
OVERLAP = 0.2
STRIDE = int(PATCH_SIZE * (1 - OVERLAP))  # 384 pixels

print("=== Generating 5-Group Clinically Grouped 480x480 Patch Dataset ===")

for split in ["train", "val"]:
    os.makedirs(os.path.join(TGT_DIR, "images", split), exist_ok=True)
    os.makedirs(os.path.join(TGT_DIR, "labels", split), exist_ok=True)

# Write classes.txt
with open(os.path.join(TGT_DIR, "classes.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(GROUP_NAMES) + "\n")

def process_split(split):
    src_img_dir = os.path.join(SRC_DIR, "images", split)
    src_lbl_dir = os.path.join(SRC_DIR, "labels", split)
    
    tgt_img_dir = os.path.join(TGT_DIR, "images", split)
    tgt_lbl_dir = os.path.join(TGT_DIR, "labels", split)
    
    img_files = glob.glob(os.path.join(src_img_dir, "*.jpg")) + glob.glob(os.path.join(src_img_dir, "*.png"))
    print(f"\nProcessing {split} split ({len(img_files)} images)...")
    
    total_patches = 0
    total_boxes = 0
    
    for idx, img_path in enumerate(img_files):
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(src_lbl_dir, base_name + ".txt")
        
        try:
            with Image.open(img_path) as img:
                img_w, img_h = img.size
                
                boxes = []
                if os.path.exists(lbl_path):
                    with open(lbl_path, "r", encoding="utf-8") as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                orig_cls = int(parts[0])
                                if orig_cls in INDEX_TO_GROUP:
                                    grp_cls = INDEX_TO_GROUP[orig_cls]
                                    x_c, y_c, w, h = map(float, parts[1:5])
                                    x1 = (x_c - w / 2) * img_w
                                    y1 = (y_c - h / 2) * img_h
                                    x2 = (x_c + w / 2) * img_w
                                    y2 = (y_c + h / 2) * img_h
                                    boxes.append((grp_cls, x1, y1, x2, y2))
                
                # Grid offsets
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
                        
                        local_boxes = []
                        for grp_cls, bx1, by1, bx2, by2 in boxes:
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
                                    local_boxes.append((grp_cls, lxc, lyc, lw, lh))
                                    
                        if local_boxes or (patch_id % 10 == 0):
                            patch_name = f"{base_name}_patch_{patch_id}"
                            out_img_path = os.path.join(tgt_img_dir, patch_name + ".jpg")
                            out_lbl_path = os.path.join(tgt_lbl_dir, patch_name + ".txt")
                            
                            crop_patch = img.crop((px1, py1, px2, py2))
                            if crop_patch.size != (PATCH_SIZE, PATCH_SIZE):
                                crop_patch = crop_patch.resize((PATCH_SIZE, PATCH_SIZE), Image.Resampling.LANCZOS)
                            crop_patch.save(out_img_path, quality=95)
                            
                            with open(out_lbl_path, "w", encoding="utf-8") as f:
                                for grp_cls, lxc, lyc, lw, lh in local_boxes:
                                    f.write(f"{grp_cls} {lxc:.6f} {lyc:.6f} {lw:.6f} {lh:.6f}\n")
                                    
                            total_patches += 1
                            total_boxes += len(local_boxes)
                        patch_id += 1
        except Exception as e:
            print(f"Error {img_path}: {e}")
            
        if (idx + 1) % 200 == 0 or (idx + 1) == len(img_files):
            print(f"[{split}] Processed {idx+1}/{len(img_files)} images...")
            
    print(f"[{split}] Created {total_patches} patches with {total_boxes} boxes.")

process_split("train")
process_split("val")

# Generate data.yaml
yaml_content = f"""path: {TGT_DIR}
train: images/train
val: images/val

names:
"""
for idx, name in enumerate(GROUP_NAMES):
    yaml_content += f"  {idx}: {name}\n"

with open(os.path.join(TGT_DIR, "data.yaml"), "w", encoding="utf-8") as f:
    f.write(yaml_content)

print(f"\nGenerated 5-Group dataset configuration: {TGT_DIR}\\data.yaml")
