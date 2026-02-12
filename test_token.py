import os
from dotenv import load_dotenv
from github import Github

load_dotenv()
token = os.getenv("GH_TOKEN")

try:
    g = Github(token)
    user = g.get_user()
    print(f"✅ Success! Connected to: {user.login}")
    print(f"Token is working and can see {user.public_repos} public repos.")
except Exception as e:
    print(f"❌ Connection Failed: {e}")