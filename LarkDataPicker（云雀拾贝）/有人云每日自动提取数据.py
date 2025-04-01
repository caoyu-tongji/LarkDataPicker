import schedule
import time
import subprocess
import os
import logging
from datetime import datetime


# 配置日志
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'auto_extract_{datetime.now().strftime("%Y-%m-%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_data_extract():
    """运行有人云数据提取脚本"""
    try:
        logging.info("开始执行数据提取任务")
        script_path = os.path.join(os.path.dirname(__file__), '有人云数据提取_自由选择时间.py')
        venv_python = os.path.join(os.path.dirname(__file__), '.venv', 'Scripts', 'python.exe')
        result = subprocess.run([venv_python, script_path], capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0:
            logging.info("数据提取任务执行成功")
            logging.debug(result.stdout)
        else:
            logging.error(f"数据提取任务执行失败: {result.stderr}")
    except Exception as e:
        logging.error(f"运行数据提取脚本时出错: {str(e)}")

def run_data_merge():
    """运行有人云数据拼接脚本"""
    try:
        logging.info("开始执行数据拼接任务")
        script_path = os.path.join(os.path.dirname(__file__), '有人云数据拼接.py')
        venv_python = os.path.join(os.path.dirname(__file__), '.venv', 'Scripts', 'python.exe')
        result = subprocess.run([venv_python, script_path], capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0:
            logging.info("数据拼接任务执行成功")
            logging.debug(result.stdout)
        else:
            logging.error(f"数据拼接任务执行失败: {result.stderr}")
    except Exception as e:
        logging.error(f"运行数据拼接脚本时出错: {str(e)}")

def main():
    # 设置定时任务：每2小时运行一次数据提取和拼接流程
    def run_workflow():
        run_data_extract()
        # 等待数据提取完成后再执行数据拼接
        time.sleep(60)  # 等待1分钟
        run_data_merge()
    
    # 立即执行一次
    run_workflow()
    logging.info("已执行初始数据提取和拼接任务")
    
    # 设置每100分钟执行一次的定时任务
    schedule.every(100).minutes.do(run_workflow)
    logging.info("已设置每100分钟运行一次数据提取和拼接任务")
    
    logging.info("自动任务调度器已启动，等待执行计划任务...")
    
    # 无限循环，持续检查是否有计划任务需要执行
    while True:
        schedule.run_pending()
        time.sleep(300)  # 每5分钟检查一次

if __name__ == "__main__":

    try:
        logging.info("=== 有人云数据自动提取系统启动 ===")
        main()
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序执行过程中出现未处理的异常: {str(e)}")
    finally:
        logging.info("=== 有人云数据自动提取系统已停止 ===")
