"""
OpenAI client for generating demand letters.
"""
import logging
import time
from typing import List, Optional, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion

from shared.config import get_settings
from shared.exceptions import OpenAIException

logger = logging.getLogger(__name__)

# Global OpenAI client instance
_openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """
    Get or create the global OpenAI client instance (singleton).
    
    Returns:
        OpenAI client instance
        
    Raises:
        OpenAIException: If API key is not configured
    """
    global _openai_client
    if _openai_client is None:
        settings = get_settings()
        if not settings.openai.api_key:
            raise OpenAIException(
                message="OpenAI API key not configured",
                detail="Please set OPENAI_API_KEY environment variable",
            )
        _openai_client = OpenAI(api_key=settings.openai.api_key)
        logger.info("OpenAI client initialized")
    return _openai_client


def build_generation_prompt(
    template_data: Dict[str, Any],
    parsed_documents: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """
    Build the prompt for letter generation from template and documents.
    
    Note: This is a convenience function. For more control, use the functions
    in prompts.py (combine_prompt_components, etc.)
    
    Args:
        template_data: Template data with letterhead, sections, opening/closing paragraphs
        parsed_documents: List of parsed documents with extracted_text and document_id
        
    Returns:
        List of message dictionaries for OpenAI Chat API
    """
    # Import here to avoid circular dependency
    from .prompts import combine_prompt_components
    
    return combine_prompt_components(
        template_data=template_data,
        parsed_documents=parsed_documents,
    )


def call_openai_api(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> str:
    """
    Call OpenAI API to generate letter content.
    
    Args:
        messages: List of message dictionaries for the chat API
        model: Model to use (defaults to config value)
        temperature: Temperature setting (defaults to config value)
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (exponential backoff)
        
    Returns:
        Generated text content
        
    Raises:
        OpenAIException: If API call fails after retries
    """
    settings = get_settings()
    client = get_openai_client()
    
    # Use provided values or fall back to config
    model = model or settings.openai.model
    temperature = temperature if temperature is not None else settings.openai.temperature
    
    # Estimate token count for logging
    estimated_tokens = estimate_token_count(messages)
    logger.info(f"Calling OpenAI API with model={model}, temperature={temperature}, estimated_tokens={estimated_tokens}")
    
    last_exception = None
    delay = retry_delay
    
    for attempt in range(max_retries):
        try:
            response: ChatCompletion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            
            # Extract content from response
            if not response.choices or not response.choices[0].message.content:
                raise OpenAIException(
                    message="Empty response from OpenAI API",
                    detail="No content in API response",
                )
            
            generated_text = response.choices[0].message.content
            logger.info(f"Successfully generated letter content ({len(generated_text)} characters)")
            return generated_text
            
        except Exception as e:
            last_exception = e
            error_msg = str(e)
            
            # Check if it's a rate limit error
            if "rate limit" in error_msg.lower() or "429" in error_msg:
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                else:
                    raise OpenAIException(
                        message="OpenAI API rate limit exceeded",
                        detail=f"Failed after {max_retries} retries: {error_msg}",
                    )
            
            # Check if it's a transient error (timeout, connection, etc.)
            if any(keyword in error_msg.lower() for keyword in ["timeout", "connection", "network", "503", "502"]):
                if attempt < max_retries - 1:
                    logger.warning(f"Transient error, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries}): {error_msg}")
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    raise OpenAIException(
                        message="OpenAI API transient error",
                        detail=f"Failed after {max_retries} retries: {error_msg}",
                    )
            
            # For other errors, don't retry
            logger.error(f"OpenAI API error: {error_msg}")
            raise OpenAIException(
                message="OpenAI API error",
                detail=error_msg,
            )
    
    # If we exhausted retries
    if last_exception:
        raise OpenAIException(
            message="OpenAI API call failed",
            detail=f"Failed after {max_retries} retries: {str(last_exception)}",
        )


def estimate_token_count(messages: List[Dict[str, str]]) -> int:
    """
    Estimate token count for messages (rough approximation).
    Uses a simple heuristic: ~4 characters per token.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Estimated token count
    """
    total_chars = sum(len(msg.get("content", "")) for msg in messages)
    # Rough approximation: 1 token ≈ 4 characters
    return total_chars // 4


def validate_response_format(response_text: str) -> bool:
    """
    Validate that the response is HTML formatted.
    
    Args:
        response_text: Generated text from OpenAI
        
    Returns:
        True if response appears to be HTML, False otherwise
    """
    # Basic check: HTML should contain at least one tag
    if "<" in response_text and ">" in response_text:
        return True
    return False

