
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

# Logo
st.image("https://raw.githubusercontent.com/chadjjoiner/auction-image-tool-ocr/main/logo.jpeg", width=250)

st.title("📸 Auction Image Tool (OCR-Based)")
st.markdown("Upload a **ZIP of all images** (tags + lot items). We’ll auto-detect lot numbers and group + rename images.")

img_zip = st.file_uploader("Upload ZIP with ALL images (tags + lot items)", type="zip")
last_lot_input = st.number_input("📍 Last lot number used in previous batch (leave 0 to start at 1)", min_value=0, value=0)
skip_lots_input = st.text_input("❌ Enter lot numbers to skip (e.g. 113, 116)").replace(" ", "")
extra_lots_input = st.text_input("➕ Enter extra lots to insert (e.g. 105A, 110B)").replace(" ", "")

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
    detected_lots = []
    skip_lots = [s.strip().upper() for s in skip_lots_input.split(",") if s.strip()]
    extra_lots = [e.strip().upper() for e in extra_lots_input.split(",") if e.strip()]
    extra_lots_iter = iter(extra_lots)

    debug_output = []

    # OCR & group
    for fname in image_files:
        fpath = os.path.join(extract_dir, fname)
        try:
            img = Image.open(fpath)
            text = pytesseract.image_to_string(img)
            debug_output.append(f"**{fname}**: {text.strip()}")
            match = re.search(r"(\d{3}[A-Z]?)", text.strip(), re.IGNORECASE)
            if match:
                lot_id = match.group(1).upper()
                if lot_id not in skip_lots:
                    current_lot = lot_id
                    lot_map[current_lot] = []
                    detected_lots.append(current_lot)
                else:
                    current_lot = None
            elif current_lot:
                lot_map[current_lot].append(fname)
        except Exception as e:
            st.warning(f"Could not read {fname}: {e}")

    # Add extra A/B lots manually
    for xlot in extra_lots:
        if xlot not in lot_map:
            lot_map[xlot] = []

    if not lot_map:
        st.error("❌ No valid lot numbers detected. Please ensure your tag images have clear numbers (e.g. 101, 105A).")
        with st.expander("🔍 OCR Debug Output"):
            for line in debug_output:
                st.markdown(line)
    else:
        st.markdown("### ✅ Detected Lots")
        st.write(sorted(lot_map.keys()))

        with st.expander("🔍 OCR Debug Output"):
            for line in debug_output:
                st.markdown(line)

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
