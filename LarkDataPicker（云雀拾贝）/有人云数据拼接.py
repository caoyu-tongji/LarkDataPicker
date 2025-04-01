import os
import datetime
import shutil
import pandas as pd

def merge_sensor_data():
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义数据源目录和目标目录
    data_date_dir = os.path.join(root_dir, 'data_date')
    data_all_dir = os.path.join(root_dir, 'data_all')
    
    # 定义已处理文件夹记录文件路径
    processed_folders_file = os.path.join(root_dir, 'processed_folders.txt')
    
    # 确保data_all目录存在
    if not os.path.exists(data_all_dir):
        os.makedirs(data_all_dir)
    
    # 获取所有日期文件夹
    all_date_folders = [f for f in os.listdir(data_date_dir) if os.path.isdir(os.path.join(data_date_dir, f))]
    
    # 按日期排序文件夹（从旧到新）
    all_date_folders.sort()
    
    # 读取已处理的文件夹列表
    processed_folders = []
    if os.path.exists(processed_folders_file):
        with open(processed_folders_file, 'r', encoding='utf-8') as f:
            processed_folders = [line.strip() for line in f.readlines()]
    
    # 过滤出未处理的文件夹
    date_folders = [folder for folder in all_date_folders if folder not in processed_folders]
    
    print(f"找到{len(all_date_folders)}个日期文件夹，其中{len(all_date_folders) - len(date_folders)}个已处理，{len(date_folders)}个待处理")
    
    # 用于跟踪已处理的传感器
    processed_sensors = set()
    
    # 遍历每个日期文件夹
    for date_folder in date_folders:
        date_path = os.path.join(data_date_dir, date_folder)
        print(f"\n处理日期文件夹: {date_folder}")
        
        # 获取当前日期文件夹中的所有传感器文件（xlsx格式）
        sensor_files = [f for f in os.listdir(date_path) if f.endswith('.xlsx')]
        
        for sensor_file in sensor_files:
            # 传感器名称就是文件名（不含扩展名）
            sensor_name = os.path.splitext(sensor_file)[0]
            processed_sensors.add(sensor_name)
            
            # 源文件路径
            source_file_path = os.path.join(date_path, sensor_file)
            
            # 目标文件路径（txt格式）
            target_file_path = os.path.join(data_all_dir, f"{sensor_name}.txt")
            
            print(f"处理传感器: {sensor_name}")
            
            try:
                # 读取Excel文件
                df = pd.read_excel(source_file_path)
                
                # 确保数据帧至少有5列
                if len(df.columns) < 5:
                    print(f"警告: {sensor_file} 列数不足，跳过处理")
                    continue
                
                # 提取第4列(时间)和第5列(值)的数据
                # 注意：pandas中列索引从0开始，所以第4列是索引3，第5列是索引4
                time_column = df.iloc[:, 3]
                value_column = df.iloc[:, 4]
                
                # 创建新的数据帧
                new_data = pd.DataFrame({
                    sensor_name: value_column,
                    '更新时间': time_column
                })
                
                # 如果目标文件已存在，则追加数据（保留表头）
                if os.path.exists(target_file_path):
                    # 读取现有的txt文件
                    existing_data = pd.read_csv(target_file_path, sep='\t')
                    
                    # 合并数据并按时间列去重
                    combined_data = pd.concat([existing_data, new_data])
                    combined_data = combined_data.drop_duplicates(subset=['更新时间'], keep='first')
                    
                    # 按时间排序
                    combined_data = combined_data.sort_values(by='更新时间')
                    
                    # 保存合并后的数据
                    combined_data.to_csv(target_file_path, sep='\t', index=False)
                    print(f"已将{date_folder}的数据追加到{sensor_name}.txt")
                else:
                    # 如果目标文件不存在，则直接保存
                    new_data.to_csv(target_file_path, sep='\t', index=False)
                    print(f"已创建新文件{sensor_name}.txt")
                    
            except Exception as e:
                print(f"处理文件 {sensor_file} 时出错: {str(e)}")
    
    # 更新已处理文件夹记录
    with open(processed_folders_file, 'a', encoding='utf-8') as f:
        for folder in date_folders:
            f.write(f"{folder}\n")
    
    print(f"\n数据合并完成，共处理了{len(processed_sensors)}个传感器文件")
    print(f"已将{len(date_folders)}个新处理的文件夹添加到记录中")

if __name__ == "__main__":
    merge_sensor_data()