from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # AWS
    aws_region: str

    # Bedrock
    bedrock_model_id: str
    bedrock_max_tokens: int = 4096

    # Glue
    glue_database: str

    # Athena
    athena_output_bucket: str
    athena_workgroup: str = "primary"

    # App
    app_env: str = "production"
    log_level: str = "INFO"
    app_port: int = 8000


settings = Settings()
