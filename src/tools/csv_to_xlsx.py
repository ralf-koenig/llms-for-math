import pandas as pd
from pathlib import Path

csv_file = Path("../python/data/autosaves/results_2026-02-11_14-02-10.csv")
xlsx_file = csv_file.with_suffix(".xlsx")

df = pd.read_csv(csv_file)
df.to_excel(xlsx_file, index=False)
