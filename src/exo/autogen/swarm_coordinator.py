"""Autogen2 Swarm Coordinator for dexo - Resource swarm coordination and governance."""

import asyncio
from dataclasses import dataclass, field
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field


class ResourceThreshold(BaseModel):
    """Minimum resource thresholds for continuous learning."""

    min_memory_gb: float = 4.0
    min_cpu_cores: int = 2
    min_gpu_memory_gb: float = 0.0
    min_network_bandwidth_mbps: float = 10.0


class SwarmNode(BaseModel):
    """Represents a node in the swarm."""

    node_id: str
    available_memory_gb: float
    cpu_cores: int
    gpu_memory_gb: float = 0.0
    network_bandwidth_mbps: float
    status: str = "idle"  # idle, busy, learning, error
    capabilities: list[str] = Field(default_factory=list)


class LearningTask(BaseModel):
    """Represents a continuous learning task."""

    task_id: str
    task_type: str  # training, fine-tuning, inference, evaluation
    priority: int = 0
    required_resources: ResourceThreshold
    assigned_nodes: list[str] = Field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed


@dataclass
class SwarmCoordinator:
    """Coordinates resource allocation and continuous learning across the dexo cluster."""

    resource_threshold: ResourceThreshold = field(
        default_factory=ResourceThreshold
    )
    nodes: dict[str, SwarmNode] = field(default_factory=dict)
    tasks: dict[str, LearningTask] = field(default_factory=dict)

    def register_node(self, node: SwarmNode) -> bool:
        """Register a node in the swarm."""
        logger.info(f"Registering node: {node.node_id}")

        # Check if node meets minimum thresholds
        if not self._meets_threshold(node):
            logger.warning(
                f"Node {node.node_id} does not meet minimum resource thresholds"
            )
            return False

        self.nodes[node.node_id] = node
        logger.info(
            f"Node {node.node_id} registered successfully. Total nodes: {len(self.nodes)}"
        )
        return True

    def _meets_threshold(self, node: SwarmNode) -> bool:
        """Check if node meets minimum resource thresholds."""
        return (
            node.available_memory_gb >= self.resource_threshold.min_memory_gb
            and node.cpu_cores >= self.resource_threshold.min_cpu_cores
            and node.gpu_memory_gb >= self.resource_threshold.min_gpu_memory_gb
            and node.network_bandwidth_mbps
            >= self.resource_threshold.min_network_bandwidth_mbps
        )

    def unregister_node(self, node_id: str) -> bool:
        """Unregister a node from the swarm."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            logger.info(f"Node {node_id} unregistered. Total nodes: {len(self.nodes)}")
            return True
        return False

    def submit_learning_task(self, task: LearningTask) -> str:
        """Submit a learning task to the swarm."""
        logger.info(f"Submitting learning task: {task.task_id}")

        # Store task
        self.tasks[task.task_id] = task

        # Try to assign nodes
        self._assign_nodes_to_task(task.task_id)

        return task.task_id

    def _assign_nodes_to_task(self, task_id: str) -> bool:
        """Assign nodes to a learning task based on resource requirements."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        # Find suitable nodes
        suitable_nodes = [
            node
            for node in self.nodes.values()
            if node.status == "idle" and self._node_suitable_for_task(node, task)
        ]

        if not suitable_nodes:
            logger.warning(f"No suitable nodes found for task {task_id}")
            return False

        # Sort by priority (could use more sophisticated algorithm)
        suitable_nodes.sort(
            key=lambda n: (n.available_memory_gb, n.cpu_cores), reverse=True
        )

        # Assign best node (or multiple nodes for distributed tasks)
        assigned_node = suitable_nodes[0]
        task.assigned_nodes = [assigned_node.node_id]
        task.status = "assigned"
        assigned_node.status = "busy"

        logger.info(f"Task {task_id} assigned to node {assigned_node.node_id}")
        return True

    def _node_suitable_for_task(self, node: SwarmNode, task: LearningTask) -> bool:
        """Check if a node is suitable for a task."""
        return (
            node.available_memory_gb >= task.required_resources.min_memory_gb
            and node.cpu_cores >= task.required_resources.min_cpu_cores
            and node.gpu_memory_gb >= task.required_resources.min_gpu_memory_gb
            and node.network_bandwidth_mbps
            >= task.required_resources.min_network_bandwidth_mbps
        )

    def get_swarm_status(self) -> dict[str, Any]:
        """Get current status of the swarm."""
        total_nodes = len(self.nodes)
        idle_nodes = sum(1 for n in self.nodes.values() if n.status == "idle")
        busy_nodes = sum(1 for n in self.nodes.values() if n.status == "busy")
        learning_nodes = sum(1 for n in self.nodes.values() if n.status == "learning")

        pending_tasks = sum(1 for t in self.tasks.values() if t.status == "pending")
        running_tasks = sum(1 for t in self.tasks.values() if t.status == "running")
        completed_tasks = sum(
            1 for t in self.tasks.values() if t.status == "completed"
        )

        return {
            "total_nodes": total_nodes,
            "idle_nodes": idle_nodes,
            "busy_nodes": busy_nodes,
            "learning_nodes": learning_nodes,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "completed_tasks": completed_tasks,
            "resource_threshold": self.resource_threshold.model_dump(),
        }

    async def run_continuous_learning(self) -> None:
        """Run continuous learning loop."""
        logger.info("Starting continuous learning coordinator")

        while True:
            try:
                # Check for pending tasks and assign them
                pending_tasks = [
                    task for task in self.tasks.values() if task.status == "pending"
                ]

                for task in pending_tasks:
                    self._assign_nodes_to_task(task.task_id)

                # Monitor task progress
                await self._monitor_tasks()

                # Wait before next iteration
                await asyncio.sleep(5.0)

            except Exception as e:
                logger.error(f"Error in continuous learning loop: {e}")
                await asyncio.sleep(10.0)

    async def _monitor_tasks(self) -> None:
        """Monitor running tasks."""
        running_tasks = [
            task for task in self.tasks.values() if task.status == "running"
        ]

        for task in running_tasks:
            # In a real implementation, check task progress from nodes
            # For now, just log
            logger.debug(
                f"Task {task.task_id} running on nodes: {task.assigned_nodes}"
            )

    def set_resource_threshold(self, threshold: ResourceThreshold) -> None:
        """Update resource thresholds for governance."""
        logger.info(f"Updating resource thresholds: {threshold}")
        self.resource_threshold = threshold

        # Re-evaluate nodes against new thresholds
        nodes_to_remove = [
            node_id
            for node_id, node in self.nodes.items()
            if not self._meets_threshold(node)
        ]

        for node_id in nodes_to_remove:
            logger.warning(
                f"Node {node_id} no longer meets thresholds, removing from swarm"
            )
            self.unregister_node(node_id)
