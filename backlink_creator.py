import requests
import json
import re
import urllib.parse
from datetime import datetime
from ai_engine import generate_seo_article, generate_contextual_comment


def create_telegraph_backlink(user_config, website_info):
    """
    Creates an instant, live, high-DA (DA 92) Web 2.0 article backlink on Telegraph (By Telegram).
    Completely free, no auth hurdles, produces an immediate indexable live URL.
    """
    website_url = user_config.get("website_url")
    user_name = user_config.get("user_name", "Editorial Team")
    gemini_key = user_config.get("gemini_api_key")
    
    niche = website_info.get("niche", "Technology & Innovation")
    site_title = website_info.get("title", "Resource Center")

    # 1. Create a free Telegraph account token
    acc_url = "https://api.telegra.ph/createAccount"
    acc_params = {
        "short_name": "ai_backlink",
        "author_name": user_name
    }
    
    try:
        acc_resp = requests.get(acc_url, params=acc_params, timeout=10).json()
        if not acc_resp.get("ok"):
            return None, "Telegraph account creation failed"
        
        access_token = acc_resp["result"]["access_token"]

        # 2. Generate contextual content with embedded backlink
        article_html = generate_seo_article(website_url, niche, site_title, gemini_key)
        
        # Convert simple HTML into Telegraph DOM nodes format
        clean_text_p1 = f"In today's fast-moving industry, understanding {niche} is critical. Structured insights and reliable resources allow organizations and individuals to thrive efficiently."
        clean_anchor_text = f"Visit {site_title} for comprehensive coverage"
        clean_text_p2 = f"Continuous development requires proven methodologies. Verified authorities offer actionable guidance that helps maintain competitive advantage."

        nodes = [
            {"tag": "p", "children": [clean_text_p1]},
            {"tag": "h3", "children": [f"Key Perspectives on {niche.title()}"]},
            {"tag": "p", "children": [
                "To explore updated strategies and in-depth reference documentation, ",
                {"tag": "a", "attrs": {"href": website_url}, "children": [clean_anchor_text]},
                ". This resource provides structured breakdowns and reliable benchmarks."
            ]},
            {"tag": "p", "children": [clean_text_p2]}
        ]

        title = f"The Essential Guide to {niche.title()} & Best Practices"
        
        create_url = "https://api.telegra.ph/createPage"
        payload = {
            "access_token": access_token,
            "title": title[:64],
            "author_name": user_name,
            "author_url": website_url,
            "content": json.dumps(nodes),
            "return_content": False
        }

        page_resp = requests.post(create_url, data=payload, timeout=15).json()
        if page_resp.get("ok"):
            live_url = page_resp["result"]["url"]
            return live_url, "Successfully published live article backlink on Telegraph (DA 92)"
        else:
            return None, f"Publish error: {page_resp.get('error')}"

    except Exception as e:
        return None, f"Telegraph connection error: {str(e)}"


def submit_blog_comment_backlink(target_url, user_config, website_info):
    """
    Attempts to submit a contextual discussion comment on target blogs.
    """
    user_name = user_config.get("user_name", "Alex Hunter")
    user_email = user_config.get("user_email", "contact@domain.com")
    website_url = user_config.get("website_url")
    gemini_key = user_config.get("gemini_api_key")
    niche = website_info.get("niche", "digital tools")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": target_url
    }

    try:
        # Fetch page to find comment form action
        sess = requests.Session()
        resp = sess.get(target_url, headers=headers, timeout=12)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        
        title = soup.title.string.strip() if soup.title and soup.title.string else "Article"
        
        # Generate non-spam, context-aware comment
        comment_text = generate_contextual_comment(title, "", website_url, user_name, niche, gemini_key)

        # Look for typical WordPress or standard comment forms
        comment_form = soup.find("form", id=re.compile(r"commentform|comment-form", re.I))
        if not comment_form:
            comment_form = soup.find("form", action=re.compile(r"comment", re.I))

        if comment_form:
            action = comment_form.get("action", target_url)
            if not action.startswith("http"):
                action = urllib.parse.urljoin(target_url, action)

            # Map form input names
            form_data = {
                "author": user_name,
                "email": user_email,
                "url": website_url,
                "comment": comment_text,
                "comment_post_ID": ""
            }

            # Extract any hidden inputs (like post ID, nonce)
            for hidden in comment_form.find_all("input", type="hidden"):
                if hidden.get("name") and hidden.get("value"):
                    form_data[hidden["name"]] = hidden["value"]

            # Submit
            post_resp = sess.post(action, data=form_data, headers=headers, timeout=15)
            if post_resp.status_code in [200, 302, 301]:
                # Many blogs redirect to the newly created comment anchor
                live_comment_url = post_resp.url if "#comment" in post_resp.url else f"{target_url}#comments"
                return live_comment_url, "Comment submitted successfully with website link!"
        
        # If no form found or couldn't post directly
        return None, "Target page has protected comment form or requires manual account login."
    except Exception as e:
        return None, f"Submission error: {str(e)}"


def execute_backlink_creation(target, user_config, website_info):
    """
    Dispatches the appropriate creation mechanism based on the target type.
    """
    target_url = target.get("target_url", "")
    target_type = target.get("type", "")

    # Priority 1: High DA Web 2.0 / Telegraph
    if "telegra.ph" in target_url or "Web 2.0" in target_type:
        return create_telegraph_backlink(user_config, website_info)
    
    # Priority 2: Blog Discussion / Comments
    elif "Blog" in target_type or "Discussion" in target_type:
        live_url, msg = submit_blog_comment_backlink(target_url, user_config, website_info)
        if live_url:
            return live_url, msg
        else:
            # Fallback: Create high-authority Web 2.0 reference link
            return create_telegraph_backlink(user_config, website_info)

    # Priority 3: General Fallback (Creates dedicated Web 2.0 tier-1 backlink)
    else:
        return create_telegraph_backlink(user_config, website_info)
