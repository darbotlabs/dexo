# dexo - Decentralized Autonomous Reasoning Engine

## New Features

### 1. Terminal User Interface (TUI)

dexo now includes a rich terminal user interface for monitoring and managing your AI cluster.

#### Running the TUI

```bash
# Start the TUI
dexo-tui

# Or specify a custom API URL
dexo-tui --api-url http://192.168.1.100:52415
```

#### Features

- **Cluster View**: Real-time monitoring of all nodes in your cluster
- **Model Management**: View and manage available models
- **Chat Interface**: (Coming soon) Interactive chat directly in the terminal
- **System Logs**: (Coming soon) View cluster logs and events

#### Keyboard Shortcuts

- `q` - Quit the application
- `r` - Refresh data from the cluster
- `d` - Toggle dark/light mode
- `Tab` - Navigate between panels

---

### 2. SWE-Agent (Software Engineering Agent)

dexo includes an autonomous software engineering agent for code analysis, generation, and testing.

#### Usage

```bash
# Analyze a code file
dexo-swe analyze path/to/file.py

# Generate code from a prompt
dexo-swe generate "Create a function to calculate fibonacci numbers" --language python

# Run tests
dexo-swe test path/to/tests/

# Auto-fix code issues
dexo-swe fix path/to/file.py
```

#### Examples

**Code Analysis:**
```bash
$ dexo-swe analyze src/exo/main.py

=== Code Analysis: src/exo/main.py ===
Complexity Score: 1.33
No issues found.
```

**Code Generation:**
```bash
$ dexo-swe generate "Create a REST API endpoint for health checks" --language python --max-tokens 1000

=== Generated Code ===
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dexo"}
```

---

### 3. Autogen2 Integration

dexo integrates with Autogen2 (ag2ai) for autonomous agent swarm coordination and resource governance.

#### Swarm Coordinator

The swarm coordinator manages resource allocation and continuous learning tasks across the cluster.

```python
from exo.autogen.swarm_coordinator import (
    SwarmCoordinator,
    SwarmNode,
    LearningTask,
    ResourceThreshold,
)

# Create coordinator with resource thresholds
coordinator = SwarmCoordinator(
    resource_threshold=ResourceThreshold(
        min_memory_gb=4.0,
        min_cpu_cores=2,
        min_gpu_memory_gb=0.0,
        min_network_bandwidth_mbps=10.0,
    )
)

# Register a node
node = SwarmNode(
    node_id="node-1",
    available_memory_gb=16.0,
    cpu_cores=8,
    gpu_memory_gb=8.0,
    network_bandwidth_mbps=1000.0,
)
coordinator.register_node(node)

# Submit a learning task
task = LearningTask(
    task_id="task-1",
    task_type="training",
    priority=1,
    required_resources=ResourceThreshold(
        min_memory_gb=8.0,
        min_cpu_cores=4,
    ),
)
coordinator.submit_learning_task(task)

# Get swarm status
status = coordinator.get_swarm_status()
print(status)
```

#### Autogen Agent Integration

Connect Autogen2 agents to the dexo cluster:

```python
from exo.autogen.agent_integration import DexoAutogenBridge, create_dexo_reasoning_team

# Create bridge to dexo
bridge = DexoAutogenBridge(dexo_api_url="http://localhost:52415")

# Create agents
assistant = bridge.create_assistant_agent(
    name="CodeAssistant",
    system_message="You are a helpful coding assistant.",
)

user_proxy = bridge.create_user_proxy_agent(name="User")

# Or create a reasoning team
architect, engineer, reviewer = create_dexo_reasoning_team()
```

---

## Configuration

### Environment Variables

dexo supports the following environment variables:

- `DEXO_HOME` - Base directory for dexo files (default: `~/.dexo`)
- `DEXO_MODELS_DIR` - Directory for model storage
- `DEXO_ENABLE_IMAGE_MODELS` - Enable image generation models (default: `false`)
- `DEXO_TRACING_ENABLED` - Enable distributed tracing (default: `false`)

**Backward Compatibility:** All `EXO_*` environment variables are still supported.

---

## Command Reference

| Command | Description |
|---------|-------------|
| `dexo` | Start dexo cluster (web dashboard) |
| `dexo-tui` | Start terminal user interface |
| `dexo-master` | Start master node only |
| `dexo-worker` | Start worker node only |
| `dexo-swe` | Software engineering agent CLI |

---

## Architecture

### Autonomous Reasoning

dexo implements autonomous reasoning through:

1. **SWE-Agent**: Autonomous code analysis and generation
2. **Autogen2 Integration**: Multi-agent collaboration and reasoning
3. **Resource Governance**: Intelligent resource allocation with minimum thresholds
4. **Continuous Learning**: Automated learning task coordination

### Components

```
┌─────────────────────────────────────────┐
│         dexo Cluster                     │
├─────────────────────────────────────────┤
│  ┌────────────┐  ┌─────────────────┐   │
│  │   Master   │  │  Autogen Swarm   │   │
│  │  (Router)  │  │  Coordinator     │   │
│  └────────────┘  └─────────────────┘   │
│         │                 │              │
│  ┌──────┴──────┐   ┌─────┴──────┐      │
│  │   Worker    │   │  SWE-Agent  │      │
│  │  (Inference)│   │  (Reasoning)│      │
│  └─────────────┘   └─────────────┘      │
│         │                 │              │
│  ┌──────┴──────────────────┴──────┐     │
│  │         API & TUI               │     │
│  └──────────────────────────────┬──┘     │
└─────────────────────────────────┼────────┘
                                  │
                        ┌─────────┴──────────┐
                        │   User Interface    │
                        │  (Web/Terminal)     │
                        └────────────────────┘
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.
