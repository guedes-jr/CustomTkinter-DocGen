import pandas as pd
import numpy as np

# Simulate reading an excel with empty cells
data = {
    'Nome': ['Alice', 'Bob', np.nan],
    'Idade': [25, np.nan, 30]
}
df = pd.DataFrame(data)

print("Antes do fillna:")
print(df)
for index, row in df.iterrows():
    print(f"Linha {index}: Nome='{row['Nome']}' (type: {type(row['Nome'])})")

# The fix
df = df.fillna("")

print("\nDepois do fillna:")
print(df)
for index, row in df.iterrows():
    print(f"Linha {index}: Nome='{row['Nome']}' (type: {type(row['Nome'])})")
    val = row['Nome']
    print(f"str(val) = '{str(val)}'")
