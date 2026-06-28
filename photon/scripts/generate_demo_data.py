"""
Generate synthetic manufacturing quality dataset for Photon demo.
500 rows, Jan-Dec 2024 weekdays, seed=42 for reproducibility.

Realistic patterns:
  - Q3 (Jul-Sep): ~30% higher redo rates (summer heat)
  - EQ-007, EQ-011: chronically high defect rates (aging equipment)
  - OP-003, OP-018: higher redo rates than average
  - Painting dept: highest scrap rates
  - Delta Industries, Titan Works: more defects (complex requirements)
  - Night shift: 20% more defects than Morning
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

N = 500

CLIENTS = [
    "Acme Corp", "Delta Industries", "Nexus Manufacturing", "Orion Systems",
    "Pacific Components", "Quantum Parts", "Stellar Fabrication", "Titan Works",
]
DEPARTMENTS = ["Assembly", "Welding", "Painting", "Quality Control", "Machining"]
EQUIPMENT_IDS = [f"EQ-{i:03d}" for i in range(1, 13)]   # EQ-001..EQ-012
OPERATOR_IDS = [f"OP-{i:03d}" for i in range(1, 26)]     # OP-001..OP-025
PRODUCT_TYPES = ["Type-A", "Type-B", "Type-C", "Type-D"]
SHIFTS = ["Morning", "Afternoon", "Night"]
LINES = ["Line-1", "Line-2", "Line-3", "Line-4"]

# --- dates ---
weekdays_2024 = pd.bdate_range("2024-01-01", "2024-12-31")
dates = np.sort(np.random.choice(weekdays_2024, size=N, replace=True))
months = pd.DatetimeIndex(dates).month

# --- categorical columns ---
client_arr = np.random.choice(CLIENTS, size=N)
dept_arr = np.random.choice(DEPARTMENTS, size=N)
equip_arr = np.random.choice(EQUIPMENT_IDS, size=N)
op_arr = np.random.choice(OPERATOR_IDS, size=N)
product_arr = np.random.choice(PRODUCT_TYPES, size=N)
shift_arr = np.random.choice(SHIFTS, size=N)
line_arr = np.random.choice(LINES, size=N)

# --- units_produced: 80-200 ---
units_produced = np.random.randint(80, 201, size=N)

# --- defect_count: base Poisson(2.5), max 15 ---
defect = np.random.poisson(2.5, size=N)

# dept modifier: Welding +2, Painting +2.5
defect += np.where(dept_arr == "Welding",   np.random.poisson(2.0, N), 0)
defect += np.where(dept_arr == "Painting",  np.random.poisson(2.5, N), 0)

# equipment modifier: EQ-007 +3, EQ-011 +3
defect += np.where(equip_arr == "EQ-007", np.random.poisson(3.0, N), 0)
defect += np.where(equip_arr == "EQ-011", np.random.poisson(3.0, N), 0)

# night shift: +20% → add Binomial(3, 0.4) ≈ 1.2 extra
defect += np.where(shift_arr == "Night", np.random.binomial(3, 0.4, N), 0)

# client modifier: Delta Industries, Titan Works +1.5
defect += np.where(
    np.isin(client_arr, ["Delta Industries", "Titan Works"]),
    np.random.poisson(1.5, N), 0
)

defect_count = np.clip(defect, 0, 15).astype(int)

# --- redo_count: base Poisson(1.5), max 8 ---
redo = np.random.poisson(1.5, size=N)

# operator modifier: OP-003, OP-018 +2
redo += np.where(np.isin(op_arr, ["OP-003", "OP-018"]), np.random.poisson(2.0, N), 0)

# Q3 (Jul-Sep): 30% more → add Poisson(0.45)
redo += np.where(np.isin(months, [7, 8, 9]), np.random.poisson(0.45, N), 0)

redo_count = np.clip(redo, 0, 8).astype(int)

# --- scrap_count: base Poisson(0.5), max 5 ---
scrap = np.random.poisson(0.5, size=N)
scrap += np.where(dept_arr == "Painting", np.random.poisson(1.5, N), 0)
scrap_count = np.clip(scrap, 0, 5).astype(int)

# --- inspection_result: correlated with defect_count ---
inspection_choices = np.empty(N, dtype=object)
low   = defect_count < 3                       # mostly Pass
high  = defect_count >= 8                      # mostly Fail
mid   = ~low & ~high

inspection_choices[low]  = np.random.choice(["Pass", "Conditional", "Fail"],
                                             size=low.sum(), p=[0.85, 0.10, 0.05])
inspection_choices[mid]  = np.random.choice(["Pass", "Conditional", "Fail"],
                                             size=mid.sum(), p=[0.40, 0.45, 0.15])
inspection_choices[high] = np.random.choice(["Pass", "Conditional", "Fail"],
                                             size=high.sum(), p=[0.10, 0.30, 0.60])

# --- assemble DataFrame ---
order_ids = [f"ORD-2024{i+1:04d}" for i in range(N)]

df = pd.DataFrame({
    "date":               pd.DatetimeIndex(dates).strftime("%Y-%m-%d"),
    "order_id":           order_ids,
    "client":             client_arr,
    "department":         dept_arr,
    "equipment_id":       equip_arr,
    "operator_id":        op_arr,
    "product_type":       product_arr,
    "units_produced":     units_produced,
    "defect_count":       defect_count,
    "redo_count":         redo_count,
    "scrap_count":        scrap_count,
    "inspection_result":  inspection_choices,
    "shift":              shift_arr,
    "line_id":            line_arr,
})

df = df.sort_values("date").reset_index(drop=True)

# --- write ---
out = Path(__file__).parent.parent / "data" / "demo" / "manufacturing_quality.csv"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)

print(f"Rows:  {len(df)}")
print(f"Saved: {out}")
print("\nFirst 5 rows:")
print(df.head().to_string())
print("\nColumn dtypes:")
print(df.dtypes.to_string())
