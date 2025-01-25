import streamlit as st
import os

def inject_google_analytics():
    """Inyecta el script de Google Analytics."""
    st.markdown(
        f"""
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={os.getenv('analytics_tag')}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', '{os.getenv('analytics_tag')}');
        </script>
        """,
        unsafe_allow_html=True
    )