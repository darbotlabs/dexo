# dexo Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/darbotlabs/dexo
cd dexo

# Install dependencies (requires uv, node, rust)
cd dashboard && npm install && npm run build && cd ..

# Install Python dependencies
uv sync
```

## Running dexo

### Option 1: Web Dashboard (Default)
```bash
# Start the full cluster with web UI
dexo

# Access at http://localhost:52415
```

### Option 2: Terminal UI
```bash
# Start with terminal interface
dexo-tui

# Keyboard shortcuts:
# q - Quit
# r - Refresh data
# d - Toggle dark mode
# Tab - Switch between tabs
```

## Using SWE-Agent

### Analyze Code
```bash
# Basic analysis
dexo-swe analyze src/exo/main.py

# Output:
# === Code Analysis: src/exo/main.py ===
# Complexity Score: 1.33
# No syntax errors found
# 
# Suggestions:
#   - Consider breaking large files into modules
```

### Generate Code
```bash
# Generate a function
dexo-swe generate "Create a function to validate email addresses" \
    --language python \
    --max-tokens 1000

# Output:
# === Generated Code ===
# import re
# 
# def validate_email(email: str) -> bool:
#     """Validate email address format."""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return bool(re.match(pattern, email))
```

### Run Tests
```bash
# Run tests on a specific path
dexo-swe test src/exo/tests/

# Output:
# === Test Results ===
# Success: True
# Tests: 50, Passed: 50, Failed: 0
```

### Auto-Fix Code
```bash
# Attempt to fix issues automatically
dexo-swe fix src/buggy_file.py

# The agent will:
# 1. Analyze the file for issues
# 2. Use the cluster to generate fixes
# 3. Provide suggested corrections
```

## Using Autogen2 Integration

### Resource Swarm Coordinator

```python
from exo.autogen.swarm_coordinator import (
    SwarmCoordinator,
    SwarmNode, 
    LearningTask,
    ResourceThreshold
)

# Initialize coordinator with governance rules
coordinator = SwarmCoordinator(
    resource_threshold=ResourceThreshold(
        min_memory_gb=4.0,      # Minimum 4GB RAM
        min_cpu_cores=2,        # Minimum 2 CPU cores
        min_gpu_memory_gb=0.0,  # GPU optional
        min_network_bandwidth_mbps=10.0  # 10 Mbps minimum
    )
)

# Register a node (enforces thresholds automatically)
node = SwarmNode(
    node_id="powerful-workstation",
    available_memory_gb=32.0,
    cpu_cores=16,
    gpu_memory_gb=24.0,
    network_bandwidth_mbps=1000.0,
    capabilities=["training", "inference", "fine-tuning"]
)

success = coordinator.register_node(node)
print(f"Node registered: {success}")

# Submit a learning task
task = LearningTask(
    task_id="train-llama-lora",
    task_type="training",
    priority=1,
    required_resources=ResourceThreshold(
        min_memory_gb=16.0,
        min_cpu_cores=8,
        min_gpu_memory_gb=8.0
    )
)

task_id = coordinator.submit_learning_task(task)
print(f"Task submitted: {task_id}")

# Monitor swarm status
status = coordinator.get_swarm_status()
print(f"""
Swarm Status:
  Total Nodes: {status['total_nodes']}
  Idle: {status['idle_nodes']}
  Busy: {status['busy_nodes']}
  Learning: {status['learning_nodes']}
  
  Pending Tasks: {status['pending_tasks']}
  Running Tasks: {status['running_tasks']}
  Completed: {status['completed_tasks']}
""")
```

### Autogen Agent Bridge

```python
from exo.autogen.agent_integration import (
    DexoAutogenBridge,
    create_dexo_reasoning_team
)

# Connect Autogen to dexo cluster
bridge = DexoAutogenBridge(dexo_api_url="http://localhost:52415")

# Create individual agents
assistant = bridge.create_assistant_agent(
    name="CodeHelper",
    system_message="You are an expert Python developer.",
)

user = bridge.create_user_proxy_agent(name="User")

# Or create a reasoning team (Architect, Engineer, Reviewer)
architect, engineer, reviewer = create_dexo_reasoning_team()

# Create a group chat for collaborative reasoning
groupchat, manager = bridge.create_group_chat(
    agents=[architect, engineer, reviewer],
    max_round=10
)

# All agents use the dexo cluster for inference
# No OpenAI API key required!
```

## Configuration

### Environment Variables

```bash
# dexo home directory
export DEXO_HOME=~/.dexo

# Custom model directory
export DEXO_MODELS_DIR=~/models

# Enable image models
export DEXO_ENABLE_IMAGE_MODELS=true

# Enable distributed tracing
export DEXO_TRACING_ENABLED=true

# Custom namespace for cluster isolation
export EXO_LIBP2P_NAMESPACE=my-private-cluster
```

### Resource Thresholds

Set minimum thresholds for continuous learning governance:

```python
from exo.autogen.swarm_coordinator import ResourceThreshold

# Conservative (for laptops)
threshold = ResourceThreshold(
    min_memory_gb=4.0,
    min_cpu_cores=2,
    min_gpu_memory_gb=0.0,
    min_network_bandwidth_mbps=10.0
)

# High-performance (for workstations)
threshold = ResourceThreshold(
    min_memory_gb=32.0,
    min_cpu_cores=16,
    min_gpu_memory_gb=24.0,
    min_network_bandwidth_mbps=1000.0
)
```

## Advanced Usage

### Multiple Nodes

Run dexo on multiple machines for distributed inference:

```bash
# Machine 1 (master + worker)
dexo

# Machine 2 (worker only)
dexo-worker

# Machine 3 (master only - coordination)
dexo-master --no-worker

# All nodes auto-discover and form a cluster
```

### TUI on Remote Cluster

```bash
# Monitor remote cluster
dexo-tui --api-url http://cluster-master:52415
```

### SWE-Agent with Custom Model

```bash
# Use a specific model for code generation
dexo-swe generate "Create a binary search function" \
    --model "mlx-community/Qwen-2.5-Coder-7B-Instruct-4bit" \
    --language python
```

## Troubleshooting

### TUI not connecting
```bash
# Check if API is running
curl http://localhost:52415/state

# Check logs
tail -f ~/.dexo/dexo.log
```

### Swarm coordinator threshold issues
```python
# Check why a node was rejected
coordinator.register_node(node)
# Look for warning: "Node X does not meet minimum resource thresholds"

# Adjust thresholds
coordinator.set_resource_threshold(
    ResourceThreshold(
        min_memory_gb=2.0,  # Lower threshold
        min_cpu_cores=1,
    )
)
```

### Autogen integration not working
```bash
# Install autogen2
pip install 'ag2[openai]>=0.8.0'

# Verify installation
python -c "import autogen; print('AG2 available')"
```

## Next Steps

1. **Explore the TUI**: Run `dexo-tui` and monitor your cluster
2. **Try SWE-Agent**: Analyze and generate code with `dexo-swe`
3. **Setup Swarm**: Configure resource governance for continuous learning
4. **Multi-Agent**: Create reasoning teams with Autogen2 integration
5. **Scale Up**: Add more nodes to increase capacity

## Documentation

- [NEW_FEATURES.md](docs/NEW_FEATURES.md) - Detailed feature documentation
- [DEXO_TRANSFORMATION.md](DEXO_TRANSFORMATION.md) - Transformation overview
- [README.md](README.md) - Main documentation
- [AGENTS.md](AGENTS.md) - For AI coding agents

## Support

- Discord: https://discord.gg/TJ4P57arEm
- X/Twitter: https://x.com/darbotlabs
- Issues: https://github.com/darbotlabs/dexo/issues
