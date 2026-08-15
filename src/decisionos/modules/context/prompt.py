from __future__ import annotations

from typing import List, Optional, Dict, Any

from decisionos.modules.rag.schemas import RagSearchResult, RagSearchResponse
from decisionos.modules.context.service import ContextBuilder


class PromptTemplate:
    """Represents a prompt template with versioning and placeholders.

    Templates define the structure of a prompt with named placeholders
    that can be filled at runtime. Templates support versioning so that
    prompt changes can be tracked and rolled back if needed.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        system_instructions: str | None = None,
        placeholder_mapping: dict[str, str] | None = None,
    ) -> None:
        self.name = name
        self.version = version
        self.system_instructions = system_instructions or ""
        self.placeholder_mapping = placeholder_mapping or {}

    def render(
        self,
        **placeholders: Any,
    ) -> str:
        """Render the prompt template with the given placeholders.

        Fills in named placeholders in the template. Placeholders are
        referenced as {placeholder_name} in the template string.

        Raises:
            KeyError: If a required placeholder is not provided
        """
        template = self._get_template()
        rendered = template

        for placeholder_name, placeholder_value in self.placeholder_mapping.items():
            placeholder_key = f"{{{placeholder_name}}}"
            if placeholder_key in rendered:
                rendered = rendered.replace(placeholder_key, str(placeholder_value))

        # Fill any remaining {placeholders} from the kwargs
        import re
        placeholder_pattern = r"\{(\w+)\}"
        found_placeholders = re.findall(placeholder_pattern, rendered)

        for ph in found_placeholders:
            if ph in placeholders:
                rendered = rendered.replace(f"{{{ph}}}", str(placeholders[ph]))
            elif ph in self.placeholder_mapping:
                # Already handled above
                pass
            else:
                # Leave as-is or raise
                raise KeyError(
                    f"Required placeholder {{ {ph} }} not provided "
                    f"and not defined in template mapping"
                )

        return rendered

    def _get_template(self) -> str:
        """Get the template string.

        Subclasses or implementations should define the actual template
        content. Default is a minimal template.
        """
        return self.system_instructions or ""


class PromptBuilder:
    """Builds the final prompt for an LLM request.

    Orchestrates context building from RAG results, template rendering,
    and prompt composition following the flow:
        RAGResult[] → ContextBuilder → Context → PromptTemplate → PromptBuilder → FinalPrompt
    """

    def __init__(
        self,
        context_builder: ContextBuilder | None = None,
        template: PromptTemplate | None = None,
        max_tokens: int = 4000,
    ) -> None:
        self.context_builder = context_builder or ContextBuilder(max_tokens=max_tokens)
        self.template = template or self._default_template()

    def _default_template(self) -> PromptTemplate:
        """Create a default prompt template.

        Returns a template suitable for most QA/use-case scenarios.
        """
        return PromptTemplate(
            name="default",
            version="1.0.0",
            system_instructions="You are a helpful assistant. Answer the user's question based on the context provided below. If the context doesn't contain the answer, say so clearly.",
            placeholder_mapping={
                "context": "CONTEXT_PLACEHOLDER",
                "user_request": "USER_REQUEST_PLACEHOLDER",
            },
        )

    def build(
        self,
        rag_results: list[RagSearchResult],
        user_request: str,
    ) -> dict[str, Any]:
        """Build the final prompt from RAG results and user request.

        Full pipeline:
            1. ContextBuilder builds bounded context from chunks
            2. Template renders with context and user request embedded

        Returns:
            Dict with 'prompt' (the final string) and 'context_info' (metadata)
        """
        # Step 1: Build context from RAG results
        _, context_info = self.context_builder.build(rag_results)

        # Step 2: Render the template
        # Extract the context chunks from the info
        chunks_info = context_info.get("chunks", [])

        # Build context string from chunks
        context_parts: list[str] = []
        for chunk in chunks_info:
            part = f"[Chunk {chunk.get('chunk_index', '?')}] {chunk.get('content', '')}"
            context_parts.append(part)

        context_string = "\n\n".join(context_parts) if context_parts else ""

        # Render template with placeholders
        rendered_prompt = self.template.render(
            context=context_string,
            user_request=user_request,
        )

        return {
            "prompt": rendered_prompt,
            "context_info": context_info,
            "template_name": self.template.name,
            "template_version": self.template.version,
        }

    def set_template(self, template: PromptTemplate) -> None:
        """Set a custom prompt template.

        Args:
            template: The PromptTemplate to use
        """
        self.template = template

    def set_context_builder(self, builder: ContextBuilder) -> None:
        """Set a custom context builder.

        Args:
            builder: The ContextBuilder to use
        """
        self.context_builder = builder