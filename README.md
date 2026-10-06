# Python Data Demo

一个可直接运行的 Python 简易数据处理项目，演示从销售明细 CSV 到清洗结果和统计报告的完整流程，适合作为数据处理、Python 编程和工程实践的简历项目示例。

## 项目介绍

项目使用 `pandas` 读取销售记录，统一字段格式，转换日期和数值类型，过滤无效数据，并计算每条记录的收入。程序会进一步按商品类别和月份汇总，输出清洗后的 CSV 与结构化 JSON 报告。

## 功能说明

- 读取并校验销售 CSV 的必需字段：`date`、`category`、`amount`、`quantity`
- 清洗日期、金额、数量和类别字段，过滤缺失、非法和非正数量记录
- 计算订单收入：`amount × quantity`
- 按类别统计订单数、销量和收入
- 按月份统计订单数和收入
- 输出 `cleaned_sales.csv` 和 `summary.json`
- 提供样例数据和自动化测试

## 环境要求

- Python 3.10 或更高版本
- pip

## 安装与运行

在项目根目录执行：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py --input data/sample_sales.csv --output-dir output
```

macOS/Linux：

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --input data/sample_sales.csv --output-dir output
```

运行成功后，`output/` 目录会生成：

- `cleaned_sales.csv`：标准化后的明细数据，增加 `revenue` 和 `month` 字段
- `summary.json`：总体指标、类别汇总和月份汇总

## 使用自己的数据

准备一个 CSV 文件，至少包含以下列：

```text
date,category,amount,quantity
2026-04-01,Notebook,12.50,3
```

然后替换输入路径：

```bash
python main.py --input path/to/your_sales.csv --output-dir output
```

## 测试

项目测试使用 Python 标准库 `unittest`，无需额外测试框架：

```bash
python -m unittest discover -s tests -v
```

## 项目结构

```text
python-data-demo/
├── data/sample_sales.csv   # 可运行的样例数据
├── output/.gitkeep         # 输出目录占位文件
├── tests/test_main.py      # 数据清洗和报告测试
├── main.py                 # 命令行入口与处理逻辑
├── requirements.txt        # Python 依赖
└── README.md               # 项目说明
```

## 简历项目经历文案

**Python 销售数据处理与分析工具**：使用 Python 和 pandas 构建命令行数据处理流程，完成 CSV 数据读取、字段校验、日期与数值清洗、异常记录过滤及衍生指标计算；按商品类别和月份生成统计汇总，并输出标准化明细 CSV 与 JSON 报告。通过模块化函数和 `unittest` 测试覆盖核心清洗、汇总与文件输出流程，提升了数据处理结果的可复现性和可维护性。

## License

This project is provided for learning and portfolio demonstration purposes.
