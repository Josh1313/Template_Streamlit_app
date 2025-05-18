
import chardet
import pandas as pd
import streamlit as st
import tempfile
import os

def app():
    st.title("Files 📚")
    st.write("Upload your CSV or Excel files for analysis.")
    st.write("This page allows you to upload files and process them.")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
    
    # Process file if uploaded
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        if df is not None:
            # Save the dataframe to session state so it can be accessed from other pages
            st.session_state.uploaded_df = df
            st.session_state.uploaded_filename = uploaded_file.name
            
            # Show preview
            st.write("### Preview of the uploaded file")
            st.dataframe(df.head())
            
            st.success(f"File '{uploaded_file.name}' is now available for analysis in the Chat page.")

def load_data(uploaded_file):
    if uploaded_file is None:
        return None

    try:
        if uploaded_file.name.endswith(".csv"):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            # Step 1: Detect encoding just once
            with open(tmp_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding'] or 'utf-8'

            # Step 2: Read the CSV with detected encoding
            df = pd.read_csv(tmp_path, encoding=encoding)

            # Step 3: Save a cleaned version as proper UTF-8
            cleaned_path = tmp_path.replace(".csv", "_utf8.csv")
            df.to_csv(cleaned_path, index=False, encoding='utf-8')

        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file).fillna(0)

        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None

        st.success(f"File '{uploaded_file.name}' loaded and converted successfully.")
        return df.fillna(0)

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None