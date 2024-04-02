import numpy as np
import pandas as pd
from scipy.integrate import quad

# 读取Excel文件
excel_file_path = r'E:\桌面\毕设\LinearDensity\_OCO3.xlsx'
df = pd.read_excel(excel_file_path)


# 定义函数
def func(l, k, b, A, sigma, dx):
    return k * (l + dx) + b + (A / (sigma * np.sqrt(2 * np.pi))) * np.exp(-(l + dx) ** 2 / (2 * sigma ** 2))


def linear_func(l, k, b, dx):
    return k * (l + dx) + b


# 初始化积分结果列表
integral_results_func = []
integral_results_linear = []

# 逐行计算积分值
for index, row in df.iterrows():
    # 读取参数值
    k = row[5]  # 第6列作为参数k
    b = row[6]  # 第7列作为参数b
    A = row[7]  # 第8列作为参数A
    sigma = row[8]  # 第9列作为参数sigma
    dx = row[9]  # 第10列作为参数dx

    # 定义积分区间
    lower_limit = -100
    upper_limit = 100

    # 求积分
    result_func, error_func = quad(func, lower_limit, upper_limit, args=(k, b, A, sigma, dx))
    result_linear, error_linear = quad(linear_func, lower_limit, upper_limit, args=(k, b, dx))

    # 将积分结果添加到列表中
    integral_results_func.append(result_func)
    integral_results_linear.append(result_linear)

# 将积分结果添加到DataFrame中
df['Integral_Result_Func'] = integral_results_func
df['Integral_Result_Linear'] = integral_results_linear

# 保存结果到新的Excel文件
output_excel_path = r'E:\桌面\毕设\LinearDensity\_OCO3_integral1.xlsx'
df.to_excel(output_excel_path, index=False)

print("Integration results saved to Excel successfully.")