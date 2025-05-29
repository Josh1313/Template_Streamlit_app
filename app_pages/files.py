import chardet
import pandas as pd
import streamlit as st
import tempfile
import os
import json
from datetime import datetime

# Configuration
DATASETS_DIR = "stored_datasets"
METADATA_FILE = "datasets_metadata.json"

def initialize_storage():
    """Initialize the datasets storage system"""
    if not os.path.exists(DATASETS_DIR):
        os.makedirs(DATASETS_DIR)
    
    if 'datasets_metadata' not in st.session_state:
        st.session_state.datasets_metadata = load_metadata()

def load_metadata():
    """Load datasets metadata from file"""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_metadata():
    """Save datasets metadata to file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(st.session_state.datasets_metadata, f, indent=2)

def clean_dataframe_for_parquet(df):
    """Clean DataFrame to ensure compatibility with parquet format"""
    df_clean = df.copy()
    
    for col in df_clean.columns:
        # Check if column has mixed types
        if df_clean[col].dtype == 'object':
            # Try to convert to numeric first
            try:
                # Attempt numeric conversion
                numeric_series = pd.to_numeric(df_clean[col], errors='coerce')
                # If most values convert successfully, use numeric
                if numeric_series.notna().sum() / len(df_clean[col]) > 0.8:
                    df_clean[col] = numeric_series
                else:
                    # Convert everything to string to ensure consistency
                    df_clean[col] = df_clean[col].astype(str)
            except:
                # If conversion fails, convert to string
                df_clean[col] = df_clean[col].astype(str)
        
        # Handle any remaining mixed types by converting to string
        elif df_clean[col].dtype.name == 'mixed' or 'mixed' in str(df_clean[col].dtype):
            df_clean[col] = df_clean[col].astype(str)
    
    # Fill any remaining NaN values
    df_clean = df_clean.fillna('')
    
    return df_clean

def save_dataset(df, filename):
    """Save dataset to storage and return dataset ID"""
    dataset_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename.replace('.', '_')}"
    file_path = os.path.join(DATASETS_DIR, f"{dataset_id}.parquet")
    
    try:
        # Clean the dataframe to ensure parquet compatibility
        df_clean = clean_dataframe_for_parquet(df)
        
        # Save as parquet for better performance
        df_clean.to_parquet(file_path, engine='pyarrow', index=False)
        
        # Update metadata
        st.session_state.datasets_metadata[dataset_id] = {
            "original_name": filename,
            "upload_date": datetime.now().isoformat(),
            "rows": len(df),
            "columns": len(df.columns),
            "file_path": file_path,
            "size_mb": round(os.path.getsize(file_path) / (1024*1024), 2)
        }
        
        save_metadata()
        return dataset_id
        
    except Exception as e:
        # If parquet still fails, fall back to pickle format
        st.warning(f"Parquet save failed, using pickle format instead. Error: {str(e)}")
        file_path_pickle = file_path.replace('.parquet', '.pkl')
        df.to_pickle(file_path_pickle)
        
        # Update metadata with pickle path
        st.session_state.datasets_metadata[dataset_id] = {
            "original_name": filename,
            "upload_date": datetime.now().isoformat(),
            "rows": len(df),
            "columns": len(df.columns),
            "file_path": file_path_pickle,
            "size_mb": round(os.path.getsize(file_path_pickle) / (1024*1024), 2),
            "format": "pickle"
        }
        
        save_metadata()
        return dataset_id

def load_dataset(dataset_id):
    """Load dataset from storage"""
    if dataset_id in st.session_state.datasets_metadata:
        metadata = st.session_state.datasets_metadata[dataset_id]
        file_path = metadata["file_path"]
        
        if os.path.exists(file_path):
            try:
                # Check if it's pickle format
                if metadata.get("format") == "pickle" or file_path.endswith('.pkl'):
                    return pd.read_pickle(file_path)
                else:
                    return pd.read_parquet(file_path)
            except Exception as e:
                st.error(f"Error loading dataset: {str(e)}")
                return None
    return None

def delete_dataset(dataset_id):
    """Delete dataset from storage"""
    if dataset_id in st.session_state.datasets_metadata:
        file_path = st.session_state.datasets_metadata[dataset_id]["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)
        del st.session_state.datasets_metadata[dataset_id]
        save_metadata()
        return True
    return False

def app():
    st.title("Files 📚")
    st.write("Upload and manage your CSV or Excel files for analysis.")
    
    # Initialize storage system
    initialize_storage()
    
    # Create tabs
    tab1, tab2 = st.tabs(["📤 Upload Files", "📋 Manage Datasets"])
    
    with tab1:
        upload_section()
    
    with tab2:
        manage_section()
    
    # Show active dataset info
    show_active_dataset()

def upload_section():
    """Handle file upload functionality"""
    st.write("### Upload a new dataset")
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        with st.spinner("Processing file..."):
            df = load_data(uploaded_file)
            
            if df is not None:
                # Show preview
                st.write("### Preview")
                st.dataframe(df.head())
                
                # Show column info
                st.write("### Column Information")
                col_info = []
                for col in df.columns:
                    col_info.append({
                        'Column': col,
                        'Type': str(df[col].dtype),
                        'Non-null': df[col].count(),
                        'Null': df[col].isnull().sum()
                    })
                st.dataframe(pd.DataFrame(col_info))
                
                # Show stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    st.metric("Size (MB)", round(uploaded_file.size / (1024*1024), 2))
                
                # Save and use buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Dataset", type="primary"):
                        with st.spinner("Saving dataset..."):
                            dataset_id = save_dataset(df, uploaded_file.name)
                            st.success(f"Dataset saved! ID: {dataset_id[:8]}...")
                            st.rerun()
                
                with col2:
                    if st.button("🚀 Use for Chat", type="secondary"):
                        # Clear any existing chat/analysis state first
                        clear_chat_state()
                        
                        st.session_state.uploaded_df = df
                        st.session_state.uploaded_filename = uploaded_file.name
                        st.success("Dataset is now active for chat!")
                        st.info("💡 Go to Chat tab to start analyzing your data.")

def manage_section():
    """Handle dataset management"""
    st.write("### Your Stored Datasets")
    
    if not st.session_state.datasets_metadata:
        st.info("No datasets stored yet.")
        return
    
    # Create dataset list
    for i, (dataset_id, meta) in enumerate(st.session_state.datasets_metadata.items()):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{meta['original_name']}**")
                format_info = f" ({meta.get('format', 'parquet')})" if meta.get('format') else ""
                st.caption(f"Uploaded: {datetime.fromisoformat(meta['upload_date']).strftime('%Y-%m-%d %H:%M')} | "
                          f"{meta['rows']} rows, {meta['columns']} cols | {meta['size_mb']} MB{format_info}")
            
            with col2:
                if st.button("👁️", key=f"preview_{i}", help="Preview"):
                    df = load_dataset(dataset_id)
                    if df is not None:
                        st.dataframe(df.head())
            
            with col3:
                if st.button("📊", key=f"use_{i}", help="Use for Chat"):
                    df = load_dataset(dataset_id)
                    if df is not None:
                        st.session_state.uploaded_df = df
                        st.session_state.uploaded_filename = meta['original_name']
                        st.session_state.current_dataset_id = dataset_id
                        st.success(f"Now using: {meta['original_name']}")
            
            with col4:
                if st.button("📥", key=f"download_{i}", help="Download"):
                    df = load_dataset(dataset_id)
                    if df is not None:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "Download",
                            csv,
                            f"{meta['original_name']}.csv",
                            "text/csv",
                            key=f"dl_{i}"
                        )
            
            with col5:
                if st.button("🗑️", key=f"delete_{i}", help="Delete"):
                    if delete_dataset(dataset_id):
                        # Clear session if this was active dataset
                        if st.session_state.get('current_dataset_id') == dataset_id:
                            clear_active_dataset()
                        st.success("Deleted!")
                        st.rerun()
        
        st.divider()

def show_active_dataset():
    """Show currently active dataset info"""
    if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
        st.write("---")
        st.write("### 🎯 Active Dataset")
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.info(f"**{st.session_state.uploaded_filename}** is ready for chat")
            # Show dataset info
            df = st.session_state.uploaded_df
            st.caption(f"📊 {len(df)} rows × {len(df.columns)} columns")
        
        with col2:
            if st.button("🔄 Refresh", help="Refresh dataset view"):
                st.rerun()
                
        with col3:
            if st.button("🚫 Clear"):
                clear_active_dataset()
                st.rerun()
                
        # Show quick preview of active dataset
        with st.expander("👀 Quick Preview", expanded=False):
            st.dataframe(st.session_state.uploaded_df.head(3))

def clear_chat_state():
    """Clear chat-related session state when switching datasets"""
    chat_keys = ['chat_history', 'chat_agent', 'analysis_results', 'last_query', 
                 'conversation_memory', 'chat_messages', 'analysis_context']
    for key in chat_keys:
        if key in st.session_state:
            del st.session_state[key]

def clear_active_dataset():
    """Clear the active dataset from session state"""
    keys_to_clear = ['uploaded_df', 'uploaded_filename', 'current_dataset_id']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Also clear chat state
    clear_chat_state()

def load_data(uploaded_file):
    """Load data from uploaded file"""
    if uploaded_file is None:
        return None

    try:
        if uploaded_file.name.endswith(".csv"):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            # Detect encoding
            with open(tmp_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding'] or 'utf-8'

            # Read CSV with detected encoding
            df = pd.read_csv(tmp_path, encoding=encoding)
            
            # Clean up temp file
            os.unlink(tmp_path)

        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None

        st.success(f"File '{uploaded_file.name}' loaded successfully.")
        return df.fillna(0)

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None