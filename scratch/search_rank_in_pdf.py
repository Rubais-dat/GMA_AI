import os

def main():
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split("\n")
    print(f"Total lines: {len(lines)}")
    
    # Let's search for "gma rank" or "getmyadmission rank" or "gma overall rank"
    found = 0
    for idx, line in enumerate(lines):
        l_lower = line.lower()
        if "gma" in l_lower and "rank" in l_lower:
            print(f"Line {idx+1}: {line.strip()}")
            found += 1
            if found >= 20:
                break
                
    if found == 0:
        print("No lines containing both 'gma' and 'rank' found.")

if __name__ == "__main__":
    main()
