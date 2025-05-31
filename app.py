"""
Streamlit Multi-Agent Chat Interface
Includes Customer Support and Chain of Thought Reasoning
"""
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agents import create_support_graph
from chain_of_thought_agent import create_reasoning_graph

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Multi-Agent AI System",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for both systems
if "messages" not in st.session_state:
    st.session_state.messages = []
if "reasoning_messages" not in st.session_state:
    st.session_state.reasoning_messages = []
if "support_app" not in st.session_state:
    try:
        st.session_state.support_app = create_support_graph()
    except Exception as e:
        st.error(f"Failed to initialize support system: {e}")
if "reasoning_app" not in st.session_state:
    try:
        st.session_state.reasoning_app = create_reasoning_graph()
    except Exception as e:
        st.error(f"Failed to initialize reasoning system: {e}")

# Sidebar for configuration
with st.sidebar:
    st.title("🤖 Multi-Agent AI System")
    st.markdown("---")
    
    # API Key configuration
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your OpenAI API key"
    )
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    st.markdown("---")
    
    # System selection
    selected_system = st.radio(
        "Select AI System:",
        ["🎧 Customer Support", "🧠 Chain of Thought Reasoning"],
        help="Choose which AI system to interact with"
    )
    
    st.markdown("---")
    
    if selected_system == "🎧 Customer Support":
        # Customer Support information
        st.subheader("Available Support Teams")
        st.markdown("""
        **🔧 Technical Support**
        - Password resets
        - Technical troubleshooting
        - API issues
        - Connectivity problems
        
        **💳 Billing Support**
        - Payment inquiries
        - Refund processing
        - Account status
        - Billing disputes
        
        **📋 General Support**
        - Account management
        - Service plan changes
        - General questions
        """)
    else:
        # Chain of Thought information
        st.subheader("Reasoning Process")
        st.markdown("""
        **🧠 How it works:**
        1. **Analyze** - Break down the problem
        2. **Gather** - Collect relevant information
        3. **Reason** - Think step by step
        4. **Evaluate** - Consider options
        5. **Conclude** - Provide reasoned answer
        
        **💡 Best for:**
        - Complex decision making
        - Problem solving
        - Strategic planning
        - Learning new concepts
        """)
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("Clear Chat", type="secondary"):
        if selected_system == "🎧 Customer Support":
            st.session_state.messages = []
        else:
            st.session_state.reasoning_messages = []
        st.rerun()

# Main interface
if selected_system == "🎧 Customer Support":
    # Customer Support Chat Interface
    st.title("🎧 Customer Support Chat")
    st.markdown("Welcome! I'm here to help you with your support needs. What can I assist you with today?")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)
            elif isinstance(message, ToolMessage):
                with st.chat_message("assistant"):
                    st.info(f"🔧 Tool Result: {message.content}")
    
    # Chat input for customer support
    if prompt := st.chat_input("Type your support question here..."):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar to continue.")
            st.stop()
        
        # Add user message to chat
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process with support system
        with st.chat_message("assistant"):
            with st.spinner("Processing your request..."):
                try:
                    # Invoke the support graph
                    result = st.session_state.support_app.invoke({
                        "messages": st.session_state.messages
                    })
                    
                    # Extract new messages from result
                    new_messages = result["messages"][len(st.session_state.messages):]
                    
                    # Display and store new messages
                    for msg in new_messages:
                        if isinstance(msg, AIMessage):
                            st.write(msg.content)
                            st.session_state.messages.append(msg)
                        elif isinstance(msg, ToolMessage):
                            st.info(f"🔧 Tool Result: {msg.content}")
                            st.session_state.messages.append(msg)
                    
                except Exception as e:
                    st.error(f"Error processing request: {e}")
                    st.error("Please check your API key and try again.")

    # Example queries for customer support
    with st.expander("💡 Example Support Queries"):
        st.markdown("""
        **Technical Issues:**
        - "I can't log into my account, I think I forgot my password"
        - "My API calls are failing with timeout errors"
        - "The service seems to be down, can you check?"
        
        **Billing Questions:**
        - "I was charged twice this month and need a refund"
        - "Can you check my current account balance?"
        - "I want to dispute a charge on my account"
        
        **General Support:**
        - "I want to upgrade my service plan to premium"
        - "How do I change my account settings?"
        - "What features are included in my current plan?"
        """)

else:
    # Chain of Thought Reasoning Interface
    st.title("🧠 Chain of Thought Reasoning")
    st.markdown("I'll help you think through complex problems step by step. What would you like me to analyze?")
    
    # Display reasoning messages
    reasoning_container = st.container()
    
    with reasoning_container:
        for message in st.session_state.reasoning_messages:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.markdown(message.content)
    
    # Chat input for reasoning
    if prompt := st.chat_input("Ask me to think through a problem..."):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar to continue.")
            st.stop()
        
        # Add user message to reasoning chat
        user_message = HumanMessage(content=prompt)
        st.session_state.reasoning_messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process with reasoning system
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking step by step..."):
                try:
                    # Invoke the reasoning graph
                    result = st.session_state.reasoning_app.invoke({
                        "messages": st.session_state.reasoning_messages
                    })
                    
                    # Extract new messages from result
                    new_messages = result["messages"][len(st.session_state.reasoning_messages):]
                    
                    # Display and store new messages
                    for msg in new_messages:
                        if isinstance(msg, AIMessage):
                            st.markdown(msg.content)
                            st.session_state.reasoning_messages.append(msg)
                    
                except Exception as e:
                    st.error(f"Error processing reasoning request: {e}")
                    st.error("Please check your API key and try again.")

    # Example queries for reasoning
    with st.expander("💡 Example Reasoning Queries"):
        st.markdown("""
        **Decision Making:**
        - "Should I switch careers from marketing to data science?"
        - "What factors should I consider when choosing a university?"
        - "How do I decide between renting vs buying a house?"
        
        **Problem Solving:**
        - "My team is missing deadlines. How can I improve our productivity?"
        - "How should I approach learning machine learning as a beginner?"
        - "What's the best way to resolve conflicts in a remote team?"
        
        **Strategic Planning:**
        - "How should I plan my startup's go-to-market strategy?"
        - "What steps should I take to improve my company's customer retention?"
        - "How can I effectively manage a project with multiple stakeholders?"
        """)

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666;'>
        <small>Multi-Agent AI System powered by LangGraph & OpenAI | Current Mode: {selected_system}</small>
    </div>
    """,
    unsafe_allow_html=True
)

# Debug information (only show in development)
if st.checkbox("Show Debug Info", value=False):
    st.subheader("Debug Information")
    
    if selected_system == "🎧 Customer Support":
        st.write("**Customer Support Messages:**")
        st.json([{
            "type": type(msg).__name__,
            "content": msg.content if hasattr(msg, 'content') else str(msg)
        } for msg in st.session_state.messages])
        
        if "support_app" in st.session_state:
            st.write("**Support App Status:** ✅ Initialized")
        else:
            st.write("**Support App Status:** ❌ Not Initialized")
    else:
        st.write("**Reasoning Messages:**")
        st.json([{
            "type": type(msg).__name__,
            "content": msg.content if hasattr(msg, 'content') else str(msg)
        } for msg in st.session_state.reasoning_messages])
        
        if "reasoning_app" in st.session_state:
            st.write("**Reasoning App Status:** ✅ Initialized")
        else:
            st.write("**Reasoning App Status:** ❌ Not Initialized") 