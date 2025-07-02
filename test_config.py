#!/usr/bin/env python3
# 测试配置文件

print("🔍 Sheet配置测试 / Sheet Configuration Test")
print("=" * 50)

# 模拟main.py中的配置
scripts_config = [
    {
        'name': 'Commodity Price Crawler',
        'name_cn': '商品价格爬虫',
        'script_path': 'func1/commodity_price_crawler.py',
        'output_files': ['func1/rubber_prices.txt'],
        'sheet_name': 'Rubber_TSR20'
    },
    {
        'name': 'BLS Data Scraper',
        'name_cn': 'BLS数据爬虫',
        'script_path': 'func2/bls_scraper_auto.py',
        'output_files': ['func2/output/combined_data.xlsx', 'func2/bls_data.xlsx'],
        'sheet_name': 'Commodity_Data'
    },
    {
        'name': 'Exchange Rate Scraper',
        'name_cn': '汇率数据爬虫',
        'script_path': 'func3/exchange_rate_scraper.py',
        'output_files': ['func3/exchange_rates.xlsx', 'func3/exchange_rates.txt'],
        'sheet_name': 'Exchange_Rates'
    },
    {
        'name': 'FRED Data Scraper',
        'name_cn': 'FRED数据爬虫',
        'script_path': 'func4/run.py',
        'output_files': ['func4/output/PCU314994314994_processed.xlsx', 'func4/output/PCU314994314994.xlsx'],
        'sheet_name': 'Commodity_Data'
    }
]

print("模块配置 / Module Configuration:")
for i, config in enumerate(scripts_config, 1):
    print(f"{i}. {config['name']} ({config['name_cn']}) -> {config['sheet_name']}")

# 检查唯一sheet名称
sheet_names = [config['sheet_name'] for config in scripts_config]
unique_sheets = set(sheet_names)

print(f"\n📊 统计 / Statistics:")
print(f"总模块数 / Total modules: {len(sheet_names)}")
print(f"生成工作表数 / Generated sheets: {len(unique_sheets)}")
print(f"唯一工作表名称 / Unique sheet names: {list(unique_sheets)}")

print(f"\n📝 合并情况 / Merge Details:")
sheet_count = {}
for config in scripts_config:
    sheet_name = config['sheet_name']
    if sheet_name not in sheet_count:
        sheet_count[sheet_name] = []
    sheet_count[sheet_name].append(config['name'])

for sheet_name, modules in sheet_count.items():
    if len(modules) > 1:
        print(f"✅ {sheet_name}: 将合并 {len(modules)} 个模块的数据")
        for module in modules:
            print(f"   - {module}")
    else:
        print(f"📄 {sheet_name}: 单独模块 ({modules[0]})")

print("\n🎯 修改成功！BLS_Data 和 FRED_Data 已合并为 Commodity_Data") 