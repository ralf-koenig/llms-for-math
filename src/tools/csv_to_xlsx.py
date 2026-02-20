import pandas as pd
from pathlib import Path

csv_file = Path("../python/data/results/qwen-coder/results_2026-02-16_21-41-15.csv")
xlsx_file = csv_file.with_suffix(".xlsx")

print("Reading csv file...", csv_file)
df = pd.read_csv(csv_file)

print("Writing xlsx file...", xlsx_file)
df.to_excel(xlsx_file, index=False)
