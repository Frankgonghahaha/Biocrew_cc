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

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (copy .env.example to .env and configure)
cp .env.example .env
# Edit .env with your API keys and configurations
```

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
python tests/test_workflow.py
python tests/test_identification_phase.py
python tests/test_design_phase.py
python tests/test_evaluation_phase.py
python tests/test_intermediate_product_check.py

# Run tool integration tests
python tests/test_tool_integration.py

# Run specific tool tests
python tests/test_carveme_fix.py
python tests/test_reaction_addition.py
```

### Development Commands
```bash
# Check code syntax
python -m py_compile main.py

# Check all Python files for syntax errors
find . -name "*.py" -exec python -m py_compile {} \;

# Run specific modules for debugging
python -c "from core.tools.design.carveme import CarvemeTool; tool = CarvemeTool(); result = tool._run('./test_data', './outputs/metabolic_models')"
```

## Code Architecture

### Core Components

1. **Agents** (`/core/agents/`) - Define agent roles, goals, and backstories
   - Each agent implements a `create_agent()` method returning a configured CrewAI agent
   - Agents use domain-specific tools for their functions
   - Key agents:
     - `identification_agent.py` - Identifies functional microbes for pollutant degradation
     - `design_agent.py` - Designs microbial agents using ctFBA methodology
     - `evaluation_agent.py` - Evaluates bio-purification effectiveness
     - `implementation_agent.py` - Generates implementation plans
     - `coordination_agent.py` - Controls workflow execution order
     - `knowledge_agent.py` - Manages domain knowledge

2. **Tasks** (`/core/tasks/`) - Define specific work units for agents
   - Each task implements a `create_task()` method
   - Tasks define dependencies and expected outputs
   - Key tasks:
     - `identification_task.py` - Microorganism identification task
     - `design_task.py` - Microbial agent design task
     - `evaluation_task.py` - Microbial agent evaluation task
     - `implementation_task.py` - Implementation plan generation task
     - `coordination_task.py` - Task coordination task

3. **Tools** (`/core/tools/`) - Domain-specific functionality implementations
   - **Database Tools** (`/core/tools/database/`) - For querying pollutant/microorganism data
     - `factory.py` - Creates and manages database tool instances
     - `envipath.py` - Accesses EnviPath database for environmental pollutant biotransformation pathways
     - `kegg.py` - Accesses KEGG database for biological pathways and genomic data
     - `ncbi.py` - Queries NCBI database for microbial genome data
     - `complementarity_query.py` - Queries microbial complementarity data
     - `pollutant_query.py` - Queries pollutant data
     - `gene_query.py` - Queries gene data
     - `organism_query.py` - Queries organism data
     - `summary.py` - Gets pollutant summary statistics
     - `search.py` - Searches pollutants by keyword
     - `name_utils.py` - Standardizes pollutant names
   - **Design Tools** (`/core/tools/design/`) - For creating microbial agents
     - `carveme.py` - Builds genome-scale metabolic models (GSMM)
     - `ctfba.py` - Calculates metabolic flux using cooperative trade-off FBA
     - `genome_processing.py` - Processes genome data
     - `genome_spot.py` - Predicts microbial environmental adaptability
     - `dlkcat.py` - Predicts degradation enzyme rates
     - `phylomint.py` - Analyzes metabolic complementarity between microbes
   - **Evaluation Tools** (`/core/tools/evaluation/`) - For assessing microbial agents
     - `reaction_addition.py` - Adds metabolic reactions to SBML models
     - `medium_recommendation.py` - Generates recommended medium components using MICOM
     - `evaluation.py` - Analyzes and evaluates microbial agent effectiveness
     - `ctfba.py` - Calculates microbial community metabolic flux (shared with design)
   - **External Tools** (`/core/tools/external/`) - Integrated external tools
     - `genome.py` - Genome tools integration
   - **Services Tools** (`/core/tools/services/`) - Service utilities
     - `genomic_data.py` - Genomic data services
     - `intermediate_check.py` - Intermediate product checking

4. **Configuration** (`/config/`) - System-wide settings and paths
   - `config.py` - Model and API configurations
   - `paths.py` - Unified directory paths for all tools

### Data Flow

1. **Knowledge Acquisition** → **Functional Execution Layer**
2. **Previous Agent Output** → **Next Agent Input**
3. **Feedback Loop**: Evaluation failures → Update prompts → Re-identify microbes

### Key Implementation Details

1. **Unified Path Management**: All tools use `/config/paths.py` for consistent directory references
2. **External Tool Integration**: External tools (CarveMe, GenomeSPOT, etc.) are internally integrated in `/core/tools/external/`
3. **Database Tools**: Specialized database tools replace generic data tools for precise data access
4. **Model Storage**: All metabolic models are stored in `/outputs/metabolic_models/`
5. **Reaction Data**: Stored as CSV files in `/data/reactions/`
6. **Genome Data**: Stored in `/data/genomes/`
7. **Medium Data**: Stored in `/data/medium/`

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

4. **Factory Pattern**: Database tools are managed by `DatabaseToolFactory` for centralized creation

5. **Path Management**: All file paths use unified configuration from `/config/paths.py`

## Workflow Processing Modes

1. **Sequential Mode** (`Process.sequential`) - Fixed order execution
2. **Hierarchical Mode** (`Process.hierarchical`) - Dynamic agent selection based on task coordination agent

## Key Dependencies

- crewai - Multi-agent framework
- langchain - LLM integration
- langchain-openai - OpenAI integration for LangChain
- cobra - Metabolic network analysis
- micom - Microbial community modeling
- pandas - Data processing
- SQLAlchemy - Database access
- python-dotenv - Environment variable management
- enviPath-python - EnviPath database access
- psycopg2-binary - PostgreSQL driver

## Project Structure

```
BioCrew/
├── main.py                 # Main application entry point
├── requirements.txt        # Project dependencies
├── .env.example           # Environment variable configuration example
├── CLAUDE.md              # Claude Code development guide
├── AGENTS.md              # Qoder development guide (this file)
├── config/                # Configuration files
│   ├── __init__.py
│   ├── config.py          # Main configuration file
│   └── paths.py           # Path configuration
├── core/                  # Core modules
│   ├── agents/            # Agent definitions
│   │   ├── __init__.py
│   │   ├── identification_agent.py     # Engineering microorganism identification agent
│   │   ├── design_agent.py             # Microbial agent design agent
│   │   ├── evaluation_agent.py         # Microbial agent evaluation agent
│   │   ├── implementation_agent.py     # Implementation plan generation agent
│   │   ├── coordination_agent.py       # Task coordination agent
│   │   └── knowledge_agent.py          # Knowledge management agent
│   ├── tasks/             # Task definitions
│   │   ├── __init__.py
│   │   ├── identification_task.py      # Microorganism identification task
│   │   ├── design_task.py              # Microbial agent design task
│   │   ├── evaluation_task.py          # Microbial agent evaluation task
│   │   ├── implementation_task.py      # Implementation plan generation task
│   │   └── coordination_task.py        # Task coordination task
│   └── tools/             # Custom tools (unified management)
│       ├── __init__.py
│       ├── database/      # Database tools
│       │   ├── __init__.py
│       │   ├── factory.py              # Database tool factory
│       │   ├── envipath.py             # EnviPath database access tool
│       │   ├── kegg.py                 # KEGG database access tool
│       │   ├── ncbi.py                 # NCBI genome query tool
│       │   ├── complementarity_query.py # Microbial complementarity query tool
│       │   ├── complementarity_model.py # Microbial complementarity data model
│       │   ├── complementarity_tool.py # Microbial complementarity query tool
│       │   ├── pollutant_query.py      # Pollutant data query tool
│       │   ├── gene_query.py           # Gene data query tool
│       │   ├── organism_query.py       # Organism data query tool
│       │   ├── summary.py              # Pollutant summary tool
│       │   ├── search.py               # Pollutant search tool
│       │   └── name_utils.py           # Pollutant name standardization tool
│       ├── external/      # External database tools
│       │   ├── __init__.py
│       │   └── genome.py               # Genome tool
│       ├── design/        # Microbial agent design tools
│       │   ├── __init__.py
│       │   ├── genome_processing.py    # Genome processing tool
│       │   ├── genome_spot.py          # GenomeSPOT tool
│       │   ├── dlkcat.py               # DLkcat tool
│       │   ├── carveme.py              # Carveme tool
│       │   ├── phylomint.py            # Phylomint tool
│       │   └── ctfba.py                # ctFBA tool
│       ├── evaluation/    # Microbial agent evaluation tools
│       │   ├── __init__.py
│       │   ├── evaluation.py           # Evaluation tool
│       │   ├── reaction_addition.py    # Metabolic reaction addition tool
│       │   ├── medium_recommendation.py # Medium recommendation tool
│       │   └── ctfba.py                # ctFBA tool (shared)
│       └── services/      # Service tools
│           ├── __init__.py
│           ├── genomic_data.py         # Genomic data service
│           └── intermediate_check.py   # Intermediate product check tool
├── data/                  # Local data
│   ├── genomes/           # Genome data
│   ├── reactions/         # Reaction data
│   └── medium/            # Medium data
├── outputs/               # Output files
│   ├── genome_features/   # Genome features
│   ├── metabolic_models/  # Metabolic models
│   └── results/           # Result files
├── tests/                 # Test files
│   ├── __init__.py
│   ├── test_workflow.py               # Complete workflow test
│   ├── test_identification_phase.py   # Engineering microorganism identification phase test
│   ├── test_design_phase.py           # Microbial agent design phase test
│   ├── test_evaluation_phase.py       # Microbial agent evaluation phase test
│   ├── test_intermediate_product_check.py  # Intermediate product check test
│   ├── test_tool_integration.py       # Tool integration test
│   ├── test_carveme_fix.py            # Carveme tool test
│   ├── test_reaction_addition.py      # Reaction addition tool test
│   └── test_full_workflow.py          # Complete workflow test
└── docs/                  # Documentation
    ├── AGENTS.md         # Agent documentation
    ├── TASKS.md          # Task documentation
    ├── TOOLS.md          # Tool documentation
    ├── TESTS.md          # Test documentation
    ├── workflow/          # Workflow documentation
    │   └── complete_workflow.md  # Complete workflow explanation
    └── tools/             # Tool detailed explanations
        ├── detailed/      # Detailed tool explanations
        │   ├── carveme_tool.md     # Carveme tool detailed explanation
        │   └── reaction_addition_tool.md  # ReactionAdditionTool detailed explanation
        └── ...
```