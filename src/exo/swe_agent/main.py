"""SWE-Agent for dexo - Software Engineering Agent with autonomous reasoning capabilities."""

import argparse
import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from loguru import logger
from pydantic import BaseModel, Field


class CodeAnalysisResult(BaseModel):
    """Result of code analysis."""

    file_path: str
    issues: list[str] = Field(default_factory=list)
    complexity_score: float = 0.0
    suggestions: list[str] = Field(default_factory=list)


class CodeGenerationRequest(BaseModel):
    """Request for code generation."""

    prompt: str
    context: str = ""
    language: str = "python"
    max_tokens: int = 2000


class CodeGenerationResult(BaseModel):
    """Result of code generation."""

    code: str
    explanation: str = ""
    language: str = "python"


class TestResult(BaseModel):
    """Result of running tests."""

    success: bool
    output: str
    test_count: int = 0
    passed_count: int = 0
    failed_count: int = 0


@dataclass
class SWEAgent:
    """Software Engineering Agent for code analysis, generation, and testing."""

    api_url: str = "http://localhost:52415"
    model_id: str = "mlx-community/Llama-3.2-1B-Instruct-4bit"

    async def analyze_code(self, file_path: Path) -> CodeAnalysisResult:
        """Analyze code for issues and complexity."""
        logger.info(f"Analyzing code: {file_path}")

        if not file_path.exists():
            return CodeAnalysisResult(
                file_path=str(file_path), issues=["File not found"]
            )

        code = file_path.read_text()
        issues: list[str] = []
        suggestions: list[str] = []

        # Basic syntax check for Python files
        if file_path.suffix == ".py":
            try:
                ast.parse(code)
            except SyntaxError as e:
                issues.append(f"Syntax error: {e}")

        # Calculate basic complexity (lines of code)
        lines = [line for line in code.split("\n") if line.strip()]
        complexity_score = len(lines) / 100.0  # Normalize to 0-1 scale roughly

        # Add suggestions based on analysis
        if len(lines) > 500:
            suggestions.append("Consider breaking this file into smaller modules")

        return CodeAnalysisResult(
            file_path=str(file_path),
            issues=issues,
            complexity_score=complexity_score,
            suggestions=suggestions,
        )

    async def generate_code(
        self, request: CodeGenerationRequest
    ) -> CodeGenerationResult:
        """Generate code using the dexo cluster."""
        logger.info(f"Generating code for: {request.prompt}")

        # Create a prompt for the model
        full_prompt = f"""You are a software engineering assistant. Generate {request.language} code for the following task:

Task: {request.prompt}

Context: {request.context}

Generate clean, well-documented, and efficient code. Include comments explaining the code."""

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}/v1/chat/completions",
                    json={
                        "model": self.model_id,
                        "messages": [{"role": "user", "content": full_prompt}],
                        "max_tokens": request.max_tokens,
                        "stream": False,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]

                    # Extract code from markdown code blocks if present
                    code = self._extract_code_from_response(content)

                    return CodeGenerationResult(
                        code=code,
                        explanation=content,
                        language=request.language,
                    )
                else:
                    logger.error(f"Code generation failed: {response.text}")
                    return CodeGenerationResult(
                        code="",
                        explanation=f"Error: {response.text}",
                        language=request.language,
                    )
        except Exception as e:
            logger.error(f"Code generation error: {e}")
            return CodeGenerationResult(
                code="", explanation=f"Error: {e}", language=request.language
            )

    def _extract_code_from_response(self, content: str) -> str:
        """Extract code from markdown code blocks."""
        import re

        # Look for code blocks
        code_block_pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(code_block_pattern, content, re.DOTALL)

        if matches:
            return matches[0].strip()

        return content.strip()

    async def run_tests(self, test_path: Path) -> TestResult:
        """Run tests for a given path."""
        logger.info(f"Running tests: {test_path}")

        if not test_path.exists():
            return TestResult(
                success=False,
                output="Test path not found",
                test_count=0,
                passed_count=0,
                failed_count=0,
            )

        try:
            # Run pytest
            result = subprocess.run(
                ["pytest", str(test_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            # Parse test results from output
            import re

            passed_match = re.search(r"(\d+) passed", output)
            failed_match = re.search(r"(\d+) failed", output)

            passed_count = int(passed_match.group(1)) if passed_match else 0
            failed_count = int(failed_match.group(1)) if failed_match else 0
            test_count = passed_count + failed_count

            return TestResult(
                success=success,
                output=output,
                test_count=test_count,
                passed_count=passed_count,
                failed_count=failed_count,
            )
        except subprocess.TimeoutExpired:
            return TestResult(
                success=False,
                output="Test execution timed out",
                test_count=0,
                passed_count=0,
                failed_count=0,
            )
        except Exception as e:
            logger.error(f"Test execution error: {e}")
            return TestResult(
                success=False,
                output=str(e),
                test_count=0,
                passed_count=0,
                failed_count=0,
            )

    async def auto_fix_issues(self, file_path: Path) -> str:
        """Automatically attempt to fix issues in code."""
        logger.info(f"Auto-fixing issues in: {file_path}")

        # First analyze the code
        analysis = await self.analyze_code(file_path)

        if not analysis.issues:
            return "No issues found to fix"

        # Generate fix request
        code = file_path.read_text()
        fix_request = CodeGenerationRequest(
            prompt=f"Fix the following issues in this code:\n{', '.join(analysis.issues)}",
            context=f"Original code:\n{code}",
            language=file_path.suffix[1:] if file_path.suffix else "python",
        )

        result = await self.generate_code(fix_request)

        if result.code:
            # Optionally write back (for now just return)
            return f"Suggested fix:\n{result.code}"
        else:
            return "Could not generate fix"


async def main_async(args: argparse.Namespace) -> None:
    """Async main function."""
    agent = SWEAgent(api_url=args.api_url, model_id=args.model)

    if args.command == "analyze":
        result = await agent.analyze_code(Path(args.file))
        print(f"\n=== Code Analysis: {result.file_path} ===")
        print(f"Complexity Score: {result.complexity_score:.2f}")
        if result.issues:
            print(f"\nIssues:")
            for issue in result.issues:
                print(f"  - {issue}")
        if result.suggestions:
            print(f"\nSuggestions:")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")

    elif args.command == "generate":
        request = CodeGenerationRequest(
            prompt=args.prompt, language=args.language, max_tokens=args.max_tokens
        )
        result = await agent.generate_code(request)
        print(f"\n=== Generated Code ===")
        print(result.code)
        if result.explanation:
            print(f"\n=== Explanation ===")
            print(result.explanation)

    elif args.command == "test":
        result = await agent.run_tests(Path(args.path))
        print(f"\n=== Test Results ===")
        print(f"Success: {result.success}")
        print(f"Tests: {result.test_count}, Passed: {result.passed_count}, Failed: {result.failed_count}")
        print(f"\nOutput:\n{result.output}")

    elif args.command == "fix":
        result = await agent.auto_fix_issues(Path(args.file))
        print(f"\n=== Auto-Fix Results ===")
        print(result)


def main() -> None:
    """Main entry point for SWE-Agent."""
    parser = argparse.ArgumentParser(
        description="dexo SWE-Agent - Software Engineering Agent with autonomous reasoning"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:52415",
        help="URL of dexo API (default: http://localhost:52415)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mlx-community/Llama-3.2-1B-Instruct-4bit",
        help="Model to use for code generation",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze code file")
    analyze_parser.add_argument("file", type=str, help="File to analyze")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code")
    generate_parser.add_argument("prompt", type=str, help="Code generation prompt")
    generate_parser.add_argument(
        "--language", type=str, default="python", help="Programming language"
    )
    generate_parser.add_argument(
        "--max-tokens", type=int, default=2000, help="Max tokens to generate"
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("path", type=str, help="Path to tests")

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Auto-fix code issues")
    fix_parser.add_argument("file", type=str, help="File to fix")

    args = parser.parse_args()

    # Run async main
    import asyncio

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
