
import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_load_environment_variables(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Pipeline Guard Test")
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")

    settings = get_settings()

    assert settings.app_name == "Pipeline Guard Test"
    assert settings.app_env == "testing"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "sqlite:///./test.db"


def test_blank_app_name_is_rejected():
    with pytest.raises(ValidationError):
        Settings(app_name="   ")


def test_blank_database_url_is_rejected():
    with pytest.raises(ValidationError):
        Settings(database_url="   ")


def test_invalid_environment_is_rejected():
    with pytest.raises(ValidationError):
        Settings(app_env="staging")


def test_default_required_columns():
    settings = Settings()
    assert settings.required_columns == ["product", "quantity", "price"]


def test_default_negative_value_columns():
    settings = Settings()
    assert settings.negative_value_columns == ["quantity", "price"]


def test_column_names_are_stripped():
    settings = Settings(required_columns=[" product ", " quantity "])
    assert settings.required_columns == ["product", "quantity"]


def test_blank_column_name_is_rejected():
    with pytest.raises(ValidationError):
        Settings(required_columns=["product", " "])


def test_duplicate_column_names_are_rejected():
    with pytest.raises(ValidationError):
        Settings(required_columns=["product", "product"])


def test_empty_required_columns_are_rejected():
    with pytest.raises(ValidationError):
        Settings(required_columns=[])
