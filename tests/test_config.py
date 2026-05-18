from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_config_missing_required_fields():
    # GIVEN / WHEN / THEN
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValidationError):
            Settings()


def test_config_default_values():
    # GIVEN
    input_required = dict(
        aws_region="eu-west-1",
        bedrock_model_id="anthropic.claude-sonnet-4-5",
        glue_database="my_db",
        athena_output_bucket="s3://my-bucket/",
    )

    # WHEN
    actual = Settings(**input_required)

    # THEN
    assert actual.bedrock_max_tokens == 4096
    assert actual.athena_workgroup == "primary"
    assert actual.app_env == "production"
    assert actual.log_level == "INFO"
    assert actual.app_port == 8000


def test_config_override_defaults():
    # GIVEN
    input_settings = dict(
        aws_region="us-east-1",
        bedrock_model_id="anthropic.claude-sonnet-4-5",
        glue_database="my_db",
        athena_output_bucket="s3://my-bucket/",
        bedrock_max_tokens=1024,
        app_env="staging",
        log_level="DEBUG",
    )

    # WHEN
    actual = Settings(**input_settings)

    # THEN
    assert actual.bedrock_max_tokens == 1024
    assert actual.app_env == "staging"
    assert actual.log_level == "DEBUG"
