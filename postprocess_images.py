# save_as: postprocess_images.py
import os, shutil, csv, hashlib, random 
from pathlib import Path
from PIL import Image
import pandas as pd

DATA_DIR = Path("dataset")  # or "dataset_selenium"
OUT_DIR = Path("dataset_clean")
OUT_DIR.mkdir(exist_ok=True)
MIN_SIZE = (50, 50)  # drop tiny images
TARGET_SIZE = (224, 224)  # optional resize for model training

seen_hashes = set()
rows = []
for cls_dir in DATA_DIR.iterdir():
    if not cls_dir.is_dir(): continue
    for img_path in cls_dir.iterdir():
        if not img_path.is_file(): continue
        try:
            with open(img_path, "rb") as f:
                data = f.read()
            sha = hashlib.sha256(data).hexdigest()
            if sha in seen_hashes:
                continue
            seen_hashes.add(sha)
            im = Image.open(img_path).convert("RGB")
            if im.size[0] < MIN_SIZE[0] or im.size[1] < MIN_SIZE[1]:
                continue            # resize and save to clean folder
            cls_out = OUT_DIR / cls_dir.name
            cls_out.mkdir(parents=True, exist_ok=True)
            out_path = cls_out / img_path.name
            im = im.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
            im.save(out_path, quality=90)
            rows.append({"filename": str(out_path), "class": cls_dir.name, "sha256": sha, "width": TARGET_SIZE[0], "height": TARGET_SIZE[1]})
        except Exception as e:
            # print("err", img_path, e)
            continue

# create dataframe and splits
df = pd.DataFrame(rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
train_pct, val_pct = 0.8, 0.1
N = len(df)
train_end = int(N * train_pct)
val_end = train_end + int(N * val_pct)
df["split"] = ["train"] * N
df.loc[train_end:val_end, "split"] = "val"
df.loc[val_end:, "split"] = "test"
df.to_csv(OUT_DIR / "metadata_clean.csv", index=False)
print("Done. Images:", len(df))
