"""OpenRouter API Client for LLM interactions"""
import os
import requests
import json
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/golden-dataset",
            "X-Title": "Golden Dataset Generator"
        }
    
    def call_llm(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict:
        """Call LLM via OpenRouter API
        
        Args:
            model: Model identifier (e.g., 'deepseek/deepseek-r1')
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dict with content, usage, etc.
        """
        start_time = time.time()
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            logger.info(f"Calling OpenRouter API with model: {model}")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "time_seconds": round(elapsed, 2),
                "raw_response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "time_seconds": round(elapsed, 2)
            }
    
    def extract_terraform_code(self, response_text: str) -> Optional[str]:
        """Extract Terraform code from LLM response
        
        Args:
            response_text: Full LLM response text
            
        Returns:
            Extracted Terraform code or None
        """
        # Try to find code blocks
        import re
        
        # Look for ```terraform, ```hcl, or ``` code blocks
        patterns = [
            r'```(?:terraform|hcl)\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                # Return the first substantial match
                for match in matches:
                    if 'provider' in match.lower() or 'resource' in match.lower():
                        return match.strip()
        
        # If no code blocks found, look for terraform/provider keywords
        if 'provider "xenorchestra"' in response_text:
            # Try to extract from "provider" to end of likely code section
            lines = response_text.split('\n')
            code_lines = []
            in_code = False
            
            for line in lines:
                if 'provider "xenorchestra"' in line or 'terraform {' in line:
                    in_code = True
                
                if in_code:
                    code_lines.append(line)
                    
                    # Stop at common ending patterns
                    if line.strip() and not line.strip().startswith('#') and \
                       any(end in line for end in ['If you have', 'Note:', 'Make sure', 'Remember']):
                        break
            
            if code_lines:
                return '\n'.join(code_lines).strip()
        
        return None
    
    def extract_questions_asked(self, response_text: str) -> List[str]:
        """Extract questions asked by LLM from response
        
        Args:
            response_text: Full LLM response text
            
        Returns:
            List of questions found
        """
        import re
        
        questions = []
        
        # Look for lines ending with ?
        question_pattern = r'([^.!?\n]+\?+)'
        matches = re.findall(question_pattern, response_text)
        
        for match in matches:
            question = match.strip()
            # Filter out very short or code-like questions
            if len(question) > 20 and not question.startswith('```'):
                questions.append(question)
        
        return questions[:10]  # Limit to first 10 questions
