import geopandas as gpd
import pandas as pd
import numpy as np
import math
import time
from datetime import datetime
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')
plt.rcParams['font.family'] = 'Arial'


# 定义断面通量函数
def func(l, k, b, A, sigma, dx):
    return k * (l + dx) + b + (A / (sigma * np.sqrt(2 * np.pi))) * np.exp(-(l + dx)**2 / (2 * sigma**2))

# 计算经纬度距离
# longitude, latitude to km
def calculate_distance(lon1, lat1, lon2, lat2):
    # 计算经向距离和纬向距离的正负
    lon_distance = (lon2 - lon1) * 111.32 * math.cos(lat1 / 180 * math.pi)
    lat_distance = (lat2 - lat1) * 111.32
    return lon_distance, lat_distance


# 定义任务函数
def process_data(regions, timestamp, center_lon, center_lat, direction, image_id):
    result = ""

    timestamp_str = str(timestamp.strftime("%Y%m%d")).split(" ")[0].replace("-", "")
    # print(timestamp_str)
    selected_points = gdf[(gdf['date_'] == timestamp_str) & (gdf['xco2_quali'] == 0)].copy()
    # print(f"{regions} {timestamp} {direction}")

    r2_final = -np.inf
    fit_params = []

    if len(selected_points):
        # print(selected_points.columns)
        # print(f"{regions} {timestamp_str} {direction}")

        lon_distances, lat_distances = calculate_distance(
            center_lon, center_lat, selected_points['Longitude'].values, selected_points['Latitude'].values)

        selected_points['lon_distance'] = lon_distances
        selected_points['lat_distance'] = lat_distances
        # selected_points['xco2']

        selected_data = []

        for index, row in selected_points.iterrows():
            lon_distance = row['lon_distance']
            lat_distance = row['lat_distance']
            xco2 = row['xco2']
            xco2_quali = row['xco2_quali']

            if (xco2_quali == 0):
                selected_data.append({'lon_distance': lon_distance, 'lat_distance': lat_distance, 'xco2': xco2})

        wind_angle = (float(direction) / 180) * math.pi

        df = pd.DataFrame(selected_data)
        output_excel_path = fr'F:\OCO-3\co2_fit_xlsx_by_no2\{regions}_{timestamp_str}.xlsx'
        df.to_excel(output_excel_path, index=False)
        time.sleep(1)
        oco3_data = pd.read_excel(output_excel_path)

        oco3_data['rotated_x'] = np.nan
        oco3_data['rotated_y'] = np.nan

        r2_final = -np.inf
        data_lens = -1
        l_values_graph = None
        f_values_graph = None
        if len(oco3_data):

            rel_x = oco3_data.iloc[:, 0]
            # rel_x = oco3_data['Longitude Distance']
            rel_y = oco3_data.iloc[:, 1]
            # rel_x = oco3_data['Latitude Distance']

            # 旋转坐标系以对齐风向
            oco3_data['rotated_x'] = math.cos(wind_angle) * rel_x + math.sin(wind_angle) * rel_y
            oco3_data['rotated_y'] = -math.sin(wind_angle) * rel_x + math.cos(wind_angle) * rel_y

            # condition = (oco3_data['rotated_y'] / oco3_data['rotated_x'] < 0.6) \
            #             | (oco3_data['rotated_y'] / oco3_data['rotated_x'] > -0.6) \
            #             & (oco3_data['rotated_y'] > 0) \
            #             & (oco3_data['rotated_y'] < 50)

            condition = (oco3_data['rotated_x'] > -120) \
                        & (oco3_data['rotated_x'] < 120) \
                        & (oco3_data['rotated_y'] > 0) \
                        & (oco3_data['rotated_y'] < 40)

            # condition = (oco3_data['rotated_y'] > -10) \
            #             & (oco3_data['rotated_y'] < 60)


            # 创建新的 DataFrame
            filtered_data = oco3_data[condition].copy()
            # filtered_data = oco3_data.copy()
            filtered_data = filtered_data.sort_values(by='rotated_x', ascending=False)  # 按照 l_values 降序排列

            l_values = filtered_data.iloc[:, 3]
            f_values = filtered_data.iloc[:, 2]
            # print(len(l_values))
            # print(len(f_values))
            data_lens = len(filtered_data)


            popt, pcov = curve_fit(func, l_values, f_values,
                                   bounds=([-np.inf, -np.inf, 5, 0.01, -20],
                                           [np.inf, np.inf, np.inf, np.inf, 20]),
                                   method='trf', maxfev=100000)

            fitted_values = func(l_values, *popt)
            r_squared = r2_score(f_values, fitted_values)

            fit_params = popt.tolist()

            try:
                # 绘制拟合曲线和散点图
                plt.figure(figsize=(8, 6))
                plt.scatter(l_values, f_values, s=5, label='Soundings of OCO-3')
                x_values = np.linspace(-95, 95, 200)
                y_values = func(x_values, *popt)
                plt.plot(x_values, y_values, 'm', label='OCO-3 fit by XCO2')
                plt.xlabel('Distance in flight direction [km]', fontsize=12)
                plt.ylabel('XCO2 [ppm]', fontsize=12)
                plt.legend()
                plt.suptitle(f'{regions}_{timestamp}', fontsize=14, y=0.95, fontweight='bold')
                plt.savefig(rf'E:\桌面\毕设\Fig\parameter summary\co2_fit_by_no2_1\{regions}_{timestamp_str}.jpg', dpi=300)
                plt.close()
            except Exception as e:
                print(e)
                pass


        result = f"{image_id} {regions} {timestamp_str} {direction} {r_squared} {data_lens} {' '.join(map(str, fit_params)) if fit_params else 'None'}\n"
        print(result)
    return result


result_list = []

# 打开 CSV 文件并获取观测中心的经纬度坐标和时间戳
csv_file_path = r'E:\桌面\matching_results_500 - 副本.csv'
data = pd.read_csv(csv_file_path)  # 1 是观测中心的经纬度坐标列，4 是时间戳列

# 打开 Shapefile 文件
shp_file_path = r'E:\桌面\毕设\Data\TargetFinal\SAM_final.shp'
gdf = gpd.read_file(shp_file_path)

#  s5p_result
excel_file_path = r'E:\桌面\毕设\Result\results with figs\S5P.xlsx'
s5p_result_df = pd.read_excel(excel_file_path, parse_dates=['start_time_', 'end_time_'])
s5p_result_df['start_time__'] = pd.to_datetime(s5p_result_df['start_time_'])
s5p_result_df['end_time__'] = pd.to_datetime(s5p_result_df['end_time_'])

# 遍历每行数据
with ThreadPoolExecutor(max_workers=10) as executor:
    for index1, row1 in data.iterrows():
        target = row1['Name_e']
        timestamp_to_find = pd.to_datetime(row1['date_list'].split())
        center_lon, center_lat = map(float, row1['geometry'].replace('(', '').replace(')', '').split(', '))

        # 遍历每行s5p_result_df数据
        for index2, row2 in s5p_result_df.iterrows():
            regions = row2['target']
            image_id = row2['image_id']
            direction = row2['direction_avg']
            start_time = row2['start_time_'].replace(tzinfo=None)
            end_time = row2['end_time_'].replace(tzinfo=None)

            for timestamp in timestamp_to_find:
                if start_time <= timestamp <= end_time:
                    # 并行处理每个时间戳
                    futures = [executor.submit(process_data, regions, timestamp, center_lon, center_lat, direction, image_id)]
                    # 获取并打印结果
                    for future in as_completed(futures):  # 等待每个任务完成
                        result = future.result()
                        if result:
                            result_list.append(result)

# 将结果写入文件
with open(r'E:\桌面\毕设\Result\results with figs\OCO3_by_S5P_Para1.txt', 'a') as txt:
    for result in result_list:
        txt.write(result)
