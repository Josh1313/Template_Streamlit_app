
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
from jsonschema import validate, ValidationError

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

BAR_SCHEMA = {
    "type": "object",
    "required": ["chart_type", "x_axis", "y_axis"],
    "properties": {
        "chart_type": {"const": "bar"},
        "x_axis": {"type": "string"},
        "y_axis": {"type": "string"}
    }
}

PIE_SCHEMA = {
    "type": "object",
    "required": ["chart_type", "labels", "values"],
    "properties": {
        "chart_type": {"const": "pie"},
        "labels": {"type": "string"},
        "values": {"type": "string"}
    }
}

def handle_visualization(action, observation):
    """Enhanced visualization handler with schema validation"""
    try:
        # Parse input data
        if isinstance(action.tool_input, dict):
            viz_data = action.tool_input
        else:
            viz_data = json.loads(str(action.tool_input).strip())

        # Validate JSON schema
        try:
            if viz_data['chart_type'] == 'bar':
                validate(viz_data, BAR_SCHEMA)
            elif viz_data['chart_type'] == 'pie':
                validate(viz_data, PIE_SCHEMA)
        except ValidationError as ve:
            st.error(f"Invalid chart parameters: {ve.message}")
            return

        # Convert JSON to DataFrame
        df = json_to_dataframe(viz_data.get('data', {}))
        
        if df.empty:
            st.warning("No data available for visualization")
            return
            
        # Generate visualization
        st.write("### Visualization")
        result = viz_tool(**viz_data)
        
        # Handle visualization results
        if "Error:" in result:
            st.error(result)
            st.info("Attempting auto-detected visualization...")
            VisualizationGenerator.create_visualization(df)
        elif "Visualization rendered" in result:
            st.success(result)
        else:
            VisualizationGenerator.create_visualization(df)

    except Exception as e:
        st.error(f"Visualization pipeline failed: {str(e)}")
        with st.expander("Technical Details"):
            st.json({
                "input_data": viz_data,
                "columns": df.columns.tolist() if not df.empty else [],
                "raw_input": str(action.tool_input)[:500]
            })

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
    
    # Modified query execution section
    if st.button("Run Query"):
        if not question:
            st.warning("Please enter a question about the dataset.")
            return
            
        with st.spinner("Analyzing data..."):
            try:
                # Enhanced prompt engineering
                prefix = st.session_state.get('CSV_PROMPT_PREFIX', CSV_PROMPT_PREFIX)
                suffix = st.session_state.get('CSV_PROMPT_SUFFIX', CSV_PROMPT_SUFFIX)
                
                # Updated visualization instructions
                if visualization_enabled:
                    suffix += """
                    When creating visualizations:
                    1. Always specify x and y parameters
                    2. Use chart_type when appropriate
                    3. Available columns: {columns}
                    """.format(columns=", ".join(df.columns.tolist()))

                # Add dataframe schema to context
                modified_prefix = prefix + f"\nData Schema:\n{json.dumps(df.dtypes.astype(str).to_dict(), indent=2)}"
                
                # Execute query
                response = agent.invoke({
                    "input": modified_prefix + question + suffix
                })
                
                # Display results
                st.write("### Results")
                st.markdown(response["output"])
                
                # Enhanced visualization handling
                if visualization_enabled:
                    st.write("### Visualization Analysis")
                    if 'intermediate_steps' in response:
                        for step in response['intermediate_steps']:
                            if isinstance(step, tuple) and len(step) > 1:
                                action, observation = step[0], step[1]
                                if hasattr(action, 'tool') and action.tool == 'viz_tool':
                                    handle_visualization(action, observation)
                    else:
                        st.info("No visualizations generated. Try being more specific about visual analysis.")
                        
            except Exception as e:
                st.error(f"Query execution failed: {str(e)}")
                st.info("Common solutions:\n1. Rephrase your question\n2. Check column names\n3. Simplify complex queries")



