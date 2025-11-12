"""
Internal Backlink Analyzer for Ghost CMS
Discover internal linking opportunities based on Ghost CMS tags and content relationships.

Author: Madusanka Premaratne
License: MIT
"""

import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import pandas as pd
from typing import List, Dict, Tuple
import re
from bs4 import BeautifulSoup
import time
import json

# Page configuration
st.set_page_config(
    page_title="Internal Backlink Analyzer (Ghost CMS)",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSTANTS
# ============================================================================

COMMON_WORDS = {
    'index', 'page', 'article', 'post', 'blog', 'category', 'tag',
    'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with'
}

DEFAULT_RELEVANCE_SCORE = 30
DEFAULT_TIMEOUT = 5
MAX_TIMEOUT = 15

# ============================================================================
# STYLING & BRANDING
# ============================================================================

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .tag-badge {
        display: inline-block;
        background-color: #e1f5ff;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 2px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Internal Backlink Opportunity Analyzer")
st.markdown("**For Ghost CMS** • Discover internal linking opportunities based on tags and content relationships")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def fetch_sitemap(sitemap_url: str) -> List[str]:
    """
    Fetch URLs from sitemap.xml with robust error handling for malformed XML
    
    Args:
        sitemap_url: URL to the sitemap.xml file
        
    Returns:
        List of URLs from the sitemap
    """
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        
        # Try to parse as XML
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            # If XML parsing fails, try to fix common issues
            content = response.text
            
            # Try to fix common XML issues
            st.warning(f"⚠️ XML parsing error on line {e.position[0]}: {e.msg}")
            st.info("Attempting to recover from malformed XML...")
            
            # Try removing invalid characters or fixing common issues
            try:
                # Try parsing with error recovery
                from xml.etree.ElementTree import XMLParser
                parser = XMLParser()
                parser.entity = {}
                root = ET.fromstring(content)
            except:
                # Last attempt: extract URLs with regex
                import re
                urls = re.findall(r'<loc>(https?://[^<]+)</loc>', content)
                if urls:
                    st.success(f"✅ Recovered {len(urls)} URLs using pattern matching")
                    return urls
                else:
                    st.error(f"❌ Could not parse sitemap. Error: {e.msg} at line {e.position[0]}, column {e.position[1]}")
                    return []
        
        # Handle namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace) if loc.text]
        
        # Try without namespace if empty
        if not urls:
            urls = [loc.text for loc in root.findall('.//loc') if loc.text]
        
        # Filter out None and empty values
        urls = [url for url in urls if url]
        
        if urls:
            st.success(f"✅ Successfully fetched {len(urls)} URLs from sitemap")
        
        return urls
        
    except requests.exceptions.Timeout:
        st.error("❌ Timeout: Sitemap took too long to load (>10 seconds)")
        return []
    except requests.exceptions.ConnectionError:
        st.error("❌ Connection Error: Could not reach the sitemap URL")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request Error: {e}")
        return []
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return []


def extract_path(url: str) -> str:
    """Extract path from URL without domain"""
    parsed = urlparse(url)
    return parsed.path.strip('/')


def fetch_page_tags(url: str, timeout: int = DEFAULT_TIMEOUT) -> List[str]:
    """
    Extract tags from Ghost CMS page
    
    Looks for tags in:
    1. Meta keywords tag
    2. Schema.org JSON-LD markup
    3. Ghost tag links in HTML
    
    Args:
        url: Page URL
        timeout: Request timeout in seconds
        
    Returns:
        List of tags found on the page
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        tags = []
        
        # Method 1: Meta keywords tag
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            tags.extend([t.strip() for t in meta_keywords['content'].split(',')])
        
        # Method 2: Schema.org JSON-LD markup
        script_tags = soup.find_all('script', {'type': 'application/ld+json'})
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'keywords' in data:
                        keywords = data['keywords']
                        if isinstance(keywords, str):
                            tags.extend([k.strip() for k in keywords.split(',')])
                        elif isinstance(keywords, list):
                            tags.extend(keywords)
            except:
                pass
        
        # Method 3: Ghost tag links
        tag_links = soup.find_all('a', {'class': re.compile(r'tag|label')})
        for tag in tag_links:
            tag_text = tag.get_text(strip=True)
            if tag_text and len(tag_text) < 50:
                tags.append(tag_text)
        
        # Clean and deduplicate tags
        tags = [t.lower().strip() for t in tags if t and len(t.strip()) > 0]
        tags = list(set(tags))
        
        return tags
    except Exception:
        return []


def get_page_title_and_description(url: str) -> Tuple[str, str]:
    """
    Extract title and description from page
    
    Args:
        url: Page URL
        
    Returns:
        Tuple of (title, description)
    """
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get title from og:title or title tag
        title_elem = soup.find('meta', {'property': 'og:title'}) or soup.find('title')
        title_text = (
            title_elem.get('content')
            if title_elem and title_elem.get('content')
            else (title_elem.get_text(strip=True) if title_elem else "")
        )
        
        # Get description from meta tag
        desc_elem = soup.find('meta', {'name': 'description'})
        desc_text = desc_elem.get('content', '') if desc_elem else ""
        
        return title_text, desc_text
    except Exception:
        return "", ""


def calculate_semantic_relevance(
    url1: str,
    url2: str,
    tags_dict: Dict[str, List[str]]
) -> Dict:
    """
    Calculate semantic relevance between two URLs
    
    Uses tag overlap (70% weight) and URL path similarity (30% weight)
    
    Args:
        url1: First URL
        url2: Second URL
        tags_dict: Dictionary mapping URLs to their tags
        
    Returns:
        Dictionary with relevance scores
    """
    path1 = extract_path(url1).lower()
    path2 = extract_path(url2).lower()
    
    # Get tags for both URLs
    tags1 = set(tags_dict.get(url1, []))
    tags2 = set(tags_dict.get(url2, []))
    
    # Extract meaningful words from paths
    words1 = set(re.findall(r'\b\w+\b', path1)) - COMMON_WORDS
    words2 = set(re.findall(r'\b\w+\b', path2)) - COMMON_WORDS
    
    # Calculate path similarity score
    if words1 and words2:
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        path_score = (intersection / union) * 100 if union > 0 else 0
    else:
        path_score = 0
    
    # Calculate tag-based relevance score
    tag_intersection = len(tags1 & tags2)
    if tag_intersection > 0:
        tag_score = min(100, 30 + (tag_intersection * 25))
    else:
        tag_score = 0
    
    # Combined score: 70% tags, 30% path similarity
    combined_semantic = (tag_score * 0.7) + (path_score * 0.3) if (tags1 or tags2) else path_score
    
    return {
        'semantic_score': round(combined_semantic, 2),
        'tag_score': round(tag_score, 2),
        'path_score': round(path_score, 2),
        'common_tags': list(tags1 & tags2),
        'tags1': list(tags1),
        'tags2': list(tags2)
    }


def find_outbound_opportunities(
    new_url: str,
    all_urls: List[str],
    tags_dict: Dict[str, List[str]],
    content_cache: Dict[str, Tuple[str, str]],
    min_relevance: float
) -> List[Dict]:
    """Find pages that the new article should link to"""
    opportunities = []
    
    for target_url in all_urls:
        if target_url == new_url:
            continue
        
        relevance = calculate_semantic_relevance(new_url, target_url, tags_dict)
        semantic_score = relevance['semantic_score']
        
        if semantic_score >= min_relevance:
            title, _ = content_cache.get(target_url, ("", ""))
            opportunities.append({
                'url': target_url,
                'title': title,
                'semantic_score': semantic_score,
                'tag_score': relevance['tag_score'],
                'path_score': relevance['path_score'],
                'common_tags': relevance['common_tags'],
                'target_tags': relevance['tags2']
            })
    
    return sorted(opportunities, key=lambda x: x['semantic_score'], reverse=True)


def find_inbound_opportunities(
    new_url: str,
    all_urls: List[str],
    tags_dict: Dict[str, List[str]],
    content_cache: Dict[str, Tuple[str, str]],
    min_relevance: float
) -> List[Dict]:
    """Find pages that should link to the new article"""
    opportunities = []
    
    for source_url in all_urls:
        if source_url == new_url:
            continue
        
        relevance = calculate_semantic_relevance(source_url, new_url, tags_dict)
        semantic_score = relevance['semantic_score']
        
        if semantic_score >= min_relevance:
            title, _ = content_cache.get(source_url, ("", ""))
            opportunities.append({
                'url': source_url,
                'title': title,
                'semantic_score': semantic_score,
                'tag_score': relevance['tag_score'],
                'path_score': relevance['path_score'],
                'common_tags': relevance['common_tags'],
                'source_tags': relevance['tags1']
            })
    
    return sorted(opportunities, key=lambda x: x['semantic_score'], reverse=True)


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

st.sidebar.header("⚙️ Configuration")

new_article_url = st.sidebar.text_input(
    "New Article URL",
    placeholder="https://example.com/article-title/",
    help="Full URL of the new article you want to analyze"
)

sitemap_url = st.sidebar.text_input(
    "Sitemap.xml URL",
    placeholder="https://example.com/sitemap.xml",
    help="URL to your sitemap.xml file"
)

min_relevance_score = st.sidebar.slider(
    "Minimum Relevance Score (%)",
    min_value=0,
    max_value=100,
    value=DEFAULT_RELEVANCE_SCORE,
    step=5,
    help="Filter opportunities by minimum relevance score"
)

st.sidebar.markdown("### ⚙️ Advanced Options")
fetch_timeout = st.sidebar.slider(
    "Page Fetch Timeout (seconds)",
    min_value=2,
    max_value=MAX_TIMEOUT,
    value=DEFAULT_TIMEOUT,
    help="Time to wait for each page to load"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**💡 Pro Tips:**")
st.sidebar.markdown("""
- Start with 30% relevance threshold for broad analysis
- Use 50%+ for highly targeted opportunities
- Ensure all URLs are publicly accessible
- Ghost CMS tags must be in meta tags or schema.org markup
""")

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

if st.sidebar.button("🔍 Analyze Internal Linking", type="primary", use_container_width=True):
    if not new_article_url or not sitemap_url:
        st.error("❌ Please provide both the new article URL and sitemap.xml URL")
    else:
        # Fetch sitemap
        with st.spinner("🔄 Fetching sitemap..."):
            all_urls = fetch_sitemap(sitemap_url)
            
            if not all_urls:
                st.error("❌ Could not fetch URLs from sitemap. Please check the URL.")
            else:
                st.success(f"✅ Found {len(all_urls)} URLs in sitemap")
                
                if new_article_url not in all_urls:
                    st.warning("⚠️ New article URL not found in sitemap. Adding it to analysis.")
                    all_urls.append(new_article_url)
        
        if all_urls:
            # Fetch tags and content
            st.markdown("---")
            st.subheader("🏷️ Fetching Tags and Content...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            tags_dict = {}
            content_cache = {}
            
            for idx, url in enumerate(all_urls):
                status_text.text(f"Analyzing {idx + 1}/{len(all_urls)}: {url}")
                progress = (idx + 1) / len(all_urls)
                progress_bar.progress(progress)
                
                tags_dict[url] = fetch_page_tags(url, timeout=fetch_timeout)
                title, desc = get_page_title_and_description(url)
                content_cache[url] = (title, desc)
                
                time.sleep(0.3)
            
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ Tags and content fetched successfully!")
            
            # Find opportunities
            with st.spinner("🔍 Finding linking opportunities..."):
                outbound = find_outbound_opportunities(
                    new_article_url, all_urls, tags_dict, content_cache, min_relevance_score
                )
                inbound = find_inbound_opportunities(
                    new_article_url, all_urls, tags_dict, content_cache, min_relevance_score
                )
            
            # Display metrics
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total URLs", len(all_urls))
            with col2:
                new_article_tags = tags_dict.get(new_article_url, [])
                st.metric("Article Tags", len(new_article_tags))
            with col3:
                st.metric("Outbound Opportunities", len(outbound))
            with col4:
                st.metric("Inbound Opportunities", len(inbound))
            
            st.markdown("---")
            
            # Show article tags
            if new_article_tags:
                st.subheader("🏷️ Article Tags")
                tags_html = " ".join([
                    f'<span class="tag-badge">{tag}</span>'
                    for tag in sorted(new_article_tags)
                ])
                st.markdown(tags_html, unsafe_allow_html=True)
                st.markdown("---")
            
            # ====== OUTBOUND OPPORTUNITIES ======
            st.header("🔗 Outbound Linking Opportunities")
            st.markdown("Pages that your new article should link to:")
            
            if outbound:
                outbound_df = pd.DataFrame([{
                    'Title': opp['title'][:50] + '...' if len(opp['title']) > 50 else opp['title'],
                    'URL': opp['url'],
                    'Score': opp['semantic_score'],
                    'Tag Score': opp['tag_score'],
                    'Common Tags': ', '.join(opp['common_tags']) if opp['common_tags'] else '-'
                } for opp in outbound])
                
                st.dataframe(outbound_df, use_container_width=True, hide_index=True)
                
                with st.expander("📄 Detailed View"):
                    for idx, opp in enumerate(outbound, 1):
                        st.markdown(f"### {idx}. {opp['title']}")
                        st.markdown(f"**URL:** `{opp['url']}`")
                        st.markdown(f"**Score:** {opp['semantic_score']}% | "
                                  f"**Tag Score:** {opp['tag_score']}% | "
                                  f"**Path Score:** {opp['path_score']}%")
                        
                        if opp['common_tags']:
                            tags_display = ", ".join(opp['common_tags'])
                            st.markdown(f"**Common Tags:** {tags_display}")
                        st.markdown("---")
                
                csv = outbound_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Outbound (CSV)",
                    data=csv,
                    file_name="outbound_opportunities.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No outbound opportunities found above the relevance threshold.")
            
            st.markdown("---")
            
            # ====== INBOUND OPPORTUNITIES ======
            st.header("📥 Inbound Linking Opportunities")
            st.markdown("Pages that should link back to your new article:")
            
            if inbound:
                inbound_df = pd.DataFrame([{
                    'Title': opp['title'][:50] + '...' if len(opp['title']) > 50 else opp['title'],
                    'URL': opp['url'],
                    'Score': opp['semantic_score'],
                    'Tag Score': opp['tag_score'],
                    'Common Tags': ', '.join(opp['common_tags']) if opp['common_tags'] else '-'
                } for opp in inbound])
                
                st.dataframe(inbound_df, use_container_width=True, hide_index=True)
                
                with st.expander("📄 Detailed View"):
                    for idx, opp in enumerate(inbound, 1):
                        st.markdown(f"### {idx}. {opp['title']}")
                        st.markdown(f"**URL:** `{opp['url']}`")
                        st.markdown(f"**Score:** {opp['semantic_score']}% | "
                                  f"**Tag Score:** {opp['tag_score']}% | "
                                  f"**Path Score:** {opp['path_score']}%")
                        
                        if opp['common_tags']:
                            tags_display = ", ".join(opp['common_tags'])
                            st.markdown(f"**Common Tags:** {tags_display}")
                        st.markdown("---")
                
                csv = inbound_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Inbound (CSV)",
                    data=csv,
                    file_name="inbound_opportunities.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No inbound opportunities found above the relevance threshold.")
            
            # ====== SUMMARY & RECOMMENDATIONS ======
            st.markdown("---")
            st.header("📋 Summary & Recommendations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔗 Outbound Strategy")
                if outbound:
                    st.markdown(f"""
                    ✅ **{len(outbound)} opportunities found**
                    
                    - Link to top {min(5, len(outbound))} pages from your article
                    - Common tags = strong topical relevance
                    - High tag score = better anchor text match
                    - Target 3-5 internal links per article
                    """)
                else:
                    st.markdown("""
                    ⚠️ **No opportunities found**
                    
                    - Add more tags to your article
                    - Review tag naming consistency
                    - Lower relevance threshold
                    """)
            
            with col2:
                st.subheader("📥 Inbound Strategy")
                if inbound:
                    st.markdown(f"""
                    ✅ **{len(inbound)} opportunities found**
                    
                    - Get links from top {min(5, len(inbound))} pages
                    - High tag overlap = strong relevance
                    - Link from related content areas
                    - Improves authority distribution
                    """)
                else:
                    st.markdown("""
                    ⚠️ **No opportunities found**
                    
                    - Article may need more specific tags
                    - Ensure tag consistency across site
                    - Review article topic relevance
                    """)

# ============================================================================
# SIDEBAR HELP & INFO
# ============================================================================

st.sidebar.markdown("---")

with st.sidebar.expander("ℹ️ How It Works"):
    st.markdown("""
    **Tag Extraction:**
    - Reads Ghost CMS meta tags
    - Parses schema.org JSON-LD markup
    - Identifies article keywords
    
    **Scoring System:**
    - Tag overlap (70% weight) = primary factor
    - URL path similarity (30% weight) = secondary
    - Higher scores = stronger relevance
    
    **Recommendations:**
    - Manual review required
    - Consider user intent
    - Verify tag accuracy
    """)

with st.sidebar.expander("🚀 Quick Start"):
    st.markdown("""
    1. Get your sitemap URL (usually `/sitemap.xml`)
    2. Paste new article URL
    3. Set relevance threshold (start at 30%)
    4. Click **Analyze**
    5. Review recommendations
    6. Export as CSV for implementation
    """)

with st.sidebar.expander("🔧 Troubleshooting"):
    st.markdown("""
    **No tags found?**
    - Verify Ghost CMS SEO settings
    - Check meta tag configuration
    - Test page is publicly accessible
    
    **Low scores?**
    - Use more specific tags
    - Standardize tag naming
    - Lower relevance threshold
    
    **Timeout errors?**
    - Increase fetch timeout
    - Check server response times
    - Verify internet connection
    
    **Need help?**
    - See GitHub: [backlink-analyzer-ghost](https://github.com)
    - Open an issue for bugs
    """)

with st.sidebar.expander("📚 Learn More"):
    st.markdown("""
    **Internal Linking Best Practices:**
    - Use descriptive anchor text
    - Link to semantically related content
    - Maintain consistent site structure
    - Improve crawlability
    - Distribute page authority
    
    **Ghost CMS Tips:**
    - Always add tags to articles
    - Use consistent tag naming
    - Organize by topic clusters
    - Review SEO settings
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; font-size: 0.8em; color: #666;">
<p><strong>Internal Backlink Analyzer | Knovik | Madusanka Premaratne</strong></p>
<p>Built for Ghost CMS</p>
<p><a href="https://github.com/KnovikLLC/ghost-backlink-analyzer-python" target="_blank">GitHub Repo</a> • 
<a href="#" target="_blank">Docs</a></p>
</div>
""", unsafe_allow_html=True)