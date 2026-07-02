from __future__ import annotations

import re

import pytest

from tests.helpers import (
    DB_CONTAINER_PORT,
    DB_HOST_PORT,
    DB_NAME,
    DB_PASSWORD,
    DB_USER,
    assert_no_host_port_5432_in_connection_strings,
)


@pytest.mark.unit
@pytest.mark.hygiene
def test_docker_compose_service_exists(docker_compose_text: str) -> None:
    assert "postgres:" in docker_compose_text


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize(
    "required",
    [
        "image: postgres:16",
        "container_name: retail_retention_postgres",
        f"POSTGRES_DB: {DB_NAME}",
        f"POSTGRES_USER: {DB_USER}",
        f"POSTGRES_PASSWORD: {DB_PASSWORD}",
        f'"{DB_HOST_PORT}:{DB_CONTAINER_PORT}"',
        "postgres_data:/var/lib/postgresql/data",
        "pg_isready",
    ],
)
def test_docker_compose_required_config(docker_compose_text: str, required: str) -> None:
    assert required in docker_compose_text


@pytest.mark.unit
@pytest.mark.hygiene
def test_docker_compose_maps_host_5433_only(docker_compose_text: str) -> None:
    assert f'"{DB_HOST_PORT}:{DB_CONTAINER_PORT}"' in docker_compose_text
    assert '"5432:5432"' not in docker_compose_text
    assert '"5432:5433"' not in docker_compose_text


@pytest.mark.unit
@pytest.mark.hygiene
def test_docker_compose_no_host_5432_mapping(docker_compose_text: str) -> None:
    host_mappings = re.findall(r'"(\d+):(\d+)"', docker_compose_text)
    assert host_mappings, "Expected at least one port mapping"
    for host_port, _container_port in host_mappings:
        assert host_port == DB_HOST_PORT


@pytest.mark.unit
@pytest.mark.hygiene
def test_env_example_no_host_5432(env_example_text: str) -> None:
    assert_no_host_port_5432_in_connection_strings(env_example_text)
    assert f"POSTGRES_PORT={DB_HOST_PORT}" in env_example_text
