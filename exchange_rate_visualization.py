#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USD/EUR汇率数据可视化 / USD/EUR Exchange Rate Data Visualization
基于Exchange_Rates.csv数据生成同比环比分析的Canvas图表
Generate Canvas charts with year-over-year and month-over-month analysis based on Exchange_Rates.csv
"""

import pandas as pd
import json
from datetime import datetime
import os

def calculate_comparisons(df):
    """
    计算同比环比数据 / Calculate year-over-year and month-over-month comparisons
    """
    # 确保数据按时间排序
    df = df.sort_values(['Year', 'Month'])
    
    # 获取最新数据
    latest_data = df.iloc[-1]
    latest_year = latest_data['Year']
    latest_month = latest_data['Month']
    latest_rate = latest_data['Exchange_Rate']
    
    # 上月数据 (环比)
    prev_month_data = df.iloc[-2] if len(df) >= 2 else None
    prev_month_rate = prev_month_data['Exchange_Rate'] if prev_month_data is not None else None
    
    # 去年同月数据 (同比)
    same_month_last_year = df[(df['Year'] == latest_year - 1) & (df['Month'] == latest_month)]
    same_month_last_year_rate = same_month_last_year['Exchange_Rate'].iloc[0] if not same_month_last_year.empty else None
    
    # 计算变化率
    mom_change = ((latest_rate - prev_month_rate) / prev_month_rate * 100) if prev_month_rate else None
    yoy_change = ((latest_rate - same_month_last_year_rate) / same_month_last_year_rate * 100) if same_month_last_year_rate else None
    
    return {
        'latest': {
            'year': int(latest_year),
            'month': int(latest_month),
            'rate': float(latest_rate),
            'date_str': f"{latest_year}年{latest_month}月"
        },
        'prev_month': {
            'rate': float(prev_month_rate) if prev_month_rate else None,
            'change': float(mom_change) if mom_change else None
        },
        'same_month_last_year': {
            'rate': float(same_month_last_year_rate) if same_month_last_year_rate else None,
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
            'x': f"{int(row['Year'])}-{int(row['Month']):02d}",
            'y': float(row['Exchange_Rate'])
        })
    
    # 预处理数据以避免f-string复杂性
    prev_rate_display = f"{comparisons['prev_month']['rate']:.6f}" if comparisons['prev_month']['rate'] is not None else 'N/A'
    prev_change_display = f"{comparisons['prev_month']['change']:+.2f}%" if comparisons['prev_month']['change'] is not None else 'N/A'
    prev_change_class = 'change-positive' if comparisons['prev_month']['change'] and comparisons['prev_month']['change'] > 0 else 'change-negative' if comparisons['prev_month']['change'] and comparisons['prev_month']['change'] < 0 else 'change-neutral'
    prev_arrow = '↗️' if comparisons['prev_month']['change'] and comparisons['prev_month']['change'] > 0 else '↘️' if comparisons['prev_month']['change'] and comparisons['prev_month']['change'] < 0 else '➡️'
    
    yoy_rate_display = f"{comparisons['same_month_last_year']['rate']:.6f}" if comparisons['same_month_last_year']['rate'] is not None else 'N/A'
    yoy_change_display = f"{comparisons['same_month_last_year']['change']:+.2f}%" if comparisons['same_month_last_year']['change'] is not None else 'N/A'
    yoy_change_class = 'change-positive' if comparisons['same_month_last_year']['change'] and comparisons['same_month_last_year']['change'] > 0 else 'change-negative' if comparisons['same_month_last_year']['change'] and comparisons['same_month_last_year']['change'] < 0 else 'change-neutral'
    yoy_arrow = '↗️' if comparisons['same_month_last_year']['change'] and comparisons['same_month_last_year']['change'] > 0 else '↘️' if comparisons['same_month_last_year']['change'] and comparisons['same_month_last_year']['change'] < 0 else '➡️'
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USD/EUR汇率数据可视化 / USD/EUR Exchange Rate Visualization</title>
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
            background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
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
            color: #2196F3;
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
        
        #exchangeRateChart {{
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>USD/EUR汇率分析</h1>
            <p>Exchange Rate Analysis Dashboard</p>
        </div>
        
        <div class="cards-container">
            <div class="card">
                <h3 class="card-title">当前汇率 / Current Rate</h3>
                <div class="card-value">{comparisons['latest']['rate']:.6f}</div>
                <p style="color: #666; margin: 0;">{comparisons['latest']['date_str']}</p>
            </div>
            
            <div class="card">
                <h3 class="card-title">环比变化 / Month-over-Month</h3>
                <div class="card-value">{prev_rate_display}</div>
                <p class="card-change {prev_change_class}">
                    {prev_change_display} 
                    <span class="trend-arrow">{prev_arrow}</span>
                </p>
            </div>
            
            <div class="card">
                <h3 class="card-title">同比变化 / Year-over-Year</h3>
                <div class="card-value">{yoy_rate_display}</div>
                <p class="card-change {yoy_change_class}">
                    {yoy_change_display}
                    <span class="trend-arrow">{yoy_arrow}</span>
                </p>
            </div>
        </div>
        
        <div class="chart-container">
            <h2 class="chart-title">USD/EUR汇率趋势图 / Exchange Rate Trend Chart</h2>
            <canvas id="exchangeRateChart"></canvas>
        </div>
        
        <div class="footer">
            <p>数据来源：<a href="https://www.x-rates.com/average/" target="_blank" style="color: #21CBF3; text-decoration: none;">X-Rates.com</a> | 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        // 图表配置和数据
        const ctx = document.getElementById('exchangeRateChart').getContext('2d');
        const chartData = {json.dumps(chart_data, indent=8)};
        
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: chartData.map(item => item.x),
                datasets: [{{
                    label: 'USD/EUR汇率',
                    data: chartData.map(item => item.y),
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#2196F3',
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
                        borderColor: '#2196F3',
                        borderWidth: 1,
                        callbacks: {{
                            label: function(context) {{
                                return 'USD/EUR: ' + context.parsed.y.toFixed(6);
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
                            maxTicksLimit: 12
                        }}
                    }},
                    y: {{
                        grid: {{
                            color: 'rgba(0,0,0,0.1)'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value.toFixed(3);
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
    print("📊 USD/EUR汇率数据可视化 / USD/EUR Exchange Rate Visualization")
    print("=" * 60)
    
    # 读取CSV数据
    csv_file = "csv_output/Exchange_Rates.csv"
    if not os.path.exists(csv_file):
        print(f"❌ 错误：找不到CSV文件 / Error: CSV file not found: {csv_file}")
        return 1
    
    print(f"📄 读取数据文件 / Reading data file: {csv_file}")
    df = pd.read_csv(csv_file)
    
    print(f"📊 数据概况 / Data overview:")
    print(f"   - 总记录数 / Total records: {len(df)}")
    print(f"   - 时间范围 / Time range: {df['Year'].min()}-{df['Month'].min():02d} 到 / to {df['Year'].max()}-{df['Month'].max():02d}")
    
    # 计算同比环比数据
    print("🔢 计算同比环比数据 / Calculating comparisons...")
    comparisons = calculate_comparisons(df)
    
    print(f"📈 分析结果 / Analysis results:")
    print(f"   - 最新汇率 / Latest rate: {comparisons['latest']['rate']:.6f} ({comparisons['latest']['date_str']})")
    if comparisons['prev_month']['change']:
        print(f"   - 环比变化 / MoM change: {comparisons['prev_month']['change']:+.2f}%")
    if comparisons['same_month_last_year']['change']:
        print(f"   - 同比变化 / YoY change: {comparisons['same_month_last_year']['change']:+.2f}%")
    
    # 生成HTML可视化
    print("🎨 生成HTML可视化页面 / Generating HTML visualization...")
    html_content = generate_html_visualization(df, comparisons)
    
    # 保存HTML文件
    output_file = "exchange_rate_visualization.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 可视化页面已生成 / Visualization page generated: {output_file}")
    print(f"🌐 请在浏览器中打开该文件查看可视化结果 / Please open the file in a browser to view the visualization")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main()) 