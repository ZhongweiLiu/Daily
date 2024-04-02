import netCDF4 as nc
import os
import shapefile
from multiprocessing import Pool
from functools import partial


# 合并成一个日期时间值
def origin_date_to_str(nc_file, i):
    # date to string
    variable = nc_file.variables['date']
    origin_data = variable[i]
    # 将日期和时间的各个部分提取出来
    year = origin_data[0]
    month = origin_data[1]
    day = origin_data[2]
    hour = origin_data[3]
    minute = origin_data[4]
    second = origin_data[5]
    microsecond = origin_data[6]
    decimal_value = (year * 1000000000000 + month * 10000000000 + day * 100000000 +
                     hour * 1000000 + minute * 10000 + second * 100 + microsecond * 1)
    return decimal_value


def count_target_data(target_name_values):
    target_name_count = {}
    for value in target_name_values:
        if value != "none":
            target_name_count[value] = target_name_count.get(value, 0) + 1
    return target_name_count


def nc4_to_shp(file_name, folder_path):
    # open .nc4 file
    full_path = os.path.join(folder_path, file_name)
    nc_file = nc.Dataset(full_path, 'r')

    sounding_group = nc_file.groups['Sounding']
    target_name_variable = sounding_group.variables['target_id']
    target_name_values = target_name_variable[:]
    print(len(target_name_values))

    retrieval_group = nc_file.groups['Retrieval']
    tcwv_variable = retrieval_group.variables['tcwv']
    tcwv_value = tcwv_variable[:]
    # print(tcwv_value)
    # print(len(tcwv_value))

    # 统计每个 target_name 对应的数据条数
    target_name_count = count_target_data(target_name_values)

    # 过滤超过1000条的 target_name 数据
    valid_target_names = [name for name, count in target_name_count.items() if count > 1500]
    # print(valid_target_names)


    latitude = nc_file.variables['latitude']
    longitude = nc_file.variables['longitude']
    sounding_id = nc_file.variables['sounding_id']
    xco2_quality_flag = nc_file.variables['xco2_quality_flag']
    xco2 = nc_file.variables['xco2']
    # print(type(xco2[10]), xco2[10])
    xco2_uncertainty = nc_file.variables['xco2_uncertainty']
    target_name = sounding_group.variables['target_name']
    pressure_level = nc_file.variables['pressure_levels']

    #     pressure_level_value.append(pressure_level[i][-1])
    # print(len(pressure_level_value))
    # print(sum(pressure_level_value)/len(pressure_level_value))

    out_name = folder_path + "\\oco3_shp\\" + file_name.split('_')[-1].split('.')[0]
    w = shapefile.Writer(out_name, shapeType=1)

    w.prj = 'GEOGCS["WGS 84",...]'  # 原本的 WGS 84 参数

    w.field('sounding_id', 'N', '20')
    w.field('xco2_quality_flag', 'N', '10')
    w.field('xco2', 'C', '8')
    w.field('xco2_uncertainty', 'C', '8')
    w.field('date', 'N', '20')
    w.field('target_name', 'C', '20')
    w.field('tcwv', 'C', '20')
    w.field('pressure_levels', 'C', '20')

    for i, value in enumerate(target_name_values):
        # if value in valid_target_names :
        if value in valid_target_names and 'China' in target_name[i]:
            w.point(longitude[i], latitude[i])
            w.record(sounding_id[i], xco2_quality_flag[i], float(xco2[i]), float(xco2_uncertainty[i]),
                     origin_date_to_str(nc_file, i), target_name[i], tcwv_value[i], pressure_level[i][-1])

    w.close()
    r = shapefile.Reader(out_name + '.shp')
    num_records = len(r.shapes())
    r.close()

    if num_records == 0:
        extensions = ['.shp', '.shx', '.dbf']
        for ext in extensions:
            file_to_delete = os.path.join(folder_path, out_name + ext)
            os.remove(file_to_delete)
        # print("Deleting:", str(os.path.join(folder_path, out_name)))
    if num_records:
        pass
        print(file_name, ' generates ', out_name, ' num:', num_records)


if __name__ == '__main__':
    folder_path = r'G:\毕设数据\不用了\oco3_data'
    file_list = os.listdir(folder_path)
    nc_files = [file for file in file_list if file.endswith('.nc4')]

    with Pool(processes=11) as pool:
        func = partial(nc4_to_shp, folder_path=folder_path)
        pool.map(func, nc_files)
