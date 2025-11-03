import os
import tiktoken
from typing import Optional, Dict, List
from openrouter_client import get_client


def count_tokens(string: str) -> int:
    """Count tokens in a string using tiktoken"""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def estimate_cost(string: str, model: str) -> float:
    """
    Estimate cost for OpenRouter API call.
    Note: OpenRouter pricing varies by model - this is an estimate.
    """
    num_tokens = count_tokens(string)
    print(f"{num_tokens} tokens")

    # Rough estimate - actual costs vary by model on OpenRouter
    # Check https://openrouter.ai/models for current pricing
    token_packages = num_tokens / 1000
    cost_per_prompt_package = 0.01  # Conservative estimate

    prompt_cost = cost_per_prompt_package * token_packages
    return prompt_cost


def call_openrouter(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 1.0,
    max_tokens: Optional[int] = None
) -> str:
    """
    Call OpenRouter API with chat messages.
    Now uses unified OpenRouterClient.

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model identifier (e.g., 'anthropic/claude-3.5-sonnet')
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text response
    """
    client = get_client()
    return client.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )


def gpt4(instruction, context, prompt, skip_cost_check=False):
    """
    Legacy function name - now uses OpenRouter instead of OpenAI.

    Args:
        instruction: System instruction/role
        context: Additional context for the assistant
        prompt: User prompt
        skip_cost_check: Skip the cost confirmation if True

    Returns:
        Generated response text
    """
    # Get environment variables
    accept = os.getenv("gpt_override_cost_check", "False").lower() == "true"
    model = os.getenv('openrouter_model', 'anthropic/claude-3.5-sonnet')

    full_text = prompt + instruction + context

    # Calculate estimated cost
    cost = estimate_cost(full_text, model)

    # Check if the user accepts
    cost_accept = accept or skip_cost_check

    if not cost_accept:
        ask = input(f"Prompt will cost approximately ${cost:.4f} to send. Y/N? ").lower()
        cost_accept = ask == "y"

    # If the user accepts the cost, send the request
    if cost_accept:
        messages = [
            {"role": "system", "content": instruction},
            {"role": "assistant", "content": f"The context provided: \n{context}"},
            {"role": "user", "content": prompt}
        ]

        try:
            answer = call_openrouter(messages, model=model)
            return answer
        except Exception as e:
            print(f"Error calling OpenRouter: {e}")
            return f"Error: {str(e)}"
    else:
        return "Declined Charges"


def generate_with_feedback(
    instruction: str,
    context: str,
    prompt: str,
    relevance_data: List[Dict],
    model: Optional[str] = None
) -> str:
    """
    Enhanced generation function for Generator mode with relevance feedback.

    Args:
        instruction: System instruction
        context: Context from ChromaDB
        prompt: User's generation request
        relevance_data: List of dicts with title, relevance, tags
        model: Model to use (optional)

    Returns:
        Generated content
    """
    model = model or os.getenv('openrouter_model', 'anthropic/claude-3.5-sonnet')

    # Build enhanced system message with relevance awareness
    top_relevant = [item for item in relevance_data if item['relevance'] > 0.7][:5]

    relevance_context = ""
    if top_relevant:
        relevance_context = "\n\nMOST RELEVANT EXISTING ELEMENTS:\n"
        for item in top_relevant:
            relevance_context += f"- {item['title']} (relevance: {item['relevance']:.2f})\n"

    enhanced_instruction = f"""{instruction}

{relevance_context}

QUALITY GUIDELINES:
1. Integrate smoothly with the most relevant existing elements
2. Maintain consistent tone and style with existing lore
3. Create meaningful connections and references
4. Avoid contradicting established facts
5. Match the depth and detail of existing entries
"""

    messages = [
        {"role": "system", "content": enhanced_instruction},
        {"role": "user", "content": context + "\n\n" + prompt}
    ]

    try:
        answer = call_openrouter(messages, model=model, temperature=0.9)
        return answer
    except Exception as e:
        print(f"Error in enhanced generation: {e}")
        return f"Error: {str(e)}"
