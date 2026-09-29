# JEE College Predictor

This tool helps you estimate your chances of admission to various engineering colleges based on your JEE Main rank.

**Disclaimer:**
- Ranks change every year based on the number of applicants, difficulty level, and seat availability.
- This tool provides an estimate based on historical data.
- Results are categorized as:
    - **Safe**: Your rank is well within the historical closing rank.
    - **Possible**: Your rank is close to the historical closing rank.
    - **Reach**: Your rank is near or slightly above the historical closing rank.

## Data Sources
- [JoSAA Opening/Closing Ranks](https://josaa.admissions.nic.in/)

## Usage
Run the tool from the command line:
```bash
python3 tools/jee_predictor.py <rank> <year>
```
Example:
```bash
python3 tools/jee_predictor.py 5000 2023
```
