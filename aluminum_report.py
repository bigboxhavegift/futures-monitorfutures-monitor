#!/usr/bin/env python3
"""
沪铝每日行情报告 - GitHub Actions 版本
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

def get_aluminum_data():
    """获取沪铝主力合约数据"""
    try:
        df = ak.futures_zh_realtime(symbol="沪铝")
        if df is not None and not df.empty:
            main = df.iloc[0]
            return {
                'symbol': main.get('symbol', ''),
                'name': main.get('name', '沪铝连续'),
                'price': float(main.get('trade', 0) or 0),
                'change': float(main.get('change', 0) or 0),
                'change_percent': float(main.get('changepercent', 0) or 0) * 100,
                'volume': int(main.get('volume', 0) or 0),
                'open': float(main.get('open', 0) or 0),
                'high': float(main.get('high', 0) or 0),
                'low': float(main.get('low', 0) or 0),
                'settlement': float(main.get('settlement', 0) or 0),
                'position': int(main.get('position', 0) or 0),
            }
    except:
        pass
    return None

def get_lme_aluminum():
    """获取LME铝数据（简化版，实际可能需要其他数据源）"""
    # 这里用模拟数据，实际可以用其他API
    return {
        'price': 0,
        'change': 0,
        'change_percent': 0,
        'inventory': 'N/A'
    }

def generate_html(data, timestamp):
    """生成沪铝报告HTML"""
    
    if not data:
        data = {'price': 0, 'change': 0, 'change_percent': 0, 'volume': 0}
    
    change_color = "#ff4d4f" if data['change_percent'] < 0 else "#52c41a"
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>沪铝每日行情 - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        .card-title {{ font-size: 1.5em; color: #333; margin-bottom: 15px; }}
        .price {{ font-size: 3em; font-weight: bold; color: {change_color}; margin: 20px 0; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-item {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
        .stat-value {{ font-size: 1.5em; font-weight: bold; color: #333; }}
        .stat-label {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.7); padding: 20px; }}
        .back-link {{ 
            display: inline-block; 
            margin-bottom: 20px; 
            color: white; 
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/futures-monitorfutures-monitor/" class="back-link">← 返回期货监控</a>
        
        <div class="header">
            <h1>📊 沪铝每日行情</h1>
            <p>主力合约实时数据</p>
            <p style="margin-top:10px;font-size:0.95em;">{timestamp}</p>
        </div>
        
        <div class="card">
            <div class="card-title">沪铝连续合约</div>
            <div class="price">{data['price']:.0f}</div>
            
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value" style="color:{change_color}">{data['change_percent']:+.2f}%</div>
                    <div class="stat-label">涨跌幅</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['change']:+.0f}</div>
                    <div class="stat-label">涨跌额</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data['volume']:,}</div>
                    <div class="stat-label">成交量</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data.get('high', 0):.0f}</div>
                    <div class="stat-label">最高</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data.get('low', 0):.0f}</div>
                    <div class="stat-label">最低</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{data.get('open', 0):.0f}</div>
                    <div class="stat-label">开盘</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>⚠️ 本报告仅供参考，不构成投资建议 | 数据来自AKShare</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def main():
    print("="*60)
    print("沪铝每日行情报告")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    data = get_aluminum_data()
    
    if data:
        print(f"✅ 获取数据成功: {data['name']} @ {data['price']}")
    else:
        print("⚠️ 未能获取实时数据，使用默认值")
        data = {'price': 0, 'change': 0, 'change_percent': 0, 'volume': 0, 'high': 0, 'low': 0, 'open': 0}
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = generate_html(data, timestamp)
    
    # 保存到docs/aluminum目录
    os.makedirs('docs/aluminum', exist_ok=True)
    html_path = 'docs/aluminum/index.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {html_path}")
    print("="*60)

if __name__ == '__main__':
    main()
