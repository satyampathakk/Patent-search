import os
from dotenv import load_dotenv
from typing import Tuple, List

# Suppress Google library warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'     # Suppress gRPC warnings
os.environ['GLOG_minloglevel'] = '2'       # Suppress Google logging

# Load environment variables from .env file
load_dotenv()


class ConfigService:
    """Centralized configuration management using environment variables."""
    
    @staticmethod
    def get_model_type() -> str:
        """
        Returns the AI model type to use: 'gemini' or 'local'.
        Defaults to 'gemini' if not specified.
        """
        model_type = os.getenv('MODEL_TYPE', 'gemini').lower()
        if model_type not in ['gemini', 'local']:
            print(f"Warning: Invalid MODEL_TYPE '{model_type}'. Defaulting to 'gemini'.")
            return 'gemini'
        return model_type
    
    @staticmethod
    def get_gemini_api_key() -> str:
        """
        Returns Gemini API key from environment.
        Raises ValueError if not set when using Gemini model.
        """
        api_key = os.getenv('GEMINI_API_KEY', '')
        if not api_key and ConfigService.get_model_type() == 'gemini':
            raise ValueError(
                "GEMINI_API_KEY environment variable is required when MODEL_TYPE is 'gemini'. "
                "Please set it in your .env file."
            )
        return api_key
    
    @staticmethod
    def get_local_model_name() -> str:
        """
        Returns local model name for sentence-transformers.
        Defaults to 'all-MiniLM-L6-v2'.
        """
        return os.getenv('LOCAL_MODEL_NAME', 'all-MiniLM-L6-v2')
    
    @staticmethod
    def get_secret_key() -> str:
        """Returns Django SECRET_KEY from environment."""
        return os.getenv('SECRET_KEY', 'django-insecure-default-key-change-in-production')
    
    @staticmethod
    def get_debug() -> bool:
        """Returns DEBUG setting from environment."""
        return os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    @staticmethod
    def validate_config() -> Tuple[bool, List[str]]:
        """
        Validates required environment variables based on model type.
        Returns (is_valid, list_of_errors).
        """
        errors = []
        model_type = ConfigService.get_model_type()
        
        if model_type == 'gemini':
            try:
                ConfigService.get_gemini_api_key()
            except ValueError as e:
                errors.append(str(e))
        
        if not errors:
            return True, []
        return False, errors
