from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from core.agent import Agent
from core.skill import Skill
from storage.store import JsonStore


@pytest.fixture
def tmp_store(tmp_path: Path) -> JsonStore[Agent]:
    return JsonStore(tmp_path / "agents", Agent)


def test_save_and_get(tmp_store):
    a = Agent(name="alpha")
    tmp_store.save(a)
    result = tmp_store.get(a.id)
    assert result is not None
    assert result.name == "alpha"


def test_list(tmp_store):
    tmp_store.save(Agent(name="a"))
    tmp_store.save(Agent(name="b"))
    assert len(tmp_store.list()) == 2


def test_delete(tmp_store):
    a = Agent(name="del-me")
    tmp_store.save(a)
    assert tmp_store.delete(a.id) is True
    assert tmp_store.get(a.id) is None


def test_find_by_name(tmp_store):
    a = Agent(name="unique-name")
    tmp_store.save(a)
    found = tmp_store.find_by_name("unique-name")
    assert found is not None
    assert found.id == a.id


def test_get_or_raise_missing(tmp_store):
    with pytest.raises(KeyError):
        tmp_store.get_or_raise("nonexistent", "agent")
