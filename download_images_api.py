import os, requests, csv, hashlib, time
from urllib.parse import urlparse
from pathlib import Path
from tqdm import tqdm

# CONFIG
API_KEY = ""    # <--- replace with your Google API key
CX = ""  # <--- replace with your Custom Search Engine ID
ENDPOINT = "https://www.googleapis.com/customsearch/v1"
OUTPUT_DIR = Path("dataset")
CLASSES = ["Naval Mine", "Torpedo Shape", "Military Submarine", "AUV (Autonomous Underwater Vehicle)"]
IMAGES_PER_CLASS = 200

OUTPUT_DIR.mkdir(exist_ok=True)

def download_image(url, dest_path):
    try:
        r = requests.get(url, stream=True, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(1024*8):
                f.write(chunk)
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limited, skip silently
            return False
        print(f"Download error ({e.response.status_code}): {url[:60]}...")
        return False
    except Exception as e:
        print(f"Download error: {str(e)[:50]}...")
        return False

rows = []
for cls in CLASSES:
    cls_dir = OUTPUT_DIR / cls
    cls_dir.mkdir(parents=True, exist_ok=True)
    print("Searching:", cls)
    # Google Custom Search API params
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": cls,
        "searchType": "image",
        "num": 10,  # max 10 per request for Google
        "start": 1
    }
    downloaded = 0
    start_index = 1
    while downloaded < IMAGES_PER_CLASS:
        params["start"] = start_index
        resp = requests.get(ENDPOINT, params=params, timeout=15)
        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
            break
        data = resp.json()
        images = data.get("items", [])
        if not images:
            break
        for img in images:
            if downloaded >= IMAGES_PER_CLASS: break
            img_url = img.get("link")
            if not img_url: continue
            parsed = urlparse(img_url)
            ext = Path(parsed.path).suffix or ".jpg"
            fname = f"{downloaded:04d}{ext}"
            dest = cls_dir / fname
            ok = download_image(img_url, dest)
            if not ok: continue
            # compute sha256
            import hashlib
            with open(dest, "rb") as fh:
                sha = hashlib.sha256(fh.read()).hexdigest()
            rows.append({
                "filename": str(dest),
                "class": cls,
                "original_url": img_url,
                "source_site": parsed.netloc,
                "width": img.get("image",{}).get("width",""),
                "height": img.get("image",{}).get("height",""),
                "sha256": sha,
                "license": ""  # Google API doesn't provide license info directly
            })
            downloaded += 1
            print(f"Downloaded {downloaded}/{IMAGES_PER_CLASS}: {cls}")
            time.sleep(0.5)  # increased delay to avoid rate limits
        start_index += len(images)
        # Google Custom Search API limit is 100 results per query
        if start_index > 100:
            break

# save metadata
with open(OUTPUT_DIR / "metadata.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print("Done. Total images:", len(rows))
