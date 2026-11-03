import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# Pre-known high authority platforms for instant high-DA backlinks
HIGH_AUTHORITY_PLATFORMS = [
    {"domain": "telegra.ph", "name": "Telegraph (By Telegram)", "da": 92, "type": "Web 2.0 Article Backlink"},
    {"domain": "hashnode.dev", "name": "Hashnode Community", "da": 88, "type": "Tech Publication Backlink"},
    {"domain": "dev.to", "name": "Dev Community", "da": 89, "type": "Article Discussion Backlink"},
    {"domain": "medium.com", "name": "Medium Publications", "da": 95, "type": "Story Reference Backlink"},
    {"domain": "quora.com", "name": "Quora Answers", "da": 93, "type": "Contextual Q&A Backlink"},
    {"domain": "github.com", "name": "GitHub Gist & Projects", "da": 96, "type": "Repository Resource Link"}
]


def extract_website_niche(website_url):
    """
    Scrapes the user's website to automatically understand its niche, title, and keywords.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    if not website_url.startswith("http"):
        website_url = "https://" + website_url

    try:
        response = requests.get(website_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        # Extract headings for topical context
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2"])[:4] if h.get_text(strip=True)]
        
        # Combine text to derive search keywords
        combined_text = f"{title} {meta_desc} {' '.join(headings)}"
        
        # Simple stopword filtering to get 2-4 primary keywords
        words = re.findall(r"\b[A-Za-z]{4,}\b", combined_text)
        stopwords = {"this", "that", "with", "from", "your", "have", "about", "more", "online", "welcome", "home", "page"}
        meaningful_words = [w for w in words if w.lower() not in stopwords]
        
        keywords = list(dict.fromkeys(meaningful_words))[:4]
        niche_summary = " ".join(keywords) if keywords else "technology digital tools"

        return {
            "url": website_url,
            "title": title or "My Website",
            "description": meta_desc or "Website specialized in online resources",
            "niche": niche_summary,
            "keywords": keywords
        }
    except Exception as e:
        # Fallback if site cannot be crawled
        parsed = urllib.parse.urlparse(website_url)
        domain_name = parsed.netloc or parsed.path
        return {
            "url": website_url,
            "title": domain_name,
            "description": "Website",
            "niche": domain_name.replace(".com", "").replace(".org", "").replace("-", " "),
            "keywords": ["resources", "guide", "tools"]
        }


def calculate_estimated_da(url):
    """
    Estimates Domain Authority based on domain TLD, length, and known platforms.
    """
    domain = urllib.parse.urlparse(url).netloc.lower()
    
    if domain.endswith(".edu") or domain.endswith(".gov"):
        return 90
    if any(plat["domain"] in domain for plat in HIGH_AUTHORITY_PLATFORMS):
        return 92
    if domain.endswith(".org"):
        return 74
    if len(domain) < 12:
        return 68
    return 62


def find_high_quality_targets(website_info, max_results=10):
    """
    Uses Search Dorks to locate high authority websites for backlinks.
    """
    niche = website_info.get("niche", "digital guide")
    user_url = website_info.get("url", "")
    user_domain = urllib.parse.urlparse(user_url).netloc.lower()

    # Search Dork variations
    dork_queries = [
        f'{niche} "leave a comment" -"comments closed"',
        f'{niche} "write for us" high authority',
        f'{niche} inurl:resources "useful links"',
        f'{niche} "submit guest post"',
        f'{niche} inurl:blog "add comment"'
    ]

    discovered = []
    
    # 1. Add guaranteed High Authority Web 2.0 platform targets first
    for plat in HIGH_AUTHORITY_PLATFORMS[:2]:
        discovered.append({
            "target_url": f"https://{plat['domain']}",
            "title": f"{plat['name']} - Instant High DA Article Backlink",
            "snippet": f"High DA ({plat['da']}) editorial publishing platform. Instant live backlink with natural anchor text.",
            "domain_authority": plat["da"],
            "type": plat["type"]
        })

    # 2. Search Web using DuckDuckGo
    try:
        with DDGS() as ddgs:
            for query in dork_queries[:3]:
                if len(discovered) >= max_results:
                    break
                try:
                    results = list(ddgs.text(query, max_results=4))
                    for item in results:
                        link = item.get("href", "")
                        domain = urllib.parse.urlparse(link).netloc.lower()
                        
                        # Avoid linking to self or duplicates
                        if not link or user_domain in domain:
                            continue
                        if any(d["target_url"] == link for d in discovered):
                            continue

                        da_score = calculate_estimated_da(link)
                        
                        # Only keep high quality (DA 55+)
                        if da_score >= 55:
                            link_type = "Blog Discussion Backlink"
                            if "resource" in link.lower() or "links" in link.lower():
                                link_type = "Resource Page Link"
                            elif "write-for-us" in link.lower() or "guest" in link.lower():
                                link_type = "Guest Post Editorial Link"

                            discovered.append({
                                "target_url": link,
                                "title": item.get("title", domain),
                                "snippet": item.get("body", "")[:200],
                                "domain_authority": da_score,
                                "type": link_type
                            })
                except Exception:
                    continue
    except Exception as e:
        print(f"Search engine error: {e}")

    return discovered
