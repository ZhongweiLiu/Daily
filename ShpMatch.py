import geopandas as gpd
import xarray as xr
import netCDF4 as nc
from shapely.geometry import Point
from scipy.spatial.distance import cdist
import pandas as pd


# 读取 Shapefile 文件
PowerPlant = r"E:\桌面\毕设\Data\TargetFinal\Target_final.shp"
PowerPlant_gdf = gpd.read_file(PowerPlant)
print('Point File Read Finished')

Oco3Shp = r"E:\桌面\毕设\Data\TargetFinal\SAM_final.shp"
Oco3Shp_gdf = gpd.read_file(Oco3Shp, encoding='UTF-8')
print('OCO-3 File Read Finished')

# 读取 NetCDF 文件
nc_file_path = "E:\\wind_uv10_2019_2023.nc"
ds = xr.open_dataset(nc_file_path)

# 提取经度和纬度信息
unique_longitude_values = ds['longitude'].values.flatten()
unique_longitude_values = list(set(unique_longitude_values))
unique_latitude_values = ds['latitude'].values.flatten()
unique_latitude_values = list(set(unique_latitude_values))

shp_coords = PowerPlant_gdf.geometry.apply(lambda point: (point.x, point.y)).tolist()
nc_coords = []
for i in range (len(unique_longitude_values)):
    for j in range (len(unique_latitude_values)):
        nc_coords.append([unique_longitude_values[i], unique_latitude_values[j]])

# 使用 scipy 中的 cdist 计算最近邻点
distances = cdist(shp_coords, nc_coords)
nearest_nc_points_idx = distances.argmin(axis=1)

# 将匹配结果添加到 GeoDataFrame 中
PowerPlant_gdf['nearest_nc_longitude'] = [nc_coords[i][0] for i in nearest_nc_points_idx]
PowerPlant_gdf['nearest_nc_latitude'] = [nc_coords[i][1] for i in nearest_nc_points_idx]

PowerPlant_gdf = PowerPlant_gdf.to_crs(epsg=3857)
Oco3Shp_gdf = Oco3Shp_gdf.to_crs(epsg=3857)

# 创建一个新的DataFrame来存储所有唯一的观测日期
unique_dates_list = []

# 为每个目标点创建缓冲区，并找出每个缓冲区内的观测值
for index, target in PowerPlant_gdf.iterrows():
    # 创建100km的缓冲区
    buffer = target['geometry'].buffer(100000)  # 100 km radius
    # 筛选出缓冲区内的观测点
    observations_within_buffer = Oco3Shp_gdf[Oco3Shp_gdf.within(buffer)]
    # 获取缓冲区内观测点的日期列表
    dates_within_buffer = (observations_within_buffer['date_']).unique()
    # 统计每个日期对应的观测点数量
    date_counts = observations_within_buffer.groupby('date_').size().to_dict()
    # 初始化当前 target 的独立 unique_dates 列表
    unique_dates = []
    # 将满足条件的日期加入到当前 target 的 unique_dates 列表中
    for date, count in date_counts.items():
        if count > 500:
            unique_dates.append(date)
    # 将当前 target 的 unique_dates 列表附加到主列表中
    unique_dates_list.append(unique_dates)

# 如果最后需要将坐标系转换回WGS84
PowerPlant_gdf = PowerPlant_gdf.to_crs(epsg=4326)
Oco3Shp_gdf = Oco3Shp_gdf.to_crs(epsg=4326)

# 添加唯一日期列表到 PowerPlant_gdf
PowerPlant_gdf['date_list'] = unique_dates_list

# 输出结果
result_df = PowerPlant_gdf[['Name_e', 'geometry', 'nearest_nc_longitude', 'nearest_nc_latitude', 'date_list']]
result_df.to_csv(r"E:\桌面\matching_results_500.csv", index=False)

