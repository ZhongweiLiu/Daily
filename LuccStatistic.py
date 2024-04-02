import pandas


# write_root_path = r'E:\桌面\data_'
write_root_path = r'E:\桌面'
excel_root_path = r'E:\桌面'
lu_type = ['water', 'shrub', 'grass', 'forest', 'barren', 'impervious', 'crop']

# for i in range(len(lu_type)):
for i in range(1):
    data = []
    # filepath = excel_root_path + '\\' + lu_type[i] + '.xlsx'
    filepath = excel_root_path + '\\' + 'ntl' + '.xlsx'
    # print(filepath)

    workbook = pandas.ExcelFile(filepath)
    names = workbook.sheet_names
    print(names)

    title = []
    title_get = pandas.read_excel(filepath, sheet_name=0)['县']
    for n in title_get:
        title.append(n)
    title = '\t'.join(title) + '\n'
    count = 0

    for j in names:
        datalist = pandas.read_excel(filepath, sheet_name=j)['SUM']
        new_list = []
        for m in datalist:
            new_list.append(str(m))
            count += 1
        data.append(new_list)
        print(j)
    print(data)
    print(count)

    # filename = write_root_path + str(lu_type[i]) + '.txt'
    filename = write_root_path + 'ntl' + '.txt'
    fp = open(filename, 'w')
    fp.write(title)
    for k in data:
        fp.write('\t'.join(k) + '\n')
    fp.close()
