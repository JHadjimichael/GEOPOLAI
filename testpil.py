import pandas as pd
df = pd.read_csv('processed_1km.csv')

num_lines = df.shape[0]

print(num_lines)