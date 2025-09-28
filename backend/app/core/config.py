from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "Multimodal AI Design Analysis Suite"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Hugging Face Configuration
    huggingface_hub_token: Optional[str] = None


    # LLM Models
    default_vision_model: str = "meta-llama/llama-3.2-11b-vision-instruct"
    default_text_model: str = "anthropic/claude-3-5-sonnet-20241022"
    code_analysis_model: str = "meta-llama/llama-3.1-70b-instruct"

    # Database
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "design_analysis"

    # Image Processing
    clip_model_name: str = "openai/clip-vit-large-patch14"
    max_image_size: int = 10485760  # 10MB
    supported_image_formats: list = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]

    # Agent Configuration
    max_concurrent_agents: int = 5
    agent_timeout: int = 300  # 5 minutes

    # API Configuration
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    api_prefix: str = "/api/v1"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Monitoring
    enable_metrics: bool = True
    log_level: str = "INFO"

    # Rate Limiting
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds

    class Config:
        # When running from backend dir, this points to repo root .env
        env_file = "../.env"
        case_sensitive = False

settings = Settings()

# Bridge env var names for downstream libraries
# - huggingface_hub (transformers) reads HUGGINGFACE_HUB_TOKEN
# - langchain integrations may read HUGGINGFACEHUB_API_TOKEN
if settings.huggingface_hub_token and not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.huggingface_hub_token
if settings.huggingfacehub_api_token and not os.environ.get("HUGGINGFACE_HUB_TOKEN"):
    os.environ["HUGGINGFACE_HUB_TOKEN"] = settings.huggingfacehub_api_token
