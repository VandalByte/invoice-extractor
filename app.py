import streamlit as st
from PIL import Image
from model import ocr_text_extract, get_model_response
import pandas as pd
import json

# page configuration
st.set_page_config(page_title="Invoice OCR", layout="wide")
st.title("📄 Invoice OCR App")
st.markdown("Upload invoices in PNG, JPG, or PDF format.")

# file uploader
uploaded_files = st.file_uploader("Choose files", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)

def show_preview(uploaded_files):
    """Display a preview of uploaded images."""
    if uploaded_files:
        cols = st.columns(5)  # create five columns for side-by-side display
        for i, uploaded_file in enumerate(uploaded_files):
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            if file_extension in ["png", "jpg", "jpeg"]:
                image = Image.open(uploaded_file)
                image = image.resize((250, 520))  # resize image for consistency
                with cols[i % 5]:
                    st.image(image, caption=f'Uploaded Image {i+1}', width=250)

@st.cache_data
def process_files(uploaded_files):
    """Process uploaded files and return extracted data."""
    all_data = []

    for uploaded_file in uploaded_files:
        # extract text using OCR
        extracted_text = ocr_text_extract(uploaded_file)
        if not extracted_text:
            st.warning(f"No text extracted from {uploaded_file.name}. Skipping...")
            continue

        # get model response (JSON data)
        json_output = get_model_response(extracted_text)
        if not json_output:
            st.error(f"Failed to process {uploaded_file.name}. Skipping...")
            continue

        # parse JSON and append to all_data
        try:
            data = json.loads(json_output)
            all_data.append(data)
        except json.JSONDecodeError:
            st.error(f"Invalid JSON response for {uploaded_file.name}. Skipping...")

    return all_data

def generate_excel(all_data):
    """Generate an Excel file from the extracted data."""
    rows = []

    for data in all_data:
        store_name = data.get("store_name", "")
        address = data.get("address", "")
        phone = data.get("phone", "")
        date_time = data.get("date_time", "")
        cashier = data.get("cashier", "")
        discount = data.get("discount", "")
        total_amount = data.get("total_amount", "")
        final_total = data.get("final_total", "")
        payment = data.get("payment", "")
        change = data.get("change", "")

        # aggregate items into a single string
        items = data.get("items", [])
        items_str = "; ".join(
            [f"{item.get('name', '')} (Qty: {item.get('quantity', '')}, Price: {item.get('unit_price', '')}, Total: {item.get('total_price', '')})"
             for item in items]
        )

        # add a single row for this invoice
        rows.append({
            "Store Name": store_name,
            "Address": address,
            "Phone": phone,
            "Date/Time": date_time,
            "Cashier": cashier,
            "Items": items_str,  # aggregated items
            "Discount": discount,
            "Total Amount": total_amount,
            "Final Total": final_total,
            "Payment": payment,
            "Change": change
        })


    df = pd.DataFrame(rows)

    excel_file = "extracted_invoice_data.xlsx"
    df.to_excel(excel_file, index=False, engine="openpyxl")

    # read the file back into bytes for download
    with open(excel_file, "rb") as f:
        excel_bytes = f.read()

    return excel_bytes

# show preview of uploaded files
show_preview(uploaded_files)

# process files and generate Excel
if uploaded_files:
    st.write("Processing files...")
    all_data = process_files(uploaded_files)

    if all_data:
        st.write("Generating Excel file...")
        excel_file = generate_excel(all_data)
        st.success("Excel file generated successfully!")
        st.download_button(
            label="Download Excel File",
            data=excel_file,
            file_name="extracted_invoice_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
