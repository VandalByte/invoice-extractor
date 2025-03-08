import json
import google.generativeai as genai
import streamlit as st
import re
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash-latest"

# configure the API
genai.configure(api_key=API_KEY)

# # extracted receipt text for TESTING
# receipt_text = """
# tan woon yann
# INDAH GIFT& HOME IECO
# 27JALAN DEDAP 13
# TAMAN JOHOR JAYA
# 81100JOH0R BAHRU.JOHOR
# Te1:07-3507405 Fax:07-3558160
# RECEIPT
# 19/10/2018
# 20:49:59#01
# Cashier: CN
# Location/sP:05/0531
# MBM026588
# Room No:01
# 050100035279
# Desc/Item
# Qty
# Price Amt(RM)
# ST-PRIVILEGE CARD/GD INDAH
# 88888
# 1
# 10.00
# 10.00
# GF-TABLE LAMP/STITCH <i
# 62483
# 1
# 55.90
# 55.90
# @ISC10.00%
# -5.59
# #Total Qty
# 2
# TOTAL AMT.
# RM
# 60.31
# ROUNDING ADJ.
# -0.01
# RH
# 60.30
# CASH.
# RM
# 70.30
# CHANGE.
# RM
# 10.00
# Thank You Please Come Again !
# Goods Sold Are Not Returnable
# Dealing In Wholesale And Retail.
# """


def get_model_response(ocr_generated_data):
    prompt = f"""
    Extract important details from the receipt, correct any spelling errors, and return a properly formatted JSON object.

    ### **Requirements:**
    - **Correct spelling mistakes** in names, addresses, and other details.
    - Ensure the output contains these fields:
    - `"store_name"`: Store name
    - `"address"`: Store address
    - `"phone"`: Contact number
    - `"date_time"`: Date and time of the transaction
    - `"cashier"`: Cashier's name
    - `"items"`: A list of purchased items with:
        - `"name"`: Item name (correct spelling if needed)
        - `"quantity"`: Quantity purchased
        - `"unit_price"`: Price per unit
        - `"total_price"`: Total price for item
    - `"discount"`: Any discount applied
    - `"total_amount"`: Total amount before rounding
    - `"final_total"`: Final payable amount after rounding
    - `"payment"`: Amount paid
    - `"change"`: Change returned

    ### **Instructions:**
    - **Fix typos and spacing issues** in store names, addresses, and product descriptions.
    - Keep **dates and numbers formatted correctly**.
    - Preserve currency (`RM`) and numerical values as extracted.
    - **Return only valid JSON** with no extra text, explanations, or formatting.

    ### **Extracted Receipt Text:**
    {ocr_generated_data}

    **Output:** Return only a valid JSON object.
    """

    model = genai.GenerativeModel(MODEL_NAME)

    response = model.generate_content(prompt)
    raw_output = response.text.strip()
    # remove triple backticks if present
    cleaned_json_text = re.sub(r"```json\n?|```", "", raw_output).strip()

    # parse response to JSON
    try:
        cleaned_data = json.loads(cleaned_json_text)
        return json.dumps(cleaned_data, indent=2)
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON response from Gemini.")
        print("RAW OUTPUT:\n", raw_output)
        # TODO: remove the line and add 'raise' catch the exception in the app.py
        # st.error(f"ERROR: Invalid JSON response from Gemini.\n\nRAW OUTPUT:\n\n{raw_output}")
    return None
