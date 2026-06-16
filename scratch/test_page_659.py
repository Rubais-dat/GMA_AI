import os
import re
import ast

def get_gma_college_data():
    query_llm_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "query_llm.py"))
    with open(query_llm_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "GMA_COLLEGE_DATA":
                    return ast.literal_eval(node.value)
    return {}

def main():
    gma_colleges = get_gma_college_data()
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = re.split(r"--- Page \d+ ---", content)
    
    page_num = 659
    page = pages[page_num]
    lines = [l.strip() for l in page.split("\n") if l.strip()]
    
    print(f"Lines for Page {page_num}:")
    for idx, l in enumerate(lines[:15]):
        print(f"  {idx+1}: {l}")
        
    matched_code = None
    for code, info in gma_colleges.items():
        code_pat = r"\b" + re.escape(code) + r"\b"
        if any(re.search(code_pat, line) for line in lines[:10]):
            matched_code = code
            print(f"Matched code by exact regex: {code}")
            break
            
        words = [w.lower() for w in info['name'].replace(".", "").replace(",", "").split() if len(w) > 3 and w.lower() not in ["medical", "college", "hospital", "institute", "sciences", "government", "govt"]]
        found_words = 0
        for w in words:
            if any(w in line.lower() for line in lines[:10]):
                found_words += 1
        if len(words) > 0 and found_words >= len(words) * 0.7:
            matched_code = code
            print(f"Matched code by words: {code} (found {found_words}/{len(words)})")
            break

    if not matched_code:
        text_header = "\n".join(lines[:10]).lower()
        print(f"text_header: {text_header}")
        if "kmct" in text_header:
            matched_code = "KCM"
            print("Matched code by manual override kmct!")
            
    print(f"Final Matched Code: {matched_code}")

if __name__ == "__main__":
    main()
