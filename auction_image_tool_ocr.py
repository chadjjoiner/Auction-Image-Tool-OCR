import streamlit as st
import zipfile
import os
import shutil
from PIL import Image
import tempfile
import pytesseract

st.image("https://raw.githubusercontent.com/chadjjoiner/auctionimagetoolv2/main/logo.jpeg", width=200)
st.title("📦 Auction Image Tool OCR")

st.markdown("""
**How it works (OCR-powered):**
1. Upload a ZIP of **all images**, including:
   - Lot tag images (with lot numbers written clearly)
   - Lot item images
2. Optionally enter:
   - Lot numbers to **skip** (e.g. 113, 116)
   - Extra lots to **insert** (e.g. 105A, 110B)
   - Last lot number used in previous batch
3. The app:
   - Uses OCR to detect lot numbers on tag images
   - Resizes and renames images:
     - `101.jpg` (tag, not included in output)
     - `101-1.jpg`, `101-2.jpg` (lot item photos)
4. Download a ZIP of organized, resized lot images.
""")


img_zip = st.file_uploader("Upload ZIP with ALL images", type="zip")

last_lot_input = st.number_input("📍 Last lot number used in previous batch (leave 0 to start at 1)", min_value=0, value=0)
skip_lots_input = st.text_input("❌ Enter lot numbers to skip (e.g. 113, 116)")
extra_lots_input = st.text_input("➕ Enter extra lots to insert (e.g. 105A, 110B)")

if img_zip and tag_zip:
    with tempfile.TemporaryDirectory() as temp_dir:
        all_dir = os.path.join(temp_dir, "all")
        tags_dir = os.path.join(temp_dir, "tags")
        resized_dir = os.path.join(temp_dir, "resized")
        os.makedirs(all_dir)
        os.makedirs(tags_dir)
        os.makedirs(resized_dir)

        with zipfile.ZipFile(img_zip, 'r') as zip_ref:
            zip_ref.extractall(all_dir)

        with zipfile.ZipFile(tag_zip, 'r') as zip_ref:
            zip_ref.extractall(tags_dir)

        def list_images(folder):
            return sorted([
                os.path.join(dp, f) for dp, _, filenames in os.walk(folder)
                for f in filenames if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith("._")
            ])

        all_imgs = list_images(all_dir)
        tag_imgs = list_images(tags_dir)

        skip_lots = [lot.strip() for lot in skip_lots_input.split(',') if lot.strip()] if skip_lots_input else []
        extra_lots = [lot.strip() for lot in extra_lots_input.split(',') if lot.strip()] if extra_lots_input else []

        base_lot_start = last_lot_input + 1
        needed_count = len(tag_imgs) - len(extra_lots)

        base_lots = [str(i) for i in range(base_lot_start, base_lot_start + needed_count + len(skip_lots) + len(extra_lots)) if str(i) not in skip_lots]

        # Insert extra lots into position immediately after base lots where applicable
        full_lots = []
        extra_lot_map = {}
        for lot in base_lots:
            full_lots.append(lot)
            for extra in extra_lots:
                if extra.startswith(lot):
                    full_lots.append(extra)

        # Use OCR to extract lot numbers from tag images
        def extract_lot_number(image_path):
            try:
                text = pytesseract.image_to_string(Image.open(image_path))
                text = text.strip().split("\n")[0]  # Take first line
                return text if text else None
            except:
                return None

        tag_map = {}
        for path in tag_imgs:
            lot_num = extract_lot_number(path)
            if lot_num:
                tag_map[os.path.basename(path)] = lot_num

        rename_plan = []
        current_lot = None
        suffix = 0

        for img_path in sorted(all_imgs):
            name = os.path.basename(img_path)

            if name in tag_map:
                current_lot = tag_map[name]
                suffix = 0
                new_name = f"{current_lot}.jpg"
                continue  # Skip saving tag image
            elif current_lot:
                suffix += 1
                new_name = f"{current_lot}-{suffix}.jpg"
            else:
                new_name = name

            with Image.open(img_path) as img:
                w, h = img.size
                size = (1500, 1125) if w > h else (1125, 1500)
                img = img.resize(size, Image.Resampling.LANCZOS)
                img.save(os.path.join(resized_dir, new_name))

            rename_plan.append((name, new_name))

        zip_out_path = os.path.join(temp_dir, "auction_image_tool_OCR_output.zip")
        with zipfile.ZipFile(zip_out_path, 'w') as zipf:
            for f in os.listdir(resized_dir):
                zipf.write(os.path.join(resized_dir, f), arcname=f)

        st.success("✅ Done! Download your renamed and resized image set:")
        with open(zip_out_path, "rb") as f:
            st.download_button("📥 Download ZIP", f, file_name="auction_image_tool_OCR_output.zip")
