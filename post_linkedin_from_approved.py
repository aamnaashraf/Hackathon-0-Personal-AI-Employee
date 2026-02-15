#!/usr/bin/env python3
"""
Script to post LinkedIn content from approved files
"""
import os
import json
import requests
from pathlib import Path
from datetime import datetime
import dotenv
import re

dotenv.load_dotenv()

def post_to_linkedin_api(post_content, access_token, person_urn):
    """
    Post content to LinkedIn API
    """
    # LinkedIn API endpoint for creating posts
    api_url = os.getenv('LINKEDIN_API_URL', 'https://api.linkedin.com/v2/')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    # Based on the error message, LinkedIn API expects either:
    # - urn:li:member:<numeric-id> for personal posts
    # - urn:li:company:<numeric-id> for company posts
    # The alphanumeric ID '86xugwmkxi2epn' needs to be converted to proper format

    # Get the sub ID from userinfo endpoint (OpenID Connect)
    userinfo_url = f"{api_url}userinfo"
    userinfo_headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)

    if userinfo_response.status_code == 200:
        userinfo_data = userinfo_response.json()
        # Use the sub ID from OpenID Connect
        sub_id = userinfo_data.get('sub')
        if sub_id:
            author_urn = f"urn:li:person:{sub_id}"
        else:
            # Fallback to person_urn from config
            author_urn = f"urn:li:person:{person_urn}"
    else:
        # If we can't get userinfo, use the person_urn from config
        author_urn = f"urn:li:person:{person_urn}"

    post_data = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    # Make the API call
    response = requests.post(
        f"{api_url}ugcPosts",
        headers=headers,
        json=post_data
    )

    return response

def log_post_activity(content_preview, status):
    """Log the post activity to a JSON file"""
    logs_dir = Path("AI_Employee_Vault/Logs")
    logs_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = logs_dir / f'{today}_linkedin.json'

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'linkedin_post',
        'content_preview': content_preview[:100],
        'status': status
    }

    # Read existing logs or create new
    if log_file.exists():
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

    return log_file

def move_to_done_folder(source_file):
    """Move the approved file to the Done folder"""
    done_dir = Path("AI_Employee_Vault/Done")
    done_dir.mkdir(exist_ok=True)

    dest_file = done_dir / source_file.name
    source_file.rename(dest_file)

    return dest_file

def update_dashboard():
    """Update the Dashboard.md with the success message and increment task count"""
    dashboard_path = Path("AI_Employee_Vault/Dashboard.md")

    if dashboard_path.exists():
        content = dashboard_path.read_text(encoding='utf-8')

        # Update or add the success message
        if "LinkedIn post successfully shared" not in content:
            content += f"\n\n- LinkedIn post successfully shared: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Find and update the completed tasks count
        completed_match = re.search(r'Completed Tasks: (\d+)', content)
        if completed_match:
            current_count = int(completed_match.group(1))
            new_count = current_count + 1
            content = content.replace(
                f'Completed Tasks: {current_count}',
                f'Completed Tasks: {new_count}'
            )
        else:
            # If no Completed Tasks section found, add it
            content += f"\n\nCompleted Tasks: 1"

        dashboard_path.write_text(content, encoding='utf-8')
    else:
        # Create dashboard if it doesn't exist
        content = f"""# AI Employee Dashboard

## Task Status
Completed Tasks: 1

## Recent Activity
- LinkedIn post successfully shared: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        dashboard_path.write_text(content, encoding='utf-8')

def process_approved_linkedin_posts():
    """Process all approved LinkedIn posts"""
    approved_dir = Path("AI_Employee_Vault/Approved")

    # Find all LinkedIn post files in the approved folder
    linkedin_files = list(approved_dir.glob("*linkedin*post*.md"))

    for file_path in linkedin_files:
        print(f"Processing LinkedIn post: {file_path.name}")

        # Extract the post content from the file
        content = file_path.read_text(encoding='utf-8')

        # Extract content between "Post Content" and "Approval Instructions"
        lines = content.split('\n')
        post_content_lines = []
        in_post_content = False

        for line in lines:
            if "## Post Content" in line:
                in_post_content = True
                continue
            elif "## Approval Instructions" in line:
                break
            elif in_post_content:
                post_content_lines.append(line)

        # Clean up the extracted content
        post_content = '\n'.join(post_content_lines).strip()

        # Remove the header markers and empty lines at the beginning
        post_content = '\n'.join([line for line in post_content.split('\n') if not line.startswith('#')])
        post_content = post_content.strip()

        # print(f"Extracted content: {post_content[:100].encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')}...")
        print("Extracted content (character count):", len(post_content))

        # Get LinkedIn configuration
        access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        person_id = os.getenv('LINKEDIN_PERSON_ID', '').split(':')[-1]  # Extract just the ID part

        if not access_token:
            print("[ERROR] LinkedIn access token not found in environment variables")
            return False

        if not person_id or person_id == 'your_person_id':
            print("[ERROR] LinkedIn person ID not properly configured")
            return False

        print(f"Attempting to post to LinkedIn profile: urn:li:person:{person_id}")

        try:
            # Actually post to LinkedIn
            response = post_to_linkedin_api(post_content, access_token, person_id)

            if response.status_code in [200, 201]:
                print(f"[SUCCESS] LinkedIn post published successfully!")
                print(f"Response: {response.text}")

                # Log the successful post
                log_file = log_post_activity(post_content, 'posted')
                print(f"Activity logged to: {log_file}")

                # Move the file to Done folder
                moved_file = move_to_done_folder(file_path)
                print(f"Moved approved file to: {moved_file}")

                # Update the dashboard
                update_dashboard()
                print("Dashboard updated with successful post")

                return True
            else:
                print(f"[ERROR] Failed to post to LinkedIn. Status: {response.status_code}, Response: {response.text}")

                # Log the failed post
                log_file = log_post_activity(post_content, 'failed')
                print(f"Failure logged to: {log_file}")

                return False

        except Exception as e:
            print(f"[ERROR] Exception occurred while posting to LinkedIn: {str(e)}")

            # Log the exception
            log_file = log_post_activity(post_content, 'error')
            print(f"Error logged to: {log_file}")

            return False

if __name__ == "__main__":
    print("Starting LinkedIn post processor...")
    success = process_approved_linkedin_posts()

    if success:
        print("LinkedIn post process completed successfully!")
    else:
        print("LinkedIn post process failed!")