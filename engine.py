import os
from github import Github, Auth
from dotenv import load_dotenv
from datetime import datetime

# Grab variables from my local .env file
load_dotenv()

class GitVisualizer:
    def __init__(self):
        # Make sure to reload the env just in case something changed
        load_dotenv()
        raw_token = os.getenv("GH_TOKEN")
        
        # Simple check: no token, no stats!
        if not raw_token:
            print("❌ Oops! GH_TOKEN is missing. Check your .env file.")
            return

        # stripping whitespace just in case I copy-pasted weirdly
        self.token = raw_token.strip()
        
        # Setting up the auth object (avoids that annoying deprecation warning)
        auth = Auth.Token(self.token)
        self.client = Github(auth=auth)
        
        # Testing the connection right away
        self.user = self.client.get_user()
        print(f"✅ Logged in as: {self.user.login}")

    def get_stats(self):
        """Go through my repos and pull the data I need."""
        if not self.client:
            return 0, {}

        # Getting all the repos I'm involved with
        repos = self.user.get_repos()
        total_stars = 0
        lang_data = {}

        print(f"📡 Looking through {self.user.public_repos} repos... this might take a sec.")

        for repo in repos:
            try:
                # I only care about my original stuff, so skipping forks
                if not repo.fork:
                    print(f"🔍 Checking: {repo.name}")
                    total_stars += repo.stargazers_count
                    
                    # Language breakdown logic
                    langs = repo.get_languages()
                    for lang, bytes_count in langs.items():
                        lang_data[lang] = lang_data.get(lang, 0) + bytes_count
            except Exception as e:
                # Some repos are weirdly restricted or empty, so I'll just skip them
                print(f"⚠️ Note: Skipping {repo.name} (Access issues)")
                continue
                
        return total_stars, lang_data

    def update_dashboard(self, stars, langs):
        """Write the final stats to my README file."""
        # Sort languages so the biggest ones show up first
        sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
        
        try:
            with open("README.md", "w", encoding="utf-8") as f:
                # The visual layout of the dashboard
                f.write(f"# 🚀 {self.user.login}'s GitHub Stats\n\n")
                f.write(f"This is an automated dashboard updated daily via a Python engine and GitHub Actions.\n\n")
                
                f.write(f"## 📊 Global Metrics\n")
                f.write(f"- **Total Stars Received:** ⭐ {stars}\n")
                f.write(f"- **Projects Tracked:** 📂 {self.user.public_repos}\n\n")
                
                f.write(f"## 🛠 Language Usage\n")
                f.write("| Language | Bytes of Code |\n| :--- | :--- |\n")
                
                # Just show my top 5 most used languages
                for lang, count in sorted_langs[:5]:
                    f.write(f"| {lang} | {count:,} |\n")
                
                # Timestamp so I know it's actually working
                f.write(f"\n\n---\n*Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
            
            print("✅ Awesome! README.md is updated.")
        except Exception as e:
            print(f"❌ Something went wrong writing the file: {e}")

if __name__ == "__main__":
    # Let's run the visualizer!
    visualizer = GitVisualizer()
    if hasattr(visualizer, 'client') and visualizer.client:
        stars_count, languages = visualizer.get_stats()
        
        # Only update if we actually found something
        if languages: 
            visualizer.update_dashboard(stars_count, languages)
        else:
            print("🤔 No data found to update.")