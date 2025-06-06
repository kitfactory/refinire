import pytest
from refinire import AgentPipeline
from pydantic import BaseModel
from dataclasses import dataclass


def test_extract_json_success():
    text = "prefix {\"score\":10, \"comment\":[\"ok\"]} suffix"
    data = AgentPipeline._extract_json(text)
    assert data == {"score": 10, "comment": ["ok"]}


def test_extract_json_fail():
    with pytest.raises(ValueError):
        AgentPipeline._extract_json("no json here")


def test_coerce_output_plain():
    pipeline = AgentPipeline(
        name="test",
        generation_instructions="",
        evaluation_instructions=None,
        model=None
    )
    assert pipeline._coerce_output("abc") == "abc"


def test_coerce_output_pydantic():
    class M(BaseModel):
        x: int
    pipeline = AgentPipeline(
        name="test",
        generation_instructions="",
        evaluation_instructions=None,
        model=None,
        output_model=M
    )
    text = '{"x":123}'
    parsed = pipeline._coerce_output(text)
    assert isinstance(parsed, M)
    assert parsed.x == 123


def test_coerce_output_dataclass():
    @dataclass
    class DC:
        a: int
    pipeline = AgentPipeline(
        name="test",
        generation_instructions="",
        evaluation_instructions=None,
        model=None,
        output_model=DC
    )
    text = '{"a":456}'
    parsed = pipeline._coerce_output(text)
    assert isinstance(parsed, DC)
    assert parsed.a == 456


def test_coerce_output_invalid_json():
    @dataclass
    class DC:
        a: int
    pipeline = AgentPipeline(
        name="test",
        generation_instructions="",
        evaluation_instructions=None,
        model=None,
        output_model=DC
    )
    text = 'not json'
    assert pipeline._coerce_output(text) == 'not json' 
