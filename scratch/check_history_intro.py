import os
import re

def main():
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = re.split(r"--- Page \d+ ---", content)
    
    print(f"Total pages: {len(pages)}")
    
    colleges = []
    current_college = None
    
    for idx, page in enumerate(pages):
        page_num = idx  # because split starts with an empty element before page 1
        lines = [l.strip() for l in page.split("\n") if l.strip()]
        if not lines:
            continue
            
        # Check if this page contains "History & Introduction"
        is_intro = False
        for line in lines[:10]:
            if "history &" in line.lower() or "history &amp;" in line.lower() or ("history" in line.lower() and "introduction" in line.lower()):
                is_intro = True
                break
                
        if is_intro:
            # Look for the college name in the lines preceding/following the history header
            # Usually the college name is right before or right after the header, or near the logo
            college_name = "Unknown"
            # Let's inspect the first 10 lines
            text_block = "\n".join(lines[:10])
            # Let's clean up and find lines that look like college names
            for line in lines[:10]:
                if any(x in line.lower() for x in ["medical college", "institute of medical", "academy of medical", "colege"]):
                    if "history" not in line.lower() and "introduction" not in line.lower() and "logo" not in line.lower() and "neva" not in line.lower():
                        college_name = line
                        break
            if college_name == "Unknown":
                # Fallback to the first non-empty non-logo line
                for line in lines[:10]:
                    if "logo" not in line.lower() and "history" not in line.lower() and "introduction" not in line.lower() and "neva" not in line.lower():
                        college_name = line
                        break
            colleges.append({
                "page": page_num,
                "detected_name": college_name,
                "lines": lines[:5]
            })

    print(f"\nFound {len(colleges)} colleges in text:")
    for c in colleges:
        print(f"Page {c['page']}: {c['detected_name']}")
        print(f"  First lines: {c['lines']}")

if __name__ == "__main__":
    main()
