# 公募基金数据获取与存储工具

这个项目使用AKShare库获取公募基金数据，包括基金基本信息、净值信息、持仓信息、基金经理信息、业绩信息和行业配置信息，并支持将数据保存为CSV文件或SQLite数据库。

## 特点

- 支持增量更新和断点续传，避免重复获取数据
- 支持多种数据存储格式（CSV和SQLite）
- 支持获取不同类型的基金数据
- 实时保存数据，防止程序中断导致数据丢失
- 可配置的数据获取参数

## 安装依赖

```bash
pip install pandas akshare tqdm sqlalchemy
```

## 使用方法

### 基本用法

```bash
python main.py
```

这将使用默认参数获取所有类型的基金数据，并以CSV格式保存到`./data`目录。

### 命令行参数

```
usage: main.py [-h] [--output {csv,sqlite}] [--data-dir DATA_DIR] [--db-name DB_NAME]
               [--modules MODULES [MODULES ...]] [--incremental] [--no-incremental]
               [--clean-temp] [--year YEAR] [--start-date START_DATE] [--end-date END_DATE]

公募基金数据获取与存储工具

optional arguments:
  -h, --help            显示帮助信息并退出
  --output {csv,sqlite}
                        数据存储格式: csv或sqlite (默认: csv)
  --data-dir DATA_DIR   数据存储目录 (默认: ./data)
  --db-name DB_NAME     SQLite数据库名称 (默认: fund_data.db)
  --modules MODULES [MODULES ...]
                        要获取的数据模块 (默认: 全部)
  --incremental         启用增量更新模式，只获取未处理的基金数据
  --no-incremental      禁用增量更新模式，获取所有基金数据
  --clean-temp          清理临时数据文件
  --year YEAR           获取指定年份的持仓和行业配置数据 (默认: 当前年份)
  --start-date START_DATE
                        净值数据开始日期，格式为YYYYMMDD (默认: 20000101)
  --end-date END_DATE   净值数据结束日期，格式为YYYYMMDD (默认: 当前日期)
```

### 示例

1. 获取所有基金数据并保存为SQLite数据库：

```bash
python main.py --output sqlite --db-name fund_database.db
```

2. 只获取基金净值和持仓信息：

```bash
python main.py --modules nav position
```

3. 获取2022年的基金持仓数据：

```bash
python main.py --modules position --year 2022
```

4. 禁用增量更新模式，重新获取所有数据：

```bash
python main.py --no-incremental
```

5. 清理临时数据文件：

```bash
python main.py --clean-temp
```

6. 获取特定时间范围的净值数据：

```bash
python main.py --modules nav --start-date 20200101 --end-date 20221231
```

## 数据模块

- `basic`: 基金基本信息
- `nav`: 基金净值信息
- `position`: 基金持仓信息
- `manager`: 基金经理信息
- `performance`: 基金业绩信息
- `industry`: 基金行业配置信息

## 项目结构

- `main.py`: 主程序，处理命令行参数并调用相应的数据获取函数
- `fund_crawler.py`: 基金数据爬取模块，使用AKShare库获取各类基金数据
- `data_storage.py`: 数据存储模块，提供CSV和SQLite存储功能
- `progress/`: 存储处理进度的目录
- `temp_data/`: 存储临时数据的目录
- `data/`: 存储最终数据的目录

## 注意事项

1. 由于基金数据量较大，获取过程可能需要较长时间，建议使用增量更新模式
2. 为避免频繁请求导致IP被封，程序会在每次请求之间随机暂停
3. 如果程序意外中断，可以直接重新运行，会自动从上次中断的地方继续
4. 临时数据文件会占用一定的磁盘空间，可以使用`--clean-temp`参数清理
