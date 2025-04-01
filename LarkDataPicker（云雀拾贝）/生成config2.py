import json
import os

# 设置docs文件夹路径
docs_folder = os.path.join(os.path.dirname(__file__), 'docs')

# 读取传感器名称
sensor_file_path = os.path.join(docs_folder, '传感器.txt')
with open(sensor_file_path, 'r', encoding='utf-8') as f:
    sensor_names = [line.strip() for line in f if line.strip()]

# 读取网址
url_file_path = os.path.join(docs_folder, '网址.txt')
with open(url_file_path, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

# 创建传感器数据列表
sensors = []
for i in range(min(len(sensor_names), len(urls))):
    sensor = {
        "name": sensor_names[i],
        "url": urls[i]
    }
    sensors.append(sensor)

# 创建配置字典
config = {
    "sensors": sensors
}

# 将配置保存到docs/config2.json文件
output_file_path = os.path.join(docs_folder, 'config2.json')
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)

print(f"成功生成docs/config2.json文件，包含{len(sensors)}个传感器数据")