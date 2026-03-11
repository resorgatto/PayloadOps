import os
import re

ROOT = r"c:\Users\renat\Desktop\Portifolio\SEAM"

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return
    
    new_content = content.replace("SEAM", "SEAM")
    new_content = new_content.replace("seam", "seam")
    new_content = new_content.replace("SEAM", "SEAM")
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")

for root, dirs, files in os.walk(ROOT):
    # Skip node_modules, .git, venv
    if '.git' in root or 'node_modules' in root or '.venv' in root or '__pycache__' in root:
        continue
        
    for file in files:
        if file.endswith(('.py', '.md', '.html', '.json', '.toml', '.env.example', '.env', '.yaml', '.yml', '.txt', '.tsx', '.ts')):
            replace_in_file(os.path.join(root, file))

print("Done string replacement.")
