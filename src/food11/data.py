import os
import hashlib
from pathlib import Path
from PIL import Image

CLASSES = [
    "Bread", "Dairy product", "Dessert", "Egg", "Fried food", "Meat",
    "Noodles-Pasta", "Rice", "Seafood", "Soup", "Vegetable-Fruit"
]

RAW_DIR = Path("data/food11_raw")
PROCESSED_DIR = Path("data/food11_processed")
MINI_DIR = Path("data/food11_processed_mini")
TARGET_SIZE = (128, 128)
MINI_LIMIT = 100

def category_from_filename(filename: str) -> str:
    """'3_120.jpg' -> 'Egg'"""
    cat_id = int(filename.split("_")[0])
    return CLASSES[cat_id]

def resize_image(img: "Image.Image", size: int = 128) -> "Image.Image":
    """Returns an RGB image of size x size."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img.resize((size, size))

def process_dataset():
    splits = ["training", "evaluation", "validation"]
    seen_hashes = set()
    
    for split in splits:
        split_raw_dir = RAW_DIR / split
        if not split_raw_dir.exists():
            print(f"Directory {split_raw_dir} not found. Skipping.")
            continue

        category_counts = {cat: 0 for cat in CLASSES}

        for file_name in os.listdir(split_raw_dir):
            if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            try:
                cat_name = category_from_filename(file_name)
            except (IndexError, ValueError):
                continue

            proc_out_dir = PROCESSED_DIR / split / cat_name
            mini_out_dir = MINI_DIR / split / cat_name

            proc_out_dir.mkdir(parents=True, exist_ok=True)
            mini_out_dir.mkdir(parents=True, exist_ok=True)

            src_img_path = split_raw_dir / file_name
            
            # Check for duplicates using the raw file bytes
            file_hash = hashlib.md5(src_img_path.read_bytes()).hexdigest()
            if file_hash in seen_hashes:
                continue
            seen_hashes.add(file_hash)

            try:
                with Image.open(src_img_path) as img:
                    resized_img = resize_image(img, TARGET_SIZE[0])
                    resized_img.save(proc_out_dir / file_name)

                    if category_counts[cat_name] < MINI_LIMIT:
                        resized_img.save(mini_out_dir / file_name)
                        category_counts[cat_name] += 1
            except Exception as e:  # noqa: BLE001
                print(f"Error processing {file_name}: {e}")

if __name__ == "__main__":
    print("Processing images into 128x128 categorized folders (skipping duplicates)...")
    process_dataset()
    print("Processing complete!")