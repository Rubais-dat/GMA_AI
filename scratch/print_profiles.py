import os
import re

def main():
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = re.split(r"--- Page \d+ ---", content)
    
    print("Page details for Basic College Profile:")
    for idx, page in enumerate(pages):
        page_num = idx
        if "basic college profile" in page.lower():
            lines = [l.strip() for l in page.split("\n") if l.strip()]
            
            # Find index of "Basic College Profile"
            profile_idx = -1
            for j, line in enumerate(lines):
                if "basic college profile" in line.lower():
                    profile_idx = j
                    break
                    
            print(f"\n--- Page {page_num} ---")
            start = max(0, profile_idx - 1)
            end = min(len(lines), profile_idx + 8)
            for line in lines[start:end]:
                print(f"  {line}")

if __name__ == "__main__":
    main()
