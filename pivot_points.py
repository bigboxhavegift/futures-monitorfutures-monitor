#!/usr/bin/env python3
"""
期货枢轴点计算 - 日K和周K
基于前一日/周的高低价计算当日支撑阻力位
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# 监控品种（主力合约）
SYMBOLS = {
    # 上期所
    'CU': '沪铜', 'AL': '沪铝', 'ZN': '沪锌', 'PB': '沪铅', 'NI': '沪镍', 'SN': '沪锡',
    'AU': '沪金', 'AG': '沪银', 'RB': '螺纹钢', 'HC': '热轧卷板', 'BU': '沥青',
    # 大商所
    'I': '铁矿石', 'J': '焦炭', 'JM': '焦煤', 'M': '豆粕', 'Y': '豆油', 'P': '棕榈油',
    'C': '玉米', 'CS': '淀粉', 'L': '聚乙烯', 'PP': '聚丙烯', 'V': 'PVC',
    'EG': '乙二醇', 'EB': '苯乙烯', 'PG': '液化石油气',
    # 郑商所
    'TA': 'PTA', 'MA': '甲醇', 'RM': '菜粕', 'OI': '菜油', 'CF': '棉花',
    'SR': '白糖', 'SA': '纯碱', 'FG': '玻璃', 'SF': '硅铁', 'SM': '锰硅',
    'UR': '尿素', 'PF': '短纤',
    # 能源中心
    'SC': '原油', 'LU': '低硫燃料油', 'NR': '20号胶',
    # 广期所
    'SI': '工业硅', 'LC': '碳酸锂',
}

def calculate_pivot_points(high, low, close):
    """
    计算枢轴点和支撑阻力位
    标准公式：
    PP = (H + L + C) / 3
    R1 = 2*PP - L
    S1 = 2*PP - H
    R2 = PP + (H - L)
    S2 = PP - (H - L)
    R3 = H + 2*(PP - L)
    S3 = L - 2*(H - PP)
    """
    pp = (high + low + close) / 3
    r1 = 2 * pp - low
    s1 = 2 * pp - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)
    r3 = high + 2 * (pp - low)
    s3 = low - 2 * (high - pp)
    
    return {
        'pp': round(pp, 2),
        'r1': round(r1, 2), 'r2': round(r2, 2), 'r3': round(r3, 2),
        's1': round(s1, 2), 's2': round(s2, 2), 's3': round(s3, 2),
        'high': high, 'low': low, 'close': close
    }

def get_daily_data(symbol_code):
    """获取日K数据（最近2天）"""
    try:
        # 使用akshare获取期货日线数据
        df = ak.futures_zh_daily_sina(symbol=symbol_code)
        if df is not None and len(df) >= 2:
            # 获取最近一个完整交易日数据
            df = df.sort_values('date', ascending=True)
            prev_day = df.iloc[-2]  # 前一交易日
            return {
                'high': float(prev_day.get('high', 0)),
                'low': float(prev_day.get('low', 0)),
                'close': float(prev_day.get('close', 0)),
                'date': prev_day.get('date', '')
            }
    except Exception as e:
        print(f"  日K获取失败: {str(e)[:30]}")
    return None

def get_weekly_data(symbol_code):
    """获取周K数据（最近2周）"""
    try:
        # 获取日线数据后按周聚合
        df = ak.futures_zh_daily_sina(symbol=symbol_code)
        if df is not None and len(df) >= 10:
            df = df.sort_values('date', ascending=True)
            df['date'] = pd.to_datetime(df['date'])
            df['week'] = df['date'].dt.isocalendar().week
            df['year'] = df['date'].dt.isocalendar().year
            
            # 按周聚合
            weekly = df.groupby(['year', 'week']).agg({
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'date': 'last'
            }).reset_index()
            
            if len(weekly) >= 2:
                prev_week = weekly.iloc[-2]
                return {
                    'high': float(prev_week['high']),
                    'low': float(prev_week['low']),
                    'close': float(prev_week['close']),
                    'date': str(prev_week['date'])[:10]
                }
    except Exception as e:
        print(f"  周K获取失败: {str(e)[:30]}")
    return None

def generate_html(daily_results, weekly_results, timestamp):
    """生成枢轴点报告HTML"""
    
    # 生成日K表格
    daily_rows = ""
    for item in daily_results:
        daily_rows += f"""
        <tr>
            <td><b>{item['name']}</b></td>
            <td>{item['code']}</td>
            <td style="color:#333;font-weight:bold;">{item['pp']}</td>
            <td style="color:#52c41a">{item['r1']}</td>
            <td style="color:#52c41a">{item['r2']}</td>
            <td style="color:#52c41a">{item['r3']}</td>
            <td style="color:#ff4d4f">{item['s1']}</td>
            <td style="color:#ff4d4f">{item['s2']}</td>
            <td style="color:#ff4d4f">{item['s3']}</td>
        </tr>"""
    
    if not daily_rows:
        daily_rows = '<tr><td colspan="9" style="text-align:center;padding:20px;">暂无数据</td></tr>'
    
    # 生成周K表格
    weekly_rows = ""
    for item in weekly_results:
        weekly_rows += f"""
        <tr>
            <td><b>{item['name']}</b></td>
            <td>{item['code']}</td>
            <td style="color:#333;font-weight:bold;">{item['pp']}</td>
            <td style="color:#52c41a">{item['r1']}</td>
            <td style="color:#52c41a">{item['r2']}</td>
            <td style="color:#52c41a">{item['r3']}</td>
            <td style="color:#ff4d4f">{item['s1']}</td>
            <td style="color:#ff4d4f">{item['s2']}</td>
            <td style="color:#ff4d4f">{item['s3']}</td>
        </tr>"""
    
    if not weekly_rows:
        weekly_rows = '<tr><td colspan="9" style="text-align:center;padding:20px;">暂无数据</td></tr>'
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>期货枢轴点 - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; color: white; margin-bottom: 30px; padding: 30px; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        .card-title {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
        th {{
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
        }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #eee; text-align: center; }}
        tr:hover {{ background: #f8f9fa; }}
        .legend {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 0.85em;
        }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; color: #666; }}
        .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.7); padding: 20px; }}
        .formula {{
            background: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-family: monospace;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 期货枢轴点分析</h1>
            <p>基于前一日/周高低收计算支撑阻力位</p>
            <p style="margin-top:10px;font-size:0.95em;">{timestamp}</p>
        </div>
        
        <div class="formula">
            <b>计算公式：</b><br>
            PP（枢轴点）= (High + Low + Close) / 3<br>
            R1 = 2×PP - Low | R2 = PP + (High-Low) | R3 = High + 2×(PP-Low)<br>
            S1 = 2×PP - High | S2 = PP - (High-Low) | S3 = Low - 2×(High-PP)
        </div>
        
        <div class="card">
            <div class="card-title">📈 日K枢轴点（基于前一交易日）</div>
            <table>
                <thead>
                    <tr>
                        <th>品种</th>
                        <th>代码</th>
                        <th>PP枢轴</th>
                        <th style="color:#52c41a">R1阻力</th>
                        <th style="color:#52c41a">R2阻力</th>
                        <th style="color:#52c41a">R3阻力</th>
                        <th style="color:#ff4d4f">S1支撑</th>
                        <th style="color:#ff4d4f">S2支撑</th>
                        <th style="color:#ff4d4f">S3支撑</th>
                    </tr>
                </thead>
                <tbody>{daily_rows}</tbody>
            </table>
        </div>
        
        <div class="card">
            <div class="card-title">📊 周K枢轴点（基于上一交易周）</div>
            <table>
                <thead>
                    <tr>
                        <th>品种</th>
                        <th>代码</th>
                        <th>PP枢轴</th>
                        <th style="color:#52c41a">R1阻力</th>
                        <th style="color:#52c41a">R2阻力</th>
                        <th style="color:#52c41a">R3阻力</th>
                        <th style="color:#ff4d4f">S1支撑</th>
                        <th style="color:#ff4d4f">S2支撑</th>
                        <th style="color:#ff4d4f">S3支撑</th>
                    </tr>
                </thead>
                <tbody>{weekly_rows}</tbody>
            </table>
        </div>
        
        <div class="legend">
            <div class="legend-item"><div class="legend-dot" style="background:#333"></div>PP 枢轴点（多空分界）</div>
            <div class="legend-item"><div class="legend-dot" style="background:#52c41a"></div>R1-R3 阻力位（绿色）</div>
            <div class="legend-item"><div class="legend-dot" style="background:#ff4d4f"></div>S1-S3 支撑位（红色）</div>
        </div>
        
        <div class="footer">
            <p>⚠️ 本报告仅供参考，不构成投资建议 | 数据来自AKShare</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("="*60)
    print("期货枢轴点计算")
    beijing_time = datetime.utcnow() + timedelta(hours=8)
    print(f"时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print("="*60)
    
    os.makedirs('docs/pivot', exist_ok=True)
    
    daily_results = []
    weekly_results = []
    
    print(f"\n📊 开始计算 {len(SYMBOLS)} 个品种...")
    
    for code, name in SYMBOLS.items():
        try:
            print(f"  {name}({code})...", end=' ')
            
            # 日K枢轴点
            daily_data = get_daily_data(code)
            if daily_data:
                daily_pivot = calculate_pivot_points(
                    daily_data['high'],
                    daily_data['low'],
                    daily_data['close']
                )
                daily_pivot['code'] = code
                daily_pivot['name'] = name
                daily_results.append(daily_pivot)
                print("日K✓", end=' ')
            
            # 周K枢轴点
            weekly_data = get_weekly_data(code)
            if weekly_data:
                weekly_pivot = calculate_pivot_points(
                    weekly_data['high'],
                    weekly_data['low'],
                    weekly_data['close']
                )
                weekly_pivot['code'] = code
                weekly_pivot['name'] = name
                weekly_results.append(weekly_pivot)
                print("周K✓")
            else:
                print("-")
                
        except Exception as e:
            print(f"失败: {str(e)[:20]}")
            continue
    
    # 生成报告
    timestamp = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    html = generate_html(daily_results, weekly_results, timestamp)
    
    html_path = 'docs/pivot/index.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n{'='*60}")
    print(f"✅ 报告已生成: {html_path}")
    print(f"✅ 日K枢轴点: {len(daily_results)} 个品种")
    print(f"✅ 周K枢轴点: {len(weekly_results)} 个品种")
    print("="*60)

if __name__ == '__main__':
    main()
