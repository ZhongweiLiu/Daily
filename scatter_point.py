import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取数据集
file_path = r'E:\桌面\2015-2019_with_PCA_and_KMeans.xlsx'
df = pd.read_excel(file_path)

# 绘制散点图
plt.figure(figsize=(10, 6))

# 根据第11列的值进行着色
plt.scatter(df['PC1'], df['PC2'], c=df.iloc[:, 14], cmap='viridis', s=0.3)

# 绘制直线 y=1.6x
x_values = np.linspace(min(df['PC1']), max(df['PC1']), 100)
y_values = 1.6 * x_values + 1
plt.plot(x_values, y_values, color='red', linestyle='--', label='y=1.6x')

plt.title('rc')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.legend()
plt.show()
