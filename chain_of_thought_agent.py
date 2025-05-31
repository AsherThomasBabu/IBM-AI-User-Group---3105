"""
Chain of Thought Reasoning Agent using LangGraph
This implements a reasoning agent that shows its step-by-step thinking process
"""
import os
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END

# Initialize OpenAI model
def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define the state for our reasoning graph
class ReasoningState(MessagesState):
    current_problem: str = ""
    step_count: int = 0

# Reasoning coordinator node
def reasoning_coordinator(state: ReasoningState):
    """Coordinates the reasoning process and manages the flow."""
    messages = state["messages"]
    
    if not messages:
        return {"messages": [AIMessage(content="Hello! I'm your Chain of Thought Reasoning Agent. I'll help you think through problems step by step. What would you like me to analyze?")]}
    
    last_message = messages[-1]
    if isinstance(last_message, HumanMessage):
        # Start the reasoning process
        reasoning_prompt = f"""🧠 **Starting Chain of Thought Analysis**

I need to think through this problem step by step: "{last_message.content}"

Let me break this down systematically using a structured reasoning approach."""
        
        return {
            "messages": state["messages"] + [AIMessage(content=reasoning_prompt)],
            "current_problem": last_message.content,
            "step_count": 0
        }
    
    return state

# Step-by-step reasoning node
def step_by_step_reasoner(state: ReasoningState):
    """Performs detailed step-by-step reasoning."""
    llm = get_llm()
    
    current_problem = state.get("current_problem", "")
    step_count = state.get("step_count", 0)
    
    if not current_problem:
        return {
            "messages": state["messages"] + [AIMessage(content="I need a problem to analyze. Please provide a question or issue you'd like me to think through.")],
            "step_count": step_count
        }
    
    # Define the reasoning steps
    step_prompts = [
        {
            "title": "Problem Analysis",
            "prompt": f"""Analyze this problem: "{current_problem}"

Break down the problem into its key components:
1. What is the core issue?
2. What are the main factors involved?
3. What context is important to consider?

Provide a clear analysis of what we're dealing with."""
        },
        {
            "title": "Information Gathering", 
            "prompt": f"""Based on the problem: "{current_problem}"

What information do we need to make a good decision? Consider:
1. What facts are relevant?
2. What assumptions might we be making?
3. What additional context would be helpful?
4. What are the key constraints or requirements?

Identify the most important information needed."""
        },
        {
            "title": "Option Generation",
            "prompt": f"""For the problem: "{current_problem}"

Generate potential approaches or solutions:
1. What are the different ways to address this?
2. What are the main options available?
3. Are there any creative or alternative approaches?
4. What would be the conventional wisdom?

List and briefly describe the main options."""
        },
        {
            "title": "Evaluation & Decision",
            "prompt": f"""Evaluate the options for: "{current_problem}"

Analyze each approach considering:
1. Pros and cons of each option
2. Feasibility and practicality
3. Potential risks and benefits
4. Resource requirements
5. Likelihood of success

Make a reasoned recommendation based on this analysis."""
        }
    ]
    
    if step_count < len(step_prompts):
        current_step = step_prompts[step_count]
        
        response = llm.invoke([
            SystemMessage(content="You are a logical reasoning expert. Provide clear, structured thinking for each step."), 
            HumanMessage(content=current_step["prompt"])
        ])
        
        step_message = f"""🔍 **Step {step_count + 1}: {current_step['title']}**

{response.content}"""
        
        return {
            "messages": state["messages"] + [AIMessage(content=step_message)],
            "current_problem": current_problem,
            "step_count": step_count + 1
        }
    
    # If we've completed all steps, just return current state
    return state

# Conclusion synthesizer node
def conclusion_synthesizer(state: ReasoningState):
    """Synthesizes all reasoning steps into a final conclusion."""
    llm = get_llm()
    
    current_problem = state.get("current_problem", "")
    messages = state.get("messages", [])
    
    # Extract reasoning steps from messages
    reasoning_steps = []
    for msg in messages:
        if isinstance(msg, AIMessage) and "Step" in msg.content and ":" in msg.content:
            # Extract just the content after the step header
            content = msg.content
            if "**" in content:
                # Find content after the step title
                parts = content.split("**", 2)
                if len(parts) > 2:
                    reasoning_steps.append(parts[2].strip())
    
    if len(reasoning_steps) < 3:
        return {
            "messages": state["messages"] + [AIMessage(content="I need more reasoning steps before I can provide a conclusion.")],
            "step_count": state.get("step_count", 0)
        }
    
    synthesis_prompt = f"""Based on the step-by-step analysis of: "{current_problem}"

Here are the reasoning steps taken:
1. Problem Analysis: {reasoning_steps[0] if len(reasoning_steps) > 0 else 'Not completed'}
2. Information Gathering: {reasoning_steps[1] if len(reasoning_steps) > 1 else 'Not completed'}
3. Option Generation: {reasoning_steps[2] if len(reasoning_steps) > 2 else 'Not completed'}
4. Evaluation & Decision: {reasoning_steps[3] if len(reasoning_steps) > 3 else 'Not completed'}

Provide a clear, actionable conclusion that:
1. Summarizes the key insights from the analysis
2. Gives a specific recommendation or answer
3. Explains the reasoning behind the recommendation
4. Acknowledges any limitations or assumptions
5. Suggests next steps if applicable

Make this practical and actionable."""
    
    response = llm.invoke([
        SystemMessage(content="You are an expert at synthesizing logical reasoning into clear, actionable conclusions."), 
        HumanMessage(content=synthesis_prompt)
    ])
    
    conclusion = f"""🎯 **Final Conclusion & Recommendation**

{response.content}

---

**Reasoning Process Summary:**
✅ **Step 1: Problem Analysis** - Identified core issues and key factors
✅ **Step 2: Information Gathering** - Determined what information is needed
✅ **Step 3: Option Generation** - Explored different approaches and solutions
✅ **Step 4: Evaluation & Decision** - Analyzed pros/cons and made recommendations

This systematic approach ensures thorough consideration of all aspects of your question."""
    
    return {
        "messages": state["messages"] + [AIMessage(content=conclusion)],
        "current_problem": current_problem,
        "step_count": state.get("step_count", 0)
    }

# Router function to determine next step
def route_reasoning_flow(state: ReasoningState) -> Literal["step_reasoner", "conclusion", "end"]:
    """Route the reasoning flow based on current state."""
    step_count = state.get("step_count", 0)
    
    # Continue reasoning for steps 1-4
    if step_count < 4:
        return "step_reasoner"
    
    # After 4 steps, synthesize conclusion
    if step_count >= 4:
        return "conclusion"
    
    return "end"

# Create the reasoning graph
def create_reasoning_graph():
    """Create the chain of thought reasoning graph."""
    
    # Create the graph
    workflow = StateGraph(ReasoningState)
    
    # Add nodes
    workflow.add_node("coordinator", reasoning_coordinator)
    workflow.add_node("step_reasoner", step_by_step_reasoner)
    workflow.add_node("conclusion", conclusion_synthesizer)
    
    # Add edges
    workflow.add_edge(START, "coordinator")
    workflow.add_edge("coordinator", "step_reasoner")
    
    # Add conditional edges for reasoning flow
    workflow.add_conditional_edges(
        "step_reasoner",
        route_reasoning_flow,
        {
            "step_reasoner": "step_reasoner",
            "conclusion": "conclusion",
            "end": END
        }
    )
    
    workflow.add_edge("conclusion", END)
    
    # Compile the graph
    app = workflow.compile()
    
    # Add graph metadata
    try:
        graph_repr = app.get_graph()
        print("🧠 Chain of Thought Reasoning Graph created successfully")
        print(f"🔗 Nodes: {list(graph_repr.nodes.keys())}")
        print(f"🔗 Edges: {len(graph_repr.edges)} connections")
        
        # Save graph visualization if possible
        try:
            graph_image = graph_repr.draw_mermaid_png()
            with open("reasoning_graph.png", "wb") as f:
                f.write(graph_image)
            print("💾 Reasoning graph visualization saved as 'reasoning_graph.png'")
        except Exception as e:
            print(f"⚠️  Could not save graph image: {e}")
            
    except Exception as e:
        print(f"⚠️  Could not get graph representation: {e}")
    
    return app

# Test function
def test_reasoning_system():
    """Test the reasoning system with sample queries."""
    app = create_reasoning_graph()
    
    test_queries = [
        "How should I approach learning a new programming language?",
        "What factors should I consider when choosing between different job offers?",
        "How can I improve my team's productivity?"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing Chain of Thought Reasoning: {query} ---")
        result = app.invoke({
            "messages": [HumanMessage(content=query)]
        })
        
        for msg in result["messages"]:
            if isinstance(msg, AIMessage) and msg.content.strip():
                print(f"🧠 Reasoning Agent: {msg.content}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_reasoning_system() 