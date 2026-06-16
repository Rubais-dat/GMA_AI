import os

def main():
    cleaned_txt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "gma_cleaned.txt"))
    with open(cleaned_txt_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if "kmct" in line.lower():
                print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    main()
