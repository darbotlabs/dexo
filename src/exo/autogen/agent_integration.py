"""Autogen2 Agent Integration for dexo - Connects AG2 agents with dexo cluster."""

from typing import Any

from loguru import logger

try:
    # Try importing ag2 (autogen2)
    import autogen  # type: ignore[import-untyped]

    AG2_AVAILABLE = True
except ImportError:
    AG2_AVAILABLE = False
    logger.warning(
        "ag2 (autogen2) not available. Install with: pip install 'ag2[openai]'"
    )


class DexoAutogenBridge:
    """Bridge between dexo cluster and Autogen2 agents."""

    def __init__(self, dexo_api_url: str = "http://localhost:52415") -> None:
        self.dexo_api_url = dexo_api_url
        self.agents: dict[str, Any] = {}

        if not AG2_AVAILABLE:
            logger.error("Autogen2 is not available. Cannot initialize bridge.")
            return

        logger.info(f"Initializing dexo-Autogen2 bridge with API: {dexo_api_url}")

    def create_assistant_agent(
        self, name: str, system_message: str, model: str = "gpt-4"
    ) -> Any | None:
        """Create an Autogen2 assistant agent that uses dexo cluster."""
        if not AG2_AVAILABLE:
            logger.error("Autogen2 not available")
            return None

        # Configure to use dexo API endpoint
        llm_config = {
            "config_list": [
                {
                    "model": model,
                    "base_url": f"{self.dexo_api_url}/v1",
                    "api_key": "dexo-key",  # dexo doesn't require real key
                }
            ],
            "temperature": 0.7,
        }

        agent = autogen.AssistantAgent(
            name=name, system_message=system_message, llm_config=llm_config
        )

        self.agents[name] = agent
        logger.info(f"Created assistant agent: {name}")
        return agent

    def create_user_proxy_agent(
        self, name: str, human_input_mode: str = "NEVER"
    ) -> Any | None:
        """Create a user proxy agent for interaction."""
        if not AG2_AVAILABLE:
            logger.error("Autogen2 not available")
            return None

        agent = autogen.UserProxyAgent(
            name=name,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply=10,
            code_execution_config={"work_dir": "coding", "use_docker": False},
        )

        self.agents[name] = agent
        logger.info(f"Created user proxy agent: {name}")
        return agent

    def create_group_chat(
        self, agents: list[Any], max_round: int = 10
    ) -> tuple[Any, Any] | tuple[None, None]:
        """Create a group chat with multiple agents."""
        if not AG2_AVAILABLE:
            logger.error("Autogen2 not available")
            return None, None

        groupchat = autogen.GroupChat(
            agents=agents, messages=[], max_round=max_round
        )

        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config={
                "config_list": [
                    {
                        "model": "gpt-4",
                        "base_url": f"{self.dexo_api_url}/v1",
                        "api_key": "dexo-key",
                    }
                ]
            },
        )

        logger.info(f"Created group chat with {len(agents)} agents")
        return groupchat, manager

    async def run_agent_conversation(
        self, initiator: Any, recipient: Any, message: str
    ) -> None:
        """Run a conversation between two agents."""
        if not AG2_AVAILABLE:
            logger.error("Autogen2 not available")
            return

        logger.info(f"Starting conversation: {initiator.name} -> {recipient.name}")
        initiator.initiate_chat(recipient, message=message)


def create_dexo_reasoning_team(
    dexo_api_url: str = "http://localhost:52415",
) -> tuple[Any, Any, Any] | tuple[None, None, None]:
    """Create a reasoning team of agents for autonomous problem solving."""
    if not AG2_AVAILABLE:
        return None, None, None

    bridge = DexoAutogenBridge(dexo_api_url)

    # Create specialized agents
    architect = bridge.create_assistant_agent(
        name="Architect",
        system_message="""You are a software architect. Your role is to:
        1. Analyze requirements and design system architecture
        2. Break down complex problems into manageable components
        3. Define interfaces and data flows
        4. Ensure scalability and maintainability""",
    )

    engineer = bridge.create_assistant_agent(
        name="Engineer",
        system_message="""You are a software engineer. Your role is to:
        1. Implement solutions based on architectural designs
        2. Write clean, efficient, and well-tested code
        3. Follow best practices and coding standards
        4. Handle edge cases and error conditions""",
    )

    reviewer = bridge.create_assistant_agent(
        name="Reviewer",
        system_message="""You are a code reviewer. Your role is to:
        1. Review code for correctness and quality
        2. Identify bugs, security issues, and performance problems
        3. Suggest improvements and optimizations
        4. Ensure code meets requirements and standards""",
    )

    return architect, engineer, reviewer
