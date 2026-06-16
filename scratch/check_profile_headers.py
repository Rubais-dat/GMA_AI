import os
import re

def main():
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = re.split(r"--- Page \d+ ---", content)
    
    colleges = []
    
    for idx, page in enumerate(pages):
        page_num = idx
        lines = [l.strip() for l in page.split("\n") if l.strip()]
        if not lines:
            continue
            
        is_profile = False
        for line in lines[:10]:
            if "basic college profile" in line.lower():
                is_profile = True
                break
                
        if is_profile:
            # Look for the college name
            college_name = "Unknown"
            for line in lines[:10]:
                if any(x in line.lower() for x in ["medical college", "institute of medical", "academy of medical", "colege"]):
                    if "profile" not in line.lower() and "logo" not in line.lower() and "neva" not in line.lower():
                        college_name = line
                        break
            if college_name == "Unknown":
                for line in lines[:10]:
                    if "logo" not in line.lower() and "profile" not in line.lower() and "neva" not in line.lower():
                        college_name = line
                        break
            colleges.append({
                "page": page_num,
                "detected_name": college_name,
                "lines": lines[:5]
            })

    print(f"\nFound {len(colleges)} pages with 'Basic College Profile':")
    for c in colleges:
        print(f"Page {c['page']}: {c['detected_name']}")
        print(f"  First lines: {c['lines']}")

if __name__ == "__main__":
    main()
