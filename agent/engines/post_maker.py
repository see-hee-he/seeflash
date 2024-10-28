# Post Maker
# Objective: Takes in context from short and long term memory along with the recent posts and generates a post or reply to one of them

# Inputs:
# Short term memory output
# Long term memory output
# Retrieved posts from front of timeline

# Outputs:
# Text generated post /reply

# Things to consider:
# Database schema. Schemas for posts and how replies are classified.

import time
import requests
from typing import List, Dict
from engines.prompts import get_tweet_prompt

def generate_post(short_term_memory: str, long_term_memories: List[Dict], recent_posts: List[Dict], external_context, llm_api_key: str) -> str:
    """
    Generate a new post or reply based on short-term memory, long-term memories, and recent posts.
    
    Args:
        short_term_memory (str): Generated short-term memory
        long_term_memories (List[Dict]): Relevant long-term memories
        recent_posts (List[Dict]): Recent posts from the timeline
        openrouter_api_key (str): API key for OpenRouter
        your_site_url (str): Your site URL for OpenRouter API
        your_app_name (str): Your app name for OpenRouter API
    
    Returns:
        str: Generated post or reply
    """

    prompt = get_tweet_prompt(external_context, short_term_memory, long_term_memories, recent_posts)

    print(f"Generating post with prompt: {prompt}")

    #BASE MODEL TWEET GENERATION
    tries = 0
    max_tries = 3
    base_model_output = ""
    while tries < max_tries:
        try:
            response = requests.post(
                url="https://api.hyperbolic.xyz/v1/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {llm_api_key}",
                },
                json = {
                "prompt": prompt,
                "model": "meta-llama/Meta-Llama-3.1-405B",
                "max_tokens": 40,
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "stop":["<|im_end|>"]
                }
            )

            if response.status_code == 200:
                content = response.json()['choices'][0]['text']
                if content and content.strip():
                    print(f"Base model generated with response: {content}")
                    base_model_output = content
                    break
            # print(f"Attempt {tries + 1} failed. Status code: {response.status_code}")
            # print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error on attempt {tries + 1}: {str(e)}")
            tries += 1
            time.sleep(1)  # Add a small delay between retries

    time.sleep(5)

    # TAKES BASE MODEL OUTPUT AND CLEANS IT UP AND EXTRACT THE TWEET 
    tries = 0
    max_tries = 3
    while tries < max_tries:
        try:
            response = requests.post(
                url="https://api.hyperbolic.xyz/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {llm_api_key}",
                },
                json = {
                "messages": [
                    {
                        "role": "system",
        	            "content": "You analyze text and extract the Tweet in it. Don't make it more concise. You MUST only respond back with the Tweet content. Do not respond with anything else."
                    },
                    {
                        "role": "user",
                        "content": base_model_output
                    }
                ],
                "model": "meta-llama/Meta-Llama-3.1-405B-Instruct",
                "max_tokens": 512,
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "stream": False,
                }
            )

            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                if content and content.strip():
                    print(f"Response: {content}")
                    return content
        except Exception as e:
            print(f"Error on attempt {tries + 1}: {str(e)}")
            tries += 1
            time.sleep(1)  # Add a small delay between retries
