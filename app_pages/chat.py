# #main.py
# import streamlit as st
# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_experimental.agents import create_pandas_dataframe_agent
# from langchain.agents.agent_types import AgentType
# from utils.visualizations import viz_tool


# # Import prompt templates
# from app_pages.model_selector import CSV_PROMPT_PREFIX, CSV_PROMPT_SUFFIX

# # Load environment variables
# load_dotenv()
# openai_key = os.getenv("OPENAI_API_KEY")

# def app():
#     st.title("Chat 💬")
#     st.write("This is where you can make questions about your data.")
#     st.write("You can interact with the LLM here.")
    
#     # Initialize the LLM model
#     model = ChatOpenAI(
#         model="gpt-4o-mini",
#         openai_api_key=openai_key,
#         temperature=0.1
#     )
    
#     st.title("ITSM Reporting and Analytics Agent")
    
#     # Check if data is available from files page
#     if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
#         df = st.session_state.uploaded_df
#         filename = st.session_state.uploaded_filename
        
#         st.success(f"Using data from: {filename}")
        
#         # Show dataset preview
#         with st.expander("Dataset Preview", expanded=False):
#             st.write(df.head(10))
        
#         # Create agent
#         agent = create_pandas_dataframe_agent(
#             llm=model,
#             df=df,
#             verbose=True,
#             agent_type=AgentType.OPENAI_FUNCTIONS,
#             handle_parsing_errors=True,
#             extra_tools=[viz_tool], 
#         )
        
#         # Get question from user
#         st.write("### Ask a Question")
#         question = st.text_input("Enter your question about the dataset:")
        
#         # Process question when button is clicked
#         if st.button("Run Query"):
#             if question:
#                 with st.spinner("Analyzing data..."):
#                     try:
#                         # Use prompt templates from model_selector
#                         if 'CSV_PROMPT_PREFIX' in st.session_state:
#                             prefix = st.session_state.CSV_PROMPT_PREFIX
#                         else:
#                             prefix = CSV_PROMPT_PREFIX
                            
#                         if 'CSV_PROMPT_SUFFIX' in st.session_state:
#                             suffix = st.session_state.CSV_PROMPT_SUFFIX
#                         else:
#                             suffix = CSV_PROMPT_SUFFIX
                        
#                         # Run query with the updated invoke() method instead of run()
#                         response = agent.invoke({"input": prefix + question + suffix})
#                         st.write("### Results")
#                         st.markdown(response["output"])
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")
#                         st.info("Try rephrasing your question or ask something simpler about the dataset.")
#             else:
#                 st.warning("Please enter a question about the dataset.")
#     else:
#         st.info("Please upload a file in the Files page first.")
#         st.write("No data available for analysis. Go to the Files page to upload a CSV or Excel file.")
import pandas as pd
import streamlit as st
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from utils.visualizations import VisualizationGenerator, viz_tool, json_to_dataframe
from app_pages.model_selector import CSV_PROMPT_PREFIX, CSV_PROMPT_SUFFIX

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

def format_agent_output(result_df: pd.DataFrame, analysis: str) -> dict:
    """Format agent output for potential visualization"""
    return {
        "data": result_df.values.tolist(),
        "columns": result_df.columns.tolist(),
        "analysis": analysis
    }

def handle_visualization(action, observation):
    """Handle visualization requests with error recovery"""
    try:
        # Parse the tool input
        if isinstance(action.tool_input, dict):
            viz_data = action.tool_input
        else:
            json_str = action.tool_input.strip()
            if not json_str.endswith('}'):
                json_str = json_str[:json_str.rfind('}')+1]
            viz_data = json.loads(json_str)
        
        # Convert to DataFrame
        df = json_to_dataframe(viz_data.get('data', {}))
        
        if df.empty:
            st.warning("No data available for visualization")
            return
        
        st.write("### Visualization")
        
        # Try the specific visualization first
        if "Missing required parameter" not in observation:
            result = viz_tool(viz_data)
            if result.startswith("Visualization created"):
                return
        
        # Fallback to auto-detected visualization
        st.info("Using auto-detected visualization")
        VisualizationGenerator.create_visualization(df)
        
    except Exception as e:
        st.warning(f"Visualization error: {str(e)}")
        if 'tool_input' in locals():
            st.code(f"Raw input: {str(action.tool_input)[:200]}...")

def app():
    st.title("Chat 💬")
    st.write("Interact with your data using natural language queries.")
    
    # Initialize the LLM model
    model = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=openai_key,
        temperature=0.1
    )
    
    st.title("ITSM Reporting and Analytics Agent")
    
    # Visualization toggle
    visualization_enabled = st.checkbox("Enable Visualizations", value=False)
    
    # Check if data is available
    if 'uploaded_df' not in st.session_state or st.session_state.uploaded_df is None:
        st.info("Please upload a file in the Files page first.")
        st.write("No data available for analysis. Go to the Files page to upload a CSV or Excel file.")
        return
    
    df = st.session_state.uploaded_df
    filename = st.session_state.uploaded_filename
    
    st.success(f"Using data from: {filename}")
    
    # Show dataset preview
    with st.expander("Dataset Preview", expanded=False):
        st.write(df.head(10))
    
    # Create agent with visualization tool
    agent = create_pandas_dataframe_agent(
        llm=model,
        df=df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        handle_parsing_errors=True,
        extra_tools=[viz_tool],
        max_iterations=8
    )
    
    # Get question from user
    st.write("### Ask a Question")
    question = st.text_input("Enter your question about the dataset:", key="query_input")
    
    # Process question when button is clicked
    if st.button("Run Query"):
        if not question:
            st.warning("Please enter a question about the dataset.")
            return
            
        with st.spinner("Analyzing data..."):
            try:
                # Use prompt templates
                prefix = st.session_state.get('CSV_PROMPT_PREFIX', CSV_PROMPT_PREFIX)
                suffix = st.session_state.get('CSV_PROMPT_SUFFIX', CSV_PROMPT_SUFFIX)
                
                # Add visualization instruction if enabled
                if visualization_enabled:
                    suffix += "\nIf appropriate, include visualizations using the viz_tool."
                
                # Run query
                response = agent.invoke({"input": prefix + question + suffix})
                
                # Display results
                st.write("### Results")
                st.markdown(response["output"])
                
                # Handle visualization if enabled
                if visualization_enabled and 'intermediate_steps' in response:
                    for step in response['intermediate_steps']:
                        if isinstance(step, tuple) and len(step) > 1:
                            action, observation = step[0], step[1]
                            if hasattr(action, 'tool') and action.tool == 'viz_tool':
                                handle_visualization(action, observation)
                                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Try rephrasing your question or ask something simpler about the dataset.")




