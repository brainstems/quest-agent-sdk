# Contributing to Quest Agent SDK

We welcome contributions! This guide will help you get started.

## Ways to Contribute

- 🐛 **Report bugs** - Create an issue with steps to reproduce
- 💡 **Suggest features** - Open an issue describing the feature
- 📝 **Improve documentation** - Fix typos, add examples, clarify explanations
- 🔧 **Submit code** - Fix bugs or implement features
- 🎓 **Share examples** - Add new integration examples

## Getting Started

### 1. Fork the Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/quest-agent-forge.git
cd quest-agent-forge/external-agent-sdk
```

### 2. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bug-fix
```

### 3. Make Your Changes

```bash
# Make changes
nano python/quest_agent_sdk.py

# Test your changes
python examples/test_my_changes.py
```

### 4. Submit Pull Request

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/my-feature
```

Then open a pull request on GitHub.

## Development Guidelines

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Add docstrings to all public functions
- Keep functions focused and small

```python
def my_function(param: str) -> Dict:
    """
    Brief description.
    
    Args:
        param: Description
    
    Returns:
        Description
    """
    pass
```

**TypeScript:**
- Use TypeScript strict mode
- Add JSDoc comments
- Use meaningful variable names

```typescript
/**
 * Brief description
 */
function myFunction(param: string): Result {
    // Implementation
}
```

### Testing

Add tests for new features:

```python
# tests/test_my_feature.py
def test_my_feature():
    assert my_function("input") == "expected"
```

### Documentation

Update documentation for any user-facing changes:
- README.md
- docs/API_REFERENCE.md
- Inline code comments
- Example files

### Commit Messages

Use conventional commits:

```
feat: add agent bidding support
fix: handle empty Redis responses
docs: update installation guide
test: add tests for schema validation
chore: update dependencies
```

## Adding Examples

We love new examples! Follow this template:

```python
"""
Example: Your Example Name
===========================

Description of what this example demonstrates.

Use Case: When to use this pattern
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from python.quest_agent_sdk import QuestAgentConfig, QuestLangChainAgent

# Your example code here

if __name__ == "__main__":
    main()
```

## Reporting Bugs

Include:
- **Description** - What went wrong?
- **Steps to reproduce** - How can we reproduce it?
- **Expected behavior** - What should happen?
- **Actual behavior** - What actually happened?
- **Environment** - OS, Python version, dependencies

## Suggesting Features

Include:
- **Use case** - Why is this needed?
- **Proposed solution** - How should it work?
- **Alternatives** - What else did you consider?
- **Examples** - Code examples if applicable

## Questions?

- Open a discussion on GitHub
- Check existing issues
- Review documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🙏
