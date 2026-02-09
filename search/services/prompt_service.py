import json
import os
from typing import Dict, Any


class PromptService:
    """Manages AI prompt templates from JSON configuration."""
    
    # Default prompts as fallback
    DEFAULT_PROMPTS = {
        "keyword_extraction": {
            "template": "Given the following innovation idea, extract 5-7 key search terms that would be most effective for finding related patents on Google Patents. Return ONLY the search terms, nothing else.\n\nIdea: {user_idea}\n\nSearch terms:",
            "max_tokens": 100
        },
        "similarity_analysis": {
            "template": "Compare the user's innovation idea with the following patent abstracts. Analyze if there are similarities and provide your assessment on:\n1. Whether the idea is novel or has significant overlap with existing patents\n2. Specific similarities found\n3. Potential areas of differentiation\n4. Recommendation on patentability\n\nUser's Idea:\n{user_idea}\n\nExisting Patents:\n{patent_data}\n\nAnalysis:",
            "max_tokens": 1500
        }
    }
    
    def __init__(self, prompts_file_path: str = 'prompts.json'):
        """Initialize with path to prompts configuration."""
        self.prompts_file_path = prompts_file_path
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from JSON file with fallback to defaults."""
        if not os.path.exists(self.prompts_file_path):
            print(f"Warning: {self.prompts_file_path} not found. Using default prompts.")
            return self.DEFAULT_PROMPTS.copy()
        
        try:
            with open(self.prompts_file_path, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            
            # Validate structure
            if not isinstance(prompts, dict):
                raise ValueError("Prompts file must contain a JSON object")
            
            # Ensure required prompt types exist
            required_types = ['keyword_extraction', 'similarity_analysis']
            for prompt_type in required_types:
                if prompt_type not in prompts:
                    print(f"Warning: '{prompt_type}' not found in prompts.json. Using default.")
                    prompts[prompt_type] = self.DEFAULT_PROMPTS[prompt_type]
            
            return prompts
        
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading {self.prompts_file_path}: {e}. Using default prompts.")
            return self.DEFAULT_PROMPTS.copy()
    
    def get_keyword_extraction_prompt(self, user_idea: str) -> str:
        """Generate keyword extraction prompt with variable substitution."""
        template = self.prompts['keyword_extraction']['template']
        return template.format(user_idea=user_idea)
    
    def get_similarity_analysis_prompt(self, user_idea: str, patent_data: str) -> str:
        """Generate similarity analysis prompt with variable substitution."""
        template = self.prompts['similarity_analysis']['template']
        return template.format(user_idea=user_idea, patent_data=patent_data)
    
    def get_max_tokens(self, prompt_type: str) -> int:
        """Get max_tokens setting for a prompt type."""
        return self.prompts.get(prompt_type, {}).get('max_tokens', 500)
    
    def reload_prompts(self) -> None:
        """Reload prompts from file."""
        self.prompts = self._load_prompts()
