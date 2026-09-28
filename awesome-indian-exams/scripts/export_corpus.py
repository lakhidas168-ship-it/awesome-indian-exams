#!/usr/bin/env python3
"""Export the exam corpus as JSONL for AI training."""
import json
import sys
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]

def get_corpus_data():
    # Logic to iterate over exams and their pages
    # For each page, split into sections
    # For each section, create a record
    # Validate: url, verification, length < 2000
    pass

def main():
    # Write to data/corpus.jsonl
    pass

if __name__ == "__main__":
    main()
