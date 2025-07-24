# 📦 Auction Image Tool OCR

A simple drag-and-drop web app for industrial auctioneers and liquidators. This tool automatically:

- Extracts lot numbers from handwritten tags using OCR
- Renames lot images accordingly (e.g., `101-1.jpg`, `101-2.jpg`)
- Resizes all images for consistent upload/presentation
- Packages the results into a downloadable ZIP

## 🧠 Features

- 🧾 OCR-based tag recognition via Tesseract
- 💡 Intelligent skipping and inserting of custom lot numbers (e.g. `113`, `105A`)
- 📐 Auto-resizing: 1500x1125 (landscape), 1125x1500 (portrait)
- ✅ Fully local or deployable to Render.com

## 🚀 How to Use

1. Upload a ZIP of **all images** (tag + lot images)
2. Upload a second ZIP of **tag images only**, in order
3. Optionally input:
   - Last used lot number
   - Lots to skip
   - Lots to insert (e.g. 110A, 110B)
4. Download your organized image set as a ZIP

## 🧰 Tech Stack

- Python
- Streamlit
- Tesseract OCR via `pytesseract`
- Pillow (image resizing)

## 🌍 Deploying to Render

1. Make sure this repo contains:
   - `auction_image_tool_ocr.py`
   - `requirements.txt`
   - `render.yaml`
   - `logo.jpeg`

2. Go to [Render.com](https://render.com)
3. Create a new Web Service
4. Connect this GitHub repo
5. Let Render install dependencies and start the app

## 🖼 Logo

To change the logo:
- Replace `logo.jpeg` in the repo root
- Keep the filename the same, or update the code reference in `auction_image_tool_ocr.py`

---

### 🙌 Created by Chad Joiner

For internal use or as a helpful public tool — feel free to fork and modify!
