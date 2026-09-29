import sys
from pathlib import Path

def check_eligibility(age_limit, qualification, attempts):
    print(f"Age limit: {age_limit}")
    print(f"Qualification: {qualification}")
    print(f"Attempts: {attempts}")
    print("Confirm in the notification.")

if __name__ == "__main__":
    # Simple CLI for the checker
    if len(sys.argv) < 4:
        print("Usage: python3 scripts/eligibility_checker.py <age> <qual> <attempts>")
    else:
        check_eligibility(sys.argv[1], sys.argv[2], sys.argv[3])
