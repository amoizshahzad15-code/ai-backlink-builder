import os
import requests
import json
import re


def generate_with_gemini(prompt, api_key):
    """
    Calls the Google Gemini 1.5/2.5 Flash API directly using official endpoint.
    """
    if not api_key:
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Gemini API request failed: {e}")
    return None


def generate_seo_article(website_url, niche, website_title, gemini_key=None):
    """
    Generates a high-quality 500-word article with natural anchor text backlink.
    """
    prompt = f"""
    Write a high-quality, informative, 500-word educational article about: {niche}.
    The article must be engaging, divided into clear headings and bullet points.
    Somewhere naturally in the second or third paragraph, integrate a contextual backlink to this website:
    URL: {website_url}
    Website Title: {website_title}
    
    Make the anchor text natural (e.g., 'comprehensive guide at {website_title}', or 'official resource on {niche}').
    Format the link in HTML format: <a href="{website_url}">Anchor Text</a>.
    Return ONLY the HTML formatted article (using <h3>, <p>, <ul>, <li>, <b>, and <a> tags).
    """

    if gemini_key:
        ai_content = generate_with_gemini(prompt, gemini_key)
        if ai_content:
            return ai_content

    # Intelligent Free Fallback Generator (No API Key Required)
    clean_anchor = f"{website_title} - Official Resource"
    return f"""
    <h3>The Comprehensive Guide to Modern {niche.title()}</h3>
    <p>In today's fast-paced digital ecosystem, mastering <b>{niche}</b> has become essential for professionals and enthusiasts alike. Whether you are looking to optimize your current workflows or build long-term sustainability, staying informed with credible resources is key.</p>
    
    <p>A recent industry analysis revealed that structured adoption yields significantly higher performance. For in-depth insights and practical implementation strategies, explore the <a href="{website_url}">{clean_anchor}</a>, which provides comprehensive coverage of key fundamentals and updated techniques.</p>
    
    <h3>Key Takeaways & Best Practices</h3>
    <ul>
        <li><b>Consistency:</b> Establish structured routines and monitor progress regularly.</li>
        <li><b>Quality Resources:</b> Rely on verified platforms such as <a href="{website_url}">{website_title}</a> to stay ahead of curve.</li>
        <li><b>Continuous Adaptation:</b> Evaluate outcomes and refine approaches based on real-time feedback.</li>
    </ul>
    
    <p>By leveraging these actionable methodologies, you can achieve consistent growth and reliable results in {niche}.</p>
    """


def generate_contextual_comment(target_title, target_snippet, website_url, user_name, niche, gemini_key=None):
    """
    Generates a thoughtful, non-spam blog discussion comment.
    """
    prompt = f"""
    Write a 3-4 sentence thoughtful, professional comment for a blog post titled '{target_title}'.
    Post snippet: '{target_snippet}'.
    Commenter name: {user_name}.
    Website topic: {niche}.
    Website URL: {website_url}.
    
    Rules:
    1. Do NOT sound spammy. Acknowledge a specific point from the post.
    2. Add one valuable insight.
    3. Naturally mention that we also explore similar topics at {website_url} if readers want supplementary data.
    """

    if gemini_key:
        ai_comment = generate_with_gemini(prompt, gemini_key)
        if ai_comment:
            return ai_comment

    # Intelligent Free Fallback
    return (
        f"Thank you for this insightful breakdown on {target_title}. "
        f"The perspective shared regarding practical implementation is spot on. "
        f"In our work surrounding {niche}, we have observed very similar patterns, especially when focusing on long-term consistency. "
        f"Appreciate you putting this together!"
    )
