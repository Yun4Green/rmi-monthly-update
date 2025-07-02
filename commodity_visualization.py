#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轮胎相关商品价格指数可视化 / Tire-Related Commodity Price Index Visualization
基于FRED_Data.csv和BLS_Data.csv数据生成综合分析的Canvas图表
Generate comprehensive Canvas charts with analysis based on FRED_Data.csv and BLS_Data.csv
"""

import pandas as pd
import json
from datetime import datetime
import os
import re

def parse_fred_data(df):
    """
    解析FRED数据 / Parse FRED data
    """
    data_records = []
    
    for _, row in df.iterrows():
        first_col = str(row.iloc[0])
        
        # 匹配年月数据格式 (例如: 2012M01 97.9)
        if re.match(r'^\d{4}M\d{2}\s+[\d.]+$', first_col):
            parts = first_col.split()
            date_str = parts[0]
            value = float(parts[1])
            
            year = int(date_str[:4])
            month = int(date_str[5:7])
            
            # 只取2015年及以后的数据
            if year >= 2015:
                data_records.append({
                    'Year': year,
                    'Month': month,
                    'Value': value,
                    'Product': '轮胎帘子布生产者价格指数',
                    'Product_EN': 'Tire Cord PPI',
                    'Source': 'FRED'
                })
    
    return pd.DataFrame(data_records)

def parse_bls_data(df):
    """
    解析BLS数据 / Parse BLS data
    """
    data_records = []
    
    # 获取产品名称
    products = {
        'PCU325212325212P': {'name': '合成橡胶制造', 'name_en': 'Synthetic Rubber'},
        'PCU325211325211': {'name': '塑料原料和树脂制造', 'name_en': 'Plastics & Resin'},
        'PCU332618332618': {'name': '其他制造金属丝产品', 'name_en': 'Wire Products'},
        'PCU3251803251806': {'name': '炭黑制造', 'name_en': 'Carbon Black'}
    }
    
    # 跳过前6行（标题行）
    for i, row in df.iterrows():
        if i < 6:
            continue
            
        date_str = str(row.iloc[0])
        if re.match(r'^\d{4}M\d{2}$', date_str):
            year = int(date_str[:4])
            month = int(date_str[5:7])
            
            # 只取2015年及以后的数据
            if year >= 2015:
                for j, (product_code, product_info) in enumerate(products.items()):
                    value_str = str(row.iloc[j + 1])
                    if value_str and value_str != 'nan' and value_str != '':
                        try:
                            value = float(value_str)
                            data_records.append({
                                'Year': year,
                                'Month': month,
                                'Value': value,
                                'Product': product_info['name'],
                                'Product_EN': product_info['name_en'],
                                'Source': 'BLS'
                            })
                        except ValueError:
                            pass
    
    return pd.DataFrame(data_records)

def calculate_latest_comparisons(df):
    """
    计算最新数据的同比环比 / Calculate latest data comparisons
    """
    comparisons = {}
    
    for product in df['Product'].unique():
        product_data = df[df['Product'] == product].sort_values(['Year', 'Month'])
        
        if len(product_data) == 0:
            continue
            
        # 获取最新数据
        latest = product_data.iloc[-1]
        latest_year = latest['Year']
        latest_month = latest['Month']
        latest_value = latest['Value']
        
        # 上月数据 (环比)
        prev_month = None
        prev_month_value = None
        if len(product_data) >= 2:
            prev_month = product_data.iloc[-2]
            prev_month_value = prev_month['Value']
        
        # 去年同月数据 (同比)
        same_month_last_year = product_data[
            (product_data['Year'] == latest_year - 1) & 
            (product_data['Month'] == latest_month)
        ]
        same_month_last_year_value = None
        if not same_month_last_year.empty:
            same_month_last_year_value = same_month_last_year.iloc[0]['Value']
        
        # 计算变化率
        mom_change = None
        yoy_change = None
        
        if prev_month_value is not None:
            mom_change = ((latest_value - prev_month_value) / prev_month_value * 100)
        
        if same_month_last_year_value is not None:
            yoy_change = ((latest_value - same_month_last_year_value) / same_month_last_year_value * 100)
        
        comparisons[product] = {
            'latest': {
                'year': int(latest_year),
                'month': int(latest_month),
                'value': float(latest_value),
                'date_str': f"{latest_year}年{latest_month}月"
            },
            'prev_month': {
                'value': float(prev_month_value) if prev_month_value is not None else None,
                'change': float(mom_change) if mom_change is not None else None
            },
            'same_month_last_year': {
                'value': float(same_month_last_year_value) if same_month_last_year_value is not None else None,
                'change': float(yoy_change) if yoy_change is not None else None
            }
        }
    
    return comparisons

def generate_html_visualization(df, comparisons):
    """
    生成HTML Canvas可视化页面 / Generate HTML Canvas visualization page
    """
    
    # 准备图表数据 - 按产品分组
    chart_datasets = []
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
    
    for i, product in enumerate(df['Product'].unique()):
        product_data = df[df['Product'] == product].sort_values(['Year', 'Month'])
        
        chart_data = []
        for _, row in product_data.iterrows():
            chart_data.append({
                'x': f"{int(row['Year'])}-{int(row['Month']):02d}",
                'y': float(row['Value'])
            })
        
        chart_datasets.append({
            'label': product,
            'data': chart_data,
            'borderColor': colors[i % len(colors)],
            'backgroundColor': colors[i % len(colors)] + '20',
            'fill': False,
            'tension': 0.4
        })
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>轮胎相关商品价格指数可视化 / Tire-Related Commodity Price Index Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .cards-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card-title {{
            font-size: 0.9em;
            color: #666;
            margin: 0 0 10px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: bold;
        }}
        
        .card-value {{
            font-size: 1.8em;
            font-weight: bold;
            margin: 0 0 8px 0;
            color: #FF6B6B;
        }}
        
        .card-meta {{
            font-size: 0.8em;
            color: #888;
            margin: 0 0 10px 0;
        }}
        
        .card-change {{
            font-size: 1em;
            font-weight: 600;
            margin: 0;
        }}
        
        .change-positive {{
            color: #4CAF50;
        }}
        
        .change-negative {{
            color: #F44336;
        }}
        
        .change-neutral {{
            color: #FF9800;
        }}
        
        .chart-container {{
            padding: 30px;
            background: white;
        }}
        
        .chart-title {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.5em;
            color: #333;
        }}
        
        #commodityChart {{
            max-height: 500px;
        }}
        
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .trend-arrow {{
            font-size: 1.2em;
            margin-left: 8px;
        }}
        
        .source-links {{
            margin-top: 10px;
        }}
        
        .source-links a {{
            color: #4ECDC4;
            text-decoration: none;
            margin: 0 10px;
        }}
        
        .source-links a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>轮胎相关商品价格指数分析</h1>
            <p>Tire-Related Commodity Price Index Analysis Dashboard</p>
        </div>
        
        <div class="cards-container">"""
    
    # 生成每个产品的卡片
    for product, comp in comparisons.items():
        # 预处理显示数据
        mom_change_display = f"{comp['prev_month']['change']:+.2f}%" if comp['prev_month']['change'] is not None else 'N/A'
        mom_change_class = 'change-positive' if comp['prev_month']['change'] and comp['prev_month']['change'] > 0 else 'change-negative' if comp['prev_month']['change'] and comp['prev_month']['change'] < 0 else 'change-neutral'
        mom_arrow = '↗️' if comp['prev_month']['change'] and comp['prev_month']['change'] > 0 else '↘️' if comp['prev_month']['change'] and comp['prev_month']['change'] < 0 else '➡️'
        
        yoy_change_display = f"{comp['same_month_last_year']['change']:+.2f}%" if comp['same_month_last_year']['change'] is not None else 'N/A'
        yoy_change_class = 'change-positive' if comp['same_month_last_year']['change'] and comp['same_month_last_year']['change'] > 0 else 'change-negative' if comp['same_month_last_year']['change'] and comp['same_month_last_year']['change'] < 0 else 'change-neutral'
        yoy_arrow = '↗️' if comp['same_month_last_year']['change'] and comp['same_month_last_year']['change'] > 0 else '↘️' if comp['same_month_last_year']['change'] and comp['same_month_last_year']['change'] < 0 else '➡️'
        
        html_content += f"""
            <div class="card">
                <h3 class="card-title">{product}</h3>
                <div class="card-value">{comp['latest']['value']:.2f}</div>
                <p class="card-meta">{comp['latest']['date_str']} | 基准指数</p>
                <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                    <div>
                        <small style="color: #666;">环比 MoM</small>
                        <p class="card-change {mom_change_class}" style="margin: 2px 0;">
                            {mom_change_display} <span class="trend-arrow">{mom_arrow}</span>
                        </p>
                    </div>
                    <div>
                        <small style="color: #666;">同比 YoY</small>
                        <p class="card-change {yoy_change_class}" style="margin: 2px 0;">
                            {yoy_change_display} <span class="trend-arrow">{yoy_arrow}</span>
                        </p>
                    </div>
                </div>
            </div>"""
    
    html_content += f"""
        </div>
        
        <div class="chart-container">
            <h2 class="chart-title">轮胎相关商品价格指数趋势图 / Tire-Related Commodity Price Index Trend Chart</h2>
            <canvas id="commodityChart"></canvas>
        </div>
        
        <div class="footer">
            <p>数据来源 / Data Sources:</p>
            <div class="source-links">
                <a href="https://fred.stlouisfed.org/series/PCU314994314994" target="_blank">FRED - Producer Price Index by Industry: Rope, Twine, Tire Cord, and Tire Fabric Mills</a>
                <a href="https://data.bls.gov/toppicks?survey=pc" target="_blank">BLS - Producer Price Index Industry Data</a>
                <a href="https://www.worldbank.org/en/research/commodity-markets" target="_blank">World Bank - Commodity Markets Research</a>
            </div>
            <p style="margin-top: 15px; font-size: 0.8em; color: #ccc;">
                <strong>数据说明 / Data Description:</strong><br>
                • FRED数据: 轮胎帘子布生产者价格指数 (基准期: 2011年12月=100) / FRED Data: Tire Cord Producer Price Index (Base: Dec 2011=100)<br>
                • BLS数据: 相关制造业生产者价格指数 / BLS Data: Related Manufacturing Producer Price Indexes<br>
                • 世界银行: 全球商品市场研究与价格监测 / World Bank: Global Commodity Markets Research & Price Monitoring
            </p>
            <p style="margin-top: 10px;">生成时间 / Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        // 图表配置和数据
        const ctx = document.getElementById('commodityChart').getContext('2d');
        const chartDatasets = {json.dumps(chart_datasets, indent=8)};
        
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                datasets: chartDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                parsing: {{
                    xAxisKey: 'x',
                    yAxisKey: 'y'
                }},
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{
                            usePointStyle: true,
                            padding: 20,
                            font: {{
                                size: 12
                            }}
                        }}
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#FF6B6B',
                        borderWidth: 1,
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(2);
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'category',
                        grid: {{
                            color: 'rgba(0,0,0,0.1)'
                        }},
                        ticks: {{
                            maxTicksLimit: 20
                        }}
                    }},
                    y: {{
                        grid: {{
                            color: 'rgba(0,0,0,0.1)'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value.toFixed(1);
                            }}
                        }}
                    }}
                }},
                interaction: {{
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    return html_content

def main():
    """主函数 / Main function"""
    print("=" * 70)
    print("📊 轮胎相关商品价格指数可视化 / Tire-Related Commodity Price Index Visualization")
    print("=" * 70)
    
    # 读取FRED数据
    fred_file = "csv_output/FRED_Data.csv"
    bls_file = "csv_output/BLS_Data.csv"
    
    if not os.path.exists(fred_file):
        print(f"❌ 错误：找不到FRED数据文件 / Error: FRED data file not found: {fred_file}")
        return 1
        
    if not os.path.exists(bls_file):
        print(f"❌ 错误：找不到BLS数据文件 / Error: BLS data file not found: {bls_file}")
        return 1
    
    print(f"📄 读取FRED数据文件 / Reading FRED data file: {fred_file}")
    fred_df_raw = pd.read_csv(fred_file)
    fred_df = parse_fred_data(fred_df_raw)
    
    print(f"📄 读取BLS数据文件 / Reading BLS data file: {bls_file}")
    bls_df_raw = pd.read_csv(bls_file)
    bls_df = parse_bls_data(bls_df_raw)
    
    # 合并数据
    combined_df = pd.concat([fred_df, bls_df], ignore_index=True)
    
    print(f"📊 数据概况 / Data overview:")
    print(f"   - FRED数据记录数 / FRED records: {len(fred_df)}")
    print(f"   - BLS数据记录数 / BLS records: {len(bls_df)}")
    print(f"   - 总记录数 / Total records: {len(combined_df)}")
    print(f"   - 商品类型 / Product types: {combined_df['Product'].nunique()}")
    print(f"   - 时间范围 / Time range: {combined_df['Year'].min()}-{combined_df['Year'].max()}")
    
    # 计算同比环比数据
    print("🔢 计算同比环比数据 / Calculating comparisons...")
    comparisons = calculate_latest_comparisons(combined_df)
    
    print(f"📈 分析结果 / Analysis results:")
    for product, comp in comparisons.items():
        print(f"   - {product}: {comp['latest']['value']:.2f} ({comp['latest']['date_str']})")
        if comp['prev_month']['change'] is not None:
            print(f"     环比 MoM: {comp['prev_month']['change']:+.2f}%")
        if comp['same_month_last_year']['change'] is not None:
            print(f"     同比 YoY: {comp['same_month_last_year']['change']:+.2f}%")
    
    # 生成HTML可视化
    print("🎨 生成HTML可视化页面 / Generating HTML visualization...")
    html_content = generate_html_visualization(combined_df, comparisons)
    
    # 保存HTML文件
    output_file = "commodity_visualization.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 可视化页面已生成 / Visualization page generated: {output_file}")
    print(f"🌐 请在浏览器中打开该文件查看可视化结果 / Please open the file in a browser to view the visualization")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main()) 