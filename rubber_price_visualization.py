#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
橡胶价格数据可视化 / Rubber Price Data Visualization
基于Rubber_Prices.csv数据生成同比环比分析的Canvas图表
Generate Canvas charts with year-over-year and month-over-month analysis based on Rubber_Prices.csv
"""

import pandas as pd
import json
from datetime import datetime
import os
import re

def parse_rubber_data(df):
    """
    解析橡胶价格数据 / Parse rubber price data
    """
    data_records = []
    
    for _, row in df.iterrows():
        date_str = str(row['Date'])
        
        # 匹配年月数据格式 (例如: 2015M01)
        if re.match(r'^\d{4}M\d{2}$', date_str):
            year = int(date_str[:4])
            month = int(date_str[5:7])
            value = float(row['Value'])
            
            # 只取2015年及以后的数据
            if year >= 2015:
                data_records.append({
                    'Year': year,
                    'Month': month,
                    'Value': value,
                    'Date_String': f"{year}-{month:02d}"
                })
    
    return pd.DataFrame(data_records)

def calculate_comparisons(df):
    """
    计算同比环比数据 / Calculate year-over-year and month-over-month comparisons
    """
    # 确保数据按时间排序
    df = df.sort_values(['Year', 'Month'])
    
    if len(df) == 0:
        return None
    
    # 获取最新数据
    latest_data = df.iloc[-1]
    latest_year = latest_data['Year']
    latest_month = latest_data['Month']
    latest_value = latest_data['Value']
    
    # 上月数据 (环比)
    prev_month_data = df.iloc[-2] if len(df) >= 2 else None
    prev_month_value = prev_month_data['Value'] if prev_month_data is not None else None
    
    # 去年同月数据 (同比)
    same_month_last_year = df[(df['Year'] == latest_year - 1) & (df['Month'] == latest_month)]
    same_month_last_year_value = same_month_last_year['Value'].iloc[0] if not same_month_last_year.empty else None
    
    # 计算变化率
    mom_change = ((latest_value - prev_month_value) / prev_month_value * 100) if prev_month_value else None
    yoy_change = ((latest_value - same_month_last_year_value) / same_month_last_year_value * 100) if same_month_last_year_value else None
    
    return {
        'latest': {
            'year': int(latest_year),
            'month': int(latest_month),
            'value': float(latest_value),
            'date_str': f"{latest_year}年{latest_month}月"
        },
        'prev_month': {
            'value': float(prev_month_value) if prev_month_value else None,
            'change': float(mom_change) if mom_change else None
        },
        'same_month_last_year': {
            'value': float(same_month_last_year_value) if same_month_last_year_value else None,
            'change': float(yoy_change) if yoy_change else None
        }
    }

def generate_html_visualization(df, comparisons):
    """
    生成HTML Canvas可视化页面 / Generate HTML Canvas visualization page
    """
    
    # 准备图表数据
    chart_data = []
    for _, row in df.iterrows():
        chart_data.append({
            'x': row['Date_String'],
            'y': float(row['Value'])
        })
    
    # 预处理显示数据
    prev_value_display = f"{comparisons['prev_month']['value']:.4f}" if comparisons['prev_month']['value'] is not None else 'N/A'
    prev_change_display = f"{comparisons['prev_month']['change']:+.2f}%" if comparisons['prev_month']['change'] is not None else 'N/A'
    prev_change_class = 'change-positive' if comparisons['prev_month']['change'] and comparisons['prev_month']['change'] > 0 else 'change-negative' if comparisons['prev_month']['change'] and comparisons['prev_month']['change'] < 0 else 'change-neutral'
    prev_arrow = '↗️' if comparisons['prev_month']['change'] and comparisons['prev_month']['change'] > 0 else '↘️' if comparisons['prev_month']['change'] and comparisons['prev_month']['change'] < 0 else '➡️'
    
    yoy_value_display = f"{comparisons['same_month_last_year']['value']:.4f}" if comparisons['same_month_last_year']['value'] is not None else 'N/A'
    yoy_change_display = f"{comparisons['same_month_last_year']['change']:+.2f}%" if comparisons['same_month_last_year']['change'] is not None else 'N/A'
    yoy_change_class = 'change-positive' if comparisons['same_month_last_year']['change'] and comparisons['same_month_last_year']['change'] > 0 else 'change-negative' if comparisons['same_month_last_year']['change'] and comparisons['same_month_last_year']['change'] < 0 else 'change-neutral'
    yoy_arrow = '↗️' if comparisons['same_month_last_year']['change'] and comparisons['same_month_last_year']['change'] > 0 else '↘️' if comparisons['same_month_last_year']['change'] and comparisons['same_month_last_year']['change'] < 0 else '➡️'
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>橡胶价格数据可视化 / Rubber Price Data Visualization</title>
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
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #FF9500 0%, #FF6B35 100%);
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
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card-title {{
            font-size: 1.1em;
            color: #666;
            margin: 0 0 15px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .card-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #FF9500;
        }}
        
        .card-meta {{
            font-size: 0.9em;
            color: #888;
            margin: 0 0 15px 0;
        }}
        
        .card-change {{
            font-size: 1.2em;
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
        
        #rubberChart {{
            max-height: 400px;
        }}
        
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .trend-arrow {{
            font-size: 1.5em;
            margin-left: 10px;
        }}
        
        .source-links {{
            margin-top: 15px;
        }}
        
        .source-links a {{
            color: #FF9500;
            text-decoration: none;
            margin: 0 10px;
        }}
        
        .source-links a:hover {{
            text-decoration: underline;
        }}
        
        .prev-value {{
            font-size: 0.8em;
            color: #888;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>橡胶价格分析</h1>
            <p>Rubber Price Analysis Dashboard</p>
        </div>
        
        <div class="cards-container">
            <div class="card">
                <h3 class="card-title">当前价格 / Current Price</h3>
                <div class="card-value">${comparisons['latest']['value']:.4f}</div>
                <p class="card-meta">{comparisons['latest']['date_str']} | USD/公斤 USD/kg</p>
            </div>
            
            <div class="card">
                <h3 class="card-title">环比变化 / Month-over-Month</h3>
                <div class="card-value">${prev_value_display}</div>
                <div class="prev-value">上月价格 / Previous Month</div>
                <p class="card-change {prev_change_class}">
                    {prev_change_display} 
                    <span class="trend-arrow">{prev_arrow}</span>
                </p>
            </div>
            
            <div class="card">
                <h3 class="card-title">同比变化 / Year-over-Year</h3>
                <div class="card-value">${yoy_value_display}</div>
                <div class="prev-value">去年同月 / Same Month Last Year</div>
                <p class="card-change {yoy_change_class}">
                    {yoy_change_display}
                    <span class="trend-arrow">{yoy_arrow}</span>
                </p>
            </div>
        </div>
        
        <div class="chart-container">
            <h2 class="chart-title">橡胶价格趋势图 / Rubber Price Trend Chart (2015-{comparisons['latest']['year']})</h2>
            <canvas id="rubberChart"></canvas>
        </div>
        
        <div class="footer">
            <p>数据来源 / Data Sources:</p>
            <div class="source-links">
                <a href="https://www.worldbank.org/en/research/commodity-markets" target="_blank">World Bank - Commodity Markets Research</a>
            </div>
            <p style="margin-top: 15px; font-size: 0.8em; color: #ccc;">
                <strong>数据说明 / Data Description:</strong><br>
                • 橡胶价格: TSR20橡胶现货价格 (美元/公斤) / Rubber Price: TSR20 Rubber Spot Price (USD/kg)<br>
                • 数据来源: 世界银行商品市场研究数据库 / Data Source: World Bank Commodity Markets Research Database<br>
                • 更新频率: 月度数据 / Update Frequency: Monthly Data
            </p>
            <p style="margin-top: 10px;">生成时间 / Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        // 图表配置和数据
        const ctx = document.getElementById('rubberChart').getContext('2d');
        const chartData = {json.dumps(chart_data, indent=8)};
        
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: chartData.map(item => item.x),
                datasets: [{{
                    label: '橡胶价格 (USD/kg)',
                    data: chartData.map(item => item.y),
                    borderColor: '#FF9500',
                    backgroundColor: 'rgba(255, 149, 0, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#FF9500',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{
                            usePointStyle: true,
                            padding: 20,
                            font: {{
                                size: 14
                            }}
                        }}
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#FF9500',
                        borderWidth: 1,
                        callbacks: {{
                            label: function(context) {{
                                return '橡胶价格: $' + context.parsed.y.toFixed(4) + '/kg';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{
                            color: 'rgba(0,0,0,0.1)'
                        }},
                        ticks: {{
                            maxTicksLimit: 15
                        }}
                    }},
                    y: {{
                        grid: {{
                            color: 'rgba(0,0,0,0.1)'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toFixed(2);
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
    print("=" * 60)
    print("📊 橡胶价格数据可视化 / Rubber Price Data Visualization")
    print("=" * 60)
    
    # 读取CSV数据
    csv_file = "csv_output/Rubber_Prices.csv"
    if not os.path.exists(csv_file):
        print(f"❌ 错误：找不到CSV文件 / Error: CSV file not found: {csv_file}")
        return 1
    
    print(f"📄 读取数据文件 / Reading data file: {csv_file}")
    df_raw = pd.read_csv(csv_file)
    df = parse_rubber_data(df_raw)
    
    print(f"📊 数据概况 / Data overview:")
    print(f"   - 总记录数 / Total records: {len(df)}")
    print(f"   - 时间范围 / Time range: {df['Year'].min()}-{df['Month'].min():02d} 到 / to {df['Year'].max()}-{df['Month'].max():02d}")
    print(f"   - 价格范围 / Price range: ${df['Value'].min():.4f} - ${df['Value'].max():.4f}")
    
    # 计算同比环比数据
    print("🔢 计算同比环比数据 / Calculating comparisons...")
    comparisons = calculate_comparisons(df)
    
    if comparisons:
        print(f"📈 分析结果 / Analysis results:")
        print(f"   - 最新价格 / Latest price: ${comparisons['latest']['value']:.4f} ({comparisons['latest']['date_str']})")
        if comparisons['prev_month']['change']:
            print(f"   - 环比变化 / MoM change: {comparisons['prev_month']['change']:+.2f}%")
        if comparisons['same_month_last_year']['change']:
            print(f"   - 同比变化 / YoY change: {comparisons['same_month_last_year']['change']:+.2f}%")
        
        # 生成HTML可视化
        print("🎨 生成HTML可视化页面 / Generating HTML visualization...")
        html_content = generate_html_visualization(df, comparisons)
        
        # 保存HTML文件
        output_file = "rubber_price_visualization.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 可视化页面已生成 / Visualization page generated: {output_file}")
        print(f"🌐 请在浏览器中打开该文件查看可视化结果 / Please open the file in a browser to view the visualization")
    else:
        print("❌ 无法计算比较数据 / Unable to calculate comparison data")
        return 1
    
    print("=" * 60)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main()) 