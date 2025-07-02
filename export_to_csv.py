#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel工作表导出为CSV / Excel Worksheet Export to CSV
将integrated_data.xlsx中的各个工作表（除Summary外）导出为独立的CSV文件
Export each worksheet (except Summary) in integrated_data.xlsx to separate CSV files
"""

import pandas as pd
import os
import sys
from datetime import datetime

def export_excel_to_csv(excel_file="integrated_data.xlsx", output_dir="csv_output"):
    """
    将Excel文件中的工作表导出为CSV文件
    Export worksheets in Excel file to CSV files
    
    Args:
        excel_file (str): Excel文件路径 / Excel file path
        output_dir (str): 输出目录 / Output directory
    """
    print(f"📊 开始导出Excel工作表到CSV / Starting export of Excel worksheets to CSV")
    print(f"📄 源文件 / Source file: {excel_file}")
    
    # 检查Excel文件是否存在 / Check if Excel file exists
    if not os.path.exists(excel_file):
        print(f"❌ 错误：找不到Excel文件 / Error: Excel file not found: {excel_file}")
        return False
    
    # 创建输出目录 / Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 创建输出目录 / Created output directory: {output_dir}")
    
    try:
        # 读取Excel文件 / Read Excel file
        print(f"🔍 读取Excel文件 / Reading Excel file...")
        excel = pd.ExcelFile(excel_file)
        
        # 获取所有工作表名称 / Get all worksheet names
        sheets = excel.sheet_names
        print(f"📋 找到工作表 / Found worksheets: {sheets}")
        
        # 导出每个工作表（除Summary外）/ Export each worksheet (except Summary)
        exported_count = 0
        for sheet in sheets:
            if sheet.lower() == "summary":
                print(f"⏭️  跳过Summary工作表 / Skipping Summary worksheet")
                continue
                
            # 修正工作表名称 (如果是Rubber_Prices，则输出文件名改为Rubber_TSR20.csv)
            output_sheet_name = "Rubber_TSR20" if sheet == "Rubber_Prices" else sheet
                
            print(f"📤 导出工作表 / Exporting worksheet: {sheet}")
            
            # 读取工作表数据 / Read worksheet data
            df = pd.read_excel(excel, sheet_name=sheet)
            
            # 构建CSV文件名 / Build CSV filename
            csv_file = os.path.join(output_dir, f"{output_sheet_name}.csv")
            
            # 导出到CSV / Export to CSV
            df.to_csv(csv_file, index=False, encoding='utf-8')
            
            # 获取文件大小 / Get file size
            file_size = os.path.getsize(csv_file)
            file_size_kb = file_size / 1024
            
            print(f"✅ 已导出 / Exported: {csv_file} ({file_size_kb:.2f} KB, {len(df)} 行记录 / rows)")
            exported_count += 1
        
        print(f"\n🎉 导出完成 / Export completed!")
        print(f"📊 总计导出 / Total exported: {exported_count} 个CSV文件 / CSV files")
        print(f"📁 输出目录 / Output directory: {os.path.abspath(output_dir)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导出过程中发生错误 / Error during export: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数 / Main function"""
    # 默认参数 / Default parameters
    excel_file = "integrated_data.xlsx"
    output_dir = "csv_output"
    
    # 处理命令行参数 / Handle command line arguments
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    print("=" * 60)
    print("📊 Excel工作表导出为CSV / Excel Worksheet Export to CSV")
    print("=" * 60)
    print(f"⏰ 开始时间 / Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行导出 / Execute export
    success = export_excel_to_csv(excel_file, output_dir)
    
    print(f"⏱️  结束时间 / End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 返回状态码 / Return status code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 