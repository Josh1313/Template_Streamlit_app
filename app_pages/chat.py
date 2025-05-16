# import streamlit as st
# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_experimental.agents import create_pandas_dataframe_agent
# from langchain.agents.agent_types import AgentType

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
#             handle_parsing_errors=True
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
                        
#                         # Run query
#                         response = agent.run(prefix + question + suffix)
#                         st.write("### Results")
#                         st.markdown(response)
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")
#                         st.info("Try rephrasing your question or ask something simpler about the dataset.")
#             else:
#                 st.warning("Please enter a question about the dataset.")
#     else:
#         st.info("Please upload a file in the Files page first.")
#         st.write("No data available for analysis. Go to the Files page to upload a CSV or Excel file.")

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# Import prompt templates
from app_pages.model_selector import CSV_PROMPT_PREFIX, CSV_PROMPT_SUFFIX

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

def app():
    st.title("Chat 💬")
    st.write("This is where you can make questions about your data.")
    st.write("You can interact with the LLM here.")
    
    # Initialize the LLM model
    model = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=openai_key,
        temperature=0.1
    )
    
    st.title("ITSM Reporting and Analytics Agent")
    
    # Check if data is available from files page
    if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
        df = st.session_state.uploaded_df
        filename = st.session_state.uploaded_filename
        
        st.success(f"Using data from: {filename}")
        
        # Show dataset preview
        with st.expander("Dataset Preview", expanded=False):
            st.write(df.head(10))
        
        # Create agent
        agent = create_pandas_dataframe_agent(
            llm=model,
            df=df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True
        )
        
        # Get question from user
        st.write("### Ask a Question")
        question = st.text_input("Enter your question about the dataset:")
        
        # Process question when button is clicked
        if st.button("Run Query"):
            if question:
                with st.spinner("Analyzing data..."):
                    try:
                        # Use prompt templates from model_selector
                        if 'CSV_PROMPT_PREFIX' in st.session_state:
                            prefix = st.session_state.CSV_PROMPT_PREFIX
                        else:
                            prefix = CSV_PROMPT_PREFIX
                            
                        if 'CSV_PROMPT_SUFFIX' in st.session_state:
                            suffix = st.session_state.CSV_PROMPT_SUFFIX
                        else:
                            suffix = CSV_PROMPT_SUFFIX
                        
                        # Run query with the updated invoke() method instead of run()
                        response = agent.invoke({"input": prefix + question + suffix})
                        st.write("### Results")
                        st.markdown(response["output"])
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.info("Try rephrasing your question or ask something simpler about the dataset.")
            else:
                st.warning("Please enter a question about the dataset.")
    else:
        st.info("Please upload a file in the Files page first.")
        st.write("No data available for analysis. Go to the Files page to upload a CSV or Excel file.")