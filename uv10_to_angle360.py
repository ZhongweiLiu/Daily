import pandas as pd
import numpy as np

# 读取Excel文件
excel_file_path = r"E:\桌面\毕设\LinearDensity\_OCO3_integral.xlsx"
df = pd.read_excel(excel_file_path)

# 将u10和v10转换为风向角度
initial_wind_directions = np.rad2deg(np.arctan2(df.iloc[:, 13], df.iloc[:, 14]))

# 根据正南风为0度的要求调整角度
wind_directions = initial_wind_directions

# 将角度值转换为0到360度的范围内的正值
wind_directions = (wind_directions + 360) % 360

# 创建新列，存储风向角度
df['Wind_Direction'] = wind_directions

# 将结果写入新的Excel文件
output_excel_path = r"E:\桌面\_OCO3_integral3.xlsx"
df.to_excel(output_excel_path, index=False)
print("Wind directions written to Excel successfully.")