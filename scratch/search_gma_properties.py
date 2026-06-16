import os
import re

def main():
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split("\n")
    
    # Find lines matching GMA patterns
    gma_lines = []
    for idx, line in enumerate(lines):
        if "gma" in line.lower():
            gma_lines.append((idx+1, line.strip()))
            
    print(f"Total occurrences of 'GMA': {len(gma_lines)}")
    print("First 30 occurrences:")
    for num, text in gma_lines[:30]:
        print(f"Line {num}: {text}")

if __name__ == "__main__":
    main()
