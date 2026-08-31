from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    password: str = ""
    name: str = "autocustomer"
    pool_size: int = 10
    pool_overflow: int = 20


class RedisConfig(BaseModel):
    url: str = "redis://127.0.0.1:6379/0"
    celery_broker: str = "redis://127.0.0.1:6379/1"
    celery_backend: str = "redis://127.0.0.1:6379/2"


class MilvusConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 19530
    db_name: str = "default"


class JWTConfig(BaseModel):
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


class SecurityConfig(BaseModel):
    aes_encryption_key: str = "change-me-to-32-byte-key!!!!!!"
    sse_ticket_ttl_seconds: int = 300


class LLMConfig(BaseModel):
    default_provider: str = "openai"
    default_endpoint: str = "https://api.openai.com/v1"
    default_api_key: str = ""
    default_model: str = "gpt-4o"


class EmbeddingConfig(BaseModel):
    provider: str = "openai"
    endpoint: str = "https://api.openai.com/v1"
    api_key: str = ""
    dim: int = 1536


class RerankConfig(BaseModel):
    endpoint: str = ""
    api_key: str = ""


class MinioConfig(BaseModel):
    endpoint: str = "127.0.0.1:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket: str = "autocustomer"


class LogConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
    )

    db: DBConfig = DBConfig()
    redis: RedisConfig = RedisConfig()
    milvus: MilvusConfig = MilvusConfig()
    jwt: JWTConfig = JWTConfig()
    security: SecurityConfig = SecurityConfig()
    llm: LLMConfig = LLMConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    rerank: RerankConfig = RerankConfig()
    minio: MinioConfig = MinioConfig()
    log: LogConfig = LogConfig()


settings = Settings()