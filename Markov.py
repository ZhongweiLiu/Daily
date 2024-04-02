import pandas as pd
import numpy as np

# 读取数据
df = pd.read_excel(r"E:\桌面\MarkovWuhan\MarkovStreet.xlsx", usecols=[2, 3, 4, 5, 6, 7])

# 函数：修改概率矩阵
def modify_probabilities(matrix, states, increase=True, adjustment=0.3):
    modified_matrix = matrix.copy()
    # 调整转换概率
    for i, state_from in enumerate(states):
        for j, state_to in enumerate(states):
            if increase and state_to > state_from:
                modified_matrix[i, j] *= (1 + adjustment)
            elif not increase and state_to < state_from:
                modified_matrix[i, j] *= (1 - adjustment)
    # 保证概率分布的一致性
    row_sums = modified_matrix.sum(axis=1, keepdims=True)
    modified_matrix /= row_sums
    return modified_matrix

# 函数：根据情景调整概率
def adjust_probabilities_based_on_scenario(matrix, states, scenario):
    adjustment_factors = {
        'High50': 0.50, 'High30': 0.30, 'High20': 0.20, 'High10': 0.10, 'Baseline': 0.00,
        'Low10': -0.10, 'Low20': -0.20, 'Low30': -0.30,  'Low50': -0.50
    }
    adjustment = adjustment_factors.get(scenario, 0.0)
    increase = adjustment > 0
    return modify_probabilities(matrix, states, increase=increase, adjustment=abs(adjustment))

# 函数：计算转移概率矩阵
def calculate_transition_matrix(data):
    # 获取唯一状态
    states = pd.unique(data.values.ravel('K'))
    state_index = {state: i for i, state in enumerate(states)}
    # 初始化转移计数矩阵
    transitions = np.zeros((len(states), len(states)), dtype=int)
    # 计算转移次数
    for row in data.itertuples(index=False, name=None):
        for (from_state, to_state) in zip(row[:-1], row[1:]):
            transitions[state_index[from_state], state_index[to_state]] += 1
    # 防止出现全零行
    probabilities = np.zeros_like(transitions, dtype=float)
    sums = transitions.sum(axis=1)
    for i, (row, total) in enumerate(zip(transitions, sums)):
        if total > 0:
            probabilities[i] = row / total
        else:
            probabilities[i, i] = 1  # 自循环，如果无转移
    return probabilities, states

# 分区域创建所有的转移概率矩阵
region_group = df.groupby(df.columns[0])
transition_matrices = {}
state_list = {}

for region_name, group in region_group:
    probabilities, states = calculate_transition_matrix(group.iloc[:, 1:])
    transition_matrices[region_name] = probabilities
    state_list[region_name] = states

# 函数：预测状态
def predict_states(transition_matrix, initial_state_distribution, steps):
    state_distribution = initial_state_distribution
    predictions = [state_distribution] # 开始时包括初始状态分布
    for _ in range(steps - 1):
        state_distribution = state_distribution @ transition_matrix
        predictions.append(state_distribution)
    return predictions


# 存储配置及预测方法
predictions_by_region = {}
scenario_list = ['High50', 'High30', 'High20','High10', 'Baseline', 'Low10', 'Low20', 'Low30', 'Low50',]

# 存储配置及预测方法
for region_name, probabilities in transition_matrices.items():
    states = state_list[region_name]
    initial_state_distribution = np.full(len(states), 1/len(states))  # 假设初始分布是均等的
    for scenario in scenario_list:
        matrix_scenario = adjust_probabilities_based_on_scenario(probabilities, states, scenario)
        predictions_by_region[(region_name, scenario)] = predict_states(matrix_scenario, initial_state_distribution, 16)  # 步数设为16

# 创建列表存储每个区域的预测结果
all_predictions_list = []

# 定义一个函数来处理`Region`索引转换为列
def region_as_column(df):
    # 将Region索引转换为列
    df = df.reset_index(level='Region', drop=False)
    return df

# 将每个区域的预测转换为DataFrame并存储在列表中
for region_scenario, predictions in predictions_by_region.items():
    region_name, scenario = region_scenario
    predicted_df = pd.DataFrame(
        predictions,
        columns=state_list[region_name],
        index=pd.MultiIndex.from_product([[region_name], [scenario], range(2015, 2031)],
                                         names=['Region', 'Scenario', 'Year'])
    )
    # 选取2020年到2030年的数据
    predicted_df = predicted_df.loc[(slice(None), slice(None), slice(2015, 2030)), :]
    all_predictions_list.append(predicted_df)

# 假定其他的数据处理已正确执行，并且`all_predictions_list`包含所有DataFrame对象
# 应用region_as_column函数并重建all_predictions_list
all_predictions_list = [region_as_column(df) for df in all_predictions_list]

# 接下来，可以将所有的DataFrame连接并输出到一个Excel文件
all_predictions_df = pd.concat(all_predictions_list)

# 将DataFrame输出到Excel文件，利用ExcelWriter确保格式正确
with pd.ExcelWriter('predictions.xlsx', engine='xlsxwriter') as writer:
    all_predictions_df.to_excel(writer, index=False) # 设置index=False以不输出索引

# 保存excel文件
all_predictions_df.to_excel(r"E:\桌面\__predicted_land_use_2015_2030.xlsx")
