from typing import Optional
from strands.models import BedrockModel


def get_bedrock_agent_model(
    model_id: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature: float = 1,
    max_tokens: int = 24000,
    thinking: bool = False,
    budget_tokens: Optional[int] = None
):
    additional_request_fields = {}
    
    if thinking:
        additional_request_fields["thinking"] = {
            "type": "enabled",
            "budget_tokens": budget_tokens if budget_tokens else 1024
        }
        additional_request_fields["anthropic_beta"] = [
            "interleaved-thinking-2025-05-14",
            "fine-grained-tool-streaming-2025-05-14"
        ]
    
    agent_model = BedrockModel(
        model_id=model_id,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_tools="default",
        additional_request_fields=additional_request_fields if additional_request_fields else None
    )
    return agent_model
