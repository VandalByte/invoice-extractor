import streamlit as st
from PIL import Image
# import pdf2image
import os

st.set_page_config(page_title="Invoice OCR", layout="wide")
st.title("📄 Invoice OCR App")
st.markdown("Upload invoices in PNG, JPG, or PDF format.")

# file uploader
uploaded_files = st.file_uploader("Choose files", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)


def show_preview(uploaded_files):
    if uploaded_files:
        cols = st.columns(5)  # create five columns for side-by-side display
        for i, uploaded_file in enumerate(uploaded_files):
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_extension in [".png", ".jpg", ".jpeg"]:
                image = Image.open(uploaded_file)
                image = image.resize((250, 520))  # resize image for consistency
                with cols[i % 5]:
                    st.image(image, caption=f'Uploaded Image {i+1}', width=250)

show_preview(uploaded_files=uploaded_files)