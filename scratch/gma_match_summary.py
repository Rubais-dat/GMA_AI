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
    
    # We will map each page to a college by checking for identifying strings in the first 15 lines of each page.
    # We'll associate each page with a college code if matched.
    page_mappings = {}
    for idx, page in enumerate(pages):
        page_num = idx
        p_clean = page.strip()
        if not p_clean:
            continue
            
        lines = [l.strip() for l in p_clean.split("\n") if l.strip()]
        if not lines:
            continue
            
        # We search the first 15 lines of the page for references to GMA college names or codes
        matched_code = None
        for code, info in gma_colleges.items():
            # Check for exact code match in the page
            code_pat = r"\b" + re.escape(code) + r"\b"
            if any(re.search(code_pat, line) for line in lines[:10]):
                matched_code = code
                break
                
            # Check for words in the name
            words = [w.lower() for w in info['name'].replace(".", "").replace(",", "").split() if len(w) > 3 and w.lower() not in ["medical", "college", "hospital", "institute", "sciences", "government", "govt"]]
            found_words = 0
            for w in words:
                if any(w in line.lower() for line in lines[:10]):
                    found_words += 1
            if len(words) > 0 and found_words >= len(words) * 0.7:
                matched_code = code
                break
        
        # Manual overrides for pages where names might be OCR'd weirdly or split
        if not matched_code:
            text_header = "\n".join(lines[:10]).lower()
            if "al-azhar" in text_header or "aamc" in text_header:
                matched_code = "AAM"
            elif "amala" in text_header or "aims" in text_header:
                matched_code = "AMC"
            elif "azeezia" in text_header or "azc" in text_header:
                matched_code = "AZC"
            elif "believers" in text_header or "bcmc" in text_header:
                matched_code = "BCM"
            elif "gokulam" in text_header or "sgmc" in text_header:
                matched_code = "GMC"
            elif "alappuzha" in text_header or "tdmc" in text_header:
                matched_code = "ALP"
            elif "calicut" in text_header or "kozhikode" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "KKM"
            elif "ernakulam" in text_header or "gmce" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "CMC"
            elif "idukki" in text_header or "gmci" in text_header:
                matched_code = "IDM"
            elif "kannur" in text_header or "gmck" in text_header:
                matched_code = "KNM"
            elif "kasaragod" in text_header or "kasaragod" in text_header:
                matched_code = "KSM"
            elif "kollam" in text_header or "parippally" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "KLM"
            elif "kottayam" in text_header or "gmck" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "KTM"
            elif "manjeri" in text_header or "gmcm" in text_header:
                matched_code = "MLP"
            elif "palakkad" in text_header or "iims" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "PKM"
            elif "konni" in text_header or "pathanamthitta" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "PTM"
            elif "thrissur" in text_header or "tcm" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "TCM"
            elif "thiruvananthapuram" in text_header or "trivandrum" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "TVM"
            elif "wayanad" in text_header or "mananthavady" in text_header:
                if "govt" in text_header or "government" in text_header:
                    matched_code = "WYM"
            elif "jubilee" in text_header or "jmmc" in text_header:
                matched_code = "JMC"
            elif "karuna" in text_header or "kmc" in text_header:
                if "kerala" not in text_header:
                    matched_code = "KMM"
            elif "kerala medical" in text_header:
                matched_code = "KEM"
            elif "kmct" in text_header:
                matched_code = "KCM"
            elif "malabar" in text_header:
                matched_code = "MMH"
            elif "orthodox" in text_header or "mosc" in text_header:
                matched_code = "MMC"
            elif "mes" in text_header:
                matched_code = "EMC"
            elif "moopen" in text_header or "wims" in text_header:
                matched_code = "DMM"
            elif "mount zion" in text_header:
                matched_code = "MZM"
            elif "palakkad institute" in text_header or "pims" in text_header:
                matched_code = "PIM"
            elif "das" in text_header or "pkd" in text_header:
                matched_code = "KDM"
            elif "pushpagiri" in text_header:
                matched_code = "PMC"
            elif "somervell" in text_header or "karakonam" in text_header:
                matched_code = "SMC"
            elif "sut" in text_header or "uthradom" in text_header:
                matched_code = "SUC"
            elif "travancore" in text_header:
                matched_code = "TRM"
            elif "sree narayana" in text_header or "snims" in text_header:
                matched_code = "SIM"

        if matched_code:
            page_mappings[page_num] = matched_code

    # For each GMA college, find the page range or list of pages in the PDF
    college_pages = {code: [] for code in gma_colleges}
    for p, code in page_mappings.items():
        college_pages[code].append(p)

    # Print summary
    print(f"{'Code':<5} | {'Type':<10} | {'GMA College Name':<55} | {'GMA Rank':<8} | {'PDF Pages':<25}")
    print("-" * 110)
    
    # Sort by Type (Govt first, then Private), then by GMA Rank
    sorted_colleges = sorted(gma_colleges.items(), key=lambda x: (x[1]['type'], x[1]['gma_rank']))
    
    found_count = 0
    missing_count = 0
    
    for code, info in sorted_colleges:
        pages_list = college_pages[code]
        if pages_list:
            found_count += 1
            # format as range or list
            pages_list.sort()
            # find consecutive ranges
            ranges = []
            start = pages_list[0]
            prev = pages_list[0]
            for p in pages_list[1:]:
                if p == prev + 1:
                    prev = p
                else:
                    if start == prev:
                        ranges.append(f"{start}")
                    else:
                        ranges.append(f"{start}-{prev}")
                    start = p
                    prev = p
            if start == prev:
                ranges.append(f"{start}")
            else:
                ranges.append(f"{start}-{prev}")
            pages_str = ", ".join(ranges)
        else:
            missing_count += 1
            pages_str = "NOT FOUND IN PDF"
            
        print(f"{code:<5} | {info['type']:<10} | {info['name'][:55]:<55} | {info['gma_rank']:<8} | {pages_str:<25}")

    print("\n" + "="*50)
    print(f"Total GMA Database Colleges: {len(gma_colleges)}")
    print(f"Colleges present in PDF: {found_count}")
    print(f"Colleges missing from PDF: {missing_count}")

if __name__ == "__main__":
    main()
