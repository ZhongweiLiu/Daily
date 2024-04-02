import pandas as pd
from scipy.stats import pearsonr

# 读取Excel文件
# file_path = r'E:\桌面\国创论文\0203\trans&attr\attr.xlsx'
file_path = r'E:\桌面\国创论文\0203\2015-2019_with_PCA_and_KMeans - 0218.xlsx'
df = pd.read_excel(file_path)

# 选取前5列数据
selected_data = df.iloc[:, 3:8]
# selected_data = df.iloc[:, 11:13]

# 计算两两列之间的Pearson相关系数及其p值
correlation_matrix = selected_data.corr(method='pearson')
p_values = selected_data.corr(method=lambda x, y: pearsonr(x, y)[1])

# 将p值保留到小数点后五位
p_values = p_values.applymap(lambda x: round(x, 5))

# 打印相关系数
print("Correlation Matrix:")
print(correlation_matrix)

# 打印p值
print("\nP Values:")
print(p_values.to_string(float_format="{:.5f}".format))