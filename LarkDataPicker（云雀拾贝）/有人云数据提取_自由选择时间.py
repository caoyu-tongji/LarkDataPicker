from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import os
import datetime
import argparse
import pyautogui
import shutil

def scrape_usr_cloud(start_date=None, end_date=None):
    # 创建日期和小时文件夹
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_hour = now.strftime("%H")
    date_hour_folder = os.path.join(os.path.dirname(__file__), 'data_date', f"{today}_{current_hour}")
    os.makedirs(date_hour_folder, exist_ok=True)
    
    # 创建临时下载目录
    downloads_folder = os.path.join(os.path.dirname(__file__), 'downloads')
    os.makedirs(downloads_folder, exist_ok=True)

    # 配置Chrome选项
    chrome_options = Options()
    # 注意：为了处理下载对话框，我们不能使用无头模式
    chrome_options.add_argument('--headless')
    #chrome_options.add_argument('--disable-gpu')
    
    # 设置下载选项
    prefs = {
        "download.default_directory": downloads_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 登录过程
        driver.get("https://account.usr.cn/#/login?type=mp_scada")
        wait = WebDriverWait(driver, 20)
        
        # 读取配置文件
        config_path = os.path.join(os.path.dirname(__file__), 'docs', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 登录
        username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='手机号码/邮箱/用户名']")))
        username_input.send_keys(config['username'])
        
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='密码']")))
        password_input.send_keys(config['password'])
        
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'login')]")))
        driver.execute_script("arguments[0].scrollIntoView();", login_button)
        time.sleep(1)
        login_button.click()
        
        # 等待登录完成并跳转
        time.sleep(5)
        
        # 循环处理每个传感器
        for sensor in config['sensors']:
            print(f"\n正在处理: {sensor['name']}")
            
            # 打开新的数据历史页面
            data_history_url = sensor['url']
            driver.execute_script(f"window.open('{data_history_url}', '_blank');")
            
            # 切换到新打开的标签页
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[-1])
            
            # 等待页面加载完成
            time.sleep(5)
            
            # 点击时间选择器图标
            time_picker = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-input__icon.el-range__icon.el-icon-time")))
            driver.execute_script("arguments[0].click();", time_picker)
            time.sleep(2)  # 等待时间选择器打开
            
            # 如果指定了开始日期和结束日期，则使用自定义时间范围
            if start_date and end_date:
                try:
                    # 获取时间选择器的输入框
                    date_inputs = driver.find_elements(By.CSS_SELECTOR, ".el-date-range-picker__editors-wrap input")
                    
                    # 清空并设置开始日期
                    start_date_input = date_inputs[0]
                    driver.execute_script("arguments[0].value = '';", start_date_input)
                    start_date_input.send_keys(start_date)
                    time.sleep(0.5)
                    
                    # 清空并设置结束日期
                    end_date_input = date_inputs[2]
                    driver.execute_script("arguments[0].value = '';", end_date_input)
                    end_date_input.send_keys(end_date)
                    time.sleep(0.5)
                    
                    # 点击确认按钮
                    confirm_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-picker-panel__footer .el-button--default")))
                    driver.execute_script("arguments[0].click();", confirm_button)
                    print(f"已设置自定义时间范围: {start_date} 至 {end_date}")
                except Exception as e:
                    print(f"设置自定义时间范围失败: {str(e)}，将使用'最近2小时'")
                    # 如果自定义时间设置失败，则使用"最近2小时"
                    recent_hours_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'el-picker-panel__shortcut') and text()='最近2小时']")))
                    driver.execute_script("arguments[0].click();", recent_hours_button)
            else:
                # 使用默认的"最近2小时"
                recent_hours_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'el-picker-panel__shortcut') and text()='最近2小时']")))
                driver.execute_script("arguments[0].click();", recent_hours_button)
            
            time.sleep(1)  # 等待时间选择器更新
            
            # 点击查询按钮
            query_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-button.search-btn.el-button--primary.el-button--small")))
            driver.execute_script("arguments[0].click();", query_button)
            print("已点击查询按钮")
            time.sleep(5)  # 等待查询结果加载
            
            # 点击下载数据按钮
            print("正在查找下载数据按钮...")
            try:
                # 增加页面加载等待时间
                time.sleep(5)
                print("尝试多种方式定位下载按钮...")
                
                # 方法1：通过CSS类名查找下载按钮
                try:
                    download_button = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, ".el-button.tab-pane-top__button.el-button--primary.el-button--small")
                    ))
                    print("方法1成功：通过CSS类找到下载按钮")
                except Exception as e:
                    print(f"方法1失败：{str(e)}")
                    # 方法2：通过XPath查找包含文本的按钮
                    try:
                        download_button = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(text(), '下载数据')]")
                        ))
                        print("方法2成功：通过文本内容找到下载按钮")
                    except Exception as e:
                        print(f"方法2失败：{str(e)}")
                        # 方法3：通过更宽泛的CSS选择器
                        download_button = wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, ".el-button--primary.el-button--small")
                        ))
                        print("方法3成功：通过宽泛CSS选择器找到下载按钮")
                
                print("找到下载数据按钮，准备点击")
                # 使用JavaScript点击按钮
                driver.execute_script("arguments[0].click();", download_button)
                print("已点击下载数据按钮")
                time.sleep(5)  # 增加等待时间，确保确认对话框出现
                
                # 处理确认下载对话框，点击确认按钮
                try:
                    # 增加等待时间，确保对话框完全显示
                    time.sleep(5)  # 增加等待时间，确保对话框完全加载
                    print("开始尝试定位确认按钮...")
                    
                    # 尝试多种方式定位确认按钮
                    confirm_button = None
                    methods = [
                        # 方法1：通过类名和位置定位
                        (By.CSS_SELECTOR, ".el-message-box__btns .el-button--primary")
                        ,
                        # 方法2：通过文本内容和类名精确定位
                        (By.XPATH, "//button[contains(@class, 'el-button--primary') and (contains(text(), '确定') or contains(text(), '确认'))]")
                        ,
                        # 方法3：通过类名定位所有主要按钮，然后选择最后一个（通常确认按钮在右侧）
                        (By.CSS_SELECTOR, ".el-button--primary")
                        ,
                        # 方法4：通过对话框内的任何按钮
                        (By.CSS_SELECTOR, ".el-message-box button")
                        ,
                        # 方法5：通过更宽泛的XPath
                        (By.XPATH, "//div[contains(@class, 'el-message-box')]//button")
                    ]
                    
                    # 逐一尝试不同的定位方法
                    for i, (by_method, selector) in enumerate(methods):
                        try:
                            print(f"尝试方法{i+1}定位确认按钮: {selector}")
                            confirm_button = wait.until(EC.element_to_be_clickable((by_method, selector)))
                            print(f"方法{i+1}成功找到确认按钮")
                            break
                        except Exception as e:
                            print(f"方法{i+1}失败: {str(e)}")
                    
                    if confirm_button:
                        print("找到确认按钮，准备点击")
                        # 尝试多种点击方式
                        try:
                            # 方法1：使用JavaScript点击
                            driver.execute_script("arguments[0].click();", confirm_button)
                            print("已使用JavaScript点击确认按钮")
                        except Exception as js_error:
                            print(f"JavaScript点击失败: {str(js_error)}，尝试其他方法")
                            try:
                                # 方法2：使用ActionChains点击
                                from selenium.webdriver.common.action_chains import ActionChains
                                actions = ActionChains(driver)
                                actions.move_to_element(confirm_button).click().perform()
                                print("已使用ActionChains点击确认按钮")
                            except Exception as action_error:
                                print(f"ActionChains点击失败: {str(action_error)}，尝试直接点击")
                                # 方法3：直接点击
                                confirm_button.click()
                                print("已直接点击确认按钮")
                        
                        print("已点击确认按钮，等待文件下载")
                    else:
                        print("无法找到确认按钮，尝试使用pyautogui点击")
                        # 使用pyautogui尝试点击屏幕中间偏右的位置（通常确认按钮的位置）
                        screen_width, screen_height = pyautogui.size()
                        # 计算对话框可能的位置（屏幕中间偏右下）
                        # 尝试多个可能的位置
                        possible_positions = [
                            (screen_width // 2 + 100, screen_height // 2 + 50),  # 中间偏右下
                            (screen_width // 2 + 150, screen_height // 2),      # 中间偏右
                            (screen_width // 2 + 200, screen_height // 2 + 30)   # 更偏右一些
                        ]
                        
                        for pos_x, pos_y in possible_positions:
                            print(f"尝试点击位置: ({pos_x}, {pos_y})")
                            pyautogui.click(pos_x, pos_y)
                            time.sleep(1)  # 点击后短暂等待
                        
                        print("已使用pyautogui尝试多个可能的确认按钮位置")
                    
                    # 无论使用哪种方式点击，都增加等待时间确保下载开始
                    time.sleep(8)  # 增加等待时间，确保下载对话框处理完成

                    
                    # 等待下载完成（通常需要一些时间）
                    print("等待下载完成...")
                    download_wait_time = 15  # 增加等待时间
                    download_success = False
                    
                    # 等待下载完成
                    for _ in range(5):  # 最多尝试检查5次
                        time.sleep(download_wait_time / 5)
                        # 检查下载文件夹中是否有新文件
                        files = os.listdir(downloads_folder)
                        csv_files = [f for f in files if f.endswith('.csv') and os.path.getmtime(os.path.join(downloads_folder, f)) > time.time() - 300]
                        
                        if csv_files:
                            print(f"检测到下载文件: {csv_files}")
                            download_success = True
                            break
                        else:
                            print("尚未检测到下载文件，继续等待...")
                    
                    if not download_success:
                        print("警告：未检测到下载文件，可能下载失败")
                        # 尝试再次点击确认按钮
                        print("尝试再次触发下载...")
                        try:
                            # 重新点击下载按钮
                            download_button = wait.until(EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, ".el-button.tab-pane-top__button.el-button--primary.el-button--small")
                            ))
                            driver.execute_script("arguments[0].click();", download_button)
                            time.sleep(5)
                            
                            # 使用pyautogui直接点击确认按钮的可能位置
                            screen_width, screen_height = pyautogui.size()
                            pyautogui.click(screen_width // 2 + 100, screen_height // 2 + 50)
                            time.sleep(10)  # 等待下载
                        except Exception as retry_error:
                            print(f"重试下载失败: {str(retry_error)}")
                    else:
                        print("文件下载成功！")
                    
                    # 查找下载的文件并移动到目标文件夹
                    print("查找下载的文件...")
                    downloaded_files = [f for f in os.listdir(downloads_folder) if f.endswith('.csv') or f.endswith('.xlsx')]
                    
                    if downloaded_files:
                        # 获取最新下载的文件（按修改时间排序）
                        downloaded_files.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_folder, x)), reverse=True)
                        latest_file = downloaded_files[0]
                        source_path = os.path.join(downloads_folder, latest_file)
                        
                        # 构建目标文件路径，使用传感器名称
                        target_filename = f"{sensor['name']}{os.path.splitext(latest_file)[1]}"
                        target_path = os.path.join(date_hour_folder, target_filename)
                        
                        # 移动文件到目标文件夹
                        shutil.move(source_path, target_path)
                        print(f"已将下载的文件移动到: {target_path}")
                    else:
                        print("未找到下载的文件")
                        
                except Exception as e:
                    print(f"处理确认对话框时出错: {str(e)}")
            except Exception as e:
                print(f"查找或点击下载按钮时出错: {str(e)}")
                print("尝试使用备用方法获取数据...")
                
                # 备用方法：直接从表格获取数据
                table_data = driver.execute_script("""
                    var result = [];
                    
                    // 获取所有表格数据
                    var tables = document.querySelectorAll('table');
                    for (var i = 0; i < tables.length; i++) {
                        var rows = tables[i].querySelectorAll('tr');
                        var tableData = [];
                        
                        for (var j = 0; j < rows.length; j++) {
                            var cells = rows[j].querySelectorAll('td, th');
                            var rowData = [];
                            
                            for (var k = 0; k < cells.length; k++) {
                                rowData.push(cells[k].textContent.trim());
                            }
                            
                            if (rowData.length > 0) {
                                tableData.push(rowData);
                            }
                        }
                        
                        if (tableData.length > 0) {
                            result.push(tableData);
                        }
                    }
                    
                    return result;
                """)
                
                if table_data:
                    try:
                        # 只保留第1和第4项元素（索引为0和3）
                        if len(table_data) >= 4:
                            filtered_data = [table_data[0], table_data[3]]
                        else:
                            # 如果数据不足4项，则使用可用的数据
                            filtered_data = [table_data[0], table_data[-1]]
                        
                        # 获取表头
                        headers = filtered_data[0][0][:2]  # 取前两个元素作为表头
                        
                        # 获取数据行
                        rows = filtered_data[1]
                        
                        # 创建格式化的数据字符串
                        formatted_data = f"{headers[1]}\t{headers[0]}\n"  # 表头行
                        for row in rows:
                            if len(row) >= 2:  # 确保行有足够的数据
                                formatted_data += f"{row[0]}\t{row[1]}\n"  # 数据行
                        
                        # 保存为txt文件
                        txt_file_path = os.path.join(date_hour_folder, f"{sensor['name']}.txt")
                        with open(txt_file_path, "w", encoding="utf-8") as f:
                            f.write(formatted_data)
                        print(f"已使用备用方法处理并保存数据到 {txt_file_path}")
                        
                    except Exception as e:
                        print(f"处理数据时出错: {str(e)}")
                else:
                    print("未找到表格数据")
            
            # 关闭当前标签页，回到主页面
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)

    except Exception as e:
        print(f"执行过程中出现错误: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='有人云数据提取工具')
    parser.add_argument('--start_date', type=str, help='开始日期，格式：YYYY-MM-DD HH:MM:SS')
    parser.add_argument('--end_date', type=str, help='结束日期，格式：YYYY-MM-DD HH:MM:SS')
    args = parser.parse_args()
    
    if args.start_date and args.end_date:
        # 打印使用的时间范围
        print(f"使用自定义时间范围: {args.start_date} 至 {args.end_date}")
    else:
        print("未指定时间范围，将使用'最近2小时'选项")
    
    # 调用爬取函数
    scrape_usr_cloud(args.start_date, args.end_date)