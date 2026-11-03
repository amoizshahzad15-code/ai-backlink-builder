import subprocess
import sys
import os

def main():
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    print("=" * 60)
    print("🚀 Starting AI Backlink Hunter & Builder Dashboard...")
    print("=" * 60)
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()
