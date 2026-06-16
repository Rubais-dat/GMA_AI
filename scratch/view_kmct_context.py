import os

def main():
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    start = max(0, 16741 - 15)
    end = min(len(lines), 16741 + 10)
    for i in range(start, end):
        print(f"Line {i+1}: {lines[i].strip()}")

if __name__ == "__main__":
    main()
