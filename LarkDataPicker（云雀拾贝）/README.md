# 云雀拾贝 (LarkDataPicker)

云雀拾贝是一个自动化数据采集和处理工具，专为有人云平台设计，可以定时提取传感器数据并进行整合分析。

## 功能特点

- 自动从有人云平台提取传感器数据
- 支持多传感器数据采集
- 数据自动拼接与整合
- 定时任务调度
- 完整的日志记录
- 数据可视化展示

## 系统要求

- Python 3.8 或更高版本
- Windows 操作系统
- Chrome浏览器（用于Selenium自动化）

## 依赖包

本项目需要以下Python包：
- schedule - 用于定时任务调度
- requests - 用于HTTP请求
- pandas - 用于数据处理
- openpyxl - 用于Excel文件操作
- selenium - 用于网页自动化
- webdriver_manager - 用于管理浏览器驱动
- beautifulsoup4 - 用于HTML解析
- lxml - 用于XML和HTML处理
- flask - 用于Web应用程序开发

## 项目结构

```
.
├── data_all/            # 存储所有传感器的合并数据
├── data_date/           # 按日期和小时存储的原始数据
├── docs/                # 配置文件和文档
│   ├── config.json      # 用户名密码和传感器配置
│   ├── 传感器.txt        # 传感器名称列表
│   └── 网址.txt          # 传感器URL列表
├── logs/                # 日志文件目录
├── templates/           # Web界面模板
│   └── index.html       # 数据可视化页面
├── 有人云数据拼接.py       # 数据拼接处理脚本
├── 有人云数据提取_自由选择时间.py  # 数据提取脚本
├── 有人云数据显示.py       # 数据可视化Web应用
├── 有人云每日自动提取数据.py  # 自动定时提取主程序
└── 生成config2.py       # 配置文件生成工具
```

## 主要文件功能说明

- **有人云每日自动提取数据.py**: 主程序，设置定时任务，每100分钟自动运行数据提取和拼接流程
- **有人云数据提取_自由选择时间.py**: 从有人云平台提取传感器数据，支持自定义时间范围
- **有人云数据拼接.py**: 将不同时间采集的数据进行合并和整理
- **有人云数据显示.py**: 基于Flask的Web应用，提供数据可视化界面
- **生成config2.py**: 辅助工具，用于生成配置文件

## 安装步骤

1. 克隆或下载本项目到本地

2. 创建并激活虚拟环境
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. 安装所需依赖包
   ```bash
   pip install schedule requests pandas openpyxl selenium webdriver_manager beautifulsoup4 lxml flask
   ```

4. 配置用户信息和传感器（两种方式）

   **方式一：直接编辑配置文件**
   - 编辑 `docs/config.json` 文件，填入有人云平台的用户名和密码
   - 添加需要监控的传感器信息，包括名称和URL
   ```json
   {
       "username": "你的用户名",
       "password": "你的密码",
       "sensors": [
           {
               "name": "传感器1名称",
               "url": "传感器1的URL"
           },
           {
               "name": "传感器2名称",
               "url": "传感器2的URL"
           }
       ]
   }
   ```

   **方式二：使用辅助工具生成配置**
   - 编辑 `docs/传感器.txt` 文件，每行填入一个传感器名称
   - 编辑 `docs/网址.txt` 文件，每行填入对应传感器的URL（确保与传感器.txt中的顺序一致）
   - 运行生成配置工具
     ```bash
     .venv\Scripts\python 生成config2.py
     ```
   - 工具会自动生成 `docs/config2.json` 文件
   - 将生成的传感器配置与用户名密码合并到 `docs/config.json` 文件中
     ```json
     {
         "username": "你的用户名",
         "password": "你的密码",
         "sensors": [...] // 这里使用生成的sensors数组内容
     }
     ```

## 使用流程

### 初次使用配置

1. 确保已完成安装步骤

2. 配置传感器信息（两种方式）
   
   **方式一：直接编辑config.json**
   - 打开 `docs/config.json` 文件
   - 填入有人云平台的用户名和密码
   - 手动添加所有传感器信息，包括名称和URL
   
   **方式二：使用辅助工具（推荐）**
   - 打开 `docs/传感器.txt` 文件，每行填入一个传感器名称，例如：
     ```
     温度传感器1
     湿度传感器2
     压力传感器3
     ```
   - 打开 `docs/网址.txt` 文件，每行填入对应传感器的URL，确保与传感器.txt中的顺序一致，例如：
     ```
     https://www.urhome.com/sensor/123456
     https://www.urhome.com/sensor/234567
     https://www.urhome.com/sensor/345678
     ```
   - 运行生成配置工具：
     ```bash
     .venv\Scripts\python 生成config2.py
     ```
   - 工具会自动生成 `docs/config2.json` 文件，包含所有传感器配置
   - 打开 `docs/config.json` 文件，填入用户名和密码，并将config2.json中的sensors数组内容复制到config.json中

3. 检查配置文件
   - 确认 `docs/config.json` 文件格式正确，包含用户名、密码和所有传感器信息
   - 确认所有传感器URL都是有效的

### 自动数据采集

1. 确保已完成安装和初次使用配置步骤

2. 运行自动提取程序
   ```bash
   .venv\Scripts\python 有人云每日自动提取数据.py
   ```
   程序将立即执行一次数据提取和拼接，然后每100分钟自动执行一次

### 手动数据提取

如需手动提取特定时间范围的数据：

```bash
.venv\Scripts\python 有人云数据提取_自由选择时间.py --start_date 2023-01-01 --end_date 2023-01-02
```

### 时间设置调整

#### 修改数据提取时间范围

默认情况下，程序使用"最近2小时"选项来提取数据。如需修改为其他时间范围（如"最近1天"），可以通过以下方式：

1. 打开 `有人云数据提取_自由选择时间.py` 文件
2. 找到约第85行左右的代码：
   ```python
   # 使用默认的"最近2小时"
   recent_hours_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'el-picker-panel__shortcut') and text()='最近2小时']")))
   ```
3. 将其中的 `text()='最近2小时'` 修改为 `text()='最近1天'` 或其他可用的时间选项

可用的时间选项通常包括：
- 最近1小时
- 最近2小时
- 最近1天
- 最近1周
- 最近1个月

#### 修改自动运行间隔

默认情况下，程序每100分钟自动执行一次数据提取和拼接。如需修改此间隔：

1. 打开 `有人云每日自动提取数据.py` 文件
2. 找到约第60行左右的代码：
   ```python
   # 设置每100分钟执行一次的定时任务
   schedule.every(100).minutes.do(run_workflow)
   ```
3. 将 `100` 修改为您需要的分钟数，例如 `60` 表示每小时执行一次

### 数据可视化

启动数据可视化Web应用：

```bash
.venv\Scripts\python 有人云数据显示.py
```

然后在浏览器中访问 http://127.0.0.1:5000 查看数据图表

## 文件夹说明

- **data_all/**: 存储所有传感器的合并数据，每个传感器一个文件
- **data_date/**: 按日期和小时存储的原始数据，格式为 `YYYY-MM-DD_HH`
- **docs/**: 存放配置文件和文档
- **logs/**: 存储程序运行日志，按日期命名
- **templates/**: 存放Web应用的HTML模板

## 注意事项

- 首次运行时，请确保已正确配置 `docs/config.json` 文件
- 程序需要Chrome浏览器和稳定的网络连接
- 如遇到问题，请查看 `logs` 目录下的日志文件
- 数据可视化界面支持数据抽样显示，适合大量数据的展示