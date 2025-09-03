# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent system built with the CrewAI framework for wastewater microbial purification technology development and optimization. The system implements a complete automated workflow through 6 AI agents collaborating to "screen functional microorganisms → design microbial agents → evaluate effectiveness → generate implementation plans".

## Codebase Architecture

The system follows a two-layer architecture with 6 types of agents:

### Functional Execution Layer (4 core agents)
1. **Engineering Microorganism Identification Agent** - Screens functional microorganisms and metabolically complementary microorganisms based on water purification goals
2. **Microbial Agent Design Agent** - Designs microbial agents using ctFBA (cooperative trade-off metabolic flux balance) method
3. **Microbial Agent Evaluation Agent** - Evaluates biological purification effectiveness and community ecological characteristics
4. **Implementation Plan Generation Agent** - Generates complete microbial purification technology implementation plans

### Support Service Layer (2 agents)
5. **Knowledge Management Agent** - Acquires, stores, and provides domain knowledge
6. **Task Coordination Agent** - Controls workflow execution order and handles multi-objective and exception situations

## Common Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Then edit .env with your API keys
```

### Running the Application
```bash
# Run the main application
python main.py
```

### Code Validation
```bash
# Check for syntax errors
python3 -m py_compile main.py

# Check all Python files for syntax errors
find . -name "*.py" -exec python3 -m py_compile {} \;
```

## Project Structure
```
BioCrew/
├── main.py                 # Main entry point
├── requirements.txt        # Project dependencies
├── .env.example           # Environment variable configuration example
├── config/
│   └── config.py          # Configuration file
├── agents/                # Agent definitions
│   ├── task_coordination_agent.py
│   ├── engineering_microorganism_identification_agent.py
│   ├── microbial_agent_design_agent.py
│   ├── microbial_agent_evaluation_agent.py
│   ├── implementation_plan_generation_agent.py
│   └── knowledge_management_agent.py
├── tasks/                 # Task definitions
│   ├── microorganism_identification_task.py
│   ├── microbial_agent_design_task.py
│   ├── microbial_agent_evaluation_task.py
│   └── implementation_plan_generation_task.py
├── tools/                 # Custom tools
│   └── evaluation_tool.py
└── models/                # Model configurations (to be completed)
```

## Key Implementation Details

### Data Flow
- Knowledge Management → Functional Execution Layer agents
- Previous agent output → Next agent input
- Feedback loop: Evaluation failure → Update prompts → Re-identify microorganisms

### Core Algorithms (To be implemented)
1. **Tool_api and Tool_Carveme** - For retrieving genomic/enzyme sequence data and converting genomes to metabolic models
2. **ctFBA algorithm** - Cooperative trade-off metabolic flux balance method for metabolic flux calculations
3. **Evaluation formulas** - Including competition index, complementarity index, Pianka niche overlap index, species knockout index

### Configuration
The system supports both DashScope (Qwen) and OpenAI model configurations through environment variables in the `.env` file.