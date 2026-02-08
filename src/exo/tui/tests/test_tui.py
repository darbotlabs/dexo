"""Tests for dexo TUI components."""

import pytest
from textual.app import App

from exo.tui.main import DexoTUI, ClusterPanel, ModelsPanel


@pytest.fixture
def tui_app() -> DexoTUI:
    """Create a TUI app instance for testing."""
    return DexoTUI(api_url="http://localhost:52415")


def test_tui_initialization(tui_app: DexoTUI) -> None:
    """Test TUI app initializes correctly."""
    assert tui_app.api_url == "http://localhost:52415"
    assert isinstance(tui_app, App)


def test_cluster_panel_initialization() -> None:
    """Test cluster panel initializes correctly."""
    panel = ClusterPanel(api_url="http://localhost:52415")
    assert panel.api_url == "http://localhost:52415"


def test_models_panel_initialization() -> None:
    """Test models panel initializes correctly."""
    panel = ModelsPanel(api_url="http://localhost:52415")
    assert panel.api_url == "http://localhost:52415"


@pytest.mark.asyncio
async def test_cluster_panel_status_update() -> None:
    """Test cluster panel can handle status updates."""
    panel = ClusterPanel(api_url="http://localhost:52415")
    panel.cluster_status = {
        "nodes": {"node1": {"status": "active"}},
        "instances": {},
    }
    # Should not raise any exceptions
    await panel.render_cluster_status()
