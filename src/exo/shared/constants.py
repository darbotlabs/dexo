import os
import sys
from pathlib import Path

_DEXO_HOME_ENV = os.environ.get("DEXO_HOME", None)


def _get_xdg_dir(env_var: str, fallback: str) -> Path:
    """Get XDG directory, prioritising DEXO_HOME environment variable if its set. On non-Linux platforms, default to ~/.dexo."""

    if _DEXO_HOME_ENV is not None:
        return Path.home() / _DEXO_HOME_ENV

    if sys.platform != "linux":
        return Path.home() / ".dexo"

    xdg_value = os.environ.get(env_var, None)
    if xdg_value is not None:
        return Path(xdg_value) / "dexo"
    return Path.home() / fallback / "dexo"


DEXO_CONFIG_HOME = _get_xdg_dir("XDG_CONFIG_HOME", ".config")
DEXO_DATA_HOME = _get_xdg_dir("XDG_DATA_HOME", ".local/share")
DEXO_CACHE_HOME = _get_xdg_dir("XDG_CACHE_HOME", ".cache")

# Models directory (data)
_DEXO_MODELS_DIR_ENV = os.environ.get("DEXO_MODELS_DIR", None)
DEXO_MODELS_DIR = (
    DEXO_DATA_HOME / "models"
    if _DEXO_MODELS_DIR_ENV is None
    else Path.home() / _DEXO_MODELS_DIR_ENV
)

# Log files (data/logs or cache)
DEXO_LOG = DEXO_CACHE_HOME / "dexo.log"
DEXO_TEST_LOG = DEXO_CACHE_HOME / "dexo_test.log"

# Identity (config)
DEXO_NODE_ID_KEYPAIR = DEXO_CONFIG_HOME / "node_id.keypair"
DEXO_CONFIG_FILE = DEXO_CONFIG_HOME / "config.toml"

# libp2p topics for event forwarding
LIBP2P_LOCAL_EVENTS_TOPIC = "worker_events"
LIBP2P_GLOBAL_EVENTS_TOPIC = "global_events"
LIBP2P_ELECTION_MESSAGES_TOPIC = "election_message"
LIBP2P_COMMANDS_TOPIC = "commands"

DEXO_MAX_CHUNK_SIZE = 512 * 1024

DEXO_IMAGE_CACHE_DIR = DEXO_CACHE_HOME / "images"
DEXO_TRACING_CACHE_DIR = DEXO_CACHE_HOME / "traces"

DEXO_ENABLE_IMAGE_MODELS = (
    os.getenv("DEXO_ENABLE_IMAGE_MODELS", "false").lower() == "true"
)

DEXO_TRACING_ENABLED = os.getenv("DEXO_TRACING_ENABLED", "false").lower() == "true"

# Backward compatibility aliases (deprecated)
EXO_CONFIG_HOME = DEXO_CONFIG_HOME
EXO_DATA_HOME = DEXO_DATA_HOME
EXO_CACHE_HOME = DEXO_CACHE_HOME
EXO_MODELS_DIR = DEXO_MODELS_DIR
EXO_LOG = DEXO_LOG
EXO_TEST_LOG = DEXO_TEST_LOG
EXO_NODE_ID_KEYPAIR = DEXO_NODE_ID_KEYPAIR
EXO_CONFIG_FILE = DEXO_CONFIG_FILE
EXO_MAX_CHUNK_SIZE = DEXO_MAX_CHUNK_SIZE
EXO_IMAGE_CACHE_DIR = DEXO_IMAGE_CACHE_DIR
EXO_TRACING_CACHE_DIR = DEXO_TRACING_CACHE_DIR
EXO_ENABLE_IMAGE_MODELS = DEXO_ENABLE_IMAGE_MODELS
EXO_TRACING_ENABLED = DEXO_TRACING_ENABLED
