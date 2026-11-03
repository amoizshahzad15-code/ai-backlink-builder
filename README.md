# 🚀 LinkFlow AI — Full Website for Vercel Deployment

Autonomous AI Backlink Builder Web App designed for instant deployment on **Vercel Serverless**.

---

## 🌟 Architecture & Features
- **Frontend (`public/index.html`):** Modern SaaS Landing Page & Control Dashboard (Tailwind CSS, Zero-build, Responsive).
- **Backend (`api/index.py`):** FastAPI Python Serverless Function running on `@vercel/python`.
- **Target Hunter:** Scrapes user website, determines niche & keywords, and finds high-DA targets (DA 80 - 95+).
- **Daily Approval Queue:** Interactive checkboxes allowing users to approve/reject discovered websites.
- **Automated Live Backlink Creator:** Context-rich article writer with natural anchor text + Telegraph API (DA 92) for instant live URLs.

---

## 🚀 How to Deploy on Vercel (Step-by-Step)

### Option 1: Via GitHub (Recommended - 2 Minutes)
1. Is folder ko GitHub repository par push karein:
   ```bash
   cd C:\Users\amoiz\.gemini\antigravity\scratch\ai_backlink_builder
   git init
   git add .
   git commit -m "Initial commit for LinkFlow AI website"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
2. **[Vercel Dashboard](https://vercel.com/new)** par jayein.
3. Apni GitHub repository select karein aur **Deploy** par click karein.
4. Vercel automatically `vercel.json` detect kar ke aapki live website bana dega (e.g., `https://linkflow-ai.vercel.app`)!

---

### Option 2: Via Vercel CLI
```bash
npm i -g vercel
cd C:\Users\amoiz\.gemini\antigravity\scratch\ai_backlink_builder
vercel
```

---

## 💻 Local Testing (Before Deploying)
Agar aap pehle apne computer par test karna chahte hain:
```bash
pip install -r requirements.txt
uvicorn api.index:app --reload --port 8000
```
Phir browser mein `public/index.html` open karein ya local server par dekhein!
