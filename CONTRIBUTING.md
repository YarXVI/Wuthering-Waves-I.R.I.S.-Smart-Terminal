# Contributing to I.R.I.S. Smart Terminal

Thank you for your interest in the I.R.I.S. Smart Terminal project! We welcome all forms of contributions, including but not limited to:
- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🎨 Code optimization
- 🧪 Test improvements

## Development Environment Setup

### 1. Fork the Project

Click the `Fork` button on the GitHub page to create your own copy of the repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/Wuthering-Waves-I.R.I.S.-Smart-Terminal.git
cd Wuthering-Waves-I.R.I.S.-Smart-Terminal
```

### 3. Add Upstream Repository

```bash
git remote add upstream https://github.com/YarXVI/Wuthering-Waves-I.R.I.S.-Smart-Terminal.git
```

### 4. Create a Development Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix-name
```

## Development Workflow

### Backend Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r agent_core/requirements.txt

# Run development server
python -m server.main

# Run tests
python -m pytest tests/ -v
```

### Frontend Development

```bash
cd desktop

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test
```

## Code Standards

### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused (single responsibility principle)

Example:

```python
def greet_user(name: str, age: int) -> str:
    """Generate a greeting message for the user.

    Args:
        name: The user's name
        age: The user's age

    Returns:
        A greeting string
    """
    return f"Hello, {name}! You are {age} years old."
```

### TypeScript/React (Frontend)

- Follow ESLint and Prettier configurations
- Use functional components with hooks
- PropTypes or TypeScript interfaces for component props
- Keep components small and reusable

Example:

```typescript
interface GreetingProps {
  name: string;
  age: number;
}

export const Greeting: React.FC<GreetingProps> = ({ name, age }) => {
  return <div>Hello, {name}! You are {age} years old.</div>;
};
```

## Commit Message Conventions

Please follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type Indicators

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation change
- `style`: Code format (no functional impact)
- `refactor`: Code refactoring
- `test`: Test related
- `chore`: Build/tool related

### Examples

```
feat(chat): add message persistence feature
fix(agent): resolve thread safety issue in AgentManager
docs(readme): update installation instructions
```

## Pull Request Process

### 1. Keep Your Branch Updated

Before submitting a PR, make sure your branch is up to date with upstream:

```bash
git fetch upstream
git merge upstream/main
```

### 2. Run Tests

Ensure all tests pass before submitting:

```bash
# Backend tests
python -m pytest tests/ -v

# Frontend tests
cd desktop && npm test
```

### 3. Submit Pull Request

- Use a clear and descriptive title
- Describe the changes in detail
- Link any related issues
- Request review from maintainers

### 4. Address Feedback

- Respond to review comments promptly
- Make necessary changes and push updates

## Reporting Issues

When reporting issues, please include:

- **Issue title**: Clear and descriptive
- **Description**: Detailed explanation of the problem
- **Steps to reproduce**: How to reproduce the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python/Node version, etc.
- **Screenshots**: If applicable

## Questions?

If you have any questions, feel free to:
- Open an issue for discussion
- Join our community discussions
- Contact the maintainers directly

Thank you for contributing to I.R.I.S. Smart Terminal!
