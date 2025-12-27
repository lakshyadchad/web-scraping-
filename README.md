# 🌊 Underwater Objects Image Dataset Builder

A complete toolkit for building machine learning image datasets by scraping images from the web. This project specifically collects images of underwater military and autonomous vehicles for computer vision tasks.

---

## 📋 Table of Contents

- [Overview](#overview)
- [What This Project Creates](#what-this-project-creates)
- [The Three Scripts](#the-three-scripts)
- [Quick Start Guide](#quick-start-guide)
- [Detailed Usage](#detailed-usage)
- [Output Structure](#output-structure)
- [Which Method Should You Use?](#which-method-should-you-use)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project helps you automatically collect and prepare image datasets for machine learning. It's designed to gather images of:

- 🎯 **Naval Mines**
- 🚀 **Torpedo Shapes**
- 🚢 **Military Submarines**
- 🤖 **AUVs (Autonomous Underwater Vehicles)**

### Greater Purpose

Building a custom image dataset is often the first step in creating:
- **Object detection models** (e.g., YOLO, Faster R-CNN)
- **Image classification systems** (e.g., ResNet, EfficientNet)
- **Computer vision applications** for underwater surveillance
- **Training datasets** for autonomous underwater navigation

Instead of manually downloading hundreds of images, this toolkit automates the entire process!

---

## 📦 What This Project Creates

```
web scraping/
├── 📄 download_images_api.py      # Google API scraper
├── 📄 scrape_images_selenium.py   # DuckDuckGo scraper
├── 📄 postprocess_images.py       # Image cleaner & organizer
│
├── 📁 dataset/                     # Raw images from Google API
│   ├── metadata.csv
│   ├── Naval Mine/
│   │   ├── 0000.jpg
│   │   ├── 0001.jpg
│   │   └── ...
│   ├── Torpedo Shape/
│   ├── Military Submarine/
│   └── AUV (Autonomous Underwater Vehicle)/
│
├── 📁 dataset_selenium/            # Raw images from DuckDuckGo
│   └── (same structure as above)
│
└── 📁 dataset_clean/               # Processed & split dataset
    ├── metadata_clean.csv
    ├── Naval Mine/
    ├── Torpedo Shape/
    ├── Military Submarine/
    └── AUV (Autonomous Underwater Vehicle)/
```

---

## 🔧 The Three Scripts

### 1️⃣ `download_images_api.py` - Google API Method

```
┌─────────────────────────────────────────┐
│  Google Custom Search API               │
│  ↓                                       │
│  Fetch image URLs (10 per request)      │
│  ↓                                       │
│  Download images                         │
│  ↓                                       │
│  Save to dataset/ folder                 │
│  ↓                                       │
│  Generate metadata.csv                   │
└─────────────────────────────────────────┘
```

**Use when:** You have API credentials and want reliable, high-quality results

---

### 2️⃣ `scrape_images_selenium.py` - DuckDuckGo Method

```
┌─────────────────────────────────────────┐
│  Open Chrome browser (headless)          │
│  ↓                                       │
│  Navigate to DuckDuckGo Images           │
│  ↓                                       │
│  Scroll page to load thumbnails          │
│  ↓                                       │
│  Click thumbnails → Get full images      │
│  ↓                                       │
│  Download images                         │
│  ↓                                       │
│  Save to dataset_selenium/ folder        │
│  ↓                                       │
│  Generate metadata.csv                   │
└─────────────────────────────────────────┘
```

**Use when:** You don't have API access or need more than 100 images per class

---

### 3️⃣ `postprocess_images.py` - Image Cleaner

```
┌─────────────────────────────────────────┐
│  Read images from dataset/               │
│  ↓                                       │
│  Remove duplicates (SHA256 hash)         │
│  ↓                                       │
│  Filter out tiny images (<50x50)         │
│  ↓                                       │
│  Resize all to 224x224                   │
│  ↓                                       │
│  Split into train/val/test (80/10/10)    │
│  ↓                                       │
│  Save to dataset_clean/                  │
│  ↓                                       │
│  Generate metadata_clean.csv             │
└─────────────────────────────────────────┘
```

**Purpose:**
- Remove duplicate images
- Standardize image sizes
- Remove corrupted/tiny images
- Create train/validation/test splits
- Prepare dataset for ML training

---

## 🚀 Quick Start Guide

### Prerequisites

Install required packages:

```powershell
pip install selenium webdriver-manager requests pillow pandas tqdm
```

### Option A: Use Google API (Recommended)

1. **Get API credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable "Custom Search API"
   - Create API key
   - Create Custom Search Engine at [cse.google.com](https://cse.google.com)
   - Get your CX (Search Engine ID)

2. **Edit `download_images_api.py`:**
   ```python
   API_KEY = "your-api-key-here"
   CX = "your-search-engine-id-here"
   ```

3. **Run:**
   ```powershell
   python download_images_api.py
   ```

### Option B: Use DuckDuckGo (No Setup Required)

```powershell
python scrape_images_selenium.py
```

### Step 3: Clean & Prepare Dataset

```powershell
python postprocess_images.py
```

**Done!** Your dataset is ready in `dataset_clean/`

---

## 📚 Detailed Usage

### Customize Your Dataset

Edit the configuration in any script:

```python
# Change the classes you want to download
CLASSES = [
    "Naval Mine", 
    "Torpedo Shape", 
    "Military Submarine", 
    "AUV (Autonomous Underwater Vehicle)"
]

# Change number of images per class
IMAGES_PER_CLASS = 150  # or 200, 500, etc.

# Change output folder
OUTPUT_DIR = Path("my_custom_dataset")
```

### Postprocessing Options

Edit `postprocess_images.py` to customize:

```python
DATA_DIR = Path("dataset")          # Source folder
OUT_DIR = Path("dataset_clean")     # Output folder
MIN_SIZE = (50, 50)                 # Minimum image dimensions
TARGET_SIZE = (224, 224)            # Resize to this size

# Train/val/test split ratios
train_pct, val_pct = 0.8, 0.1       # 80% train, 10% val, 10% test
```

---

## 📊 Output Structure

### Metadata CSV Files

Each script generates a CSV file with tracking information:

**`dataset/metadata.csv`** (from API):
```csv
filename,class,original_url,source_site,width,height,sha256,license
dataset\Naval Mine\0000.jpg,Naval Mine,https://example.com/img.jpg,example.com,800,600,abc123...,
```

**`dataset_clean/metadata_clean.csv`** (after processing):
```csv
filename,class,sha256,width,height,split
dataset_clean\Naval Mine\0000.jpg,Naval Mine,abc123...,224,224,train
dataset_clean\Naval Mine\0001.jpg,Naval Mine,def456...,224,224,val
dataset_clean\Naval Mine\0002.jpg,Naval Mine,ghi789...,224,224,test
```

The `split` column tells you which images to use for:
- **train**: Training your model (80%)
- **val**: Validating during training (10%)
- **test**: Final evaluation (10%)

---


```

### For Best Results:

1. **Start with API method** if you have credentials
2. **Supplement with Selenium** if you need more images
3. **Always run postprocess** to clean the dataset

You can even combine both:
```powershell
# Download from both sources
python download_images_api.py
python scrape_images_selenium.py

# Merge and clean
# (manually copy images or edit postprocess_images.py to read from both folders)
python postprocess_images.py
```

---

## 🔧 Troubleshooting

### Common Issues

**Problem:** "ChromeDriver not found"
```powershell
# Solution: Install webdriver-manager
pip install webdriver-manager
```

**Problem:** "API quota exceeded"
```
# Solution: 
# 1. Wait 24 hours for quota reset
# 2. Use Selenium method instead
# 3. Upgrade to paid Google API plan
```

**Problem:** "No images downloaded"
```
# Solutions:
# 1. Check internet connection
# 2. DuckDuckGo may have changed HTML structure
# 3. Try different search terms in CLASSES
# 4. Use API method instead
```

**Problem:** "Module not found"
```powershell
# Install all dependencies
pip install selenium webdriver-manager requests pillow pandas tqdm
```

**Problem:** Images are corrupted/wrong
```
# Solution: Run postprocess_images.py
# It will filter out bad images automatically
```

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### ⚠️ Important Legal Notice

**The MIT License applies ONLY to the source code in this repository.**

The images downloaded using these tools are **NOT** covered by this license and remain subject to their original copyright holders' terms.

**You are responsible for:**
- ✅ Respecting copyright laws for all downloaded images
- ✅ Complying with Google API and DuckDuckGo terms of service
- ✅ Following fair use guidelines (academic/research purposes)
- ✅ Verifying licensing rights before commercial use
- ✅ Ensuring proper attribution when required

**We are NOT responsible for any copyright violations or misuse of downloaded content.**

---

## 🤝 Contributing

To improve this project:
1. Add support for more search engines (Bing, Yahoo)
2. Implement better duplicate detection
3. Add progress bars with `tqdm`
4. Create automatic annotation tools
5. Add data augmentation pipeline
6. Add more classes like other therts in ocean 
7. how to increase it efficiency to collect thousand of image 

---

## 📞 Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Verify all dependencies are installed
3. Try the alternative scraping method
4. Check that websites haven't changed their structure

---

