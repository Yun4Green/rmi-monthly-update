#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序 / Main Program
依次执行四个子模块的数据爬取脚本，并将结果合并到一个Excel文件中
Execute four sub-module data scraping scripts sequentially and merge results into one Excel file

作者: AI Assistant
日期: 2025-07-01
"""

import os
import sys
import subprocess
import pandas as pd
import openpyxl
from datetime import datetime
import logging
from pathlib import Path
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main_execution.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataIntegrator:
    """数据整合器类 / Data Integrator Class"""
    
    def __init__(self, output_filename="integrated_data.xlsx"):
        self.output_filename = output_filename
        self.scripts_config = [
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
        
    def execute_script(self, script_path):
        """
        执行单个脚本 / Execute single script
        
        Args:
            script_path (str): 脚本路径
            
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        try:
            logger.info(f"开始执行脚本 / Starting script: {script_path}")
            
            # 获取脚本所在目录
            script_dir = os.path.dirname(script_path)
            script_name = os.path.basename(script_path)
            
            # 切换到脚本目录执行
            original_cwd = os.getcwd()
            if script_dir:
                os.chdir(script_dir)
                logger.info(f"切换到目录 / Changed to directory: {script_dir}")
            
            # 执行脚本
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            # 切换回原目录
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                logger.info(f"脚本执行成功 / Script executed successfully: {script_path}")
                if result.stdout:
                    logger.info(f"输出 / Output:\n{result.stdout}")
                return True
            else:
                logger.error(f"脚本执行失败 / Script execution failed: {script_path}")
                logger.error(f"错误码 / Return code: {result.returncode}")
                if result.stderr:
                    logger.error(f"错误信息 / Error output:\n{result.stderr}")
                if result.stdout:
                    logger.error(f"标准输出 / Standard output:\n{result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"脚本执行超时 / Script execution timeout: {script_path}")
            return False
        except Exception as e:
            logger.error(f"执行脚本时发生异常 / Exception during script execution: {script_path}")
            logger.error(f"异常信息 / Exception details: {str(e)}")
            logger.error(f"堆栈跟踪 / Stack trace:\n{traceback.format_exc()}")
            return False
        finally:
            # 确保回到原目录
            try:
                os.chdir(original_cwd)
            except:
                pass
    
    def read_txt_data(self, file_path):
        """
        读取文本文件数据 / Read text file data
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            pd.DataFrame: 数据框
        """
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if ':' in line:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                date_str = parts[0].strip()
                                value_str = parts[1].strip()
                                # 提取数值（去掉单位）
                                try:
                                    value = float(value_str.split()[0])
                                    data.append({'Date': date_str, 'Value': value})
                                except:
                                    pass
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"读取文本文件失败 / Failed to read text file {file_path}: {e}")
            return pd.DataFrame()
    
    def read_excel_data(self, file_path, sheet_name=None):
        """
        读取Excel文件数据 / Read Excel file data
        
        Args:
            file_path (str): 文件路径
            sheet_name (str): 工作表名称（可选）
            
        Returns:
            pd.DataFrame: 数据框
        """
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            logger.info(f"成功读取Excel文件 / Successfully read Excel file: {file_path}")
            logger.info(f"数据形状 / Data shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"读取Excel文件失败 / Failed to read Excel file {file_path}: {e}")
            return pd.DataFrame()
    
    def process_output_files(self, config):
        """
        处理输出文件 / Process output files
        
        Args:
            config (dict): 脚本配置
            
        Returns:
            pd.DataFrame: 处理后的数据框
        """
        output_files = config['output_files']
        combined_data = pd.DataFrame()
        
        for file_path in output_files:
            if not os.path.exists(file_path):
                logger.warning(f"输出文件不存在 / Output file does not exist: {file_path}")
                continue
                
            try:
                if file_path.endswith('.txt'):
                    df = self.read_txt_data(file_path)
                elif file_path.endswith(('.xlsx', '.xls')):
                    df = self.read_excel_data(file_path)
                else:
                    logger.warning(f"不支持的文件格式 / Unsupported file format: {file_path}")
                    continue
                
                if not df.empty:
                    # 添加数据源信息
                    df['Source_File'] = os.path.basename(file_path)
                    df['Data_Source'] = config['name']
                    df['Generated_At'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if combined_data.empty:
                        combined_data = df
                    else:
                        combined_data = pd.concat([combined_data, df], ignore_index=True)
                
            except Exception as e:
                logger.error(f"处理输出文件时发生错误 / Error processing output file {file_path}: {e}")
        
        return combined_data
    
    def create_integrated_excel(self, all_data):
        """
        创建整合的Excel文件 / Create integrated Excel file
        
        Args:
            all_data (dict): 所有数据字典
        """
        try:
            with pd.ExcelWriter(self.output_filename, engine='openpyxl') as writer:
                # 创建汇总sheet
                summary_data = []
                for config in self.scripts_config:
                    sheet_name = config['sheet_name']
                    data = all_data.get(sheet_name, pd.DataFrame())
                    
                    # 添加数据来源网站
                    data_source_url = {
                        'Commodity Price Crawler': 'https://www.worldbank.org/en/research/commodity-markets',
                        'BLS Data Scraper': 'https://data.bls.gov/toppicks?survey=pc',
                        'Exchange Rate Scraper': 'https://www.x-rates.com/average/',
                        'FRED Data Scraper': 'https://fred.stlouisfed.org/series/PCU314994314994'
                    }
                    
                    summary_data.append({
                        'Module': config['name'],
                        'Module_CN': config['name_cn'],
                        'Sheet_Name': sheet_name,
                        'Records_Count': len(data),
                        'Status': 'Success' if not data.empty else 'No Data',
                        'Source_URL': data_source_url.get(config['name'], ''),
                        'Generated_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                logger.info("创建汇总工作表 / Created summary worksheet")
                
                # 写入各个模块的数据（只为每个唯一的sheet_name创建一个工作表）
                processed_sheets = set()
                for config in self.scripts_config:
                    sheet_name = config['sheet_name']
                    
                    # 跳过已经处理过的sheet
                    if sheet_name in processed_sheets:
                        continue
                    
                    processed_sheets.add(sheet_name)
                    data = all_data.get(sheet_name, pd.DataFrame())
                    
                    if not data.empty:
                        data.to_excel(writer, sheet_name=sheet_name, index=False)
                        logger.info(f"写入数据到工作表 / Wrote data to worksheet: {sheet_name} ({len(data)} 行记录 / records)")
                    else:
                        # 创建空的工作表并添加说明
                        empty_df = pd.DataFrame({
                            'Status': ['No data available'],
                            'Message': [f'No output data found for sheet: {sheet_name}'],
                            'Generated_At': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                        })
                        empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        logger.warning(f"创建空工作表 / Created empty worksheet: {sheet_name}")
                
                # Metadata工作表已移除，根据用户需求
            
            logger.info(f"整合Excel文件创建成功 / Integrated Excel file created successfully: {self.output_filename}")
            
        except Exception as e:
            logger.error(f"创建整合Excel文件失败 / Failed to create integrated Excel file: {e}")
            raise
    
    def run(self):
        """
        运行主程序 / Run main program
        """
        logger.info("=" * 80)
        logger.info("🚀 数据整合程序启动 / Data Integration Program Started")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        all_data = {}
        execution_results = {}
        
        try:
            # 依次执行各个脚本
            for i, config in enumerate(self.scripts_config, 1):
                logger.info(f"\n📊 [{i}/{len(self.scripts_config)}] 执行模块 / Executing module: {config['name']} ({config['name_cn']})")
                logger.info(f"📁 脚本路径 / Script path: {config['script_path']}")
                
                # 执行脚本
                success = self.execute_script(config['script_path'])
                execution_results[config['name']] = success
                
                if success:
                    logger.info(f"✅ 模块执行成功 / Module executed successfully: {config['name']}")
                    
                    # 处理输出文件
                    logger.info("📤 处理输出文件 / Processing output files...")
                    data = self.process_output_files(config)
                    
                    # 如果sheet_name已存在，合并数据；否则创建新的
                    if config['sheet_name'] in all_data:
                        if not data.empty and not all_data[config['sheet_name']].empty:
                            all_data[config['sheet_name']] = pd.concat([all_data[config['sheet_name']], data], ignore_index=True)
                            logger.info(f"📈 合并数据到现有工作表 / Merged data to existing sheet: {config['sheet_name']}")
                        elif not data.empty:
                            all_data[config['sheet_name']] = data
                    else:
                        all_data[config['sheet_name']] = data
                    
                    if not data.empty:
                        logger.info(f"📈 获取到 {len(data)} 条数据记录 / Retrieved {len(data)} data records")
                    else:
                        logger.warning("⚠️  未获取到有效数据 / No valid data retrieved")
                else:
                    logger.error(f"❌ 模块执行失败 / Module execution failed: {config['name']}")
                    if config['sheet_name'] not in all_data:
                        all_data[config['sheet_name']] = pd.DataFrame()
                
                logger.info(f"{'='*50}")
            
            # 创建整合的Excel文件
            logger.info("\n📋 创建整合Excel文件 / Creating integrated Excel file...")
            self.create_integrated_excel(all_data)
            
            # 执行汇总
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("\n" + "=" * 80)
            logger.info("🎉 数据整合程序完成 / Data Integration Program Completed")
            logger.info("=" * 80)
            logger.info(f"⏱️  总耗时 / Total duration: {duration}")
            logger.info(f"📁 输出文件 / Output file: {self.output_filename}")
            
            # 执行结果汇总
            success_count = sum(1 for result in execution_results.values() if result)
            total_count = len(execution_results)
            
            logger.info(f"📊 执行结果 / Execution results: {success_count}/{total_count} 成功 / successful")
            
            for name, result in execution_results.items():
                status = "✅ 成功 / Success" if result else "❌ 失败 / Failed"
                logger.info(f"   {name}: {status}")
            
            if success_count == total_count:
                logger.info("🎊 所有模块执行成功！/ All modules executed successfully!")
            elif success_count > 0:
                logger.warning(f"⚠️  部分模块执行成功 / Partial success: {success_count}/{total_count}")
            else:
                logger.error("💥 所有模块执行失败 / All modules failed")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ 程序执行过程中发生严重错误 / Critical error during program execution: {e}")
            logger.error(f"堆栈跟踪 / Stack trace:\n{traceback.format_exc()}")
            raise

def main():
    """主函数 / Main function"""
    try:
        print("🔧 数据整合系统 / Data Integration System")
        print("=" * 60)
        print("依次执行四个数据爬虫模块并整合结果")
        print("Execute four data scraping modules sequentially and integrate results")
        print("=" * 60)
        
        # 创建数据整合器并运行
        integrator = DataIntegrator()
        integrator.run()
        
        print(f"\n✅ 程序执行完成！请查看输出文件: {integrator.output_filename}")
        print(f"✅ Program completed! Please check output file: {integrator.output_filename}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行 / User interrupted execution")
        return 1
    except Exception as e:
        print(f"\n❌ 程序执行失败 / Program execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 