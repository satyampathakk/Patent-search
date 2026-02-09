from abc import ABC, abstractmethod
from typing import Dict, Any
import google.generativeai as genai
import time

from .config_service import ConfigService
from .prompt_service import PromptService


class AIAdapter(ABC):
    """Abstract base class for AI adapters."""
    
    @abstractmethod
    def extract_keywords(self, user_idea: str) -> str:
        """Extract search keywords from user idea."""
        pass
    
    @abstractmethod
    def analyze_similarity(self, user_idea: str, patent_data: str) -> str:
        """Analyze similarity between idea and patents."""
        pass


class GeminiAdapter(AIAdapter):
    """Adapter for Google Gemini API."""
    
    def __init__(self, api_key: str, prompt_service: PromptService):
        """Initialize Gemini API client."""
        self.prompt_service = prompt_service
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    
    def extract_keywords(self, user_idea: str) -> str:
        """Use Gemini API for keyword extraction with retry logic."""
        prompt = self.prompt_service.get_keyword_extraction_prompt(user_idea)
        return self._call_with_retry(prompt)
    
    def analyze_similarity(self, user_idea: str, patent_data: str) -> str:
        """Use Gemini API for similarity analysis with retry logic."""
        prompt = self.prompt_service.get_similarity_analysis_prompt(user_idea, patent_data)
        return self._call_with_retry(prompt)
    
    def _call_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Call Gemini API with retry logic."""
        for attempt in range(max_retries):
            try:
                chat = self.model.start_chat()
                response = chat.send_message(prompt)
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Gemini API failed after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
        return ""


class LocalModelAdapter(AIAdapter):
    """Adapter for local transformer models."""
    
    _model_cache = {}
    _text_generation_model = None
    
    def __init__(self, model_name: str, prompt_service: PromptService):
        """Initialize local transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            self.SentenceTransformer = SentenceTransformer
            self.cosine_similarity = cosine_similarity
            self.np = np
        except ImportError as e:
            raise ImportError(
                "Local model dependencies not installed. "
                "Please run: pip install sentence-transformers scikit-learn numpy"
            ) from e
        
        self.model_name = model_name
        self.prompt_service = prompt_service
        self.embedding_model = self._load_embedding_model()
        self.text_model = self._load_text_generation_model()
    
    def _load_embedding_model(self):
        """Load embedding model with caching."""
        if self.model_name not in self._model_cache:
            print(f"Loading embedding model: {self.model_name}...")
            self._model_cache[self.model_name] = self.SentenceTransformer(self.model_name)
            print(f"Embedding model loaded successfully.")
        return self._model_cache[self.model_name]
    
    def _load_text_generation_model(self):
        """Load text generation model for keyword extraction (lazy loading)."""
        if LocalModelAdapter._text_generation_model is None:
            try:
                from transformers import pipeline
                print("Loading text generation model for keyword extraction...")
                # Use a small, fast model for text generation
                LocalModelAdapter._text_generation_model = pipeline(
                    "text2text-generation",
                    model="google/flan-t5-small",
                    max_length=100,
                    device=-1  # CPU
                )
                print("Text generation model loaded successfully.")
            except ImportError:
                print("Warning: transformers library not installed. Using fallback keyword extraction.")
                LocalModelAdapter._text_generation_model = None
            except Exception as e:
                print(f"Warning: Could not load text generation model: {e}. Using fallback.")
                LocalModelAdapter._text_generation_model = None
        return LocalModelAdapter._text_generation_model
    
    def extract_keywords(self, user_idea: str) -> str:
        """Use transformer model for keyword extraction, similar to Gemini."""
        # Try using text generation model first (like Gemini)
        if self.text_model is not None:
            try:
                prompt = self.prompt_service.get_keyword_extraction_prompt(user_idea)
                result = self.text_model(prompt, max_length=100, do_sample=False)
                keywords = result[0]['generated_text'].strip()
                
                # Clean up the output
                if keywords:
                    return keywords
            except Exception as e:
                print(f"Text generation failed: {e}. Using fallback method.")
        
        # Fallback: Use embedding-based keyword extraction
        return self._extract_keywords_with_embeddings(user_idea)
    
    def _extract_keywords_with_embeddings(self, user_idea: str) -> str:
        """Fallback: Extract keywords using sentence embeddings and similarity."""
        # Split into sentences/phrases
        words = user_idea.split()
        if len(words) <= 7:
            return user_idea
        
        # Create candidate phrases (1-3 word combinations)
        candidates = []
        for i in range(len(words)):
            # Single words
            if len(words[i]) > 3:  # Skip very short words
                candidates.append(words[i])
            # Two-word phrases
            if i < len(words) - 1:
                candidates.append(f"{words[i]} {words[i+1]}")
            # Three-word phrases
            if i < len(words) - 2:
                candidates.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Remove duplicates
        candidates = list(set(candidates))[:50]  # Limit to 50 candidates
        
        if not candidates:
            return ' '.join(words[:7])
        
        # Encode the full idea and candidates
        idea_embedding = self.embedding_model.encode([user_idea])[0]
        candidate_embeddings = self.embedding_model.encode(candidates)
        
        # Calculate similarity scores
        similarities = self.cosine_similarity([idea_embedding], candidate_embeddings)[0]
        
        # Get top 5-7 keywords
        top_indices = self.np.argsort(similarities)[-7:][::-1]
        top_keywords = [candidates[i] for i in top_indices]
        
        return ' '.join(top_keywords[:7])
    
    def analyze_similarity(self, user_idea: str, patent_data: str) -> str:
        """Use embeddings and cosine similarity for analysis."""
        # Generate embeddings
        idea_embedding = self.embedding_model.encode([user_idea])[0]
        
        # Split patent data into individual patents
        patents = patent_data.split('\n\n')
        patents = [p.strip() for p in patents if p.strip()]
        
        if not patents:
            return "No patent data available for analysis."
        
        patent_embeddings = self.embedding_model.encode(patents)
        
        # Calculate similarities
        similarities = self.cosine_similarity([idea_embedding], patent_embeddings)[0]
        
        # Format response
        analysis = self._format_analysis(user_idea, patents, similarities)
        return analysis
    
    def _format_analysis(self, user_idea: str, patents: list, similarities) -> str:
        """Format similarity analysis as natural language."""
        avg_similarity = self.np.mean(similarities)
        max_similarity = self.np.max(similarities)
        max_idx = self.np.argmax(similarities)
        
        analysis = "## Patent Similarity Analysis\n\n"
        
        # Overall assessment
        if max_similarity > 0.8:
            analysis += "**Assessment:** Your idea shows significant overlap with existing patents. "
            analysis += "Patentability may be challenging without substantial differentiation.\n\n"
        elif max_similarity > 0.6:
            analysis += "**Assessment:** Your idea has moderate similarity to existing patents. "
            analysis += "There may be opportunities for differentiation and patentability.\n\n"
        else:
            analysis += "**Assessment:** Your idea appears relatively novel compared to the analyzed patents. "
            analysis += "Good potential for patentability with proper documentation.\n\n"
        
        # Specific similarities
        analysis += "### Similarity Scores:\n"
        for i, (patent, sim) in enumerate(zip(patents[:5], similarities[:5])):
            if patent.strip():
                analysis += f"- Patent {i+1}: {sim:.2%} similarity\n"
        
        # Most similar patent
        if max_similarity > 0.5 and patents[max_idx].strip():
            analysis += f"\n### Most Similar Patent:\n"
            analysis += f"Similarity: {max_similarity:.2%}\n"
            analysis += f"Content: {patents[max_idx][:200]}...\n\n"
        
        # Recommendations
        analysis += "### Recommendations:\n"
        if max_similarity > 0.7:
            analysis += "- Conduct a detailed prior art search\n"
            analysis += "- Identify unique aspects of your innovation\n"
            analysis += "- Consider consulting a patent attorney\n"
        else:
            analysis += "- Document your unique approach and implementation\n"
            analysis += "- Conduct a comprehensive patent search\n"
            analysis += "- Consider filing a provisional patent application\n"
        
        return analysis


class AIService:
    """Factory class that selects appropriate AI adapter based on configuration."""
    
    def __init__(self):
        """Initialize with appropriate adapter based on config."""
        self.config = ConfigService()
        self.prompt_service = PromptService()
        self.adapter = self._create_adapter()
    
    def _create_adapter(self) -> AIAdapter:
        """Create appropriate adapter based on configuration."""
        model_type = self.config.get_model_type()
        
        if model_type == 'gemini':
            api_key = self.config.get_gemini_api_key()
            return GeminiAdapter(api_key, self.prompt_service)
        elif model_type == 'local':
            model_name = self.config.get_local_model_name()
            return LocalModelAdapter(model_name, self.prompt_service)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def process_patent_search(self, user_idea: str, patent_data: str = None) -> Dict[str, Any]:
        """
        Complete patent search workflow.
        If patent_data is provided, skip keyword extraction.
        """
        try:
            # Extract keywords
            keywords = self.adapter.extract_keywords(user_idea)
            
            # If patent_data is provided, analyze it
            if patent_data:
                analysis = self.adapter.analyze_similarity(user_idea, patent_data)
            else:
                analysis = "Patent data not provided. Please scrape patents first."
            
            return {
                'success': True,
                'keywords': keywords,
                'patent_data': patent_data or '',
                'analysis': analysis
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'keywords': '',
                'patent_data': '',
                'analysis': f"Error processing search: {str(e)}"
            }
