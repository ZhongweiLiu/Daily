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

# 提取经纬度坐标对
lon_s5p, lat_s5p = 109, 34.25

# 根据经纬度筛选数据
selected_u10 = []
selected_v10 = []

# 找到对应经纬度的索引
lon_index = np.where(longitude_era5 == lon_s5p)[0]
lat_index = np.where(latitude_era5 == lat_s5p)[0]

# 筛选对应时间和经纬度的数据
for i in range(len(u10)):
    if lon_index and lat_index:
        selected_u10.append(u10[i][0][lon_index[0]][lat_index[0]])
        selected_v10.append(v10[i][0][lon_index[0]][lat_index[0]])

# 创建DataFrame保存数据
data = {'time': time_era5, 'u10': selected_u10, 'v10': selected_v10}

# 转换时间为年-月-日-小时形式
time_values = pd.to_datetime(data['time'], unit='h', origin='1900-01-01 00:00:00')
data['time_formatted'] = time_values.strftime('%Y-%m-%d-%H')

df = pd.DataFrame(data)

# 将DataFrame写入Excel文件
output_excel_path = r'E:\桌面\Xi‘an_uv10.xlsx'
df.to_excel(output_excel_path, index=False)
print("Data written to Excel successfully.")

# 关闭.nc文件
era5_nc_file.close()
