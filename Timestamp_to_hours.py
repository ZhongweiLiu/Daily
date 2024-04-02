import pandas as pd

# 读取Excel文件
excel_file_path = r"E:\桌面\matching_results_second.xlsx"
df = pd.read_excel(excel_file_path)

# 提取时间戳列，并按空格分隔
timestamps = df.iloc[3, 4].split()

# 初始化列表来存储计算得到的小时数
hours_since_1900 = []

# 计算每个时间戳相对于"1900-01-01 00:00:00"的小时数，并将结果添加到列表中
for timestamp in timestamps:
    # 将时间戳转换为Pandas的日期时间格式
    timestamp_dt = pd.to_datetime(timestamp, format='%Y%m%d%H%M')
    # 计算相对于"1900-01-01 00:00:00"的小时数，并四舍五入取整数，然后添加到列表中
    hours_since_1900.append(round((timestamp_dt - pd.Timestamp('1900-01-01 00:00:00')).total_seconds() / 3600))
    print(f"Original Timestamp: {timestamp}, Hours since 1900: {hours_since_1900[-1]}")

# 创建新的 DataFrame
new_df = pd.DataFrame({'Original_Timestamp': timestamps, 'Hours_Since_1900': hours_since_1900})

# 将新的 DataFrame 写入 Excel 文件
output_excel_path = r"E:\桌面\Chifeng_hours.xlsx"
new_df.to_excel(output_excel_path, index=False)
print("Data written to Excel successfully.")
