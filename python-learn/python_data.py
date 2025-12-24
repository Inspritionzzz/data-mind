import numpy as np
import pandas as pd
import matplotlib


# 1. series
s = pd.Series(data=[1, 2, 3, 4], index=["a", "b", "c", "d"])
print(s)

# 2. DataFrame
df = pd.DataFrame(data=[[1, 3, 5], [2, 6, 9]], columns=["java", "python", "SQL"])
print(df)

print(df[:1])