
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from datetime import datetime

# Import prompt templates
from app_pages.model_selector import CSV_PROMPT_PREFIX, CSV_PROMPT_SUFFIX

# Load environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

def initialize_chat_history():
    """Initialize chat history in session state"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_agent' not in st.session_state:
        st.session_state.chat_agent = None

def add_message_to_history(role, content, timestamp=None):
    """Add a message to chat history"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M:%S")
    
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

def display_chat_messages():
    """Display chat messages in a clean format"""
    if st.session_state.chat_history:
        # Display only the last few messages in a clean way
        recent_messages = st.session_state.chat_history[-4:]  # Show last 4 messages
        
        for message in recent_messages:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])

def create_agent_instance(df):
    """Create and cache the pandas dataframe agent"""
    model = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=openai_key,
        temperature=0.1
    )
    
    agent = create_pandas_dataframe_agent(
        llm=model,
        df=df,
        verbose=False,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        handle_parsing_errors=True
    )
    
    return agent

def process_user_query(agent, question):
    """Process user query and return response"""
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
        
        # Run query with the updated invoke() method
        response = agent.invoke({"input": prefix + question + suffix})
        return response["output"], None
    except Exception as e:
        return None, str(e)

def app():
    st.title("Chat 💬")
    st.write("This is where you can make questions about your data.")
    st.write("You can interact with the LLM here.")
    
    # Initialize chat history
    initialize_chat_history()
    
    st.title("Analytics Agent")
    
    # Check if data is available from files page
    if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
        df = st.session_state.uploaded_df
        filename = st.session_state.uploaded_filename
        
        st.success(f"Using data from: {filename}")
        
        # Show dataset preview (collapsible)
        with st.expander("Dataset Preview", expanded=False):
            st.write(df.head(5))
        
        # Create or reuse agent
        if st.session_state.chat_agent is None:
            with st.spinner("Initializing AI agent..."):
                st.session_state.chat_agent = create_agent_instance(df)
        
        # Chat Interface Section
        st.write("---")
        st.write("### 💬 Chat with your Data")
        
        # Display recent chat messages using Streamlit's native chat interface
        display_chat_messages()
        
        # Chat input using Streamlit's chat_input
        if prompt := st.chat_input("Ask me anything about your dataset..."):
            # Add user message to history
            add_message_to_history("user", prompt)
            
            # Display user message immediately
            st.chat_message("user").write(prompt)
            
            # Process the question
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response, error = process_user_query(st.session_state.chat_agent, prompt)
                    
                    if response:
                        st.write(response)
                        add_message_to_history("assistant", response)
                    else:
                        error_msg = f"An error occurred: {error}\n\nTry rephrasing your question."
                        st.error(error_msg)
                        add_message_to_history("assistant", error_msg)
        
        # Optional: Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
    
    else:
        st.info("Please upload a file in the Files page first.")
        st.write("No data available for analysis. Go to the Files page to upload a CSV or Excel file.")
        
        # Show some helpful information while waiting for data
        st.write("### What you can do once data is loaded:")
        st.write("- Ask natural language questions about your data")
        st.write("- Get statistical summaries and insights")
        st.write("- Explore trends and patterns")
        st.write("- Perform data quality checks")
        st.write("- Have ongoing conversations about your analysis")