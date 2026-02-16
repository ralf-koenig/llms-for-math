import pandas as pd
from pathlib import Path

csv_file = Path("../python/data/autosaves/results_2026-02-09_19-35-36.csv")
xlsx_file = csv_file.with_suffix(".xlsx")

print("Reading csv file...", csv_file)
df = pd.read_csv(csv_file)

print("Writing xlsx file...", xlsx_file)
df.to_excel(xlsx_file, index=False)
