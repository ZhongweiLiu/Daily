import netCDF4 as nc
import pandas as pd
import numpy as np

# 读取.nc文件
era5_nc_file_path = r'E:\wind_uv10_2019_2023.nc'
era5_nc_file = nc.Dataset(era5_nc_file_path, 'r')

# 读取字段数据
time_era5 = era5_nc_file.variables['time'][:]
longitude_era5 = era5_nc_file.variables['longitude'][:]
latitude_era5 = era5_nc_file.variables['latitude'][:]
u10 = era5_nc_file.variables['u10'][:]
v10 = era5_nc_file.variables['v10'][:]

# 读取Excel文件并解析日期时间列
excel_file_path = r'E:\桌面\ERA5_XY.xlsx'
df = pd.read_excel(excel_file_path, parse_dates=['start_time', 'end_time'])
# # 转换日期时间为时区无关形式
# df['start_time'] = df['start_time'].dt.tz_localize(None)
# df['end_time'] = df['end_time'].dt.tz_localize(None)

# 定义起始时间
start_time = pd.to_datetime('1900-01-01 00:00:00').tz_localize('UTC')

# 创建新列以存储数据
df['selected_u10'] = np.nan
df['selected_v10'] = np.nan

# 处理每一行数据
for index, row in df.iterrows():
    # 提取时间戳
    start_time_s5p = (row['start_time'] - start_time).total_seconds() / 3600
    end_time_s5p = (row['end_time'] - start_time).total_seconds() / 3600

    # 提取经纬度坐标对
    lon_s5p, lat_s5p = map(float, row['geometry_nearst'].strip('()').split(','))

    # 根据时间和经纬度筛选数据
    selected_u10 = []
    selected_v10 = []

    # 找到对应时间段内的索引
    time_indices = np.where((time_era5 >= start_time_s5p) & (time_era5 <= end_time_s5p))[0]
    # 找到对应经纬度的索引
    lon_index = np.where(longitude_era5 == lon_s5p)[0]
    lat_index = np.where(latitude_era5 == lat_s5p)[0]

    # 筛选对应时间和经纬度的数据
    for time_idx in time_indices:
        if lon_index and lat_index:
            selected_u10.append(u10[time_idx][0][lon_index[0]][lat_index[0]])
            selected_v10.append(v10[time_idx][0][lon_index[0]][lat_index[0]])

    # 将数据存储到DataFrame中
    df.at[index, 'selected_u10'] = str(selected_u10)
    df.at[index, 'selected_v10'] = str(selected_v10)

# 将DataFrame写入Excel文件
output_excel_path = r'E:\桌面\ERA5_with_uv10.xlsx'
# 删除时间列
df.drop(['start_time', 'end_time'], axis=1, inplace=True)
df.to_excel(output_excel_path, index=False)
print("Data written to Excel successfully.")

# 关闭.nc文件
era5_nc_file.close()
