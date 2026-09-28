import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def generate_feed():
    updates_file = Path("UPDATES.md")
    if not updates_file.exists():
        return
    
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "Awesome Indian Exams Updates"
    ET.SubElement(channel, "link").text = "https://awesome-indian-exams.github.io"
    ET.SubElement(channel, "description").text = "New pages and verified changes."

    with open(updates_file, 'r') as f:
        for line in f:
            if line.startswith("- **"):
                parts = line.split(" · ")
                if len(parts) < 4: continue
                date_str = parts[0].replace("- **", "").replace(" UTC**", "")
                task_id = parts[1].replace("`", "")
                title = parts[3].strip().replace("[", "").replace("]", "")
                
                item = ET.SubElement(channel, "item")
                ET.SubElement(item, "title").text = f"{task_id}: {title}"
                ET.SubElement(item, "pubDate").text = date_str
                ET.SubElement(item, "guid").text = task_id
    
    print(ET.tostring(root, encoding='unicode'))

if __name__ == "__main__":
    generate_feed()
