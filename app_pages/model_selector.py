# import streamlit as st

# def app():
#     st.title("Chat templates prompts 🛠️")
#     st.write("Here you can  configure your models here.")
#     st.write("You can choose differente approach.")
    
#     CSV_PROMPT_PREFIX = """
#     You are a data analysis expert working with a pandas DataFrame called 'df'. 
#     When answering questions:
#     1. Always begin by examining the DataFrame structure (columns, data types, basic stats)
#     2. Write clear, executable Python code
#     3. Execute your code and base your answers on the results
#     """

#     CSV_PROMPT_SUFFIX = """
#     Make your answer helpful and informative. Format numbers over 1,000 with commas.
#     Include an explanation section at the end explaining how you arrived at your answer.
#     """
import streamlit as st

def app():
    st.title("Chat templates prompts 🛠️")
    st.write("Here you can configure your models here.")
    st.write("You can choose different approach.")
    
    # Define prompt templates
    if "CSV_PROMPT_PREFIX" not in st.session_state:
        st.session_state.CSV_PROMPT_PREFIX = """
        You are a data analysis expert working with a pandas DataFrame called 'df'.
        
        When answering questions:
        1. Always begin by examining the DataFrame structure (columns, data types, basic stats)
        2. Write clear, executable Python code
        3. Execute your code and base your answers on the results
        """
    
    if "CSV_PROMPT_SUFFIX" not in st.session_state:
        st.session_state.CSV_PROMPT_SUFFIX = """
        Make your answer helpful and informative. Format numbers over 1,000 with commas.
        Include an explanation section at the end explaining how you arrived at your answer.
        """
    
    # Allow user to customize prompts
    st.subheader("Customize CSV Analysis Prompts")
    
    st.text_area("Prefix Prompt (instructions given before the user's question)",
                value=st.session_state.CSV_PROMPT_PREFIX,
                height=200,
                key="prefix_input")
    
    st.text_area("Suffix Prompt (instructions given after the user's question)",
                value=st.session_state.CSV_PROMPT_SUFFIX,
                height=150,
                key="suffix_input")
    
    # Update button
    if st.button("Update Prompts"):
        st.session_state.CSV_PROMPT_PREFIX = st.session_state.prefix_input
        st.session_state.CSV_PROMPT_SUFFIX = st.session_state.suffix_input
        st.success("Prompts updated successfully!")

# Export these constants for use in other modules
CSV_PROMPT_PREFIX = """
You are a data analysis expert working with a pandas DataFrame called 'df'.

When answering questions:
1. Always begin by examining the DataFrame structure (columns, data types, basic stats)
2. Write clear, executable Python code
3. Execute your code and base your answers on the results
"""

CSV_PROMPT_SUFFIX = """
Make your answer helpful and informative. Format numbers over 1,000 with commas.
Include an explanation section at the end explaining how you arrived at your answer.
"""    