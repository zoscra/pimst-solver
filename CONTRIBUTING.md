# Contributing to PIMST

Thank you for your interest in contributing to PIMST! 🎉

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🧪 Add test cases and benchmarks
- 💻 Submit code improvements
- 🌍 Translate documentation

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/pimst-solver.git
   cd pimst-solver
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## Development Setup

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=pimst tests/

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Code Style

- Follow PEP 8
- Use `black` for formatting
- Add type hints
- Write docstrings for all public functions
- Keep functions focused and testable

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Include benchmark tests for performance-critical code

## Submitting Changes

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```
2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
3. **Open a Pull Request**
   - Describe your changes
   - Link related issues
   - Include test results
   - Update documentation if needed

## Pull Request Guidelines

- ✅ One feature per PR
- ✅ Clear description of changes
- ✅ All tests passing
- ✅ No decrease in code coverage
- ✅ Updated documentation
- ✅ Follow existing code style

## Reporting Bugs

When reporting bugs, please include:
- Python version
- PIMST version
- Operating system
- Minimal reproducible example
- Expected vs. actual behavior
- Error messages/stack traces

## Suggesting Features

When suggesting features:
- Check if it's already been suggested
- Explain the use case
- Describe expected behavior
- Consider performance implications

## Code Review Process

1. Maintainer will review within 1-2 weeks
2. Address feedback if requested
3. Once approved, maintainer will merge
4. Your contribution will be included in next release

## Community Guidelines

- Be respectful and inclusive
- Help others learn
- Give constructive feedback
- Celebrate contributions

## Questions?

- Open an issue for questions
- Join discussions on GitHub Discussions
- Email: hello@pimst.io

## License

By contributing, you agree that your contributions will be licensed under the AGPL-3.0 License.

---

Thank you for making PIMST better! 🚀
