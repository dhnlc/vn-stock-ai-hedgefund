"""Base agent utilities built on top of the Agno framework.

This module defines :class:`BaseAgent`, a lightweight wrapper around
:class:`agno.agent.Agent`. The wrapper simplifies instantiation by enforcing
common configuration used across this project (Markdown output enabled, strict
JSON mode off, etc.).
"""

import asyncio
from typing import Any, Sequence

from agno.agent import Agent


class BaseAgent(Agent):
    """Base class for all project agents.

    Subclasses should extend this class instead of the raw ``agno.agent.Agent``
    to inherit the standard configuration. Additional convenience methods for
    message formatting, logging or shared memory access can be added here to
    reduce duplication.
    """

    def __init__(
        self,
        *,
        model: Any,
        tools: Sequence[Any] | None = None,
        instructions: str | None = None,
        markdown: bool = True,
        name: str | None = None,
        agent_id: str | None = None,
        description: str | None = None,
        monitoring: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a new :class:`BaseAgent`.

        Args:
            model: The underlying language model implementation accepted by
                Agno (e.g. an Anthropic Claude wrapper, OpenAI GPT wrapper,
                etc.). Consult the Agno docs for supported models.
            tools: Optional iterable of Agno tool instances to be attached to
                this agent.
            instructions: Optional system instructions governing the behaviour
                of the agent.
            markdown: When *True* the agent will emit Markdown formatted
                content. Defaults to *True*.
            **kwargs: Additional keyword arguments forwarded to the Agno
                :class:`Agent` constructor.
        """
        super().__init__(
            model=model,
            tools=list(tools) if tools is not None else None,
            instructions=instructions,
            markdown=markdown,
            name=name,
            agent_id=agent_id,
            description=description,
            monitoring=monitoring,
            **kwargs,
        )

    async def arun(self, *args: Any, **kwargs: Any) -> Any:
        """Async wrapper around Agent.run using a thread executor.

        This prevents blocking the event loop while leveraging the synchronous
        Agno Agent API under the hood.
        """
        return await asyncio.to_thread(super().run, *args, **kwargs)
