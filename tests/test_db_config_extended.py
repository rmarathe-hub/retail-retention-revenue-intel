from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from tests.conftest import load_module_from_path
from tests.helpers import DB_HOST_PORT, DB_NAME, DB_PASSWORD, DB_USER


@pytest.fixture(scope="module")
def db_config_module(project_root):
    return load_module_from_path("db_config_ext", project_root / "scripts/db_config.py")


@pytest.mark.unit
@pytest.mark.hygiene
def test_default_port_constant_is_5433(db_config_module) -> None:
    assert db_config_module.DEFAULT_PORT == "5433"


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize(
    ("env", "expected_fragment"),
    [
        (
            {"DATABASE_URL": "postgresql://u:p@localhost:5433/db"},
            "postgresql+psycopg2://u:p@localhost:5433/db",
        ),
        (
            {"DATABASE_URL": "postgresql+psycopg2://u:p@localhost:5433/db"},
            "postgresql+psycopg2://u:p@localhost:5433/db",
        ),
    ],
)
def test_database_url_normalization(db_config_module, env: dict, expected_fragment: str) -> None:
    with patch.dict(os.environ, {**env, "POSTGRES_PASSWORD": "x"}, clear=True):
        assert db_config_module.get_database_url() == expected_fragment


@pytest.mark.unit
@pytest.mark.hygiene
def test_components_default_to_docker_credentials(db_config_module) -> None:
    with patch.dict(os.environ, {"POSTGRES_PASSWORD": DB_PASSWORD}, clear=True):
        url = db_config_module.get_database_url()
        assert DB_USER in url
        assert DB_PASSWORD in url
        assert DB_HOST_PORT in url
        assert DB_NAME in url
        assert ":5432/" not in url


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize("bad_port", ["5432", "5434"])
def test_explicit_bad_host_port_not_default(db_config_module, bad_port: str) -> None:
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "",
            "POSTGRES_PORT": bad_port,
            "POSTGRES_PASSWORD": "secret",
        },
        clear=True,
    ):
        url = db_config_module.get_database_url()
        assert f":{bad_port}/" in url
        if bad_port == "5432":
            assert db_config_module.DEFAULT_PORT != "5432"
