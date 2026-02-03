"""Tests for Autogen integration."""

import pytest

from exo.autogen.swarm_coordinator import (
    LearningTask,
    ResourceThreshold,
    SwarmCoordinator,
    SwarmNode,
)


@pytest.fixture
def coordinator() -> SwarmCoordinator:
    """Create a SwarmCoordinator instance for testing."""
    return SwarmCoordinator(
        resource_threshold=ResourceThreshold(
            min_memory_gb=4.0,
            min_cpu_cores=2,
            min_gpu_memory_gb=0.0,
            min_network_bandwidth_mbps=10.0,
        )
    )


@pytest.fixture
def valid_node() -> SwarmNode:
    """Create a valid node that meets thresholds."""
    return SwarmNode(
        node_id="node-1",
        available_memory_gb=16.0,
        cpu_cores=8,
        gpu_memory_gb=8.0,
        network_bandwidth_mbps=1000.0,
    )


@pytest.fixture
def invalid_node() -> SwarmNode:
    """Create a node that doesn't meet thresholds."""
    return SwarmNode(
        node_id="node-2",
        available_memory_gb=1.0,  # Below threshold
        cpu_cores=1,  # Below threshold
        gpu_memory_gb=0.0,
        network_bandwidth_mbps=5.0,  # Below threshold
    )


def test_register_valid_node(coordinator: SwarmCoordinator, valid_node: SwarmNode) -> None:
    """Test registering a node that meets thresholds."""
    result = coordinator.register_node(valid_node)
    assert result is True
    assert valid_node.node_id in coordinator.nodes


def test_register_invalid_node(
    coordinator: SwarmCoordinator, invalid_node: SwarmNode
) -> None:
    """Test registering a node that doesn't meet thresholds."""
    result = coordinator.register_node(invalid_node)
    assert result is False
    assert invalid_node.node_id not in coordinator.nodes


def test_unregister_node(coordinator: SwarmCoordinator, valid_node: SwarmNode) -> None:
    """Test unregistering a node."""
    coordinator.register_node(valid_node)
    result = coordinator.unregister_node(valid_node.node_id)
    assert result is True
    assert valid_node.node_id not in coordinator.nodes


def test_submit_learning_task(
    coordinator: SwarmCoordinator, valid_node: SwarmNode
) -> None:
    """Test submitting a learning task."""
    coordinator.register_node(valid_node)

    task = LearningTask(
        task_id="task-1",
        task_type="training",
        priority=1,
        required_resources=ResourceThreshold(
            min_memory_gb=8.0,
            min_cpu_cores=4,
        ),
    )

    task_id = coordinator.submit_learning_task(task)
    assert task_id == "task-1"
    assert task_id in coordinator.tasks


def test_get_swarm_status(coordinator: SwarmCoordinator, valid_node: SwarmNode) -> None:
    """Test getting swarm status."""
    coordinator.register_node(valid_node)
    status = coordinator.get_swarm_status()

    assert status["total_nodes"] == 1
    assert status["idle_nodes"] == 1
    assert "resource_threshold" in status


def test_set_resource_threshold(
    coordinator: SwarmCoordinator, valid_node: SwarmNode
) -> None:
    """Test updating resource thresholds."""
    coordinator.register_node(valid_node)

    # Set higher thresholds that the node doesn't meet
    new_threshold = ResourceThreshold(
        min_memory_gb=32.0,  # Higher than node's 16GB
        min_cpu_cores=16,  # Higher than node's 8 cores
    )

    coordinator.set_resource_threshold(new_threshold)

    # Node should be removed
    assert valid_node.node_id not in coordinator.nodes
