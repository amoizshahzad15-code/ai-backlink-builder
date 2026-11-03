import json
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "backlinks_db.json")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "user_config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "website_url": "",
        "user_email": "",
        "user_name": "Webmaster",
        "email_app_password": "",
        "gemini_api_key": ""
    }


def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "targets": [],  # List of target dicts
        "history": []   # Created live links
    }


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def add_discovered_targets(new_targets):
    """Adds newly found targets if not already in the database."""
    db = load_db()
    existing_urls = {t["target_url"] for t in db["targets"]}
    existing_history = {h["live_url"] for h in db["history"]}

    added_count = 0
    for target in new_targets:
        url = target.get("target_url")
        if url and url not in existing_urls and url not in existing_history:
            target_entry = {
                "id": f"tgt_{int(datetime.now().timestamp() * 1000)}_{added_count}",
                "target_url": url,
                "title": target.get("title", "High Authority Website"),
                "snippet": target.get("snippet", ""),
                "domain_authority": target.get("domain_authority", 65),
                "type": target.get("type", "Web 2.0 Article / Discussion"),
                "status": "PENDING_APPROVAL",  # PENDING_APPROVAL, APPROVED, REJECTED, COMPLETED
                "discovered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "live_url": None,
                "error": None
            }
            db["targets"].append(target_entry)
            added_count += 1

    save_db(db)
    return added_count


def update_target_status(target_id, new_status):
    db = load_db()
    for t in db["targets"]:
        if t["id"] == target_id:
            t["status"] = new_status
            break
    save_db(db)


def mark_target_completed(target_id, live_url, notes=""):
    db = load_db()
    for t in db["targets"]:
        if t["id"] == target_id:
            t["status"] = "COMPLETED"
            t["live_url"] = live_url
            # Add to history
            db["history"].append({
                "target_id": target_id,
                "target_url": t["target_url"],
                "live_url": live_url,
                "domain_authority": t.get("domain_authority", 65),
                "type": t.get("type", "Backlink"),
                "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "notes": notes
            })
            break
    save_db(db)
