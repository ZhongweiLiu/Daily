import time

import geopandas as gpd
import pandas as pd
import numpy as np
import math
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from multiprocessing import Pool, Manager
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')
plt.rcParams['font.family'] = 'Arial'

# 定义断面通量函数
def func(l, k, b, A, sigma, dx):
    return k * (l + dx) + b + (A / (sigma * np.sqrt(2 * np.pi))) * np.exp(-(l + dx) ** 2 / (2 * sigma ** 2))


# 计算经纬度距离
# longitude, latitude to km
def calculate_distance(lon1, lat1, lon2, lat2):
    # 计算经向距离和纬向距离的正负
    lon_distance = (lon2 - lon1) * 111.32 * math.cos(lat1 / 180 * math.pi)
    lat_distance = (lat2 - lat1) * 111.32
    return lon_distance, lat_distance


# 打开 Shapefile 文件
# shp_file_path = r'E:\桌面\毕设\Data\test\SAM_final_test.shp'
shp_file_path = r'E:\桌面\毕设\Data\TargetFinal\SAM_final.shp'
gdf = gpd.read_file(shp_file_path)

# 打开 CSV 文件并获取观测中心的经纬度坐标和时间戳
csv_file_path = r'E:\桌面\matching_results_500 - 副本.csv'
data = pd.read_csv(csv_file_path)  # 1 是观测中心的经纬度坐标列，4 是时间戳列


# 定义任务函数
def process_data(args):
    regions, timestamp, center_lon, center_lat = args
    selected_points = gdf[gdf['date_'] == timestamp].copy()

    if len(selected_points):
        lon_distances, lat_distances = calculate_distance(
            center_lon, center_lat, selected_points['Longitude'].values, selected_points['Latitude'].values)
        selected_points['lon_distance'] = lon_distances
        selected_points['lat_distance'] = lat_distances

        # print(selected_points)
        selected_data = []

        for lon_distance, lat_distance, quali, xco2, uncer in zip(selected_points['lon_distance'],
                                                                   selected_points['lat_distance'],
                                                                   selected_points['xco2_quali'],
                                                                   selected_points['xco2'],
                                                                   selected_points['xco2_uncer']):

            if (lon_distance ** 2 + lat_distance ** 2 <= 10000) & (quali == 0):
                selected_data.append({'xco2_quali': quali,
                                      'xco2': xco2,
                                      'Longitude Distance': lon_distance,
                                      'Latitude Distance': lat_distance,
                                      'xco2_uncer': uncer})

        df = pd.DataFrame(selected_data)
        output_excel_path = fr'F:\OCO-3\co2_fit_xlsx\{regions}_{timestamp}.xlsx'
        df.to_excel(output_excel_path, index=False)
        time.sleep(1)
        oco3_data = pd.read_excel(output_excel_path)

        oco3_data['rotated_x'] = np.nan
        oco3_data['rotated_y'] = np.nan

        r2_final = -np.inf
        direction_final = -1
        data_lens = -1
        optimal_direction_data = None
        l_values_graph = None
        f_values_graph = None
        fit_params_graph = None

        if len(oco3_data):

            results = []

            for i in range(0, 360):

                wind_angle = (float(i) / 180) * math.pi

                # 计算相对位置
                # print(type(oco3_data))
                # print(oco3_data.head())

                rel_x = oco3_data.iloc[:, 2]
                # rel_x = oco3_data['Longitude Distance']
                rel_y = oco3_data.iloc[:, 3]
                # rel_x = oco3_data['Latitude Distance']

                try:
                    # 旋转坐标系以对齐风向
                    oco3_data['rotated_x'] = math.cos(wind_angle) * rel_x + math.sin(wind_angle) * rel_y
                    oco3_data['rotated_y'] = -math.sin(wind_angle) * rel_x + math.cos(wind_angle) * rel_y

                    # condition = (oco3_data['rotated_y'] / oco3_data['rotated_x'] < 0.6) \
                    #             | (oco3_data['rotated_y'] / oco3_data['rotated_x'] > -0.6) \
                    #             & (oco3_data['rotated_y'] > 0) \
                    #             & (oco3_data['rotated_y'] < 30)

                    condition = (oco3_data['rotated_x'] > -100) \
                                & (oco3_data['rotated_x'] < 100) \
                                & (oco3_data['rotated_y'] > 0) \
                                & (oco3_data['rotated_y'] < 50)

                    # 创建新的 DataFrame
                    filtered_data = oco3_data[condition].copy()
                    filtered_data = filtered_data.sort_values(by='rotated_x', ascending=False)  # 按照 l_values 降序排列
                    data_lens = len(filtered_data)

                    # print(filtered_data.columns)
                    # df2 = pd.DataFrame(filtered_data)
                    # df2.to_excel(r'E:\桌面\filter。xlsx')
                    l_values = filtered_data.iloc[:, 5]
                    f_values = filtered_data.iloc[:, 1]
                    # print(len(l_values))
                    # print(len(f_values))

                    popt, pcov = curve_fit(func, l_values, f_values,
                                           bounds=([-np.inf, -np.inf, 0.01, 0.01, -20],
                                                   [np.inf, np.inf, np.inf, np.inf, 20]),
                                           method='trf',
                                           maxfev=10000)

                    fitted_values = func(l_values, *popt)
                    r_squared = r2_score(f_values, fitted_values)
                    results.append((i, data_lens, r_squared, popt, l_values, f_values))

                    # if r_squared > r2_final:
                    #     r2_final = r_squared
                    #     l_values_graph = l_values
                    #     f_values_graph = f_values
                    #     direction_final = i
                    #     fit_params_graph = fitted_values
                    #     optimal_direction_data = filtered_data
                    #     five_fit_params = popt.tolist()

                except Exception as e:
                    # print(e)
                    pass

            # print(fit_params_graph)
            best_result = max(results, key=lambda x: x[2])
            direction_final, data_lens_result, r2_final, popt_values, l_values_graph, f_values_graph = best_result

            try:
                plt.figure(figsize=(8, 6))
                plt.scatter(l_values_graph, f_values_graph, s=5, label='Soundings of OCO-3')
                x_values = np.linspace(-95, 95, 200)
                y_values = func(x_values, *popt_values)
                plt.plot(x_values, y_values, 'm', label='OCO-3 fit by XCO2')
                plt.xlabel('Distance in flight direction [km]', fontsize=12)
                plt.ylabel('XCO2 [ppm]', fontsize=12)
                plt.legend()
                plt.suptitle(f'{regions}_{timestamp}', fontsize=14, y=0.95, fontweight='bold')
                plt.savefig(rf'E:\桌面\毕设\Fig\parameter summary\co2_fit_1_0\{regions}_{timestamp}.jpg', dpi=300)
                plt.close()
            except Exception as e:
                pass

            fit_params = " ".join(str(param) for param in popt_values)
            result = f"{regions} {timestamp} {direction_final} {r2_final} {data_lens} {fit_params}\n"
            print(result)
    return result


if __name__ == '__main__':
    # 使用多核并行计算来处理多个zip文件
    with Pool(processes=11) as pool:
        args_list = [(row['Name_e'], timestamp, *map(float, row['geometry'].replace('(', '').replace(')', '').split(', ')))
                     for index, row in data.iterrows() for timestamp in row['date_list'].split()]
        result_list = pool.map(process_data, args_list)

    # 将结果写入文件
    with open(r'E:\桌面\毕设\Result\results with figs\OCO3_Para1_0.txt', 'a') as txt:
        for result in result_list:
            txt.write(result)
