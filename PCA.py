import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# 读取数据集
file_path = r'E:\桌面\国创论文\0203\original_data\处理18.xlsx'
df = pd.read_excel(file_path)

# 提取特征变量
X = df.iloc[:, 3:8].values

# 标准化数据
scaler = StandardScaler()
X_standardized = scaler.fit_transform(X)

# 执行主成分分析
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_standardized)

# 将主成分分析得到的X、Y坐标添加为新的两列到DataFrame中
df['PC1'] = X_pca[:, 0]
df['PC2'] = X_pca[:, 1]

# 使用KMeans进行聚类（分为5类）
kmeans = KMeans(n_clusters=5, max_iter=5000, random_state=100)
df['Cluster'] = kmeans.fit_predict(X_standardized)

# 绘制可视化结果
plt.figure(figsize=(10, 6))

# 根据不同标签的不同颜色进行绘制
label_colors = {0: 'red', 1: 'green', 2: 'blue', 3: 'orange', 4: 'purple'}
for cluster, color in label_colors.items():
    cluster_data = df[df['Cluster'] == cluster]
    plt.scatter(cluster_data['PC1'], cluster_data['PC2'], label=f'Cluster {cluster}', color=color, s=3)

plt.title('PCA and KMeans Clustering')
plt.xlabel('主成分1')
plt.ylabel('主成分2')
plt.legend()
plt.show()

# 将DataFrame保存为新的Excel文件
output_file_path = r'E:\桌面\2018_with_PCA.xlsx'
df.to_excel(output_file_path, index=False)

# 输出主成分解释百分比
explained_variance_ratio = pca.explained_variance_ratio_
print(f'Explained Variance: PC1={explained_variance_ratio[0]:.2%}, PC2={explained_variance_ratio[1]:.2%}')
