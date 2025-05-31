"""
Customer Support Ticket System using Supervisor-Worker Pattern
"""
import os
from typing import Annotated, Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import create_react_agent
import json

# Initialize OpenAI model
def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Customer Support Tools
@tool
def check_account_status(customer_id: str) -> str:
    """Check the account status for a customer."""
    # Simulate account status check
    statuses = ["Active", "Suspended", "Pending", "Closed"]
    import random
    status = random.choice(statuses)
    return f"Customer {customer_id} account status: {status}"

@tool
def check_billing_info(customer_id: str) -> str:
    """Check billing information for a customer."""
    # Simulate billing info
    import random
    balance = round(random.uniform(-100, 500), 2)
    last_payment = "2024-01-15"
    return f"Customer {customer_id} - Current balance: ${balance}, Last payment: {last_payment}"

@tool
def create_refund(customer_id: str, amount: float, reason: str) -> str:
    """Process a refund for a customer."""
    return f"Refund of ${amount} processed for customer {customer_id}. Reason: {reason}. Refund ID: REF-{customer_id}-001"

@tool
def escalate_to_manager(ticket_id: str, reason: str) -> str:
    """Escalate a ticket to manager."""
    return f"Ticket {ticket_id} escalated to manager. Reason: {reason}. Manager will respond within 2 hours."

@tool
def check_technical_logs(customer_id: str, service: str) -> str:
    """Check technical logs for a specific service."""
    # Simulate technical log check
    import random
    issues = ["No issues found", "Connection timeout detected", "API rate limit exceeded", "Service degradation"]
    issue = random.choice(issues)
    return f"Technical logs for customer {customer_id} service '{service}': {issue}"

@tool
def reset_password(customer_id: str) -> str:
    """Reset password for a customer account."""
    return f"Password reset initiated for customer {customer_id}. Reset link sent to registered email."

@tool
def update_service_plan(customer_id: str, new_plan: str) -> str:
    """Update customer service plan."""
    return f"Service plan updated for customer {customer_id} to '{new_plan}'. Changes will take effect immediately."

# Define the state for our graph
class SupportState(MessagesState):
    active_agent: str = "supervisor"
    ticket_category: str = ""
    customer_id: str = ""
    next_agent: str = "general_agent"

# Create specialized agents
def create_technical_agent():
    """Technical support agent for technical issues."""
    tools = [check_technical_logs, reset_password, escalate_to_manager]
    system_prompt = """You are a Technical Support Specialist. You help customers with:
    - Technical issues and troubleshooting
    - Password resets
    - Service connectivity problems
    - API and integration issues
    
    Always be helpful and provide clear technical guidance. If you cannot resolve an issue, escalate to manager."""
    
    return create_react_agent(
        get_llm(),
        tools,
        prompt=system_prompt
    )

def create_billing_agent():
    """Billing support agent for payment and billing issues."""
    tools = [check_billing_info, create_refund, check_account_status, escalate_to_manager]
    system_prompt = """You are a Billing Support Specialist. You help customers with:
    - Billing inquiries and payment issues
    - Refund processing
    - Account status checks
    - Payment method updates
    
    Always verify customer information before processing any financial transactions."""
    
    return create_react_agent(
        get_llm(),
        tools,
        prompt=system_prompt
    )

def create_general_agent():
    """General support agent for other inquiries."""
    tools = [check_account_status, update_service_plan, escalate_to_manager]
    system_prompt = """You are a General Support Specialist. You help customers with:
    - General account inquiries
    - Service plan changes
    - General questions about services
    - Account management
    
    Provide friendly and helpful assistance for all general inquiries."""
    
    return create_react_agent(
        get_llm(),
        tools,
        prompt=system_prompt
    )

# Supervisor agent
def supervisor_node(state: SupportState):
    """Supervisor agent that routes tickets to appropriate specialists."""
    messages = state["messages"]
    
    # Get the latest user message
    last_message = messages[-1] if messages else None
    if not last_message or not isinstance(last_message, HumanMessage):
        return {"messages": [AIMessage(content="Hello! How can I help you today?")]}
    
    # Check if we're in an ongoing conversation with an agent
    # Look for the last routing message to determine current active agent
    current_active_agent = None
    for msg in reversed(messages[:-1]):  # Exclude the current user message
        if isinstance(msg, AIMessage) and "routing your request to our" in msg.content.lower():
            if "technical agent" in msg.content.lower():
                current_active_agent = "technical_agent"
            elif "billing agent" in msg.content.lower():
                current_active_agent = "billing_agent"
            elif "general agent" in msg.content.lower():
                current_active_agent = "general_agent"
            break
    
    # If we have an active agent and the user isn't explicitly asking for a new type of help,
    # continue with the same agent
    user_content = last_message.content.lower()
    
    # Keywords that indicate user wants to switch to a different type of support
    billing_keywords = ["billing", "payment", "refund", "charge", "invoice", "account balance"]
    technical_keywords = ["password", "login", "technical", "api", "connection", "error", "bug", "down", "not working"]
    general_keywords = ["plan", "upgrade", "downgrade", "account settings", "general"]
    
    # Check if user is explicitly requesting a different type of support
    is_requesting_billing = any(keyword in user_content for keyword in billing_keywords)
    is_requesting_technical = any(keyword in user_content for keyword in technical_keywords)
    is_requesting_general = any(keyword in user_content for keyword in general_keywords)
    
    # If we have an active agent and user isn't requesting a different type of support,
    # continue with the current agent
    if current_active_agent and not (is_requesting_billing or is_requesting_technical or is_requesting_general):
        return {
            "messages": state["messages"],
            "active_agent": current_active_agent,
            "next_agent": current_active_agent
        }
    
    # Otherwise, analyze the message to determine routing (new conversation or explicit switch)
    llm = get_llm()
    
    # Include more context for better routing decisions
    conversation_context = ""
    if len(messages) > 1:
        recent_messages = messages[-3:]  # Last 3 messages for context
        conversation_context = f"\nRecent conversation context:\n"
        for msg in recent_messages[:-1]:  # Exclude current message
            if isinstance(msg, HumanMessage):
                conversation_context += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                conversation_context += f"Assistant: {msg.content}\n"
    
    routing_prompt = f"""
    You are a customer support supervisor. Analyze the following customer message and determine which specialist should handle it:

    Customer message: "{last_message.content}"
    {conversation_context}

    Available specialists:
    1. technical_agent - For technical issues, password resets, connectivity problems, API issues, service outages
    2. billing_agent - For billing inquiries, payments, refunds, account status, charges, current account balance, payment history
    3. general_agent - For general questions, service plans, account management

    Respond with ONLY the agent name (technical_agent, billing_agent, or general_agent) and a brief reason.
    Format: agent_name|reason
    """
    
    response = llm.invoke([HumanMessage(content=routing_prompt)])
    
    try:
        agent_choice, reason = response.content.split("|", 1)
        agent_choice = agent_choice.strip()
        reason = reason.strip()
    except:
        agent_choice = "general_agent"
        reason = "Unable to categorize, routing to general support"
    
    # Create handoff message
    handoff_message = AIMessage(
        content=f"I'm routing your request to our {agent_choice.replace('_', ' ').title()} team. {reason}"
    )
    
    return {
        "messages": state["messages"] + [handoff_message],
        "active_agent": agent_choice,
        "next_agent": agent_choice
    }

# Router function for conditional edges
def route_to_agent(state: SupportState):
    """Route to the appropriate agent based on supervisor decision."""
    next_agent = state.get("next_agent", "general_agent")
    return next_agent

# Create the graph
def create_support_graph():
    """Create the customer support graph with supervisor-worker pattern."""
    
    # Create agents
    technical_agent = create_technical_agent()
    billing_agent = create_billing_agent()
    general_agent = create_general_agent()
    
    # Create the graph
    workflow = StateGraph(SupportState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("technical_agent", technical_agent)
    workflow.add_node("billing_agent", billing_agent)
    workflow.add_node("general_agent", general_agent)
    
    # Add edges - START goes to supervisor
    workflow.add_edge(START, "supervisor")
    
    # Add conditional edges from supervisor to agents
    # This will show the routing connections in the graph
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "technical_agent": "technical_agent",
            "billing_agent": "billing_agent", 
            "general_agent": "general_agent"
        }
    )
    
    # All agents route to END
    workflow.add_edge("technical_agent", END)
    workflow.add_edge("billing_agent", END)
    workflow.add_edge("general_agent", END)
    
    # Compile the graph
    app = workflow.compile()
    
    # Add graph metadata for LangSmith visualization
    try:
        # Try to get the graph representation
        graph_repr = app.get_graph()
        print("📊 Graph structure created successfully")
        print(f"🔗 Nodes: {list(graph_repr.nodes.keys())}")
        print(f"🔗 Edges: {len(graph_repr.edges)} connections")
        
        # Save graph visualization if possible
        try:
            graph_image = graph_repr.draw_mermaid_png()
            with open("support_graph.png", "wb") as f:
                f.write(graph_image)
            print("💾 Graph visualization saved as 'support_graph.png'")
        except Exception as e:
            print(f"⚠️  Could not save graph image: {e}")
            
    except Exception as e:
        print(f"⚠️  Could not get graph representation: {e}")
    
    return app

# Test function
def test_support_system():
    """Test the support system with sample queries."""
    app = create_support_graph()
    
    test_queries = [
        "I can't log into my account, I think I forgot my password",
        "I was charged twice this month and need a refund",
        "I want to upgrade my service plan to premium"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing: {query} ---")
        result = app.invoke({
            "messages": [HumanMessage(content=query)]
        })
        
        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                print(f"Assistant: {msg.content}")
            elif isinstance(msg, ToolMessage):
                print(f"Tool Result: {msg.content}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_support_system() 