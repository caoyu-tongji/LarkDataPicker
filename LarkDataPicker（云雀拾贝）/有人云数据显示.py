from flask import Flask, render_template, jsonify, request
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # 获取所有传感器名称
    sensors = []
    data_dir = os.path.join(os.path.dirname(__file__), 'data_all')
    if os.path.exists(data_dir):
        # 获取所有传感器文件名
        sensors = [f.replace('.txt', '') for f in os.listdir(data_dir) if f.endswith('.txt')]
    
    # 获取所有日期文件夹
    dates = []
    date_dir = os.path.join(os.path.dirname(__file__), 'data_date')
    if os.path.exists(date_dir):
        # 获取所有日期文件夹名
        dates = [d for d in os.listdir(date_dir) if os.path.isdir(os.path.join(date_dir, d))]
        dates.sort(reverse=True)  # 按日期降序排列
    
    return render_template('index.html', sensors=sensors, dates=dates)

@app.route('/get_sensor_data/<sensor_name>')
def get_sensor_data(sensor_name):
    # 获取采样参数，默认为True
    sampling = request.args.get('sampling', 'true').lower() == 'true'
    
    # 默认从data_all获取全部数据
    data_dir = os.path.join(os.path.dirname(__file__), 'data_all')
    data_file = os.path.join(data_dir, f'{sensor_name}.txt')
    
    if os.path.exists(data_file):
        try:
            # 读取数据文件
            df = pd.read_csv(data_file, sep='\t')
            
            # 检查数据列
            print(f"列名: {df.columns.tolist()}")
            
            # 确保数据至少有两列
            if len(df.columns) < 2:
                return jsonify({'error': f'数据格式错误: 列数不足，当前列: {df.columns.tolist()}'})
            
            # 转换时间格式
            try:
                df['更新时间'] = pd.to_datetime(df['更新时间'])
            except Exception as e:
                print(f"时间格式转换错误: {str(e)}")
                return jsonify({'error': f'时间格式转换错误: {str(e)}'})
                
            # 按时间排序
            df = df.sort_values('更新时间')
            
            # 获取第一列名称（传感器值列）
            value_column = df.columns[0]
            
            # 检查数值列是否包含非数值数据
            if not pd.to_numeric(df[value_column], errors='coerce').notna().all():
                # 尝试清理数据
                df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
                # 删除NaN值
                df = df.dropna(subset=[value_column])
                print(f"警告: 数值列包含非数值数据，已进行清理")
                
                if df.empty:
                    return jsonify({'error': '清理后数据为空，无法显示'})

            # 记录原始数据点数量
            original_count = len(df)
            
            # 数据抽样 - 如果启用采样且数据点超过500个，进行抽样
            if sampling and len(df) > 500:
                # 计算抽样间隔
                sample_step = len(df) // 500
                # 使用系统抽样方法选择数据点
                df = df.iloc[::sample_step].copy()
                print(f"数据已抽样，从{original_count}个点减少到{len(df)}个点")
            else:
                print(f"使用完整数据集，共{len(df)}个数据点")

            # 准备数据
            data = {
                'labels': df['更新时间'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'values': df[value_column].tolist(),
                'sampled': sampling and original_count > 500,
                'originalCount': original_count,
                'sampledCount': len(df)
            }
            
            # 检查数据是否为空
            if not data['labels'] or not data['values']:
                return jsonify({'error': '处理后数据为空，无法显示'})
                
            print(f"成功处理数据: {len(data['labels'])}个数据点")
            return jsonify(data)
        except Exception as e:
            import traceback
            print(f"处理传感器数据时出错: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': f'处理数据时出错: {str(e)}'})
    
    return jsonify({'error': '数据不可用'})

@app.route('/get_sensor_data/<sensor_name>/<date>')
def get_daily_sensor_data(sensor_name, date):
    # 获取采样参数，默认为True
    sampling = request.args.get('sampling', 'true').lower() == 'true'
    
    # 从data_date/日期文件夹获取单日数据
    data_dir = os.path.join(os.path.dirname(__file__), 'data_date', date)
    data_file = os.path.join(data_dir, f'{sensor_name}.txt')
    
    if os.path.exists(data_file):
        try:
            # 读取数据文件
            df = pd.read_csv(data_file, sep='\t')
            
            # 检查数据列
            print(f"列名: {df.columns.tolist()}")
            
            # 确保数据至少有两列
            if len(df.columns) < 2:
                return jsonify({'error': f'数据格式错误: 列数不足，当前列: {df.columns.tolist()}'})
            
            # 转换时间格式
            try:
                df['更新时间'] = pd.to_datetime(df['更新时间'])
            except Exception as e:
                print(f"时间格式转换错误: {str(e)}")
                return jsonify({'error': f'时间格式转换错误: {str(e)}'})
                
            # 按时间排序
            df = df.sort_values('更新时间')
            
            # 获取第一列名称（传感器值列）
            value_column = df.columns[0]
            
            # 检查数值列是否包含非数值数据
            if not pd.to_numeric(df[value_column], errors='coerce').notna().all():
                # 尝试清理数据
                df[value_column] = pd.to_numeric(df[value_column], errors='coerce')
                # 删除NaN值
                df = df.dropna(subset=[value_column])
                print(f"警告: 数值列包含非数值数据，已进行清理")
                
                if df.empty:
                    return jsonify({'error': '清理后数据为空，无法显示'})
            
            # 记录原始数据点数量
            original_count = len(df)
            
            # 数据抽样 - 如果启用采样且数据点超过500个，进行抽样
            if sampling and len(df) > 500:
                # 计算抽样间隔
                sample_step = len(df) // 500
                # 使用系统抽样方法选择数据点
                df = df.iloc[::sample_step].copy()
                print(f"数据已抽样，从{original_count}个点减少到{len(df)}个点")
            else:
                print(f"使用完整数据集，共{len(df)}个数据点")
            
            # 准备数据
            data = {
                'labels': df['更新时间'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'values': df[value_column].tolist(),
                'sampled': sampling and original_count > 500,
                'originalCount': original_count,
                'sampledCount': len(df)
            }
            
            # 检查数据是否为空
            if not data['labels'] or not data['values']:
                return jsonify({'error': '处理后数据为空，无法显示'})
                
            print(f"成功处理数据: {len(data['labels'])}个数据点")
            return jsonify(data)
        except Exception as e:
            import traceback
            print(f"处理传感器数据时出错: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': f'处理数据时出错: {str(e)}'})
    
    return jsonify({'error': '数据不可用'})

if __name__ == '__main__':
    app.run(debug=True)