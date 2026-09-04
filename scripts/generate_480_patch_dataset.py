import os
import glob
from PIL import Image
import shutil

# Source & Target Directories
SRC_DIR = r"E:\old\blackbridge_yolo"
TGT_DIR = r"E:\old\blackbridge_yolo_480patch"

PATCH_SIZE = 480
OVERLAP = 0.2
STRIDE = int(PATCH_SIZE * (1 - OVERLAP))  # 384 pixels

print("=== Generating 480x480 Native High-Res Patch Dataset ===")

# Create target directories
for split in ["train", "val"]:
    os.makedirs(os.path.join(TGT_DIR, "images", split), exist_ok=True)
    os.makedirs(os.path.join(TGT_DIR, "labels", split), exist_ok=True)

# Copy classes.txt
src_classes = os.path.join(SRC_DIR, "classes.txt")
if os.path.exists(src_classes):
    shutil.copy(src_classes, os.path.join(TGT_DIR, "classes.txt"))

def process_split(split):
    src_img_dir = os.path.join(SRC_DIR, "images", split)
    src_lbl_dir = os.path.join(SRC_DIR, "labels", split)
    
    tgt_img_dir = os.path.join(TGT_DIR, "images", split)
    tgt_lbl_dir = os.path.join(TGT_DIR, "labels", split)
    
    img_files = glob.glob(os.path.join(src_img_dir, "*.jpg")) + glob.glob(os.path.join(src_img_dir, "*.png"))
    print(f"\nProcessing {split} set: {len(img_files)} images...")
    
    total_patches = 0
    total_boxes = 0
    
    for idx, img_path in enumerate(img_files):
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(src_lbl_dir, base_name + ".txt")
        
        try:
            with Image.open(img_path) as img:
                img_w, img_h = img.size
                
                # Parse existing boxes if label file exists
                global_boxes = []
                if os.path.exists(lbl_path):
                    with open(lbl_path, "r", encoding="utf-8") as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                cls_id = int(parts[0])
                                x_c, y_c, w, h = map(float, parts[1:5])
                                # Convert to absolute xyxy
                                x1 = (x_c - w / 2) * img_w
                                y1 = (y_c - h / 2) * img_h
                                x2 = (x_c + w / 2) * img_w
                                y2 = (y_c + h / 2) * img_h
                                global_boxes.append((cls_id, x1, y1, x2, y2))
                
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
                        
                        # Find overlapping boxes inside this patch
                        local_boxes = []
                        for cls_id, bx1, by1, bx2, by2 in global_boxes:
                            # Intersection rectangle
                            ix1 = max(px1, bx1)
                            iy1 = max(py1, by1)
                            ix2 = min(px2, bx2)
                            iy2 = min(py2, by2)
                            
                            if ix2 > ix1 and iy2 > iy1:
                                orig_area = (bx2 - bx1) * (by2 - by1)
                                inter_area = (ix2 - ix1) * (iy2 - iy1)
                                
                                # Retain box if at least 30% of its area is in the patch
                                if inter_area / (orig_area + 1e-6) >= 0.3:
                                    # Convert to local patch coordinates (0 to PATCH_SIZE)
                                    lx1 = ix1 - px1
                                    ly1 = iy1 - py1
                                    lx2 = ix2 - px1
                                    ly2 = iy2 - py1
                                    
                                    actual_pw = px2 - px1
                                    actual_ph = py2 - py1
                                    
                                    # YOLO normalized format
                                    lw = (lx2 - lx1) / actual_pw
                                    lh = (ly2 - ly1) / actual_ph
                                    lxc = (lx1 + lx2) / (2.0 * actual_pw)
                                    lyc = (ly1 + ly2) / (2.0 * actual_ph)
                                    
                                    local_boxes.append((cls_id, lxc, lyc, lw, lh))
                        
                        # Save patch image and labels if boxes exist (or keep 10% empty patches for background)
                        if local_boxes or (patch_id % 10 == 0):
                            patch_name = f"{base_name}_patch_{patch_id}"
                            out_img_path = os.path.join(tgt_img_dir, patch_name + ".jpg")
                            out_lbl_path = os.path.join(tgt_lbl_dir, patch_name + ".txt")
                            
                            crop_patch = img.crop((px1, py1, px2, py2))
                            # Resize if boundary patch is smaller than 480x480
                            if crop_patch.size != (PATCH_SIZE, PATCH_SIZE):
                                crop_patch = crop_patch.resize((PATCH_SIZE, PATCH_SIZE), Image.Resampling.LANCZOS)
                                
                            crop_patch.save(out_img_path, quality=95)
                            
                            with open(out_lbl_path, "w", encoding="utf-8") as f:
                                for cls_id, lxc, lyc, lw, lh in local_boxes:
                                    f.write(f"{cls_id} {lxc:.6f} {lyc:.6f} {lw:.6f} {lh:.6f}\n")
                                    
                            total_patches += 1
                            total_boxes += len(local_boxes)
                            
                        patch_id += 1
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            
        if (idx + 1) % 100 == 0 or (idx + 1) == len(img_files):
            print(f"[{split}] Processed {idx+1}/{len(img_files)} images...")
            
    print(f"Finished {split} set: {total_patches} patches created, {total_boxes} total bounding boxes.")

process_split("train")
process_split("val")

# Generate data.yaml
yaml_content = f"""path: E:/old/blackbridge_yolo_480patch
train: images/train
val: images/val

names:
"""

# Read names from classes.txt
if os.path.exists(src_classes):
    with open(src_classes, "r", encoding="utf-8") as f:
        classes = [line.strip() for line in f if line.strip()]
        for i, name in enumerate(classes):
            yaml_content += f"  {i}: {name}\n"

data_yaml_path = os.path.join(TGT_DIR, "data.yaml")
with open(data_yaml_path, "w", encoding="utf-8") as f:
    f.write(yaml_content)

print(f"\nCreated dataset configuration file: {data_yaml_path}")
print("=== 480x480 Patch Dataset Creation Complete! ===")
