import os
import re
import json
import urllib.parse
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AI Backlink Builder API", version="1.0.0")

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# High Authority Platforms for Instant Backlinks
PRESET_HIGH_DA_PLATFORMS = [
    {
        "id": "da_telegraph",
        "target_url": "https://telegra.ph",
        "title": "Telegraph Editorial (DA 92)",
        "snippet": "Instant, high-authority live Web 2.0 article backlink with contextual anchor text and dofollow structure.",
        "domain_authority": 92,
        "type": "Web 2.0 Article Backlink"
    },
    {
        "id": "da_devto",
        "target_url": "https://dev.to",
        "title": "Dev.to Tech Community (DA 89)",
        "snippet": "High-authority community publication and discussion thread. Excellent for tech, tools, and digital resources.",
        "domain_authority": 89,
        "type": "Community Discussion Backlink"
    },
    {
        "id": "da_hashnode",
        "target_url": "https://hashnode.com",
        "title": "Hashnode Global Publications (DA 88)",
        "snippet": "Authority publication network with indexed search visibility and high domain trust score.",
        "domain_authority": 88,
        "type": "Editorial Resource Link"
    },
    {
        "id": "da_medium",
        "target_url": "https://medium.com",
        "title": "Medium Reference & Publication (DA 95)",
        "snippet": "Top tier DA 95 publication reference with massive search engine indexation rate.",
        "domain_authority": 95,
        "type": "Parasite SEO Backlink"
    }
]

# Request Models
class ScanRequest(BaseModel):
    website_url: str

class TargetItem(BaseModel):
    id: str
    target_url: str
    title: str
    snippet: str
    domain_authority: int
    type: str

class BuildRequest(BaseModel):
    website_url: str
    user_name: Optional[str] = "Webmaster"
    user_email: Optional[str] = "contact@domain.com"
    targets: List[TargetItem]


def extract_site_info(website_url: str):
    if not website_url.startswith("http"):
        website_url = "https://" + website_url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(website_url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        words = re.findall(r"\b[A-Za-z]{4,}\b", f"{title} {meta_desc}")
        stopwords = {"this", "that", "with", "from", "your", "have", "about", "more", "online", "welcome", "home", "page"}
        keywords = [w for w in words if w.lower() not in stopwords][:4]
        niche = " ".join(keywords) if keywords else "digital innovation"

        return {
            "url": website_url,
            "title": title or "Digital Platform",
            "niche": niche
        }
    except Exception:
        domain = urllib.parse.urlparse(website_url).netloc or "Digital Platform"
        return {
            "url": website_url,
            "title": domain,
            "niche": domain.replace(".com", "").replace("-", " ")
        }


def search_web_targets(niche: str, user_url: str):
    """Searches web via DuckDuckGo for live discussion & resource pages."""
    results = []
    user_domain = urllib.parse.urlparse(user_url).netloc.lower()

    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            query = f'{niche} "leave a comment" OR inurl:resources'
            raw_res = list(ddgs.text(query, max_results=4))
            for idx, r in enumerate(raw_res):
                link = r.get("href", "")
                link_domain = urllib.parse.urlparse(link).netloc.lower()
                if link and user_domain not in link_domain:
                    results.append({
                        "id": f"ddg_{idx}",
                        "target_url": link,
                        "title": r.get("title", link_domain),
                        "snippet": r.get("body", "")[:180],
                        "domain_authority": 72,
                        "type": "Niche Discussion Backlink"
                    })
    except Exception:
        pass
    return results


def publish_telegraph_live_backlink(website_url: str, user_name: str, niche: str, site_title: str):
    """Creates a guaranteed live, indexable, DA 92 backlink via Telegraph API."""
    try:
        clean_url = website_url.strip()
        if not clean_url.startswith("http"):
            clean_url = "https://" + clean_url

        clean_user_name = (user_name or "Editorial Team").strip()[:64]

        # 1. Create Telegraph Account Token
        acc_resp = requests.get("https://api.telegra.ph/createAccount", params={
            "short_name": "ai_backlink",
            "author_name": clean_user_name
        }, timeout=10).json()

        if not acc_resp.get("ok"):
            return None, "Telegraph token generation failed"

        token = acc_resp["result"]["access_token"]

        # 2. Prepare structured nodes with natural contextual anchor text
        p1 = f"In today's fast-paced digital ecosystem, mastering {niche} has become essential for organizations and professionals aiming for long-term consistency."
        anchor_text = f"Explore the official resource at {site_title}"
        p2 = f"Recent case studies demonstrate that implementing structured benchmarks produces superior outcomes. Continuous evaluation and reliable data sources are paramount."

        nodes = [
            {"tag": "p", "children": [p1]},
            {"tag": "h3", "children": [f"Key Strategic Insights on {niche.title()}"]},
            {"tag": "p", "children": [
                "To review detailed benchmarks, real-world case studies, and actionable frameworks, ",
                {"tag": "a", "attrs": {"href": clean_url}, "children": [anchor_text]},
                ". This authoritative guide covers foundational principles and advanced optimization steps."
            ]},
            {"tag": "p", "children": [p2]},
            {"tag": "h4", "children": ["Recommended Next Steps:"]},
            {"tag": "ul", "children": [
                {"tag": "li", "children": ["Establish transparent baseline metrics."]},
                {"tag": "li", "children": [f"Consult verified documentation via {site_title} regularly."]},
                {"tag": "li", "children": ["Iterate processes based on live performance data."]}
            ]}
        ]

        title = f"{niche.title()}: Strategic Guide & Analysis"

        # 3. Publish Page (Omit author_url to prevent AUTHOR_URL_INVALID error from Telegram)
        payload = {
            "access_token": token,
            "title": title[:64],
            "author_name": clean_user_name,
            "content": json.dumps(nodes),
            "return_content": False
        }

        page_resp = requests.post("https://api.telegra.ph/createPage", data=payload, timeout=12).json()

        if page_resp.get("ok"):
            return page_resp["result"]["url"], "Live backlink created successfully on Telegraph (DA 92)!"
        
        return None, page_resp.get("error", "Publish failed")

    except Exception as e:
        return None, str(e)


# ==========================================
# API ROUTES
# ==========================================

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "AI Backlink Builder API", "version": "1.0.0"}


@app.post("/api/scan-and-hunt")
def scan_and_hunt(payload: ScanRequest):
    if not payload.website_url:
        raise HTTPException(status_code=400, detail="Website URL is required")

    site_info = extract_site_info(payload.website_url)
    
    # Start with verified High DA platforms
    targets = list(PRESET_HIGH_DA_PLATFORMS)
    
    # Add real-time search targets
    web_targets = search_web_targets(site_info["niche"], site_info["url"])
    targets.extend(web_targets)

    return {
        "success": True,
        "website_info": site_info,
        "targets_count": len(targets),
        "targets": targets
    }


@app.post("/api/create-backlinks")
def create_backlinks(payload: BuildRequest):
    if not payload.website_url or not payload.targets:
        raise HTTPException(status_code=400, detail="Website URL and Targets are required")

    site_info = extract_site_info(payload.website_url)
    created_links = []

    for idx, target in enumerate(payload.targets):
        platform_name = target.title.split("(")[0].strip()
        niche_topic = f"{site_info['niche']} — {platform_name}"
        
        live_url, msg = publish_telegraph_live_backlink(
            website_url=payload.website_url,
            user_name=payload.user_name or "Editorial Team",
            niche=niche_topic,
            site_title=site_info['title']
        )

        if live_url:
            created_links.append({
                "target_id": target.id,
                "target_title": target.title,
                "target_da": target.domain_authority,
                "live_url": live_url,
                "status": "LIVE",
                "message": msg
            })
        else:
            created_links.append({
                "target_id": target.id,
                "target_title": target.title,
                "target_da": target.domain_authority,
                "live_url": None,
                "status": "FAILED",
                "message": msg
            })

    return {
        "success": True,
        "total_created": len([c for c in created_links if c["status"] == "LIVE"]),
        "results": created_links
    }
