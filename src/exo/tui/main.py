"""Terminal User Interface for dexo - Main application."""

import argparse
import asyncio
from typing import Any

import httpx
from loguru import logger
from rich.console import Console
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Label, Static, TabbedContent, TabPane

console = Console()


class ClusterPanel(Static):
    """Panel showing cluster status and nodes."""

    cluster_status: reactive[dict[str, Any]] = reactive({})

    def __init__(self, api_url: str) -> None:
        super().__init__()
        self.api_url = api_url

    def compose(self) -> ComposeResult:
        yield Label("Cluster Status", id="cluster-title")
        yield Static("Loading cluster information...", id="cluster-content")

    async def update_cluster_status(self) -> None:
        """Fetch and update cluster status from API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/state", timeout=5.0)
                if response.status_code == 200:
                    self.cluster_status = response.json()
                    await self.render_cluster_status()
        except Exception as e:
            logger.error(f"Failed to fetch cluster status: {e}")
            self.query_one("#cluster-content", Static).update(f"Error: {e}")

    async def render_cluster_status(self) -> None:
        """Render cluster status information."""
        status = self.cluster_status
        if not status:
            return

        nodes = status.get("nodes", {})
        instances = status.get("instances", {})

        content = f"""
[bold]Nodes:[/bold] {len(nodes)}
[bold]Model Instances:[/bold] {len(instances)}

[bold]Connected Nodes:[/bold]
"""
        for node_id, node_info in nodes.items():
            content += f"  • {node_id[:12]}... - {node_info.get('status', 'unknown')}\n"

        self.query_one("#cluster-content", Static).update(content)


class ModelsPanel(Static):
    """Panel for managing models."""

    models: reactive[list[dict[str, Any]]] = reactive([])

    def __init__(self, api_url: str) -> None:
        super().__init__()
        self.api_url = api_url

    def compose(self) -> ComposeResult:
        yield Label("Available Models", id="models-title")
        yield Static("Loading models...", id="models-content")

    async def update_models(self) -> None:
        """Fetch and update models from API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/models", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    self.models = data.get("data", [])
                    await self.render_models()
        except Exception as e:
            logger.error(f"Failed to fetch models: {e}")
            self.query_one("#models-content", Static).update(f"Error: {e}")

    async def render_models(self) -> None:
        """Render models list."""
        if not self.models:
            self.query_one("#models-content", Static).update("No models available")
            return

        content = "[bold]Models:[/bold]\n\n"
        for model in self.models[:10]:  # Show first 10
            content += f"  • {model.get('id', 'unknown')}\n"

        if len(self.models) > 10:
            content += f"\n... and {len(self.models) - 10} more"

        self.query_one("#models-content", Static).update(content)


class ChatPanel(Static):
    """Panel for chat interface."""

    def compose(self) -> ComposeResult:
        yield Label("Chat Interface", id="chat-title")
        yield Static(
            "Chat interface coming soon...\nUse the web dashboard at http://localhost:52415 for now.",
            id="chat-content",
        )


class LogsPanel(Static):
    """Panel for viewing logs."""

    def compose(self) -> ComposeResult:
        yield Label("System Logs", id="logs-title")
        yield Static("Logs display coming soon...", id="logs-content")


class DexoTUI(App[None]):
    """Terminal User Interface for dexo cluster management."""

    CSS = """
    Screen {
        background: $surface;
    }

    #cluster-title, #models-title, #chat-title, #logs-title {
        color: $accent;
        text-style: bold;
        padding: 1;
    }

    #cluster-content, #models-content, #chat-content, #logs-content {
        padding: 1;
        height: 100%;
    }

    TabbedContent {
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def __init__(self, api_url: str = "http://localhost:52415") -> None:
        super().__init__()
        self.api_url = api_url
        self.cluster_panel: ClusterPanel | None = None
        self.models_panel: ModelsPanel | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with TabbedContent(initial="cluster"):
            with TabPane("Cluster", id="cluster"):
                self.cluster_panel = ClusterPanel(self.api_url)
                yield self.cluster_panel
            with TabPane("Models", id="models"):
                self.models_panel = ModelsPanel(self.api_url)
                yield self.models_panel
            with TabPane("Chat", id="chat"):
                yield ChatPanel()
            with TabPane("Logs", id="logs"):
                yield LogsPanel()
        yield Footer()

    async def on_mount(self) -> None:
        """Called when app starts."""
        self.title = "dexo - Decentralized Autonomous Reasoning Engine"
        self.sub_title = f"Connected to {self.api_url}"
        # Start periodic updates
        self.set_interval(5.0, self.refresh_data)
        # Initial data load
        await self.refresh_data()

    async def refresh_data(self) -> None:
        """Refresh data from API."""
        if self.cluster_panel:
            await self.cluster_panel.update_cluster_status()
        if self.models_panel:
            await self.models_panel.update_models()

    def action_refresh(self) -> None:
        """Handle refresh action."""
        asyncio.create_task(self.refresh_data())

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


def main() -> None:
    """Main entry point for dexo TUI."""
    parser = argparse.ArgumentParser(
        description="dexo Terminal User Interface - Decentralized Autonomous Reasoning Engine"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:52415",
        help="URL of dexo API (default: http://localhost:52415)",
    )
    args = parser.parse_args()

    app = DexoTUI(api_url=args.api_url)
    app.run()


if __name__ == "__main__":
    main()
