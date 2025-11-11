# 🚀 Quick Start Guide

Get up and running with the Internal Backlink Analyzer in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- A Ghost CMS website with a sitemap.xml
- Git (for cloning the repository)

## Installation (Local)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/backlink-analyzer-ghost.git
cd backlink-analyzer-ghost
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

### 5. Open in Browser

Visit: `http://localhost:8501`

## First Analysis

### Step 1: Get Your Sitemap URL

Find your sitemap.xml (usually at):
```
https://yourdomain.com/sitemap.xml
```

### Step 2: Enter Details

In the left sidebar:
1. **New Article URL**: Paste the URL of your new article
2. **Sitemap URL**: Paste your sitemap URL
3. **Relevance Score**: Start with 30% (default)

### Step 3: Click Analyze

Click the blue "Analyze Internal Linking" button

### Step 4: Review Results

Wait for the analysis to complete (1-5 minutes depending on your site size)

**Results will show:**
- **Outbound Opportunities**: Pages to link FROM your article
- **Inbound Opportunities**: Pages to link TO your article
- Relevance scores and common tags

### Step 5: Export

Download results as CSV:
- 📥 Download Outbound (CSV)
- 📥 Download Inbound (CSV)

## Deploy Online (Free)

### Option A: Streamlit Cloud (Easiest)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

2. **Deploy**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repo and `app.py`
   - Deploy!

✅ Your app is live at: `https://your-app-name.streamlit.app`

### Option B: Railway ($5-20/month)

1. Push code to GitHub (same as above)
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Railway auto-deploys!

✅ Your app is live at: `https://your-app-domain.railway.app`

See [DEPLOYMENT.md](./DEPLOYMENT.md) for more options.

## Common Questions

### Q: How long does analysis take?

**A**: Depends on your site size:
- 50 URLs: ~1-2 minutes
- 100 URLs: ~2-3 minutes
- 500+ URLs: ~10+ minutes

### Q: Why are tags not being found?

**A**: Check:
1. Ghost CMS has tags added to articles
2. Meta tags are in HTML head
3. Article is publicly accessible
4. Relevance threshold isn't too high

### Q: Can I analyze multiple sites?

**A**: Yes! Just run the app multiple times with different sitemaps.

### Q: How do I use the results?

**A**:
1. Review the CSV files
2. Check top opportunities (80%+ score)
3. Manually verify relevance
4. Add links to your articles
5. Update Ghost CMS

### Q: Is my data safe?

**A**: Yes!
- No data is stored or logged
- All processing is local
- Streamlit Cloud doesn't retain data
- Open source code you can audit

## Troubleshooting

### "Module not found" Error

```bash
pip install --upgrade -r requirements.txt
```

### "Connection timeout" Error

1. Check internet connection
2. Verify sitemap URL is correct
3. Increase fetch timeout in Advanced Options

### App is slow

1. Reduce number of URLs analyzed
2. Upgrade to Railway or DigitalOcean
3. Enable caching (if deployed)

### No results found

1. Check relevance threshold (lower = more results)
2. Verify your articles have tags
3. Ensure tags are in meta tags

## Next Steps

1. **Customize**: Edit app.py for your needs
2. **Deploy**: Share your app with your team
3. **Integrate**: Add links based on recommendations
4. **Monitor**: Track SEO improvements

## Resources

- 📖 [Full Documentation](./README.md)
- 🚀 [Deployment Guide](./DEPLOYMENT.md)
- 🤝 [Contributing Guide](./CONTRIBUTING.md)
- 📞 [Support & Issues](https://github.com/yourusername/backlink-analyzer-ghost/issues)

## Tips for Best Results

### For Ghost CMS Setup

1. **Use consistent tags**
   - Singular or plural (pick one)
   - Same spelling/capitalization
   - Topic-focused tags

2. **Add keywords to meta tags**
   ```html
   <meta name="keywords" content="seo, blogging, ghost cms">
   ```

3. **Add schema.org markup**
   (Ghost does this automatically in most cases)

### For Analysis

1. **Start with high-value articles**
   - New pillar content
   - Core topic articles
   - Traffic drivers

2. **Review recommendations**
   - Manual verification is important
   - Check user intent
   - Consider context

3. **Implement strategically**
   - Aim for 3-5 internal links per article
   - Use descriptive anchor text
   - Maintain site structure

## Getting Help

- 🐛 **Found a bug?** → [Open issue](https://github.com/yourusername/backlink-analyzer-ghost/issues/new?template=bug_report.md)
- 💡 **Have an idea?** → [Feature request](https://github.com/yourusername/backlink-analyzer-ghost/issues/new?template=feature_request.md)
- 📚 **Need help?** → Check [README](./README.md) or open a [discussion](https://github.com/yourusername/backlink-analyzer-ghost/discussions)

---

**Happy analyzing! 🎉**

Questions? Start with the [README](./README.md) or join our [discussions](https://github.com/yourusername/backlink-analyzer-ghost/discussions).
