#!/usr/bin/env python3
"""
Update GitHub Repository Description for ROM Cleanup Tool
"""

import requests
import os
import json

def update_github_description():
    """Update the GitHub repository description"""
    
    # GitHub API configuration
    REPO_OWNER = "Blainear"
    REPO_NAME = "rom-collection-cleanup-tool"
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Generate a new token with 'repo' permissions")
        print("3. Set the environment variable: set GITHUB_TOKEN=your_token")
        return False
    
    # New repository description
    new_description = "🎮 Advanced ROM collection cleanup tool with API integration, process control, and enhanced region detection. Perfect for organizing retro game collections!"
    
    # Repository topics/tags
    new_topics = [
        "rom-cleanup",
        "retro-gaming",
        "file-organization",
        "duplicate-removal",
        "python",
        "gui-application",
        "game-collection",
        "api-integration",
        "process-control",
        "region-detection"
    ]
    
    # API endpoint
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    
    # Headers
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    # Update data
    update_data = {
        "description": new_description,
        "topics": new_topics,
        "homepage": "https://github.com/Blainear/rom-collection-cleanup-tool",
        "has_issues": True,
        "has_projects": False,
        "has_wiki": False,
        "has_downloads": True,
        "default_branch": "main"
    }
    
    try:
        print(f"🚀 Updating GitHub repository: {REPO_OWNER}/{REPO_NAME}")
        print(f"📝 New description: {new_description}")
        print(f"🏷️ New topics: {', '.join(new_topics)}")
        
        # Update the repository
        response = requests.patch(api_url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            repo_info = response.json()
            print("✅ Repository updated successfully!")
            print(f"🔗 Repository URL: {repo_info['html_url']}")
            print(f"📝 Description: {repo_info['description']}")
            print(f"🏷️ Topics: {', '.join(repo_info.get('topics', []))}")
            return True
        else:
            print(f"❌ Failed to update repository: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating repository: {e}")
        return False

def main():
    """Main function"""
    print("GitHub Repository Description Updater")
    print("=" * 50)
    
    success = update_github_description()
    
    if success:
        print("\n🎉 Repository description updated successfully!")
        print("📋 Next steps:")
        print("1. Visit the repository page to verify the changes")
        print("2. Check that the description and topics are correct")
        print("3. The repository should now have better discoverability")
    else:
        print("\n❌ Failed to update repository description")
        print("📋 Manual steps:")
        print("1. Go to https://github.com/Blainear/rom-collection-cleanup-tool")
        print("2. Click 'Settings' tab")
        print("3. Scroll down to 'General' section")
        print("4. Update the description to:")
        print("   '🎮 Advanced ROM collection cleanup tool with API integration, process control, and enhanced region detection. Perfect for organizing retro game collections!'")
        print("5. Add topics: rom-cleanup, retro-gaming, file-organization, duplicate-removal, python, gui-application, game-collection, api-integration, process-control, region-detection")
        print("6. Click 'Save changes'")

if __name__ == "__main__":
    main() 