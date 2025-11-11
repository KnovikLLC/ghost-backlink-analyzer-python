# 🚀 Deployment Guide

Complete guide for deploying the Internal Backlink Analyzer to production.

## Quick Comparison

| Platform | Cost | Setup Time | Best For |
|----------|------|-----------|----------|
| **Streamlit Cloud** | FREE | 5 min | Quick demos, testing |
| **Railway** | $5-20/mo | 10 min | Small-medium projects |
| **DigitalOcean** | $5+/mo | 15 min | Production apps |
| **Docker** | Varies | 20 min | Maximum flexibility |

---

## Option 1: Streamlit Cloud (Recommended for Starting)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Internal Backlink Analyzer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/backlink-analyzer-ghost.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: `YOUR_USERNAME/backlink-analyzer-ghost`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **Deploy**

### Step 3: Access Your App

Your app is now live at: `https://your-app-name.streamlit.app`

### Pros ✅
- Completely free
- Automatic SSL/HTTPS
- Auto-deploy from GitHub
- Built-in analytics

### Cons ❌
- Limited to 1GB RAM
- Slower for large datasets
- Timeout after 1 hour inactivity

---

## Option 2: Railway (Production Ready)

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub or email

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub"**
3. Connect your GitHub account
4. Select `backlink-analyzer-ghost` repository
5. Railway auto-detects and configures
6. Click **Deploy**

### Step 3: Custom Domain (Optional)

1. Go to project settings
2. Click **"Custom Domain"**
3. Add your domain (e.g., `analyzer.yourdomain.com`)
4. Update DNS records (instructions provided)

### Pros ✅
- Very affordable ($5-20/month)
- Good performance
- Auto-scaling
- GitHub integration
- Easy custom domain

### Cons ❌
- Not free
- Fewer features than enterprise options

**Estimated Cost**: $5-20/month depending on usage

---

## Option 3: DigitalOcean App Platform (Professional)

### Step 1: Create DigitalOcean Account

1. Sign up at [digitalocean.com](https://digitalocean.com)
2. Add billing information

### Step 2: Create App

1. Go to **App Platform**
2. Click **"Create App"**
3. Select **"GitHub"** as source
4. Connect GitHub account
5. Select `backlink-analyzer-ghost` repository
6. Configure:
   - **Branch**: `main`
   - **Build command**: (auto-detected)
   - **Run command**: `streamlit run app.py --server.port 8080`

### Step 3: Configure Environment

1. Set environment variables if needed
2. Add custom domain
3. Configure SSL/TLS

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait for build to complete
3. Access your app at provided URL

### Pros ✅
- Professional hosting
- Excellent uptime (99.99%)
- Custom domains included
- Environment variables
- Auto-scaling
- Better performance

### Cons ❌
- Not free ($5+/month)
- Slightly steeper learning curve

**Estimated Cost**: $5-30/month depending on resources

---

## Option 4: Docker + Manual Deployment

### Step 1: Build Docker Image

```bash
docker build -t backlink-analyzer:latest .
```

### Step 2: Test Locally

```bash
docker run -p 8501:8501 backlink-analyzer:latest
```

Visit `http://localhost:8501`

### Step 3: Push to Docker Registry

```bash
# Docker Hub
docker tag backlink-analyzer:latest yourusername/backlink-analyzer:latest
docker push yourusername/backlink-analyzer:latest

# Or GitHub Container Registry
docker tag backlink-analyzer:latest ghcr.io/yourusername/backlink-analyzer:latest
docker push ghcr.io/yourusername/backlink-analyzer:latest
```

### Step 4: Deploy

Deploy to any container hosting:
- **DigitalOcean App Platform**
- **AWS ECS / ECR**
- **Google Cloud Run**
- **Azure Container Instances**
- **Kubernetes cluster**

### Docker Deployment Example (DigitalOcean)

1. Go to App Platform
2. Select **Container Registry** as source
3. Select your image
4. Configure port: `8501`
5. Deploy!

---

## Environment Variables

Create `.streamlit/secrets.toml` for configuration:

```toml
# Database (if needed)
[connections]
database_url = "postgresql://..."

# API Keys
api_key = "your-api-key"
```

Access in code:

```python
import streamlit as st
api_key = st.secrets.get("api_key", None)
```

---

## Custom Domain Setup

### For Streamlit Cloud

1. In app settings → **Custom domain**
2. Add your domain
3. Update DNS CNAME record pointing to:
   ```
   your-app-name.streamlit.app
   ```

### For Railway/DigitalOcean

1. In project settings → **Domains**
2. Add your domain
3. Update DNS CNAME or A record
4. SSL certificate auto-provisioned

### DNS Configuration

**CNAME Record:**
```
analytics.yourdomain.com  CNAME  your-app-domain.com
```

**A Record:**
```
analytics.yourdomain.com  A  123.45.67.89
```

---

## Monitoring & Maintenance

### View Logs

**Streamlit Cloud:**
- App settings → Manage app → "Logs"

**Railway:**
- Project dashboard → Deployment logs

**DigitalOcean:**
- App Platform → Logs tab

### Update Code

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Auto-deployed! (usually within 1-2 minutes)
```

### Monitor Performance

- Check response times
- Monitor memory usage
- Review error logs
- Track user metrics

### Scaling

If app becomes slower:

**Streamlit Cloud:**
- Limited scaling, consider upgrading to paid tier

**Railway/DigitalOcean:**
- Increase instance size
- Enable auto-scaling
- Add caching

---

## Troubleshooting

### "Module not found" Error

```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
- Ensure `requirements.txt` in root directory
- Check all dependencies listed
- Redeploy after fixing

### "Timeout" Errors

```
requests.exceptions.ConnectTimeout
```

**Solution:**
- Increase fetch timeout in app
- Check server status
- Reduce number of URLs analyzed
- Increase platform resources

### "Out of Memory" Error

```
MemoryError
```

**Solution:**
- Upgrade platform tier
- Reduce dataset size
- Enable caching
- Stream large results

### DNS Not Resolving

**Solution:**
- Wait 24-48 hours for DNS propagation
- Verify DNS records are correct
- Clear browser cache
- Try different device/browser

---

## Performance Tips

### For Streamlit Cloud

1. **Reduce Data Size**
   - Analyze fewer URLs at a time
   - Use pagination

2. **Enable Caching**
   ```python
   @st.cache_data(ttl=3600)
   def fetch_sitemap(url):
       # Your code
   ```

3. **Optimize Assets**
   - Minimize image sizes
   - Use efficient data formats

### For Production (Railway/DigitalOcean)

1. **Increase Resources**
   - More CPU/RAM
   - Better network

2. **Enable CDN**
   - Cache static assets
   - Reduce latency

3. **Database Optimization**
   - Index frequently queried fields
   - Archive old data

---

## Backup & Recovery

### GitHub as Backup

```bash
# Your code is automatically backed up in GitHub
# To restore:
git clone https://github.com/yourusername/backlink-analyzer-ghost.git
```

### Scheduled Backups

For sensitive data, set up automated backups:
- GitHub Actions
- Cloud provider snapshots
- External backup service

---

## Security Best Practices

1. **Never commit secrets**
   ```bash
   # Use .gitignore
   .streamlit/secrets.toml
   .env
   ```

2. **Use environment variables**
   ```python
   import os
   api_key = os.getenv('API_KEY')
   ```

3. **Enable HTTPS** (auto-configured on most platforms)

4. **Regular updates**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## Cost Optimization

### Streamlit Cloud
- Free tier is sufficient for most uses

### Railway
- Pay as you go, typically $5-10/month
- Optimize by reducing idle time

### DigitalOcean
- Start with $5/month droplet
- Scale up as needed

### Docker
- Free to build and run
- Only pay for hosting platform

---

## Next Steps

1. **Choose your platform** based on your needs
2. **Follow deployment steps** for your chosen option
3. **Set up monitoring** to track performance
4. **Gather feedback** and iterate
5. **Scale** as usage grows

## Support

For deployment issues:

1. Check platform documentation
2. Review application logs
3. Open an issue on GitHub
4. Contact platform support

---

**Happy deploying! 🚀**
