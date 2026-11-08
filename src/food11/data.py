import os
from pathlib import Path
from PIL import Image

CATEGORIES = {
    "0": "Bread",
    "1": "Dairy product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried food",
    "5": "Meat",
    "6": "Noodles-Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable-Fruit",
}

RAW_DIR = Path("data/food11_raw")
PROCESSED_DIR = Path("data/food11_processed")
MINI_DIR = Path("data/food11_processed_mini")
TARGET_SIZE = (128, 128)
MINI_LIMIT = 100

def process_dataset():
    splits = ["training", "evaluation", "validation"]
    
    for split in splits:
        split_raw_dir = RAW_DIR / split
        if not split_raw_dir.exists():
            print(f"Directory {split_raw_dir} not found. Skipping.")
            continue

        category_counts = {cat: 0 for cat in CATEGORIES.values()}

        for file_name in os.listdir(split_raw_dir):
            if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            # Extract category ID from filename (e.g., "0_123.jpg" -> "0")
            cat_id = file_name.split("_")[0]
            if cat_id not in CATEGORIES:
                continue

            cat_name = CATEGORIES[cat_id]
            
            # Target output directories
            proc_out_dir = PROCESSED_DIR / split / cat_name
            mini_out_dir = MINI_DIR / split / cat_name

            proc_out_dir.mkdir(parents=True, exist_ok=True)
            mini_out_dir.mkdir(parents=True, exist_ok=True)

            src_img_path = split_raw_dir / file_name

            try:
                with Image.open(src_img_path) as img:
                    resized_img = img.resize(TARGET_SIZE)

                    # Save full processed dataset image
                    resized_img.save(proc_out_dir / file_name)

                    # Save mini dataset image (up to 100 images per category per split)
                    if category_counts[cat_name] < MINI_LIMIT:
                        resized_img.save(mini_out_dir / file_name)
                        category_counts[cat_name] += 1

            except Exception as e:
                print(f"Error processing {file_name}: {e}")

if __name__ == "__main__":
    print("Processing images into 128x128 categorized folders...")
    process_dataset()
    print("Processing complete!")