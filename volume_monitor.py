#!/usr/bin/env python3
"""
成交量异动监控 - 日K成交量超出前一日2倍以上
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# 监控的期货品种
MONITOR_SYMBOLS = {
    '沪铜': 'CU', '沪铝': 'AL', '沪锌': 'ZN', '沪铅': 'PB', 
    '沪镍': 'NI', '沪锡': 'SN', '沪金': 'AU', '沪银': 'AG',
    '螺纹钢': 'RB', '热轧卷板': 'HC', '铁矿石': 'I', 
    '焦炭': 'J', '焦煤': 'JM', '豆粕': 'M', '豆油': 'Y',
    'PTA': 'TA', '甲醇': 'MA', '纯碱': 'SA', '玻璃': 'FG',
    '原油': 'SC', '苯乙烯': 'EB', '乙二醇': 'EG',
}

def get_daily_volume(symbol_code, days=5):
    """获取品种日K成交量数据"""
    try:
        # 使用akshare获取期货历史数据
        df = ak.futures_zh_daily(symbol=symbol_code)
        if df is not None and len(df) >= 2:
            # 按日期排序，取最近2天
            df = df.sort_values('date', ascending=False).head(2)
            return df
    except:
        pass
    return None

def check_volume_surge(symbol_name, symbol_code):
    """检查成交量是否超过前一日2倍以上"""
    df = get_daily_volume(symbol_code)
    if df is not None and len(df) >= 2:
        today_volume = df.iloc[0]['volume']
        prev_volume = df.iloc[1]['volume']
        
        if prev_volume > 0:
            volume_ratio = today_volume / prev_volume
            if volume_ratio >= 2.0:
                return {
                    'name': symbol_name,
                    'symbol': symbol_code,
                    'today_volume': int(today_volume),
                    'prev_volume': int(prev_volume),
                    'ratio': round(volume_ratio, 2),
                    'price_change': round(df.iloc[0].get('close', 0) - df.iloc[1].get('close', 0), 2)
                }
    return None

def generate_report(surge_list, timestamp):
    """生成HTML报告"""
    
    rows = ""
    for item in surge_list:
        rows += f"""
        <tr>
            <td><b>{item['name']}</b></td>
            <td>{item['symbol']}</td>
            <td style="color:#ff4d4f;font-weight:bold;">{item['ratio']}x</td>
            <td>{item['today_volume']:,}</td>
            <td>{item['prev_volume']:,}</td>
            <td>{item['price_change']:+.2f}</td>
        </tr>"""
    
    if not rows:
        rows = """
        <tr>
            <td colspan="6" style="text-align:center;padding:40px;color:#999;">
                <div style="font-size:48px;margin-bottom:10px;">✅</div>
                <div>今日无成交量异动品种</div>
            </td>
        </tr>"""
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>成交量异动监控 - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ text-align: center; color: white; margin-bottom: 30px; padding: 30px; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .card-title {{
            font-size: 1.5em; 
            color: #333; 
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .badge {{
            background: #ff4d4f;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.7em;
        }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{
            background: linear-gradient(135deg, #f093fb, #f5576c);
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
        }}
        th:first-child {{ border-radius: 8px 0 0 0; }}
        th:last-child {{ border-radius: 0 8px 0 0; }}
        td {{ padding: 14px 12px; border-bottom: 1px solid #f0f0f0; }}
        tr:hover {{ background: #f8f9fa; }}
        .alert {{ 
            background: #fff2f0; 
            border: 1px solid #ffccc7; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px;
            color: #cf1322;
        }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.7); padding: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 成交量异动监控</h1>
            <p>日K成交量超出前一日2倍以上</p>
            <p style="margin-top:10px;font-size:0.95em;">{timestamp}</p>
        </div>
        
        <div class="card">
            <div class="card-title">
                异动品种列表（成交量 ≥ 2倍）
                <span class="badge">发现 {len(surge_list)} 个</span>
            </div>
            
            <div class="alert">
                ⚠️ 成交量突然放大可能意味着资金异动，需结合价格走势判断方向
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>品种</th>
                        <th>代码</th>
                        <th>放量倍数</th>
                        <th>今日成交量</th>
                        <th>昨日成交量</th>
                        <th>涨跌</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>⚠️ 本报告仅供参考，不构成投资建议 | 数据来自AKShare</p>
            <p style="margin-top:5px;opacity:0.7">监控条件：日K成交量 ≥ 前一日 2倍</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def main():
    print("="*60)
    print("成交量异动监控 - 日K放量2倍以上")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    print(f"\n📊 监控 {len(MONITOR_SYMBOLS)} 个品种...")
    surge_list = []
    
    for name, code in MONITOR_SYMBOLS.items():
        result = check_volume_surge(name, code)
        if result:
            surge_list.append(result)
            print(f"  🚨 {name}: 放量 {result['ratio']}x")
    
    # 按放量倍数排序
    surge_list.sort(key=lambda x: x['ratio'], reverse=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = generate_report(surge_list, timestamp)
    
    # 保存到docs/volume目录
    os.makedirs('docs/volume', exist_ok=True)
    html_path = 'docs/volume/index.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n{'='*60}")
    print(f"✅ 报告已生成: {html_path}")
    print(f"✅ 发现 {len(surge_list)} 个放量品种")
    print("="*60)

if __name__ == '__main__':
    main()
