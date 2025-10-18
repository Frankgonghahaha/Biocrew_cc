# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## Project Overview

This is a multi-agent system built with the CrewAI framework for wastewater microbial purification technology development. The system uses 6 types of AI agents working together to automate the full process of "screening functional microbes → designing microbial agents → evaluating effectiveness → generating implementation plans".

The system implements a two-layer architecture:
1. **Functional Execution Layer** (4 core agents):
   - Engineering Microorganism Identification Agent
   - Microbial Agent Design Agent
   - Microbial Agent Evaluation Agent
   - Implementation Plan Generation Agent
2. **Support Services Layer** (2 agents):
   - Knowledge Management Agent
   - Task Coordination Agent

## Common Commands

### Running the Application
```bash
# Run main application
python main.py

# Run with specific mode selection
python main.py
# Then select mode: 1 for sequential, 2 for hierarchical
```

### Running Tests
```bash
# Run specific test files
python tests/test_microbial_agent_workflow.py
python tests/test_identification_phase.py
python tests/test_design_phase.py
python tests/test_evaluation_phase.py
python tests/test_intermediate_product_check.py

# Run tool integration tests
python tests/test_tool_integration.py
```

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (copy .env.example to .env and configure)
cp .env.example .env
# Edit .env with your API keys and configurations

# Check code syntax
python -m py_compile main.py

# Run specific modules for debugging
python -c "from tools.microbial_agent_design.carveme_tool.carveme_tool import CarvemeTool; tool = CarvemeTool(); result = tool._run('./test_data', './outputs/metabolic_models')"
```

## Code Architecture

### Core Components

1. **Agents** (`/agents/`) - Define agent roles, goals, and backstories
   - Each agent implements a `create_agent()` method returning a configured CrewAI agent
   - Agents use domain-specific tools for their functions

2. **Tasks** (`/tasks/`) - Define specific work units for agents
   - Each task implements a `create_task()` method
   - Tasks define dependencies and expected outputs

3. **Tools** (`/tools/`) - Domain-specific functionality implementations
   - **Design Tools** (`/tools/microbial_agent_design/`) - For creating microbial agents
     - CarveMe tool for building genome-scale metabolic models
     - ctFBA tool for metabolic flux calculation
     - Database query tools for pollutant/microorganism data
   - **Evaluation Tools** (`/tools/microbial_agent_evaluation/`) - For assessing microbial agents
     - Reaction addition tool for modifying SBML models
     - Medium recommendation tool for growth media
     - Evaluation tool for analyzing results

4. **Configuration** (`/config/`) - System-wide settings and paths
   - `config.py` - Model and API configurations
   - `paths.py` - Unified directory paths for all tools

### Data Flow

1. **Knowledge Acquisition** → **Functional Execution Layer**
2. **Previous Agent Output** → **Next Agent Input**
3. **Feedback Loop**: Evaluation failures → Update prompts → Re-identify microbes

### Key Implementation Details

1. **Unified Path Management**: All tools use `/config/paths.py` for consistent directory references
2. **External Tool Integration**: External tools (CarveMe, GenomeSPOT, etc.) are internally integrated in `/tools/external_tools/`
3. **Database Tools**: Specialized database tools replace generic data tools for precise data access
4. **Model Storage**: All metabolic models are stored in `/outputs/metabolic_models/`
5. **Reaction Data**: Stored as CSV files in `/tools/data/reactions/`

### Important Architecture Patterns

1. **Tool Structure**: All tools inherit from `crewai.tools.BaseTool` with:
   - Dedicated Pydantic model for input parameters
   - `_run()` method with explicit parameter definitions
   - Consistent result format with status, data, and error information

2. **Agent Structure**: Agents implement:
   - `create_agent()` method returning configured CrewAI Agent
   - Clear role, goal, and backstory definitions
   - Domain-specific tool integration

3. **Task Structure**: Tasks implement:
   - `create_task()` method returning configured CrewAI Task
   - Clear descriptions and expected outputs
   - Context dependencies for proper sequencing

## Workflow Processing Modes

1. **Sequential Mode** (`Process.sequential`) - Fixed order execution
2. **Hierarchical Mode** (`Process.hierarchical`) - Dynamic agent selection based on task coordination agent

## Key Dependencies

- crewai - Multi-agent framework
- langchain - LLM integration
- cobra - Metabolic network analysis
- micom - Microbial community modeling
- pandas - Data processing
- SQLAlchemy - Database access