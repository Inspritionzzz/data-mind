import os
import pandas as pd

# \\WA_Fn-UseC_-Telco-Customer-Churn.xlsx
# \\WA_Fn-UseC_-Telco-Customer-Churn-result.xlsx
original_path = r"D:\\Users\\jason\\Desktop\\github\\awesome-python\\python-learn\\excel-tool"
result_path = r"D:\\Users\\jason\\Desktop\\github\\awesome-python\\python-learn\\excel-tool"

# original_path = "D:\\Users\\jason\Desktop\github\\awesome-python\\python-learn\\excel-tool\\WA_Fn-UseC_-Telco-Customer-Churn.xlsx"
# result_path = "D:\Users\jason\Desktop\github\awesome-python\python-learn\excel-tool\WA_Fn-UseC_-Telco-Customer-Churn-result.xlsx"

result_df = pd.DataFrame()

for file in os.listdir(original_path):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(original_path, file))
        sample_df = df.sample(n=10, axis=0)
        sample_df = sample_df.iloc[:, 1:]
        result_df = pd.concat([result_df, sample_df])

result_df.to_csv(os.path.join(result_path, "Train_Model_1.csv"), index = False)
