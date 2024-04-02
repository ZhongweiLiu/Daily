import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate
from sklearn.metrics import mean_squared_error, mean_absolute_error

# 导入数据
file_path = "E:/桌面/MarkovWuhan/200m_Reg.xlsx"
df = pd.read_excel(file_path, engine='openpyxl')

# 选择自变量与因变量的列
X = df.iloc[:, 1:6]  # 第2-6列为自变量
y = df.iloc[:, 6]  # 第7列为因变量

# 构建OLS回归模型
model = LinearRegression()

# 设置十折交叉验证
kf = KFold(n_splits=10, shuffle=True, random_state=1)

# 评分指标
scoring = {'r2': 'r2',
           'mse': 'neg_mean_squared_error',
           'mae': 'neg_mean_absolute_error'}

# 执行十折交叉验证
cv_results = cross_validate(model, X, y, cv=kf, scoring=scoring, return_estimator=True)

# 从交叉验证结果中计算平均R²、RMSE和MAE
r2_scores = cv_results['test_r2']
rmse_scores = np.sqrt(-cv_results['test_mse'])
mae_scores = -cv_results['test_mae']

print("Average R2:", np.mean(r2_scores))
print("Average RMSE:", np.mean(rmse_scores))
print("Average MAE:", np.mean(mae_scores))

# 提取每折交叉验证中的模型的系数
coefficients = []
for model in cv_results['estimator']:
    coefficients.append(model.coef_)

average_coefficients = np.mean(coefficients, axis=0)

# 打印平均系数
print("Average coefficients for each feature:")
for idx, coef in enumerate(average_coefficients):
    print(f"Coefficient for X{idx + 1}: {coef}")
