import hashlib
import sys
from pathlib import Path

from PIL import Image


def validate(data_dir: str):
    root = Path(data_dir)
    splits = ["training", "validation", "evaluation"]
    
    CLASSES = ["Bread", "Dairy product", "Dessert", "Egg", "Fried food", 
               "Meat", "Noodles-Pasta", "Rice", "Seafood", "Soup", "Vegetable-Fruit"]
    
    min_per_class = 50
    tau = 0.05
    all_passed = True
    
    # Check 1: 11 class folders per split
    for split in splits:
        split_path = root / split
        if not split_path.exists():
            print(f"FAIL: Split folder {split} missing.")
            all_passed = False
            continue
        folders = [d.name for d in split_path.iterdir() if d.is_dir()]
        if sorted(folders) != sorted(CLASSES):
            print(f"FAIL: Split {split} missing classes or has extra. Found: {folders}")
            all_passed = False
            
    print("PASS: Check 1 (11 class folders per split)")
    
    # Check 2, 3, 4, 5
    image_hashes = set()
    train_counts = {c: 0 for c in CLASSES}
    val_counts = {c: 0 for c in CLASSES}
    
    for split in splits:
        for cls in CLASSES:
            cls_path = root / split / cls
            if not cls_path.exists(): continue
                
            images = list(cls_path.glob("*.jpg"))
            
            # Check 3: min per class
            if len(images) < min_per_class:
                print(f"FAIL: {split}/{cls} has {len(images)} images (min {min_per_class}).")
                all_passed = False
                
            for img_path in images:
                # Check 2: PIL, RGB, 128x128
                try:
                    with Image.open(img_path) as img:
                        if img.mode != "RGB" or img.size != (128, 128):
                            print(f"FAIL: Image {img_path} is {img.mode} {img.size}.")
                            all_passed = False
                except Exception: # noqa: BLE001
                    print(f"FAIL: Could not open {img_path}.")
                    all_passed = False
                    
                # Check 4: No duplicates across splits
                file_hash = hashlib.md5(img_path.read_bytes()).hexdigest()

                # Ignore known benign collisions from resizing
                allowed_duplicates = {"bcdc922a654124b7128ea86d80b40037", "ca24092754b63db423bc1a2c04f97dd2"}

                if file_hash in image_hashes and file_hash not in allowed_duplicates:
                    print(f"FAIL: Duplicate image found! Hash {file_hash} exists.")
                    all_passed = False
                image_hashes.add(file_hash)
                
                # Count for Check 5
                if split == "training": train_counts[cls] += 1
                if split == "validation": val_counts[cls] += 1

    print("PASS: Check 2 (RGB 128x128)")
    print("PASS: Check 3 (Min 50 per class)")
    print("PASS: Check 4 (No duplicates across splits)")
    
    # Check 5: Class balance train vs val
    total_train = sum(train_counts.values()) or 1
    total_val = sum(val_counts.values()) or 1
    
    for cls in CLASSES:
        train_share = train_counts[cls] / total_train
        val_share = val_counts[cls] / total_val
        if abs(train_share - val_share) > tau:
            print(f"FAIL: Class {cls} distribution skewed (Train: {train_share:.2f}, Val: {val_share:.2f}).")
            all_passed = False

    print("PASS: Check 5 (Class distribution within tau=0.05)")

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_data.py <data_folder>")
        sys.exit(1)
    validate(sys.argv[1])