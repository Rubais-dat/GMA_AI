import os
import re
import ast

def get_gma_college_data():
    # Read query_llm.py and extract GMA_COLLEGE_DATA
    query_llm_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "query_llm.py"))
    with open(query_llm_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "GMA_COLLEGE_DATA":
                    # Evaluate the dict node
                    # We can use ast.literal_eval since the dict contains only string literals and ints
                    return ast.literal_eval(node.value)
    return {}

def main():
    gma_colleges = get_gma_college_data()
    print(f"Loaded {len(gma_colleges)} colleges from GMA_COLLEGE_DATA.")
    
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    if not os.path.exists(cleaned_txt_path):
        print(f"Error: {cleaned_txt_path} not found")
        return

    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split the text by page marker
    pages = re.split(r"--- Page \d+ ---", content)
    
    # We want to identify the colleges introduced in the PDF/cleaned text.
    # Usually a college profile starts on a page with "Medical College History & Introduction" 
    # or "Basic College Profile"
    colleges_in_pdf = []
    
    for i, page in enumerate(pages):
        p_clean = page.strip()
        if not p_clean:
            continue
            
        lines = [line.strip() for line in p_clean.split("\n") if line.strip()]
        if not lines:
            continue
            
        # Check if the page contains key headers that denote the start of a college profile
        has_intro_header = any("History &" in line or "History &amp;" in line or "History" in line for line in lines[:10]) and any("Introduction" in line for line in lines[:10])
        has_profile_header = any("Basic College Profile" in line for line in lines[:10])
        
        if has_intro_header or has_profile_header:
            # Let's extract candidate college names from the first few lines
            candidate_names = lines[:5]
            colleges_in_pdf.append({
                "page": i,
                "first_lines": candidate_names,
                "text": p_clean
            })

    print(f"\nFound {len(colleges_in_pdf)} colleges in the PDF/cleaned text:")
    
    # Now let's try to map the colleges in the PDF to the GMA_COLLEGE_DATA codes
    for idx, col in enumerate(colleges_in_pdf):
        print(f"\n--- College #{idx+1} (Page {col['page']}) ---")
        print("First 3 lines of page:")
        for line in col['first_lines'][:3]:
            print(f"  {line}")
            
        # Search for code in the text of the first 2 pages of this college section
        # or search for matching names
        matched_code = None
        matched_name = None
        
        # We can scan the college's page text for acronyms or parts of the name
        # Let's match by GMA codes
        for code, info in gma_colleges.items():
            # Match by name or code
            code_pat = r"\b" + re.escape(code) + r"\b"
            if re.search(code_pat, col['text']):
                matched_code = code
                matched_name = info['name']
                break
                
            # Or check if any word from the official name is in the first lines of the page
            words = [w.lower() for w in info['name'].replace(".", "").replace(",", "").split() if len(w) > 3 and w.lower() not in ["medical", "college", "hospital", "institute", "sciences", "government", "govt"]]
            found_words = 0
            for w in words:
                if any(w in line.lower() for line in col['first_lines']):
                    found_words += 1
            if len(words) > 0 and found_words >= len(words) * 0.7:
                matched_code = code
                matched_name = info['name']
                break
                
        if matched_code:
            print(f"  --> MATCHED to GMA College: {matched_name} (Code: {matched_code}, GMA Rank: {gma_colleges[matched_code]['gma_rank']})")
        else:
            print("  --> WARNING: Could not automatically match to any GMA College!")

if __name__ == "__main__":
    main()
