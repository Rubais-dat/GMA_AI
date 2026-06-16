import os
import pandas as pd

def main():
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "smartchoice_data.csv"))
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return
        
    df = pd.read_csv(csv_path)
    print("Columns in smartchoice_data.csv:")
    print(df.columns.tolist())
    print("\nFirst 3 rows:")
    print(df.head(3))
    
    # Check if 'gma' is in any column name or text
    gma_cols = [c for c in df.columns if 'gma' in c.lower() or 'rank' in c.lower()]
    print(f"\nColumns matching 'gma' or 'rank': {gma_cols}")

if __name__ == "__main__":
    main()
