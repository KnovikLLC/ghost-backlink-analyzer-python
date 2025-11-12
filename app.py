"""
Enhanced Internal Backlink Analyzer for Ghost CMS
Advanced semantic analysis with differentiated linking strategies and diversity mechanisms.

Author: Madusanka Premaratne
Enhanced Version: 3.0
License: MIT
"""

import streamlit as st
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import pandas as pd
from typing import List, Dict, Tuple, Set
import re
from bs4 import BeautifulSoup
import time
import json
import numpy as np
from datetime import datetime
from collections import Counter
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Enhanced Backlink Analyzer (Ghost CMS)",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSTANTS
# ============================================================================

COMMON_WORDS = {
    'index', 'page', 'article', 'post', 'blog', 'category', 'tag',
    'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might'
}

DEFAULT_RELEVANCE_SCORE = 30
DEFAULT_TIMEOUT = 5
MAX_TIMEOUT = 15
MAX_LINKS_PER_SILO = 2  # Diversity constraint
DIVERSITY_PENALTY = 0.15  # 15% penalty for same-silo links after limit

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
    .score-high { color: #28a745; font-weight: bold; }
    .score-medium { color: #ffc107; font-weight: bold; }
    .score-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Enhanced Internal Backlink Analyzer v3.0")
st.markdown("**Advanced Semantic Analysis** • Differentiated linking strategies • Smart diversity mechanisms")

# ============================================================================
# ENHANCED HELPER FUNCTIONS
# ============================================================================

class ContentAnalyzer:
    """Advanced content analysis with TF-IDF and semantic similarity"""
    
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.urls = []
        
    def fit_content(self, content_dict: Dict[str, str]):
        """Fit TF-IDF vectorizer on all content"""
        self.urls = list(content_dict.keys())
        texts = list(content_dict.values())
        
        if not texts or all(not t for t in texts):
            return
        
        # Initialize TF-IDF with optimized parameters
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        except:
            self.tfidf_matrix = None
    
    def get_similarity(self, url1: str, url2: str) -> float:
        """Calculate cosine similarity between two URLs"""
        if self.tfidf_matrix is None or url1 not in self.urls or url2 not in self.urls:
            return 0.0
        
        idx1 = self.urls.index(url1)
        idx2 = self.urls.index(url2)
        
        similarity = cosine_similarity(
            self.tfidf_matrix[idx1:idx1+1],
            self.tfidf_matrix[idx2:idx2+1]
        )[0][0]
        
        return float(similarity * 100)  # Convert to percentage


def extract_silo_from_url(url: str) -> str:
    """Extract silo/category from URL path"""
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    
    if len(path_parts) > 0:
        # First path segment often indicates silo/category
        return path_parts[0].lower()
    return 'root'


def fetch_sitemap(sitemap_url: str) -> List[str]:
    """Fetch URLs from sitemap.xml with robust error handling"""
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        
        # Try to parse as XML
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            # Fallback to regex extraction
            content = response.text
            urls = re.findall(r'<loc>(https?://[^<]+)</loc>', content)
            if urls:
                st.success(f"✅ Recovered {len(urls)} URLs using pattern matching")
                return urls
            else:
                st.error(f"❌ Could not parse sitemap")
                return []
        
        # Handle namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace) if loc.text]
        
        if not urls:
            urls = [loc.text for loc in root.findall('.//loc') if loc.text]
        
        urls = [url for url in urls if url]
        
        if urls:
            st.success(f"✅ Successfully fetched {len(urls)} URLs from sitemap")
        
        return urls
        
    except Exception as e:
        st.error(f"❌ Error fetching sitemap: {str(e)}")
        return []


def fetch_page_content(url: str, timeout: int = DEFAULT_TIMEOUT) -> Dict:
    """
    Enhanced content extraction including title, description, tags, headings, and body text
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('meta', {'property': 'og:title'}) or soup.find('title')
        title = (
            title_elem.get('content')
            if title_elem and title_elem.get('content')
            else (title_elem.get_text(strip=True) if title_elem else "")
        )
        
        # Extract description
        desc_elem = soup.find('meta', {'name': 'description'})
        description = desc_elem.get('content', '') if desc_elem else ""
        
        # Extract tags
        tags = []
        
        # Method 1: Meta keywords
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            tags.extend([t.strip() for t in meta_keywords['content'].split(',')])
        
        # Method 2: Schema.org JSON-LD
        script_tags = soup.find_all('script', {'type': 'application/ld+json'})
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'keywords' in data:
                    keywords = data['keywords']
                    if isinstance(keywords, str):
                        tags.extend([k.strip() for k in keywords.split(',')])
                    elif isinstance(keywords, list):
                        tags.extend(keywords)
            except:
                pass
        
        # Method 3: Tag links
        tag_links = soup.find_all('a', {'class': re.compile(r'tag|label')})
        for tag in tag_links:
            tag_text = tag.get_text(strip=True)
            if tag_text and len(tag_text) < 50:
                tags.append(tag_text)
        
        # Clean tags
        tags = list(set([t.lower().strip() for t in tags if t and len(t.strip()) > 0]))
        
        # Extract headings
        headings = []
        for h_tag in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = h_tag.get_text(strip=True)
            if heading_text:
                headings.append(heading_text)
        
        # Extract body text (limit to main content)
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|post|article'))
        
        if main_content:
            body_text = main_content.get_text(separator=' ', strip=True)
        else:
            body_text = soup.get_text(separator=' ', strip=True)
        
        # Limit body text to reasonable length
        body_text = ' '.join(body_text.split()[:1000])
        
        # Extract publish date if available
        date_elem = soup.find('meta', {'property': 'article:published_time'}) or \
                   soup.find('time', {'datetime': True})
        
        publish_date = None
        if date_elem:
            date_str = date_elem.get('content') or date_elem.get('datetime')
            if date_str:
                try:
                    publish_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass
        
        # Calculate content depth metrics
        word_count = len(body_text.split())
        heading_count = len(headings)
        
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'headings': headings,
            'body_text': body_text,
            'word_count': word_count,
            'heading_count': heading_count,
            'publish_date': publish_date,
            'silo': extract_silo_from_url(url)
        }
        
    except Exception as e:
        return {
            'title': '',
            'description': '',
            'tags': [],
            'headings': [],
            'body_text': '',
            'word_count': 0,
            'heading_count': 0,
            'publish_date': None,
            'silo': extract_silo_from_url(url)
        }


def calculate_enhanced_relevance(
    url1: str,
    url2: str,
    content_cache: Dict,
    content_analyzer: ContentAnalyzer,
    link_direction: str = 'outbound'
) -> Dict:
    """
    Enhanced relevance calculation with multiple factors
    
    Factors considered:
    - Tag overlap (30%)
    - Content similarity via TF-IDF (30%)
    - URL path similarity (10%)
    - Content depth alignment (10%)
    - Temporal relevance (10%)
    - Silo diversity (10%)
    """
    
    content1 = content_cache.get(url1, {})
    content2 = content_cache.get(url2, {})
    
    # 1. Tag-based similarity
    tags1 = set(content1.get('tags', []))
    tags2 = set(content2.get('tags', []))
    
    tag_intersection = len(tags1 & tags2)
    if tag_intersection > 0:
        tag_score = min(100, 30 + (tag_intersection * 25))
    else:
        tag_score = 0
    
    # 2. Content similarity (TF-IDF)
    content_score = content_analyzer.get_similarity(url1, url2)
    
    # 3. URL path similarity
    path1 = extract_path(url1).lower()
    path2 = extract_path(url2).lower()
    
    words1 = set(re.findall(r'\b\w+\b', path1)) - COMMON_WORDS
    words2 = set(re.findall(r'\b\w+\b', path2)) - COMMON_WORDS
    
    if words1 and words2:
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        path_score = (intersection / union) * 100 if union > 0 else 0
    else:
        path_score = 0
    
    # 4. Content depth alignment
    wc1 = content1.get('word_count', 0)
    wc2 = content2.get('word_count', 0)
    
    if wc1 > 0 and wc2 > 0:
        depth_diff = abs(wc1 - wc2) / max(wc1, wc2)
        depth_score = (1 - depth_diff) * 100
    else:
        depth_score = 50  # Neutral score if no data
    
    # 5. Temporal relevance (for inbound links, prefer linking from newer to older)
    temporal_score = 50  # Default neutral
    date1 = content1.get('publish_date')
    date2 = content2.get('publish_date')
    
    if date1 and date2:
        if link_direction == 'inbound':
            # For inbound: source (url1) should be newer than target (url2)
            if date1 > date2:
                temporal_score = 70
            else:
                temporal_score = 30
        else:  # outbound
            # For outbound: prefer linking to established (older) content
            if date2 < date1:
                temporal_score = 70
            else:
                temporal_score = 50
    
    # 6. Silo diversity bonus
    silo1 = content1.get('silo', 'root')
    silo2 = content2.get('silo', 'root')
    
    if silo1 != silo2:
        diversity_score = 70  # Bonus for cross-silo linking
    else:
        diversity_score = 30  # Lower score for same-silo
    
    # Calculate weighted final score with direction-specific weights
    if link_direction == 'outbound':
        # For outbound: prioritize content relevance and established content
        weights = {
            'tag': 0.25,
            'content': 0.35,
            'path': 0.10,
            'depth': 0.10,
            'temporal': 0.10,
            'diversity': 0.10
        }
    else:  # inbound
        # For inbound: prioritize diverse sources and temporal relevance
        weights = {
            'tag': 0.20,
            'content': 0.30,
            'path': 0.10,
            'depth': 0.10,
            'temporal': 0.15,
            'diversity': 0.15
        }
    
    final_score = (
        tag_score * weights['tag'] +
        content_score * weights['content'] +
        path_score * weights['path'] +
        depth_score * weights['depth'] +
        temporal_score * weights['temporal'] +
        diversity_score * weights['diversity']
    )
    
    return {
        'final_score': round(final_score, 2),
        'tag_score': round(tag_score, 2),
        'content_score': round(content_score, 2),
        'path_score': round(path_score, 2),
        'depth_score': round(depth_score, 2),
        'temporal_score': round(temporal_score, 2),
        'diversity_score': round(diversity_score, 2),
        'common_tags': list(tags1 & tags2),
        'silo1': silo1,
        'silo2': silo2
    }


def extract_path(url: str) -> str:
    """Extract path from URL without domain"""
    parsed = urlparse(url)
    return parsed.path.strip('/')


def apply_diversity_penalties(opportunities: List[Dict], max_per_silo: int = MAX_LINKS_PER_SILO) -> List[Dict]:
    """
    Apply diversity penalties to avoid over-linking within same silos
    """
    silo_counts = Counter()
    
    for opp in opportunities:
        silo = opp.get('target_silo', opp.get('source_silo', 'root'))
        silo_counts[silo] += 1
        
        # Apply penalty if silo is overrepresented
        if silo_counts[silo] > max_per_silo:
            penalty_multiplier = 1 - (DIVERSITY_PENALTY * (silo_counts[silo] - max_per_silo))
            opp['final_score'] *= max(0.5, penalty_multiplier)  # Cap penalty at 50%
            opp['diversity_penalty'] = True
        else:
            opp['diversity_penalty'] = False
    
    return opportunities


def find_enhanced_outbound_opportunities(
    new_url: str,
    all_urls: List[str],
    content_cache: Dict,
    content_analyzer: ContentAnalyzer,
    min_relevance: float,
    max_results: int = 20
) -> List[Dict]:
    """
    Find outbound linking opportunities with enhanced logic
    
    Strategy:
    - Prioritize pillar/cornerstone content
    - Favor established (older) articles
    - Encourage cross-silo linking for topic mesh
    - Apply diversity to avoid repetitive patterns
    """
    opportunities = []
    
    for target_url in all_urls:
        if target_url == new_url:
            continue
        
        relevance = calculate_enhanced_relevance(
            new_url, target_url, content_cache, content_analyzer, 'outbound'
        )
        
        if relevance['final_score'] >= min_relevance:
            target_content = content_cache.get(target_url, {})
            
            # Boost score for pillar content (high word count, many headings)
            if target_content.get('word_count', 0) > 1500:
                relevance['final_score'] *= 1.1  # 10% boost for long-form content
            
            opportunities.append({
                'url': target_url,
                'title': target_content.get('title', ''),
                'final_score': relevance['final_score'],
                'tag_score': relevance['tag_score'],
                'content_score': relevance['content_score'],
                'path_score': relevance['path_score'],
                'depth_score': relevance['depth_score'],
                'temporal_score': relevance['temporal_score'],
                'diversity_score': relevance['diversity_score'],
                'common_tags': relevance['common_tags'],
                'target_silo': relevance['silo2'],
                'word_count': target_content.get('word_count', 0),
                'publish_date': target_content.get('publish_date')
            })
    
    # Sort by score
    opportunities = sorted(opportunities, key=lambda x: x['final_score'], reverse=True)
    
    # Apply diversity penalties
    opportunities = apply_diversity_penalties(opportunities[:max_results * 2])
    
    # Re-sort after penalties and return top results
    opportunities = sorted(opportunities, key=lambda x: x['final_score'], reverse=True)
    
    return opportunities[:max_results]


def find_enhanced_inbound_opportunities(
    new_url: str,
    all_urls: List[str],
    content_cache: Dict,
    content_analyzer: ContentAnalyzer,
    min_relevance: float,
    max_results: int = 20
) -> List[Dict]:
    """
    Find inbound linking opportunities with differentiated logic
    
    Strategy:
    - Prioritize newer content linking to this article
    - Look for content at similar depth/detail level
    - Encourage diverse source silos
    - Different scoring weights than outbound
    """
    opportunities = []
    new_content = content_cache.get(new_url, {})
    
    for source_url in all_urls:
        if source_url == new_url:
            continue
        
        relevance = calculate_enhanced_relevance(
            source_url, new_url, content_cache, content_analyzer, 'inbound'
        )
        
        if relevance['final_score'] >= min_relevance:
            source_content = content_cache.get(source_url, {})
            
            # Boost score for content published after the new article (if dates available)
            if new_content.get('publish_date') and source_content.get('publish_date'):
                if source_content['publish_date'] > new_content['publish_date']:
                    relevance['final_score'] *= 1.15  # 15% boost for newer content
            
            opportunities.append({
                'url': source_url,
                'title': source_content.get('title', ''),
                'final_score': relevance['final_score'],
                'tag_score': relevance['tag_score'],
                'content_score': relevance['content_score'],
                'path_score': relevance['path_score'],
                'depth_score': relevance['depth_score'],
                'temporal_score': relevance['temporal_score'],
                'diversity_score': relevance['diversity_score'],
                'common_tags': relevance['common_tags'],
                'source_silo': relevance['silo1'],
                'word_count': source_content.get('word_count', 0),
                'publish_date': source_content.get('publish_date')
            })
    
    # Sort by score
    opportunities = sorted(opportunities, key=lambda x: x['final_score'], reverse=True)
    
    # Apply stronger diversity for inbound to get links from various sources
    opportunities = apply_diversity_penalties(opportunities[:max_results * 2], max_per_silo=1)
    
    # Re-sort and return top results
    opportunities = sorted(opportunities, key=lambda x: x['final_score'], reverse=True)
    
    # Add variation: if multiple opportunities have very similar scores, shuffle slightly
    if len(opportunities) > 5:
        # Group by score ranges
        score_groups = []
        current_group = []
        last_score = opportunities[0]['final_score']
        
        for opp in opportunities:
            if abs(opp['final_score'] - last_score) < 5:  # Within 5% score range
                current_group.append(opp)
            else:
                if current_group:
                    score_groups.append(current_group)
                current_group = [opp]
                last_score = opp['final_score']
        
        if current_group:
            score_groups.append(current_group)
        
        # Shuffle within groups for variety
        import random
        random.seed(hash(new_url))  # Consistent shuffle per URL
        
        shuffled_opportunities = []
        for group in score_groups:
            if len(group) > 1:
                random.shuffle(group)
            shuffled_opportunities.extend(group)
        
        opportunities = shuffled_opportunities
    
    return opportunities[:max_results]


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

st.sidebar.markdown("### 🎯 Analysis Settings")

min_relevance_score = st.sidebar.slider(
    "Minimum Relevance Score (%)",
    min_value=0,
    max_value=100,
    value=DEFAULT_RELEVANCE_SCORE,
    step=5,
    help="Filter opportunities by minimum relevance score"
)

max_results = st.sidebar.number_input(
    "Max Results per Type",
    min_value=5,
    max_value=50,
    value=20,
    step=5,
    help="Maximum number of results to show"
)

st.sidebar.markdown("### ⚙️ Advanced Options")

analysis_mode = st.sidebar.selectbox(
    "Analysis Mode",
    ["Balanced", "Content-Focused", "Tag-Focused", "Diversity-Focused"],
    help="Choose analysis priority"
)

fetch_timeout = st.sidebar.slider(
    "Page Fetch Timeout (seconds)",
    min_value=2,
    max_value=MAX_TIMEOUT,
    value=DEFAULT_TIMEOUT,
    help="Time to wait for each page to load"
)

enable_tfidf = st.sidebar.checkbox(
    "Enable TF-IDF Content Analysis",
    value=True,
    help="Use advanced content similarity (slower but more accurate)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Version 3.0 Features")
st.sidebar.markdown("""
✅ **Differentiated Strategies**
- Unique logic for inbound vs outbound
- Direction-specific scoring weights

✅ **Advanced Semantics**
- TF-IDF content analysis
- Multi-factor relevance scoring

✅ **Smart Diversity**
- Avoids repetitive patterns
- Cross-silo linking bonus
- Variation in suggestions
""")

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

if st.sidebar.button("🔍 Analyze Internal Linking", type="primary", use_container_width=True):
    if not new_article_url or not sitemap_url:
        st.error("❌ Please provide both the new article URL and sitemap.xml URL")
    else:
        # Initialize containers for results
        content_cache = {}
        content_analyzer = ContentAnalyzer()
        
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
            # Fetch content with progress tracking
            st.markdown("---")
            st.subheader("📚 Analyzing Content...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Create columns for live metrics
            metric_cols = st.columns(4)
            metrics = {
                'pages': metric_cols[0].empty(),
                'tags': metric_cols[1].empty(),
                'words': metric_cols[2].empty(),
                'silos': metric_cols[3].empty()
            }
            
            total_tags = set()
            total_words = 0
            silos = set()
            
            for idx, url in enumerate(all_urls):
                status_text.text(f"Analyzing {idx + 1}/{len(all_urls)}: {url[:50]}...")
                progress = (idx + 1) / len(all_urls)
                progress_bar.progress(progress)
                
                # Fetch comprehensive content
                content = fetch_page_content(url, timeout=fetch_timeout)
                content_cache[url] = content
                
                # Update metrics
                total_tags.update(content.get('tags', []))
                total_words += content.get('word_count', 0)
                silos.add(content.get('silo', 'root'))
                
                # Update live metrics
                metrics['pages'].metric("Pages Analyzed", f"{idx + 1}/{len(all_urls)}")
                metrics['tags'].metric("Unique Tags", len(total_tags))
                metrics['words'].metric("Total Words", f"{total_words:,}")
                metrics['silos'].metric("Silos Found", len(silos))
                
                time.sleep(0.1)  # Rate limiting
            
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ Content analysis complete!")
            
            # Prepare TF-IDF analysis if enabled
            if enable_tfidf:
                with st.spinner("🧮 Building semantic model..."):
                    # Combine all text content for TF-IDF
                    text_content = {}
                    for url, content in content_cache.items():
                        combined_text = ' '.join([
                            content.get('title', ''),
                            content.get('description', ''),
                            ' '.join(content.get('headings', [])),
                            content.get('body_text', '')
                        ])
                        text_content[url] = combined_text
                    
                    content_analyzer.fit_content(text_content)
                    st.success("✅ Semantic model ready!")
            
            # Find opportunities with enhanced algorithms
            with st.spinner("🔍 Finding linking opportunities with advanced algorithms..."):
                outbound = find_enhanced_outbound_opportunities(
                    new_article_url, all_urls, content_cache, 
                    content_analyzer, min_relevance_score, max_results
                )
                
                inbound = find_enhanced_inbound_opportunities(
                    new_article_url, all_urls, content_cache,
                    content_analyzer, min_relevance_score, max_results
                )
            
            # Display enhanced metrics
            st.markdown("---")
            st.header("📊 Analysis Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            new_article_content = content_cache.get(new_article_url, {})
            
            with col1:
                st.metric("Total URLs", len(all_urls))
            with col2:
                st.metric("Article Tags", len(new_article_content.get('tags', [])))
            with col3:
                st.metric("Outbound Opportunities", len(outbound))
            with col4:
                st.metric("Inbound Opportunities", len(inbound))
            
            # Show article details
            if new_article_content:
                st.markdown("---")
                st.subheader("📄 Article Details")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Title:** {new_article_content.get('title', 'N/A')}")
                    st.markdown(f"**Silo:** `{new_article_content.get('silo', 'root')}`")
                with col2:
                    st.markdown(f"**Word Count:** {new_article_content.get('word_count', 0):,}")
                    st.markdown(f"**Headings:** {new_article_content.get('heading_count', 0)}")
                with col3:
                    if new_article_content.get('publish_date'):
                        st.markdown(f"**Published:** {new_article_content['publish_date'].strftime('%Y-%m-%d')}")
                    if new_article_content.get('tags'):
                        tags_html = " ".join([
                            f'<span class="tag-badge">{tag}</span>'
                            for tag in sorted(new_article_content['tags'])[:10]
                        ])
                        st.markdown("**Tags:**")
                        st.markdown(tags_html, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ====== OUTBOUND OPPORTUNITIES ======
            st.header("🔗 Outbound Linking Opportunities")
            st.markdown("**Strategy:** Link to established pillar content, encourage cross-silo connections")
            
            if outbound:
                # Create enhanced dataframe
                outbound_df = pd.DataFrame([{
                    'Title': opp['title'][:60] + '...' if len(opp['title']) > 60 else opp['title'],
                    'Silo': opp['target_silo'],
                    'Score': f"{opp['final_score']:.1f}%",
                    'Content Match': f"{opp['content_score']:.1f}%",
                    'Tags Match': f"{opp['tag_score']:.1f}%",
                    'Words': f"{opp['word_count']:,}" if opp['word_count'] else '-',
                    'Common Tags': ', '.join(opp['common_tags'][:3]) if opp['common_tags'] else '-',
                    'URL': opp['url']
                } for opp in outbound])
                
                st.dataframe(
                    outbound_df.drop('URL', axis=1),
                    use_container_width=True,
                    hide_index=True
                )
                
                with st.expander("📊 Detailed Scoring Breakdown"):
                    for idx, opp in enumerate(outbound[:10], 1):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{idx}. {opp['title']}**")
                            st.markdown(f"🔗 `{opp['url']}`")
                            
                            # Score breakdown
                            scores_text = (
                                f"**Overall:** {opp['final_score']:.1f}% | "
                                f"**Content:** {opp['content_score']:.1f}% | "
                                f"**Tags:** {opp['tag_score']:.1f}% | "
                                f"**Diversity:** {opp['diversity_score']:.1f}%"
                            )
                            st.markdown(scores_text)
                            
                            if opp.get('diversity_penalty'):
                                st.warning("⚠️ Diversity penalty applied (same silo over-representation)")
                        
                        with col2:
                            if opp['final_score'] >= 70:
                                st.markdown('<p class="score-high">Strong Match</p>', unsafe_allow_html=True)
                            elif opp['final_score'] >= 40:
                                st.markdown('<p class="score-medium">Good Match</p>', unsafe_allow_html=True)
                            else:
                                st.markdown('<p class="score-low">Fair Match</p>', unsafe_allow_html=True)
                        
                        st.markdown("---")
                
                # Download button
                csv = outbound_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Outbound Opportunities (CSV)",
                    data=csv,
                    file_name=f"outbound_opportunities_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No outbound opportunities found. Try lowering the relevance threshold or adding more tags.")
            
            st.markdown("---")
            
            # ====== INBOUND OPPORTUNITIES ======
            st.header("📥 Inbound Linking Opportunities")
            st.markdown("**Strategy:** Get links from diverse sources, prioritize newer content and different silos")
            
            if inbound:
                # Create enhanced dataframe
                inbound_df = pd.DataFrame([{
                    'Title': opp['title'][:60] + '...' if len(opp['title']) > 60 else opp['title'],
                    'Silo': opp['source_silo'],
                    'Score': f"{opp['final_score']:.1f}%",
                    'Content Match': f"{opp['content_score']:.1f}%",
                    'Tags Match': f"{opp['tag_score']:.1f}%",
                    'Words': f"{opp['word_count']:,}" if opp['word_count'] else '-',
                    'Common Tags': ', '.join(opp['common_tags'][:3]) if opp['common_tags'] else '-',
                    'URL': opp['url']
                } for opp in inbound])
                
                st.dataframe(
                    inbound_df.drop('URL', axis=1),
                    use_container_width=True,
                    hide_index=True
                )
                
                with st.expander("📊 Detailed Scoring Breakdown"):
                    for idx, opp in enumerate(inbound[:10], 1):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{idx}. {opp['title']}**")
                            st.markdown(f"🔗 `{opp['url']}`")
                            
                            # Score breakdown
                            scores_text = (
                                f"**Overall:** {opp['final_score']:.1f}% | "
                                f"**Content:** {opp['content_score']:.1f}% | "
                                f"**Tags:** {opp['tag_score']:.1f}% | "
                                f"**Temporal:** {opp['temporal_score']:.1f}% | "
                                f"**Diversity:** {opp['diversity_score']:.1f}%"
                            )
                            st.markdown(scores_text)
                            
                            if opp.get('diversity_penalty'):
                                st.warning("⚠️ Diversity penalty applied")
                        
                        with col2:
                            if opp['final_score'] >= 70:
                                st.markdown('<p class="score-high">Strong Match</p>', unsafe_allow_html=True)
                            elif opp['final_score'] >= 40:
                                st.markdown('<p class="score-medium">Good Match</p>', unsafe_allow_html=True)
                            else:
                                st.markdown('<p class="score-low">Fair Match</p>', unsafe_allow_html=True)
                        
                        st.markdown("---")
                
                # Download button
                csv = inbound_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Inbound Opportunities (CSV)",
                    data=csv,
                    file_name=f"inbound_opportunities_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No inbound opportunities found. Try lowering the relevance threshold.")
            
            # ====== INSIGHTS & RECOMMENDATIONS ======
            st.markdown("---")
            st.header("💡 Insights & Recommendations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔗 Outbound Strategy")
                if outbound:
                    # Analyze silo distribution
                    silo_dist = Counter([o['target_silo'] for o in outbound[:10]])
                    
                    st.markdown(f"""
                    ✅ **{len(outbound)} opportunities found**
                    
                    **Top Silos to Link To:**
                    {', '.join([f'`{s}` ({c})' for s, c in silo_dist.most_common(3)])}
                    
                    **Recommendations:**
                    - Implement top {min(5, len(outbound))} links
                    - Mix cross-silo and same-silo links
                    - Use descriptive anchor text with keywords
                    - Consider content depth alignment
                    """)
                else:
                    st.markdown("""
                    ⚠️ **Optimization needed**
                    
                    - Add more specific tags
                    - Increase content depth
                    - Lower threshold to find matches
                    """)
            
            with col2:
                st.subheader("📥 Inbound Strategy")
                if inbound:
                    # Analyze source diversity
                    source_silos = set([o['source_silo'] for o in inbound[:10]])
                    
                    st.markdown(f"""
                    ✅ **{len(inbound)} opportunities found**
                    
                    **Source Diversity:** {len(source_silos)} different silos
                    
                    **Recommendations:**
                    - Update top {min(5, len(inbound))} pages
                    - Prioritize diverse source silos
                    - Focus on newer content first
                    - Build gradual link equity
                    """)
                else:
                    st.markdown("""
                    ⚠️ **Optimization needed**
                    
                    - Review content positioning
                    - Ensure proper tag usage
                    - Consider content refresh
                    """)
            
            # Silo analysis
            if outbound or inbound:
                st.markdown("---")
                st.subheader("🗂️ Silo Analysis")
                
                all_silos = set()
                if outbound:
                    all_silos.update([o['target_silo'] for o in outbound])
                if inbound:
                    all_silos.update([o['source_silo'] for o in inbound])
                
                new_silo = new_article_content.get('silo', 'root')
                
                st.markdown(f"**Article Silo:** `{new_silo}`")
                st.markdown(f"**Related Silos:** {', '.join([f'`{s}`' for s in all_silos if s != new_silo][:5])}")
                
                if len(all_silos) > 1:
                    st.success("✅ Good cross-silo connectivity potential")
                else:
                    st.warning("⚠️ Limited to single silo - consider broader linking strategy")

# ============================================================================
# SIDEBAR HELP & VERSION INFO
# ============================================================================

st.sidebar.markdown("---")

with st.sidebar.expander("📈 What's New in v3.0"):
    st.markdown("""
    **Major Enhancements:**
    
    ✅ **Differentiated Strategies**
    - Unique algorithms for inbound vs outbound
    - Direction-specific scoring weights
    
    ✅ **Advanced Content Analysis**
    - TF-IDF vectorization
    - Cosine similarity scoring
    - Full content extraction
    
    ✅ **Smart Diversity**
    - Avoids repetitive same-silo patterns
    - Variation in suggestions
    - Cross-silo bonus
    
    ✅ **Multi-Factor Scoring**
    - Tag overlap (20-25%)
    - Content similarity (30-35%)
    - Temporal relevance (10-15%)
    - Silo diversity (10-15%)
    - Content depth (10%)
    - URL similarity (10%)
    """)

with st.sidebar.expander("🚀 Quick Tips"):
    st.markdown("""
    **For Best Results:**
    
    1. **Start with 30% threshold**
       - Provides broad analysis
       - Adjust based on results
    
    2. **Review top 5-10 matches**
       - Quality over quantity
       - Manual review recommended
    
    3. **Mix silo strategies**
       - 70% same-silo for relevance
       - 30% cross-silo for diversity
    
    4. **Update regularly**
       - Re-analyze after content updates
       - Track implementation results
    """)

with st.sidebar.expander("🔧 Troubleshooting"):
    st.markdown("""
    **Same results issue?**
    - v3.0 uses different algorithms for each direction
    - Check if content has sufficient variation
    
    **Repetitive patterns?**
    - Diversity penalties now applied
    - Suggestions vary with similar scores
    
    **No content scores?**
    - Enable TF-IDF analysis
    - Check if pages load correctly
    
    **Low relevance scores?**
    - Add more descriptive content
    - Use consistent tagging
    - Lower threshold to 20%
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; font-size: 0.8em; color: #666;">
<p><strong>Enhanced Backlink Analyzer v3.0</strong></p>
<p>Built by Knovik • Madusanka Premaratne</p>
<p>Advanced Semantic Analysis for Ghost CMS</p>
</div>
""", unsafe_allow_html=True)