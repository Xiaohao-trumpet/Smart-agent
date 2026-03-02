"""
Setup verification script.
Checks that all required files and dependencies are in place.
"""

import sys
import os
from pathlib import Path


def check_file(path: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(path).exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} (MISSING)")
        return False


def check_directory(path: str, description: str) -> bool:
    """Check if a directory exists."""
    if Path(path).is_dir():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description}: {path} (MISSING)")
        return False


def check_python_version() -> bool:
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version: {version.major}.{version.minor}.{version.micro} (Need 3.11+)")
        return False


def check_imports() -> bool:
    """Check if key dependencies can be imported."""
    imports = [
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("langchain", "LangChain"),
        ("langgraph", "LangGraph"),
        ("openai", "OpenAI"),
    ]
    
    all_ok = True
    for module, name in imports:
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"✗ {name} not installed")
            all_ok = False
    
    return all_ok


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Conversational AI System - Setup Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    # Python version
    print("Checking Python version...")
    checks.append(check_python_version())
    print()
    
    # Core files
    print("Checking core files...")
    checks.append(check_file("requirements.txt", "Requirements file"))
    checks.append(check_file("README.md", "README"))
    checks.append(check_file(".env.example", "Environment example"))
    checks.append(check_file("Dockerfile", "Dockerfile"))
    print()
    
    # Backend structure
    print("Checking backend structure...")
    checks.append(check_directory("backend", "Backend directory"))
    checks.append(check_file("backend/__init__.py", "Backend init"))
    checks.append(check_file("backend/main.py", "Main API file"))
    checks.append(check_file("backend/config.py", "Config file"))
    checks.append(check_file("backend/session_store.py", "Session store"))
    print()
    
    # Backend modules
    print("Checking backend modules...")
    checks.append(check_directory("backend/agents", "Agents module"))
    checks.append(check_file("backend/agents/graph.py", "Graph definition"))
    checks.append(check_file("backend/agents/node_calls.py", "Node implementations"))
    
    checks.append(check_directory("backend/models", "Models module"))
    checks.append(check_file("backend/models/universal_chat.py", "Universal chat"))
    
    checks.append(check_directory("backend/prompts", "Prompts module"))
    checks.append(check_file("backend/prompts/system.txt", "System prompt"))
    checks.append(check_file("backend/prompts/it_helpdesk.txt", "IT helpdesk prompt"))
    checks.append(check_file("backend/prompts/prompt_factory.py", "Prompt factory"))
    
    checks.append(check_directory("backend/utils", "Utils module"))
    checks.append(check_file("backend/utils/logging.py", "Logging utils"))
    checks.append(check_file("backend/utils/exceptions.py", "Exception types"))
    print()
    
    # Tests
    print("Checking tests...")
    checks.append(check_directory("tests", "Tests directory"))
    checks.append(check_file("tests/test_api.py", "API tests"))
    checks.append(check_file("tests/test_graph.py", "Graph tests"))
    checks.append(check_file("tests/test_universal_chat.py", "Model tests"))
    checks.append(check_file("tests/test_session_store.py", "Session tests"))
    checks.append(check_file("tests/test_prompt_factory.py", "Prompt tests"))
    checks.append(check_file("tests/test_config.py", "Config tests"))
    print()
    
    # Frontend
    print("Checking frontend...")
    checks.append(check_directory("frontend", "Frontend directory"))
    checks.append(check_file("frontend/docker-compose.yml", "Docker Compose"))
    print()
    
    # Dependencies
    print("Checking Python dependencies...")
    checks.append(check_imports())
    print()
    
    # Environment
    print("Checking environment...")
    if Path(".env").exists():
        print("✓ .env file exists")
        checks.append(True)
    else:
        print("⚠ .env file not found (copy from .env.example)")
        checks.append(False)
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ All checks passed! You're ready to go.")
        print()
        print("Next steps:")
        print("1. Configure .env with your API key")
        print("2. Run: python run_backend.py")
        print("3. Test: curl http://localhost:8000/health")
        print("4. Start OpenWebUI: cd frontend && docker-compose up -d")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
