#prompt template
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
        When creating visualizations:
        1. Always specify the chart_type (bar, pie)
        2. Include required parameters:
         - Bar charts require: x_axis (category) and y_axis (value)
        - Pie charts require: labels (categories) and values (numbers)

        Example bar chart format:
        {
          "chart_type": "bar",
          "x_axis": "Department",
          "y_axis": "Base_Salary"
        }

        Example pie chart format:
        {
          "chart_type": "pie", 
          "labels": "Department",
          "values": "Headcount"
        }

        If unsure about parameters, just provide the data and we'll auto-detect the best visualization.
        """
    
    if "CSV_PROMPT_SUFFIX" not in st.session_state:
        st.session_state.CSV_PROMPT_SUFFIX = """
        Make your answer helpful and informative. Format numbers over 1,000 with commas.
        Include an explanation section at the end explaining how you arrived at your answer.
        Make sure to answer in the input language.
        be charming and friendly.
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

When creating visualizations:
1. Always specify the chart_type (bar, pie, donut, histogram, time_series)
2. Include all required parameters:
   - For bar charts: x (category) and y (value)
   - For pie/donut: names (categories) and values (numbers)
3. Example format:
{
  "chart_type": "pie",
  "data": {
    "Division": ["Division A", "Division B"],
    "Longevity_Pay": [10000, 20000]
  },
  "names": "Division",
  "values": "Longevity_Pay",
  "title": "Longevity Pay by Division"
}

If unsure about parameters, just provide the data and we'll auto-detect the best visualization.
"""

CSV_PROMPT_SUFFIX = """
Make your answer helpful and informative. Format numbers over 1,000 with commas.
Include an explanation section at the end explaining how you arrived at your answer.
Make sure to answer in the input language.
be charming and friendly.
"""    