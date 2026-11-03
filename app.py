import streamlit as st
import time
import pandas as pd
from database import (
    load_config, save_config, load_db, 
    add_discovered_targets, update_target_status, mark_target_completed
)
from target_finder import extract_website_niche, find_high_quality_targets
from backlink_creator import execute_backlink_creation

# Page setup
st.set_page_config(
    page_title="AI Backlink Hunter & Builder",
    page_icon="🚀",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E88E5; margin-bottom: 0px; }
    .subtitle { font-size: 1rem; color: #666; margin-bottom: 20px; }
    .da-badge { background-color: #E3F2FD; color: #0D47A1; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem; }
    .status-badge { background-color: #E8F5E9; color: #1B5E20; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.85rem; }
    .card { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px; padding: 15px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# Load existing user config & database
config = load_config()
db = load_db()

st.markdown('<div class="main-title">🚀 Autonomous AI Backlink Hunter & Builder</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">100% Free AI Automation: Google Dork Target Hunting → Daily User Approval → Automated Live Link Creation</div>', unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📋 Daily Approval Queue", "🌐 Live Backlinks Report", "⚙️ Setup & Credentials"])

# ==========================================
# TAB 3: SETUP & CREDENTIALS
# ==========================================
with tab3:
    st.subheader("Website & Automation Settings")
    st.write("Apni website aur details enter karein jiske liye AI ne backlinks banane hain.")
    
    col1, col2 = st.columns(2)
    with col1:
        site_url = st.text_input("Aapki Website ka URL:", value=config.get("website_url", ""), placeholder="https://mywebsite.com")
        user_name = st.text_input("Author / Commenter Name:", value=config.get("user_name", "Webmaster"))
        gemini_key = st.text_input("Gemini API Key (Optional):", value=config.get("gemini_api_key", ""), type="password", help="Bina key ke bhi built-in fallback engine se chalega!")

    with col2:
        user_email = st.text_input("User Email:", value=config.get("user_email", ""), placeholder="user@gmail.com")
        email_password = st.text_input("Email App Password (Optional):", value=config.get("email_app_password", ""), type="password", help="Sign-up verification emails auto-read karne ke liye.")

    if st.button("💾 Save Settings", use_container_width=True):
        new_config = {
            "website_url": site_url.strip(),
            "user_name": user_name.strip(),
            "user_email": user_email.strip(),
            "email_app_password": email_password.strip(),
            "gemini_api_key": gemini_key.strip()
        }
        save_config(new_config)
        st.success("✅ Settings successfully save ho gayi hain!")
        time.sleep(1)
        st.rerun()

# ==========================================
# TAB 1: DAILY APPROVAL QUEUE
# ==========================================
with tab1:
    st.subheader("🎯 Daily Discovered Backlink Targets")
    
    user_url = config.get("website_url")
    if not user_url:
        st.warning("⚠️ Pehle 'Setup & Credentials' tab mein ja kar apni Website ka URL enter karein.")
    else:
        top_col1, top_col2 = st.columns([3, 1])
        with top_col1:
            st.info(f"Target Promotion Website: **{user_url}**")
        with top_col2:
            if st.button("🔍 Scan & Hunt New Targets", type="primary", use_container_width=True):
                with st.spinner("AI website ka niche scan kar ke high-authority websites dhoond raha hai..."):
                    site_info = extract_website_niche(user_url)
                    new_targets = find_high_quality_targets(site_info, max_results=8)
                    added = add_discovered_targets(new_targets)
                    st.success(f"Google Search se {added} naye high-quality backlink targets mil gaye!")
                    time.sleep(1)
                    st.rerun()

        # Display Pending Targets
        pending_targets = [t for t in db["targets"] if t.get("status") == "PENDING_APPROVAL"]
        
        if not pending_targets:
            st.write("Koi naye targets pending nahi hain. **'🔍 Scan & Hunt New Targets'** button daba kar naye targets dhoondein!")
        else:
            st.write(f"**{len(pending_targets)} Websites Approval ke liye ready hain.** Jin par link banana hai, unhe select karein:")
            
            # Form for batch approval
            with st.form("approval_form"):
                selected_ids = []
                for target in pending_targets:
                    col_check, col_details = st.columns([0.5, 9.5])
                    with col_check:
                        is_selected = st.checkbox("", key=f"sel_{target['id']}", value=True)
                        if is_selected:
                            selected_ids.append(target["id"])
                    
                    with col_details:
                        st.markdown(f"""
                        <div class="card">
                            <span class="da-badge">DA: {target.get('domain_authority', 65)}+</span> &nbsp;
                            <b><a href="{target['target_url']}" target="_blank">{target.get('title')}</a></b>
                            <div style="color: #555; font-size: 0.9rem; margin-top: 4px;">{target.get('snippet')}</div>
                            <div style="font-size: 0.8rem; color: #888; margin-top: 6px;">Type: <i>{target.get('type')}</i> | URL: {target['target_url']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit_build = st.form_submit_button("🚀 Approve Selected & Build Backlinks Now", type="primary", use_container_width=True)
                with col_btn2:
                    reject_all = st.form_submit_button("❌ Reject Unselected Targets", use_container_width=True)

            if submit_build:
                if not selected_ids:
                    st.error("Pehle kam az kam aik target select karein!")
                else:
                    st.write(f"🔄 **{len(selected_ids)} Backlinks banane ka process shuru ho gaya hai...**")
                    progress_bar = st.progress(0)
                    
                    site_info = extract_website_niche(user_url)
                    created_count = 0
                    
                    for idx, target_id in enumerate(selected_ids):
                        target = next((t for t in pending_targets if t["id"] == target_id), None)
                        if target:
                            with st.status(f"Creating backlink on: {target.get('title')[:40]}..."):
                                live_url, msg = execute_backlink_creation(target, config, site_info)
                                if live_url:
                                    mark_target_completed(target_id, live_url, msg)
                                    created_count += 1
                                    st.write(f"✅ Live Link: [{live_url}]({live_url})")
                                else:
                                    update_target_status(target_id, "FAILED")
                                    st.write(f"⚠️ {msg}")
                        
                        progress_bar.progress((idx + 1) / len(selected_ids))
                        time.sleep(1)

                    st.success(f"🎉 Process mukammal! **{created_count}** Live Backlinks create ho gaye!")
                    time.sleep(2)
                    st.rerun()

            if reject_all:
                for target in pending_targets:
                    if target["id"] not in selected_ids:
                        update_target_status(target["id"], "REJECTED")
                st.info("Unselected targets reject kar diye gaye.")
                time.sleep(1)
                st.rerun()

# ==========================================
# TAB 2: LIVE BACKLINKS REPORT
# ==========================================
with tab2:
    st.subheader("🌐 Live Created Backlinks")
    history = db.get("history", [])
    
    if not history:
        st.info("Abhi tak koi backlink create nahi hua. Pehle 'Daily Approval Queue' se targets approve karein!")
    else:
        st.write(f"Aapki website ke **{len(history)}** Live Backlinks ban chukay hain:")
        
        report_data = []
        for item in reversed(history):
            report_data.append({
                "Live Backlink URL": item.get("live_url"),
                "Domain Authority": f"DA {item.get('domain_authority', 65)}+",
                "Type": item.get("type"),
                "Date Created": item.get("completed_at"),
                "Status": "🟢 Live & Active"
            })
            
        df = pd.DataFrame(report_data)
        st.dataframe(df, use_container_width=True)

        # Direct clickable links list
        st.markdown("### 🔗 Direct Clickable Links:")
        for idx, item in enumerate(reversed(history), 1):
            st.markdown(f"**{idx}.** <span class='status-badge'>Active</span> [{item.get('live_url')}]({item.get('live_url')}) — *(DA {item.get('domain_authority')}+)*", unsafe_allow_html=True)
