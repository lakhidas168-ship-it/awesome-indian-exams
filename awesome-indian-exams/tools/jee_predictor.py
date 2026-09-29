import csv
import sys
from pathlib import Path

def predict(rank, year):
    """
    Predicts college admission chances based on JEE rank and historical data.
    
    Safe: rank <= 80% of closing rank
    Possible: 80% < rank <= 100% of closing rank
    Reach: 100% < rank <= 120% of closing rank
    """
    data_path = Path(f"data/josaa/{year}.csv")
    if not data_path.exists():
        return f"Data for {year} not found."
    
    results = []
    with open(data_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                closing_rank = int(row['ClosingRank'])
            except (ValueError, KeyError):
                continue
                
            if rank <= closing_rank * 0.8:
                status = "Safe"
            elif rank <= closing_rank:
                status = "Possible"
            elif rank <= closing_rank * 1.2:
                status = "Reach"
            else:
                continue
            results.append(f"{row['Institute']} - {row['Program']} ({row['Category']}): {status}")
    return "\n".join(results)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 tools/jee_predictor.py <rank> <year>")
        sys.exit(1)
    try:
        print(predict(int(sys.argv[1]), sys.argv[2]))
    except ValueError:
        print("Rank must be an integer.")
        sys.exit(1)
