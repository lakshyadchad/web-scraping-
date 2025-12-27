# save_as: scrape_images_selenium.py
import os, time, csv, hashlib
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import requests
from tqdm import tqdm

CLASSES = ["Naval Mine", "Torpedo Shape", "Military Submarine", "AUV (Autonomous Underwater Vehicle)"]
IMAGES_PER_CLASS = 150
OUTPUT_DIR = Path("dataset_selenium")
OUTPUT_DIR.mkdir(exist_ok=True)

# set up driver
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
from selenium.webdriver.chrome.service import Service
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def download_image(url, path):
    try:
        r = requests.get(url, stream=True, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        # print("dl err", e)
        return False

rows = []
for cls in CLASSES:
    cls_dir = OUTPUT_DIR / cls
    cls_dir.mkdir(parents=True, exist_ok=True)
    query = cls.replace(" ", "+")
    url = f"https://duckduckgo.com/?q={query}&t=h_&iax=images&ia=images"
    driver.get(url)
    time.sleep(2)
    # Find the JS variable token required by DuckDuckGo image results (they lazy-load via XHR)
    # Simpler approach: scroll and collect thumbnail <img> tags
    thumbnails = set()
    scrolls = 0
    while len(thumbnails) < IMAGES_PER_CLASS and scrolls < 40:
        # scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.0 + (scrolls % 3) * 0.5)
        imgs = driver.find_elements(By.CSS_SELECTOR, "img.tile--img__img")
        for im in imgs:
            src = im.get_attribute("src")
            if src and src.startswith("http"):
                thumbnails.add(src)
        scrolls += 1

    print(f"Found {len(thumbnails)} thumbnails for {cls}")
    count = 0
    for src in list(thumbnails):
        if count >= IMAGES_PER_CLASS: break
        # some thumbnails are data URLs or tiny thumbnails — try to open and get a better src by clicking the tile
        try:
            # attempt to click the thumbnail element that has this src
            elems = driver.find_elements(By.CSS_SELECTOR, f"img[src='{src}']")
            if elems:
                elems[0].click()
                time.sleep(0.5)
                # full image appears in a panel; get src from .detail__media--img or 'img.detail__media'
                imgs_full = driver.find_elements(By.CSS_SELECTOR, "img.detail__media--img, img.detail__media")
                full_url = None
                for imf in imgs_full:
                    fu = imf.get_attribute("src")
                    if fu and fu.startswith("http"):
                        full_url = fu
                        break
                if not full_url:
                    full_url = src
            else:
                full_url = src
        except Exception:
            full_url = src
        ext = os.path.splitext(full_url)[1].split("?")[0]
        if len(ext) > 5 or ext == "": ext = ".jpg"
        fname = cls_dir / f"{count:04d}{ext}"
        ok = download_image(full_url, fname)
        if not ok:
            # try fallback: download thumbnail src
            ok = download_image(src, fname)
            if not ok:
                continue
        with open(fname, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()
        rows.append({
            "filename": str(fname), "class": cls, "original_url": full_url, "source_site": "duckduckgo.com", "sha256": sha
        })
        count += 1
        time.sleep(0.2)
    print(f"Downloaded {count} for {cls}")

# save metadata
if rows:
    import csv
    with open(OUTPUT_DIR / "metadata.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Total images downloaded: {len(rows)}")
else:
    print("No images were downloaded. Check your internet connection or try a different search engine.")

driver.quit()
print("Done.")
