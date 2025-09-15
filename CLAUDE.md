# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent system built with the CrewAI framework for wastewater microbial purification technology development and optimization. The system implements a complete automated workflow through 6 AI agents collaborating to "screen functional microorganisms → design microbial agents → evaluate effectiveness → generate implementation plans". 

Note: The core algorithms (Tool_api, Tool_Carveme, ctFBA, and evaluation formulas) are currently only described in the agent backstories and task descriptions, with actual implementation pending as indicated by TODO comments throughout the codebase.

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
python3 main.py
```

### Code Validation
```bash
# Check for syntax errors
python3 -m py_compile main.py

# Check all Python files for syntax errors
find . -name "*.py" -exec python3 -m py_compile {} \;
```

### Testing
```bash
# Run specific test files (note: some tests require proper data directory structure)
python3 tests/test_local_data_query.py
python3 tests/test_engineering_microorganism_identification.py
python3 tests/test_database_tools.py
python3 tests/test_envipath_tool.py
python3 tests/test_autonomous_agent.py

# Run a single test function (if the test file supports it)
python3 -c "from tests.test_local_data_query import test_local_data_query; test_local_data_query()"
```

## Project Structure
```
BioCrew/
├── main.py                 # Main entry point (fully implemented)
├── requirements.txt        # Project dependencies
├── .env.example           # Environment variable configuration example
├── config/
│   └── config.py          # Configuration file (fully implemented)
├── agents/                # Agent definitions (fully implemented with TODOs for core algorithms)
│   ├── task_coordination_agent.py
│   ├── engineering_microorganism_identification_agent.py
│   ├── microbial_agent_design_agent.py
│   ├── microbial_agent_evaluation_agent.py
│   ├── implementation_plan_generation_agent.py
│   └── knowledge_management_agent.py
├── tasks/                 # Task definitions (fully implemented with TODOs for core algorithms)
│   ├── microorganism_identification_task.py
│   ├── microbial_agent_design_task.py
│   ├── microbial_agent_evaluation_task.py
│   └── implementation_plan_generation_task.py
├── tools/                 # Custom tools (partially implemented)
│   ├── evaluation_tool.py
│   ├── local_data_retriever.py          # Local data access tool
│   ├── smart_data_query_tool.py         # Smart data querying tool
│   ├── mandatory_local_data_query_tool.py  # Mandatory data querying tool
│   ├── envipath_tool.py                 # EnviPath database access tool
│   └── kegg_tool.py                     # KEGG database access tool
├── data/                  # Local data files (Genes and Organism directories)
│   ├── Genes/
│   └── Organism/
├── tests/                 # Test files for all components
│   ├── test_autonomous_agent.py
│   ├── test_database_tools.py
│   ├── test_engineering_microorganism_identification.py
│   ├── test_envipath_tool.py
│   └── test_local_data_query.py
└── models/                # Model configurations (to be completed)
```

## Key Implementation Details

### Data Flow
- Knowledge Management → Functional Execution Layer agents
- Previous agent output → Next agent input
- Feedback loop: Evaluation failure → Update prompts → Re-identify microorganisms

### Core Algorithms (Partially implemented, with TODOs)
1. **Tool_api and Tool_Carveme** - For retrieving genomic/enzyme sequence data and converting genomes to metabolic models
   - Currently only described in agent backstories, actual implementation pending
2. **ctFBA algorithm** - Cooperative trade-off metabolic flux balance method for metabolic flux calculations
   - Currently only described in agent backstories, actual implementation pending
3. **Evaluation formulas** - Including competition index, complementarity index, Pianka niche overlap index, species knockout index
   - Currently only described in agent backstories, actual implementation pending

### Configuration
The system supports both DashScope (Qwen) and OpenAI model configurations through environment variables in the `.env` file.

### Local Data Access
The system uses local Excel data files stored in `data/Genes` and `data/Organism` directories. Several tools have been implemented to access this data:

1. **LocalDataRetriever** - Core tool for reading Excel files from local directories
2. **SmartDataQueryTool** - Intelligent querying tool that can automatically identify and retrieve relevant data based on text input
3. **MandatoryLocalDataQueryTool** - Ensures data is always retrieved from local sources

These tools support:
- Reading data for specific pollutants
- Accessing multiple worksheets within Excel files
- Searching for data files by pollutant names
- Handling both gene data and organism data

### External Database Access Tools

The system integrates with external databases through the following tools:

4. **EnviPathTool** - Accesses environmental contaminant biotransformation pathway data from the enviPath database
   - `_run(operation, **kwargs)` - Unified interface for all EnviPath operations
   - Operations: `search_compound`, `get_pathway_info`, `get_compound_pathways`, `search_pathways_by_keyword`
   - Also supports direct method calls: `search_compound(compound_name)`, `get_pathway_info(pathway_id)`, etc.

5. **KeggTool** - Accesses biological pathway and genomic data from the KEGG database
   - `_run(operation, **kwargs)` - Unified interface for all KEGG operations
   - Operations: `get_database_info`, `list_entries`, `find_entries`, `get_entry`, `link_entries`, `convert_id`, `search_pathway_by_compound`, `search_genes_by_pathway`, `search_enzymes_by_compound`
   - Also supports direct method calls for each operation

### Evaluation Tool

6. **EvaluationTool** - Analyzes and evaluates microbial agent effectiveness
   - `_run(operation, **kwargs)` - Unified interface for evaluation operations
   - Operations: `analyze_evaluation_result`, `check_core_standards`
   - Also supports direct method calls: `analyze_evaluation_result(evaluation_report)`, `check_core_standards(evaluation_report)`

## Development Guidelines

### Code Organization
- Each agent is defined in its own file in the `agents/` directory
- Each task is defined in its own file in the `tasks/` directory
- Shared functionality should be implemented in the `tools/` directory
- Configuration is managed through the `config/` directory
- Local data is stored in the `data/` directory
- Tests are located in the `tests/` directory

### Tool Structure
All tools follow a consistent pattern:
1. Each tool inherits from `crewai.tools.BaseTool` for CrewAI compatibility
2. Tools implement a unified `_run(operation, **kwargs)` method as the main entry point
3. Tools provide direct method calls for specific operations for backward compatibility
4. Tools use `object.__setattr__` and `object.__getattribute__` to handle instance attributes and avoid Pydantic validation issues
5. Tools return consistent result formats with `status`, `data`, and error information

### Agent Structure
Agents follow a consistent pattern:
1. Each agent is implemented as a class with a `create_agent()` method
2. The `create_agent()` method returns a configured CrewAI Agent instance
3. Agents define their role, goal, and backstory
4. Agents can use custom tools for specialized functionality

### Task Structure
Tasks follow a consistent pattern:
1. Each task is implemented as a class with a `create_task()` method
2. The `create_task()` method returns a configured CrewAI Task instance
3. Tasks define their description and expected output
4. Tasks can depend on other tasks through the context parameter

### Adding New Features
1. To add a new agent, create a new file in the `agents/` directory following the existing pattern
2. To add a new task, create a new file in the `tasks/` directory following the existing pattern
3. Register new agents and tasks in `main.py`
4. Update the Crew configuration in `main.py` to include new agents and tasks
5. For data access functionality, implement new tools in the `tools/` directory
6. Add corresponding test files in the `tests/` directory

### Testing
The project includes several test files for validating functionality:
1. `tests/test_local_data_query.py` - Tests local data retrieval functionality
2. `tests/test_engineering_microorganism_identification.py` - Tests the identification agent functionality
3. `tests/test_database_tools.py` - Tests database tool functionality (EnviPath and KEGG)
4. `tests/test_envipath_tool.py` - Tests EnviPath tool specifically
5. `tests/test_autonomous_agent.py` - Tests autonomous agent functionality

When adding new functionality:
1. Manually test the new features by running the application
2. Verify that the new agents/tasks integrate correctly with existing components
3. Check that the output format matches expectations
4. Add specific test files for new functionality in the `tests/` directory
5. Run existing tests to ensure no regressions were introduced

Note: Some tests may require the proper data directory structure to run successfully. The data files should be located in `data/Genes` and `data/Organism` directories.