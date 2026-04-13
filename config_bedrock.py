import boto3
from langchain_aws import ChatBedrock

def get_bedrock_llm(max_tokens=100, temperature=0.3):
    """Get Bedrock LLM with minimal token usage"""
    return ChatBedrock(
        model_id="amazon.nova-pro-v1:0",  # Amazon Nova Pro
        model_kwargs={
            "max_tokens": max_tokens,
            "temperature": temperature
        }
    )
