# Contributing Guide

Thank you for your interest in contributing to the Conversational AI System!

## Development Setup

1. **Fork and clone the repository**

```bash
git clone <your-fork-url>
cd conversational-ai-system
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints for all function parameters and return values
- Use Google-style docstrings
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Example

```python
def process_message(user_id: str, message: str, temperature: float = 0.7) -> str:
    """
    Process a user message and generate a response.
    
    Args:
        user_id: Unique identifier for the user
        message: The user's input message
        temperature: Sampling temperature for response generation
    
    Returns:
        The generated response text
    
    Raises:
        ValueError: If message is empty
        ModelAPIException: If model API call fails
    """
    if not message:
        raise ValueError("Message cannot be empty")
    
    # Implementation here
    return response
```

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
python run_tests.py coverage

# Specific test file
pytest tests/test_api.py -v

# Specific test function
pytest tests/test_api.py::test_health_check -v
```

### Writing Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Use fixtures for common setup
- Mock external dependencies

### Test Structure

```python
def test_feature_name():
    """Test description of what is being tested."""
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

## Adding New Features

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Implement the Feature

- Write clean, documented code
- Follow the existing architecture
- Add appropriate error handling
- Update configuration if needed

### 3. Add Tests

- Unit tests for individual components
- Integration tests for feature flow
- Test edge cases and error conditions

### 4. Update Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Update ARCHITECTURE.md for architectural changes
- Add examples if applicable

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for refactoring
- `chore:` for maintenance

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

## Project Structure Guidelines

### Adding a New Node (LangGraph)

1. Add node function in `backend/agents/node_calls.py`
2. Update `ChatState` in `backend/agents/graph.py` if needed
3. Update graph flow in `create_chat_graph()`
4. Add tests in `tests/test_graph.py`

### Adding a New Endpoint

1. Add endpoint in `backend/main.py`
2. Create Pydantic models for request/response
3. Add error handling
4. Add logging
5. Add tests in `tests/test_api.py`
6. Update API documentation in README.md

### Adding a New Prompt

1. Create `.txt` file in `backend/prompts/`
2. Update `prompt_factory.py` if needed
3. Add tests in `tests/test_prompt_factory.py`
4. Document in README.md

### Adding a New Configuration Option

1. Add to `ModelConfig` or `AppConfig` in `backend/config.py`
2. Add environment variable to `.env.example`
3. Document in README.md
4. Add tests in `tests/test_config.py`

## Code Review Process

### Before Submitting

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No unnecessary dependencies added
- [ ] No sensitive data in code
- [ ] Commit messages are clear

### Review Checklist

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications
- Security considerations
- Backward compatibility

## Common Tasks

### Adding a New Model Backend

1. Test with UniversalChat (no code changes needed)
2. Add configuration example to README.md
3. Add to "Switching Model Backends" section
4. Test thoroughly

### Updating Dependencies

1. Update `requirements.txt`
2. Test all functionality
3. Update documentation if API changes
4. Note breaking changes in commit message

### Fixing a Bug

1. Write a test that reproduces the bug
2. Fix the bug
3. Verify test passes
4. Add regression test if needed
5. Document fix in commit message

## Getting Help

- Check existing documentation
- Review similar code in the project
- Ask questions in pull request comments
- Refer to ARCHITECTURE.md for design decisions

## Phase 2+ Contributions

For Phase 2+ features (memory, tools, RL):

1. Review extension points in ARCHITECTURE.md
2. Discuss design in an issue first
3. Follow the established patterns
4. Ensure backward compatibility
5. Add comprehensive tests
6. Update documentation thoroughly

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Feel free to open an issue for:
- Feature requests
- Bug reports
- Documentation improvements
- General questions

Thank you for contributing!
