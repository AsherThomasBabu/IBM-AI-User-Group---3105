# Multi-Agent AI System - Customer Support & Chain of Thought Reasoning

A comprehensive multi-agent AI system built with LangGraph that demonstrates two powerful patterns:
1. **Supervisor-Worker Pattern** for customer support
2. **Chain of Thought Reasoning** for transparent problem-solving

## Features

### 🎧 Customer Support System
- **Supervisor-Worker Architecture**: Intelligent routing of customer queries to specialized agents
- **🔧 Technical Support Agent**: Handles password resets, technical troubleshooting, API issues
- **💳 Billing Support Agent**: Manages payment inquiries, refunds, account status checks
- **📋 General Support Agent**: Assists with account management and service plan changes
- **🛠️ Tool Integration**: Each agent has access to relevant tools for their domain

### 🧠 Chain of Thought Reasoning System
- **Transparent Thinking**: Shows step-by-step reasoning process
- **Structured Analysis**: 4-step systematic approach to problem-solving
- **Decision Support**: Helps with complex decisions and strategic planning
- **Educational**: Demonstrates how AI can think through problems logically

### 💬 Unified Interface
- **Streamlit Web App**: Clean, modern interface for both systems
- **System Selector**: Easy switching between customer support and reasoning modes
- **Real-time Processing**: Live interaction with both AI systems

## Architecture

### Customer Support Flow
```
Customer Query → Supervisor Agent → Routes to:
                                  ├── Technical Agent (password, API, connectivity)
                                  ├── Billing Agent (payments, refunds, billing)
                                  └── General Agent (account, plans, general)
```

### Chain of Thought Flow
```
User Problem → Coordinator → Step-by-Step Reasoner → Conclusion Synthesizer
                            ├── Step 1: Problem Analysis
                            ├── Step 2: Information Gathering
                            ├── Step 3: Option Generation
                            └── Step 4: Evaluation & Decision
```

## Setup Instructions

### 1. Clone and Navigate
```bash
cd "IBM AI User Group"  # or your project directory
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

Or set it directly in the Streamlit interface.

### 5. Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

### Customer Support System
1. **Select Customer Support** in the sidebar
2. **Enter API Key**: Add your OpenAI API key
3. **Start Chatting**: Type your support request
4. **Watch the Routing**: See how the supervisor routes to specialists
5. **See Tool Usage**: Watch agents use tools to resolve issues

### Chain of Thought Reasoning
1. **Select Chain of Thought Reasoning** in the sidebar
2. **Enter API Key**: Add your OpenAI API key
3. **Ask Complex Questions**: Pose problems that require thinking
4. **Follow the Steps**: Watch the AI think through each step
5. **Get Reasoned Conclusions**: Receive well-supported recommendations

## Example Queries

### Customer Support Examples

#### Technical Support
- "I can't log into my account, I think I forgot my password"
- "My API calls are failing with timeout errors"
- "The service seems to be down, can you check?"

#### Billing Support
- "I was charged twice this month and need a refund"
- "Can you check my current account balance?"
- "I want to dispute a charge on my account"

#### General Support
- "I want to upgrade my service plan to premium"
- "How do I change my account settings?"
- "What features are included in my current plan?"

### Chain of Thought Examples

#### Decision Making
- "Should I switch careers from marketing to data science?"
- "What factors should I consider when choosing a university?"
- "How do I decide between renting vs buying a house?"

#### Problem Solving
- "My team is missing deadlines. How can I improve our productivity?"
- "How should I approach learning machine learning as a beginner?"
- "What's the best way to resolve conflicts in a remote team?"

#### Strategic Planning
- "How should I plan my startup's go-to-market strategy?"
- "What steps should I take to improve my company's customer retention?"
- "How can I effectively manage a project with multiple stakeholders?"

## Available Tools

### Customer Support Tools

#### Technical Agent Tools
- `check_technical_logs`: Check system logs for issues
- `reset_password`: Initiate password reset process
- `escalate_to_manager`: Escalate complex technical issues

#### Billing Agent Tools
- `check_billing_info`: Retrieve customer billing information
- `create_refund`: Process refund requests
- `check_account_status`: Check customer account status
- `escalate_to_manager`: Escalate billing disputes

#### General Agent Tools
- `check_account_status`: Check customer account status
- `update_service_plan`: Modify customer service plans
- `escalate_to_manager`: Escalate general inquiries

### Chain of Thought Process
The reasoning system follows a structured 4-step approach:
1. **Problem Analysis**: Break down the problem into components
2. **Information Gathering**: Identify what information is needed
3. **Option Generation**: Explore different approaches and solutions
4. **Evaluation & Decision**: Analyze pros/cons and make recommendations

## Project Structure

```
├── app.py                          # Streamlit interface (multi-system)
├── agents.py                       # Customer support agents and graph
├── chain_of_thought_agent.py       # Chain of thought reasoning system
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env                           # Environment variables (create this)
├── presentation_outline.md         # Supervisor-worker presentation guide
└── chain_of_thought_presentation.md # Chain of thought presentation guide
```

## Key Components

### Customer Support System

#### Supervisor Agent
- Analyzes incoming customer messages
- Routes requests to appropriate specialist agents
- Uses LLM to understand intent and categorize requests

#### Worker Agents
- **Technical Agent**: Specialized in technical issues and troubleshooting
- **Billing Agent**: Handles financial and billing-related queries
- **General Agent**: Manages general account and service inquiries

### Chain of Thought System

#### Reasoning Coordinator
- Receives user problems and initiates reasoning process
- Sets up the structured thinking framework

#### Step-by-Step Reasoner
- Performs systematic analysis through 4 defined steps
- Each step builds on previous insights
- Maintains clear reasoning trail

#### Conclusion Synthesizer
- Combines all reasoning steps into actionable recommendations
- Provides clear explanations of the logical path
- Acknowledges limitations and suggests next steps

## Development

### Testing the Systems

#### Test Customer Support
```bash
python agents.py
```

#### Test Chain of Thought Reasoning
```bash
python chain_of_thought_agent.py
```

### Customizing the Systems

#### Customer Support Customization
- Modify agent prompts in `agents.py`
- Add new tools by creating functions with the `@tool` decorator
- Adjust routing logic in the supervisor node

#### Chain of Thought Customization
- Modify reasoning steps in `chain_of_thought_agent.py`
- Adjust the number of reasoning steps (currently 4)
- Customize prompts for different domains (business, technical, personal)

### Adding New Features
1. **New Agent Types**: Add specialized agents for new domains
2. **Enhanced Reasoning**: Add domain-specific reasoning patterns
3. **Visual Elements**: Add charts, diagrams, or flowcharts
4. **Memory**: Implement conversation history and context retention

## Dependencies

- `streamlit>=1.39.0`: Web interface
- `langgraph>=0.2.50`: Multi-agent orchestration
- `langchain-openai>=0.2.10`: OpenAI integration
- `langchain>=0.3.10`: Core LangChain functionality
- `python-dotenv>=1.0.0`: Environment variable management

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your OpenAI API key is set correctly
2. **Import Errors**: Ensure all dependencies are installed in the virtual environment
3. **Graph Compilation Issues**: Check that all agent nodes are properly defined
4. **Empty Messages**: If you see empty responses, check the message flow in debug mode

### Debug Mode
Enable debug mode in the Streamlit interface to see:
- Message flow between agents
- Tool execution results
- Graph state information
- Reasoning step progression

## Use Cases

### Customer Support System
- **Business**: Automate customer service operations
- **Education**: Teach multi-agent system design
- **Development**: Template for building support systems

### Chain of Thought Reasoning
- **Decision Making**: Personal and business decisions
- **Problem Solving**: Systematic approach to complex problems
- **Education**: Demonstrate transparent AI reasoning
- **Consulting**: Structure thinking for strategic planning

## Presentation Materials

This project includes presentation materials for the IBM AI User Group:
- `presentation_outline.md`: 15-minute supervisor-worker pattern presentation
- `chain_of_thought_presentation.md`: 15-minute chain of thought reasoning presentation

## License

This project is for educational purposes as part of the IBM AI User Group presentation on multi-agent orchestration patterns and advanced reasoning techniques.

## Next Steps

### Customer Support Enhancements
- Add memory/persistence for conversation history
- Implement more sophisticated routing logic
- Add real integrations with customer support systems
- Enhance tool capabilities with actual API calls

### Chain of Thought Enhancements
- Add visual reasoning with diagrams and flowcharts
- Implement collaborative reasoning with multiple agents
- Create domain-specific reasoning patterns (legal, medical, financial)
- Add interactive reasoning where users can guide the process

### System Integration
- Combine both systems for comprehensive AI assistance
- Add cross-system learning and knowledge sharing
- Implement unified conversation history
- Create hybrid workflows that use both patterns # IBM-AI-User-Group---3105
