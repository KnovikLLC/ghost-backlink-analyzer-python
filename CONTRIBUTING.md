# Contributing to Internal Backlink Analyzer

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

Be respectful, inclusive, and professional. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## How to Contribute

### 1. Report Bugs

Found a bug? Open an issue with:
- Clear, descriptive title
- Step-by-step reproduction instructions
- Expected vs. actual behavior
- Your environment (OS, Python version, etc.)
- Screenshots if applicable

```markdown
## Title
Tag extraction not working

## Description
When analyzing Ghost CMS articles, no tags are extracted even though they exist.

## Steps to Reproduce
1. Enter sitemap URL
2. Enter article URL
3. Click Analyze

## Expected
Tags should be extracted from meta tags

## Actual
No tags found (empty list)

## Environment
- OS: macOS 12.6
- Python: 3.11.2
- Streamlit: 1.28.1
```

### 2. Suggest Enhancements

Have an idea? Open an issue with:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach

```markdown
## Feature
Add support for WordPress blogs

## Use Case
Many users have WordPress sites, not just Ghost CMS

## Proposed Solution
Create separate tag extraction for WordPress meta tags
```

### 3. Submit Pull Requests

#### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/backlink-analyzer-ghost.git
cd backlink-analyzer-ghost

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create feature branch
git checkout -b feature/your-feature-name
```

#### Code Style

Follow PEP 8:

```bash
# Format code
black app.py

# Check for issues
flake8 app.py

# Type checking
mypy app.py
```

#### Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=./ tests/
```

#### Commit Messages

Write clear commit messages:

```
git commit -m "Add feature: WordPress tag extraction

- Extracts tags from WordPress meta tags
- Supports custom post meta
- Improves relevance for WordPress users"
```

#### Pull Request Process

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Title: Clear, concise
   - Description: Why? What? How?
   - Link related issues
   - Include tests

4. **Pull Request Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Related Issues
   Fixes #123

   ## How to Test
   1. Step 1
   2. Step 2

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] Tests added/updated
   - [ ] All tests pass
   ```

## Development Workflow

### Project Structure

```
backlink-analyzer-ghost/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── requirements-dev.txt   # Dev dependencies
├── Dockerfile            # Docker configuration
├── .streamlit/
│   └── config.toml       # Streamlit config
├── README.md             # Documentation
├── DEPLOYMENT.md         # Deployment guide
├── LICENSE               # MIT License
└── tests/                # Test suite
    └── test_app.py
```

### Adding Features

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Write code**
   - Follow existing code style
   - Add type hints
   - Write docstrings

3. **Add tests**
   ```python
   def test_feature():
       result = my_feature()
       assert result == expected
   ```

4. **Update documentation**
   - Update README if needed
   - Add docstrings
   - Include examples

5. **Submit PR**

### Code Review Process

- At least 1 maintainer review required
- Address all feedback
- Keep PRs focused and manageable
- Be open to suggestions

## Areas for Contribution

### High Priority
- [ ] WordPress support
- [ ] Performance optimization
- [ ] Better error handling
- [ ] More comprehensive tests

### Medium Priority
- [ ] Additional CMS support
- [ ] UI/UX improvements
- [ ] Documentation
- [ ] Language translations

### Low Priority
- [ ] Code refactoring
- [ ] Aesthetic changes
- [ ] Optional features

## Testing Guidelines

### Unit Tests

```python
# tests/test_app.py
import pytest
from app import fetch_sitemap, calculate_semantic_relevance

def test_fetch_sitemap_valid_url():
    """Test fetching sitemap with valid URL"""
    urls = fetch_sitemap("https://example.com/sitemap.xml")
    assert len(urls) > 0
    assert all(isinstance(url, str) for url in urls)

def test_fetch_sitemap_invalid_url():
    """Test handling of invalid URL"""
    urls = fetch_sitemap("https://invalid-domain-12345.com/sitemap.xml")
    assert urls == []

def test_calculate_relevance():
    """Test relevance score calculation"""
    tags_dict = {
        "url1": ["seo", "ghost"],
        "url2": ["seo", "cms"]
    }
    result = calculate_semantic_relevance("url1", "url2", tags_dict)
    assert result['semantic_score'] > 0
```

### Integration Tests

```python
def test_full_analysis_flow():
    """Test complete analysis workflow"""
    # Setup
    sitemap_url = "https://example.com/sitemap.xml"
    article_url = "https://example.com/article/"
    
    # Execute
    urls = fetch_sitemap(sitemap_url)
    
    # Assert
    assert article_url in urls
```

## Documentation

### README Updates

- Keep it concise
- Use clear examples
- Include troubleshooting
- Add screenshots if helpful

### Code Comments

```python
def calculate_semantic_relevance(url1, url2, tags_dict):
    """
    Calculate semantic relevance between two URLs.
    
    Uses Jaccard similarity of tags (70% weight) and 
    URL path similarity (30% weight).
    
    Args:
        url1: First URL
        url2: Second URL
        tags_dict: Dict mapping URLs to their tags
        
    Returns:
        Dict with relevance scores:
            - semantic_score: 0-100
            - tag_score: 0-100
            - path_score: 0-100
    """
    # Implementation
```

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> Dict:
    """
    Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
        
    Examples:
        >>> result = my_function("test", 42)
        >>> result['key']
        'value'
    """
```

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (no functional changes)
- `refactor`: Code refactor
- `perf`: Performance improvement
- `test`: Test additions/updates
- `chore`: Build, CI, dependencies

### Example

```
feat(tag-extraction): add WordPress support

- Implement WordPress meta tag extraction
- Add support for custom post meta
- Include fallback to standard meta tags

Closes #45
```

## Performance Considerations

- Minimize external API calls
- Cache when appropriate
- Profile before optimizing
- Consider memory usage for large datasets

## Security Guidelines

1. Never commit secrets
2. Use environment variables
3. Validate user input
4. Sanitize URLs
5. Handle errors gracefully

## Questions?

- Open an issue
- Join discussions
- Check existing documentation
- Ask on [Discussions](https://github.com/yourusername/backlink-analyzer-ghost/discussions)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing! 🙏
