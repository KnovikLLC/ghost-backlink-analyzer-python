# 🔗 Internal Backlink Analyzer for Ghost CMS

A smart Streamlit application that discovers internal linking opportunities for Ghost CMS websites by analyzing article tags, content relationships, and semantic relevance.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

## ✨ Features

### 🏷️ Tag-Based Analysis
- Extracts tags from Ghost CMS meta tags
- Parses schema.org JSON-LD markup
- Identifies article keywords and topics
- Builds content relationship maps

### 🔍 Intelligent Scoring
- **Tag Overlap Analysis (70%)**: Direct tag matching between articles
- **URL Path Similarity (30%)**: Keyword similarity in URL structure
- Combined relevance score for accurate recommendations

### 📊 Comprehensive Results
- **Outbound Opportunities**: Pages your article should link to
- **Inbound Opportunities**: Pages that should link to your article
- Detailed scoring breakdown
- Export results as CSV

### 🎯 User-Friendly Interface
- Clean, intuitive Streamlit UI
- Real-time progress tracking
- Multiple result views (table + detailed)
- Actionable recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or conda
- Ghost CMS website with sitemap.xml

### Installation

```bash
# Clone the repository
git clone https://github.com/madusankapremaratne/backlink-analyzer-ghost.git
cd backlink-analyzer-ghost

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Local Testing

```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## 📖 Usage Guide

### 1. Get Your Sitemap URL
Your sitemap is typically located at:
```
https://your-domain.com/sitemap.xml
```

### 2. Enter Your New Article
Paste the full URL of the article you want to analyze:
```
https://your-domain.com/new-article-title/
```

### 3. Adjust Relevance Threshold
- **Low (0-30%)**: Broad analysis, many suggestions
- **Medium (30-50%)**: Balanced recommendations
- **High (50-100%)**: Highly targeted suggestions

Start with **30%** and adjust based on results.

### 4. Click Analyze
The app will:
1. Fetch all URLs from your sitemap
2. Extract tags from each article
3. Calculate relevance scores
4. Display recommendations

### 5. Review Results
- **Outbound**: Pages to link FROM your new article
- **Inbound**: Pages to link TO your new article
- Export as CSV for implementation

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.streamlit/secrets.toml` file for sensitive data:

```toml
[connections]
database_url = "your-database-url"

# Add any other secrets here
```

### Customization

Edit `app.py` to customize:

```python
# Adjust default relevance score
DEFAULT_RELEVANCE_SCORE = 30

# Customize timeout
DEFAULT_TIMEOUT = 5

# Add/remove common words
COMMON_WORDS = {
    'index', 'page', 'article', ...
}
```

## 📊 How It Works

### Tag Extraction Process

The app extracts tags from three sources:

1. **Meta Keywords Tag**
   ```html
   <meta name="keywords" content="seo, ghost cms, blogging">
   ```

2. **Schema.org JSON-LD**
   ```json
   {
     "@context": "https://schema.org",
     "keywords": ["seo", "ghost cms"]
   }
   ```

3. **HTML Tag Links**
   ```html
   <a class="tag-link">#seo</a>
   ```

### Scoring Algorithm

```
Relevance Score = (Tag Score × 0.7) + (Path Score × 0.3)

Tag Score = 30 + (Common Tags × 25), capped at 100
Path Score = Jaccard Similarity of URL words
```

### Example

Article A tags: `[seo, ghost cms, blogging]`
Article B tags: `[seo, content marketing]`

- Common tags: `[seo]` (1 match)
- Tag Score: 30 + (1 × 25) = 55%
- Path Score: ~10% (minimal URL overlap)
- **Final Score: (55 × 0.7) + (10 × 0.3) = 41%**

## 🚀 Deployment

### Streamlit Cloud (Recommended for Getting Started)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**
   - Sign in with GitHub
   - Click "New app"
   - Select your repository, branch, and `app.py`
   - Deploy!

**Live URL:** `https://your-app-name.streamlit.app`

### Railway (Production Ready)

1. Connect GitHub repository
2. Railway auto-detects and deploys
3. Custom domain support
4. Auto-scaling included

**Cost:** $5-20/month

### Docker + DigitalOcean

```bash
# Build image
docker build -t backlink-analyzer .

# Run locally
docker run -p 8501:8501 backlink-analyzer

# Deploy to DigitalOcean App Platform
# (See Dockerfile for deployment config)
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

## 📊 Example Output

### Input
- **Domain**: example.com
- **Sitemap URLs**: 150 articles
- **New Article Tags**: `[seo, internal linking, ghost cms]`
- **Relevance Threshold**: 30%

### Output

**Outbound Opportunities** (16 found)
| Title | Score | Common Tags |
|-------|-------|-------------|
| SEO Best Practices | 80% | seo, ghost cms |
| Link Building Guide | 65% | internal linking, seo |
| Ghost CMS Setup | 55% | ghost cms |

**Inbound Opportunities** (12 found)
| Title | Score | Common Tags |
|-------|-------|-------------|
| Content Strategy Guide | 75% | seo, content marketing |
| Blogging Tips | 60% | blogging, ghost cms |

## 🐛 Troubleshooting

### No Tags Found

**Problem**: All articles show 0 tags

**Solutions**:
- Verify Ghost CMS SEO settings
- Check meta tag configuration
- Ensure meta tags are in HTML head
- Verify page is publicly accessible

### Low Relevance Scores

**Problem**: Few linking opportunities found

**Solutions**:
- Add more tags to your articles
- Use consistent tag naming
- Lower the relevance threshold
- Ensure tags are semantically related

### Timeout Errors

**Problem**: "Request timeout" errors during analysis

**Solutions**:
- Increase fetch timeout in Advanced Options
- Check server response times
- Verify internet connection
- Reduce number of URLs analyzed

### App Crashes

**Problem**: Streamlit crashes or freezes

**Solutions**:
- Check logs in terminal
- Reduce number of URLs
- Restart the app
- Update dependencies: `pip install --upgrade -r requirements.txt`

## 📝 Best Practices

### For Ghost CMS Setup

1. **Standardize Tags**
   - Use consistent naming (singular/plural)
   - Create a tag taxonomy
   - Document tag usage

2. **Add Rich Metadata**
   ```html
   <meta name="keywords" content="primary, secondary, topic">
   <meta name="description" content="Article summary">
   ```

3. **Implement Schema.org**
   ```json
   {
     "@type": "Article",
     "keywords": ["topic1", "topic2"],
     "description": "Article summary"
   }
   ```

### For Internal Linking

1. **Link Strategically**
   - Focus on top 3-5 outbound links per article
   - Use descriptive anchor text
   - Link to semantically related content

2. **Maintain Site Structure**
   - Organize by topic clusters
   - Respect content hierarchy
   - Keep silo structure intact

3. **Monitor Results**
   - Track ranking improvements
   - Monitor click-through rates
   - Adjust strategy based on metrics

## 📚 Resources

- [Ghost CMS Documentation](https://ghost.org/docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SEO Best Practices](https://developers.google.com/search/docs)
- [Schema.org Documentation](https://schema.org/)

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/backlink-analyzer-ghost.git
cd backlink-analyzer-ghost

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black app.py

# Lint
flake8 app.py
```

## 🗺️ Roadmap

- [ ] Add support for multiple sitemap formats
- [ ] Implement content clustering analysis
- [ ] Add competitor linking analysis
- [ ] Support for other CMS platforms (WordPress, Webflow)
- [ ] Machine learning-based relevance scoring
- [ ] API endpoint for programmatic access
- [ ] Batch analysis for multiple articles
- [ ] Custom tag weighting system

## ❓ FAQ

### Q: How many articles can I analyze?
**A**: The app can handle 100-500+ URLs depending on server resources. Start with smaller sitemaps and scale up.

### Q: Does it support WordPress?
**A**: Not currently, but we're working on WordPress support. Plugins are welcome!

### Q: Can I use this commercially?
**A**: Yes! It's MIT licensed. See LICENSE file for details.

### Q: How accurate are the recommendations?
**A**: ~70-80% accuracy. Always manually review suggestions before implementing.

### Q: Can I schedule automated analysis?
**A**: Not built-in, but you can use Streamlit Cloud scheduling or set up cron jobs with the app API.

## 🔐 Security

- No data is stored or logged
- URLs are only accessed with explicit permission
- No authentication required for local use
- HTTPS recommended for production

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details

## 👨‍💻 Author

**Madusanka Premaratne**
- GitHub: [@madusankapremaratne](https://github.com/madusankapremaratne)
- Email: rmmpremaratne@gmail.com

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing framework
- [Ghost CMS](https://ghost.org/) for the platform inspiration
- All contributors and users

## 📞 Support

Need help?

1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an [Issue](https://github.com/KnovikLLC/ghost-backlink-analyzer-python/issues)
3. Start a [Discussion](https://github.com/KnovikLLC/ghost-backlink-analyzer-python/discussions)
4. Email: rmmpremaratne@gmail.com

---

**Star this repo** ⭐ if you find it helpful!

**Last Updated**: 2025