# 图书数据爬虫与可视化分析

这是一个范围受限的 Python 作品集演示项目：从 `books.toscrape.com` 公开练习站点抓取图书卡片，使用 Pandas 清洗并统计价格和评分，再用 Matplotlib 输出 PNG 图表。

## 合规与范围

- 默认数据源是专门用于爬虫练习的公开演示站点。
- 默认只抓取 1 页，页间延迟 1 秒；不登录、不绕过验证、不访问后台接口。
- 演示站点没有可核验的销量字段，因此程序不会把评分、库存或评价信息冒充销量。
- 如果输入页面明确提供 `data-sales` 属性，程序才会统计 `total_sales`；否则 `sales_field_available` 为 `false`。

## 安装

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 运行

```bash
python main.py --pages 1 --delay 1 --output-dir output
```

输出文件包括：

- `books_cleaned.csv`：清洗后的图书明细
- `summary.json`：书籍数量、平均价格、平均评分和评分分布
- `rating_distribution.png`：评分分布图
- `price_distribution.png`：价格分布图
- `sales_rating.png`：仅在输入确实包含销量字段时生成

## 复核

运行后可检查 `summary.json`、CSV 和 PNG 图表，并把终端命令、文件列表和仓库页面作为项目截图。上传到 TalentAI 前应将仓库链接、姓名、学历证明和工作证明替换为真实内容。
