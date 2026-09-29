import os
import datetime
import json
import subprocess

def get_telegram_config():
    env_path = os.path.expanduser("~/.hive/agents.env")
    if not os.path.exists(env_path):
        return None, None
    
    config = {}
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key] = value
    
    return config.get("TELEGRAM_BOT_TOKEN"), config.get("TELEGRAM_CHAT_ID")

def get_newest_updates():
    updates = []
    if not os.path.exists("UPDATES.md"):
        return updates
    
    with open("UPDATES.md", "r") as f:
        lines = f.readlines()
        
    for line in lines:
        if line.startswith("- **"):
            parts = line.split(" · ")
            if len(parts) >= 4:
                task_id = parts[1].replace("`", "")
                desc = parts[3].strip()
                updates.append(f"{task_id}: {desc}")
    return updates[:5]

def build_message():
    updates = get_newest_updates()
    if not updates:
        return None
    
    msg = "Daily Update from Awesome Indian Exams:\n\n"
    for u in updates:
        msg += f"- {u}\n"
    return msg

def post_to_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    # Using curl as per requirements (macOS bash 3.2 compatible)
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-d", f"chat_id={chat_id}",
        "-d", f"text={message}"
    ]
    subprocess.run(cmd, capture_output=True)

if __name__ == "__main__":
    token, chat_id = get_telegram_config()
    if not token or not chat_id:
        exit(0)
    
    last_post_file = ".telegram_last_post"
    today = datetime.date.today().isoformat()
    if os.path.exists(last_post_file):
        with open(last_post_file, "r") as f:
            if f.read().strip() == today:
                exit(0)
    
    message = build_message()
    if message:
        post_to_telegram(token, chat_id, message)
        with open(last_post_file, "w") as f:
            f.write(today)
