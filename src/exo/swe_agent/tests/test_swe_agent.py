"""Tests for dexo SWE-Agent."""

from pathlib import Path

import pytest

from exo.swe_agent.main import (
    CodeAnalysisResult,
    CodeGenerationRequest,
    CodeGenerationResult,
    SWEAgent,
    TestResult,
)


@pytest.fixture
def swe_agent() -> SWEAgent:
    """Create SWE-Agent instance for testing."""
    return SWEAgent(api_url="http://localhost:52415")


@pytest.mark.asyncio
async def test_analyze_nonexistent_file(swe_agent: SWEAgent) -> None:
    """Test analyzing a file that doesn't exist."""
    result = await swe_agent.analyze_code(Path("/nonexistent/file.py"))
    assert not result.issues == []
    assert "File not found" in result.issues


@pytest.mark.asyncio
async def test_analyze_valid_python_file(swe_agent: SWEAgent, tmp_path: Path) -> None:
    """Test analyzing a valid Python file."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def hello():\n    return 'world'\n")

    result = await swe_agent.analyze_code(test_file)
    assert result.file_path == str(test_file)
    assert result.issues == []
    assert result.complexity_score > 0


@pytest.mark.asyncio
async def test_analyze_invalid_python_file(
    swe_agent: SWEAgent, tmp_path: Path
) -> None:
    """Test analyzing an invalid Python file."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def hello(\n")  # Invalid syntax

    result = await swe_agent.analyze_code(test_file)
    assert len(result.issues) > 0
    assert any("Syntax error" in issue for issue in result.issues)


def test_extract_code_from_markdown(swe_agent: SWEAgent) -> None:
    """Test extracting code from markdown code blocks."""
    markdown_text = """Here is some code:

```python
def hello():
    return "world"
```

That's the code!
"""
    code = swe_agent._extract_code_from_response(markdown_text)
    assert 'def hello():' in code
    assert 'return "world"' in code


def test_code_generation_request_defaults() -> None:
    """Test CodeGenerationRequest defaults."""
    request = CodeGenerationRequest(prompt="test prompt")
    assert request.context == ""
    assert request.language == "python"
    assert request.max_tokens == 2000


@pytest.mark.asyncio
async def test_run_tests_nonexistent_path(swe_agent: SWEAgent) -> None:
    """Test running tests on nonexistent path."""
    result = await swe_agent.run_tests(Path("/nonexistent/path"))
    assert not result.success
    assert "not found" in result.output.lower()
