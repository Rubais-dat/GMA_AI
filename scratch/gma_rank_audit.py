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

def clean_name(name):
    # Remove punctuation and generic words for name comparison
    name = name.lower()
    for word in ["government", "govt", "medical", "college", "hospital", "institute", "sciences", "science", "and", "research", "centre", "academy", "self-financing", "private", "of"]:
        name = name.replace(word, "")
    return re.sub(r"[^a-z]", "", name).strip()

def main():
    gma_colleges = get_gma_college_data()
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = re.split(r"--- Page \d+ ---", content)
    
    pdf_colleges = []
    
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
            
            # Look around "Basic College Profile" to find the college name
            college_name = None
            # Check lines after "Basic College Profile" for "Name of Institution:" or "Name:"
            for line in lines[profile_idx+1:profile_idx+10]:
                if "name of institution" in line.lower() or "name of the institution" in line.lower():
                    college_name = line.split(":", 1)[1].strip()
                    break
                elif "name" in line.lower() and ":" in line:
                    parts = line.split(":", 1)
                    if any(x in parts[1].lower() for x in ["medical", "college", "institute", "hospital", "academy"]):
                        college_name = parts[1].strip()
                        break
            
            # If not found, check lines just before "Basic College Profile" or the first few lines of the page
            if not college_name:
                for line in lines[max(0, profile_idx-4):profile_idx+5]:
                    if any(x in line.lower() for x in ["medical college", "institute of medical", "academy of medical", "colege"]) and "profile" not in line.lower() and "logo" not in line.lower() and "history" not in line.lower():
                        college_name = line
                        break
                        
            if not college_name:
                # Fallback to first non-logo, non-profile line in the first 5 lines
                for line in lines[:5]:
                    if "logo" not in line.lower() and "profile" not in line.lower() and "neva" not in line.lower() and "history" not in line.lower() and "introduction" not in line.lower():
                        college_name = line
                        break
                        
            if not college_name:
                college_name = f"Unknown College (Page {page_num})"
                
            pdf_colleges.append({
                "page": page_num,
                "name": college_name,
                "text": page
            })

    # Dedup by name
    unique_pdf_colleges = []
    seen = set()
    for pc in pdf_colleges:
        c_name = clean_name(pc['name'])
        # Avoid duplicate pages of the same college if they are close
        if c_name not in seen:
            seen.add(c_name)
            unique_pdf_colleges.append(pc)

    print(f"Auditing {len(unique_pdf_colleges)} colleges found in the PDF against GMA Database:\n")
    print(f"{'#':<3} | {'College Name in PDF':<60} | {'GMA Code':<8} | {'GMA Rank':<8}")
    print("-" * 90)
    
    missing_ranks = []
    
    for i, pc in enumerate(unique_pdf_colleges):
        pdf_name = pc['name']
        cleaned_pdf = clean_name(pdf_name)
        
        matched_code = None
        for code, info in gma_colleges.items():
            cleaned_gma = clean_name(info['name'])
            # Check if one is a substring of the other or highly similar
            if cleaned_pdf in cleaned_gma or cleaned_gma in cleaned_pdf:
                matched_code = code
                break
                
        # If no match, search the whole page text for code
        if not matched_code:
            for code, info in gma_colleges.items():
                if re.search(r"\b" + re.escape(code) + r"\b", pc['text']):
                    matched_code = code
                    break
                    
        # Let's try some manual mappings based on common acronyms if not matched
        if not matched_code:
            if "td" in pdf_name.lower() or "alappuzha" in pdf_name.lower():
                matched_code = "ALP"
            elif "calicut" in pdf_name.lower() or "kozhikode" in pdf_name.lower() or "kozhikkode" in pdf_name.lower():
                if "government" in pdf_name.lower() or "govt" in pdf_name.lower():
                    matched_code = "KKM"
            elif "karakonam" in pdf_name.lower() or "somervell" in pdf_name.lower():
                matched_code = "SMC"
            elif "sut" in pdf_name.lower() or "uthradom" in pdf_name.lower():
                matched_code = "SUC"
            elif "amala" in pdf_name.lower():
                matched_code = "AMC"
            elif "orthodox" in pdf_name.lower() or "kolenchery" in pdf_name.lower() or "mosc" in pdf_name.lower():
                matched_code = "MMC"
            elif "moopen" in pdf_name.lower() or "dm wims" in pdf_name.lower() or "wayanad" in pdf_name.lower():
                if "government" not in pdf_name.lower() and "govt" not in pdf_name.lower():
                    matched_code = "DMM"
            elif "mes" in pdf_name.lower() or "perinthalmanna" in pdf_name.lower():
                matched_code = "EMC"
                
        if matched_code:
            rank = gma_colleges[matched_code]['gma_rank']
            print(f"{i+1:<3} | {pdf_name[:60]:<60} | {matched_code:<8} | {rank:<8}")
        else:
            print(f"{i+1:<3} | {pdf_name[:60]:<60} | {'MISSING':<8} | {'MISSING':<8}")
            missing_ranks.append(pc)

    print("\n" + "="*50)
    print(f"Total Colleges in PDF: {len(unique_pdf_colleges)}")
    print(f"Successfully matched: {len(unique_pdf_colleges) - len(missing_ranks)}")
    print(f"Missing GMA Rank: {len(missing_ranks)}")
    if missing_ranks:
        print("\nDetails of Colleges missing GMA Rank:")
        for mr in missing_ranks:
            print(f"- Page {mr['page']}: {mr['name']}")

if __name__ == "__main__":
    main()
