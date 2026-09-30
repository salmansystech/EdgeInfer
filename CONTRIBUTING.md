# Contributing to EdgeInfer

Thank you for contributing to EdgeInfer!

## Getting Started

1. Fork and clone the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes with tests

## Development Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused

## Adding Support

### New Hardware Target
1. Add specs to `Config.HARDWARE_TARGETS`
2. Test with example models
3. Update README

### New Optimization Technique
1. Extend `OptimizationAgent`
2. Add benchmarking data
3. Document expected improvements

## Testing

```bash
python -m pytest tests/
```

## Commit Messages

- Clear, descriptive messages
- Reference issues: "Add feature #123"

## Pull Request Process

1. Ensure tests pass
2. Update documentation
3. Reference related issues

Thank you! 🎉
