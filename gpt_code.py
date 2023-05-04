import os
import openai
import tiktoken


def gpt4_cost(string: str) -> float:
    # Set the API key for OpenAI
    openai.api_key = os.getenv('openai_api_key')
    encoding = tiktoken.get_encoding("cl100k_base")

    # Calculate the number of tokens
    num_tokens = len(encoding.encode(string))
    print(f"{num_tokens} tokens")

    # Calculate the cost of sending the string to the API
    token_packages = num_tokens / 1000
    cost_per_prompt_package = .03
    prompt_cost = cost_per_prompt_package * token_packages

    return prompt_cost


def gpt4(instruction, context, prompt):
    # Get the environment variables for GPT-4
    accept = os.getenv("gpt_override_cost_check")
    openai.api_key = os.getenv('openai_api_key')
    openai_model = os.getenv('openai_model')

    full_text = prompt + instruction + context

    # Calculate the cost of sending the text to GPT-4
    cost = gpt4_cost(full_text)

    # Check if the user accepts
    if accept:
        print(cost)
        cost_accept = True
    else:
        ask = input(f"Prompt will cost {cost} to send. Y/N?").lower()
        cost_accept = ask == "y"

    # If the user accepts the cost, send the request
    if cost_accept:
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "assistant", "content": f"The prompt from which this story was made was: \n{context}"},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
        )
        # Extract and return the answer
        answer = response.choices[0]['message']['content']
        return answer
    else:
        return "Declined Charges"
