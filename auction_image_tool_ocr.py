
import streamlit as st
import zipfile
import os
import shutil
from PIL import Image
import pytesseract
import re
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Auction Image Tool OCR", layout="centered")

st.title("📸 Auction Image Tool (OCR-based)")
st.markdown("Upload a **ZIP of all images** (tags and items). We'll detect lot numbers automatically, group and rename them, and prepare a download.")

img_zip = st.file_uploader("Upload ZIP with ALL images (tags + lot items)", type="zip")
last_lot_input = st.number_input("📍 Last lot number used in previous batch (leave 0 to start at 1)", min_value=0, value=0)

if img_zip:
    with zipfile.ZipFile(img_zip, "r") as zip_ref:
        extract_dir = "extracted_images"
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)

        zip_ref.extractall(extract_dir)
        image_files = sorted([
            f for f in os.listdir(extract_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

    lot_map = {}
    current_lot = None
    lot_counter = last_lot_input

    # Detect lot numbers and group images
    for fname in image_files:
        fpath = os.path.join(extract_dir, fname)
        try:
            img = Image.open(fpath)
            text = pytesseract.image_to_string(img)
            match = re.search(r"(?:lot\s*)?(\d{3}[A-Z]?)", text, re.IGNORECASE)
            if match:
                current_lot = match.group(1).upper()
                lot_map[current_lot] = []
            elif current_lot:
                lot_map[current_lot].append(fname)
        except Exception as e:
            st.warning(f"Could not read {fname}: {e}")

    # Prepare output
    output_dir = "renamed_images"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    renamed_files = []
    for lot, files in lot_map.items():
        for idx, original_name in enumerate(files, start=1):
            ext = os.path.splitext(original_name)[1]
            new_name = f"{lot}-{idx}{ext}"
            shutil.copy(os.path.join(extract_dir, original_name), os.path.join(output_dir, new_name))
            renamed_files.append(new_name)

    # Create zip
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for file in renamed_files:
            zipf.write(os.path.join(output_dir, file), arcname=file)
    zip_buffer.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.success("🎉 Done! Download your renamed lot images below:")
    st.download_button(
        label="📦 Download Renamed ZIP",
        data=zip_buffer,
        file_name=f"renamed_lots_{timestamp}.zip",
        mime="application/zip"
    )
