#!/usr/bin/env python3
"""
ETF RSI 超卖筛选报告 - GitHub Actions 版本
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

def calculate_rsi(prices, period=14):
    """计算RSI指标"""
    if len(prices) < period + 1:
        return None
    
    deltas = np.diff(prices)
    gains = deltas.copy()
    losses = deltas.copy()
    gains[gains < 0] = 0
    losses[losses > 0] = 0
    losses = abs(losses)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_etf_rsi():
    """获取ETF RSI数据"""
    results = []
    try:
        # 获取ETF列表
        etf_list = ak.fund_etf_spot_em().head(100)  # 前100只
        
        for idx, row in etf_list.iterrows():
            try:
                code = row['代码']
                name = row['名称']
                
                # 获取历史数据
                hist = ak.fund_etf_hist_em(
                    symbol=code, 
                    period="daily",
                    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
                    end_date=datetime.now().strftime('%Y%m%d'),
                    adjust=""
                )
                
                if len(hist) >= 15:
                    prices = hist['收盘'].values
                    rsi = calculate_rsi(prices)
                    current_price = prices[-1]
                    
                    if rsi is not None:
                        results.append({
                            'code': code,
                            'name': name,
                            'rsi': round(rsi, 2),
                            'price': round(current_price, 3)
                        })
            except:
                continue
                
    except Exception as e:
        print(f"Error: {e}")
    
    return results

def generate_html(etf_data, timestamp):
    """生成RSI报告HTML"""
    
    # 筛选超卖（RSI < 30）
    oversold = [e for e in etf_data if e['rsi'] < 30]
    oversold.sort(key=lambda x: x['rsi'])
    
    # 生成表格行
    rows = ""
    for item in oversold[:20]:  # 只显示前20
        rsi_color = "#ff4d4f" if item['rsi'] < 20 else "#faad14"
        rows += f"""
        <tr>
            <td><b>{item['code']}</b></td>
            <td>{item['name']}</td>
            <td style="color:{rsi_color};font-weight:bold;font-size:1.1em;">{item['rsi']}</td>
            <td>{item['price']}</td>
        </tr>"""
    
    if not rows:
        rows = """
        <tr>
            <td colspan="4" style="text-align:center;padding:40px;color:#999;">
                <div style="font-size:48px;margin-bottom:10px;">✅</div>
                <div>当前没有RSI < 30的超卖ETF</div>
            </td>
        </tr>"""
    
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETF RSI超卖筛选 - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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
            background: linear-gradient(135deg, #11998e, #38ef7d);
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
        }}
        th:first-child {{ border-radius: 8px 0 0 0; }}
        th:last-child {{ border-radius: 0 8px 0 0; }}
        td {{ padding: 14px 12px; border-bottom: 1px solid #f0f0f0; }}
        tr:hover {{ background: #f8f9fa; }}
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
    </style>
</head>
<body>
    <div class="container">
        <a href="/futures-monitorfutures-monitor/" class="back-link">← 返回期货监控</a>
        
        <div class="header">
            <h1>📉 ETF RSI超卖筛选</h1>
            <p>RSI < 30 可能超卖，关注反弹机会</p>
            <p style="margin-top:10px;font-size:0.95em;">{timestamp}</p>
        </div>
        
        <div class="card">
            <div class="card-title">
                超卖ETF列表 (RSI < 30)
                <span class="badge">找到 {len(oversold)} 只</span>
            </div>
            
            <table>
                <thead>
                    <tr><th>代码</th><th>名称</th><th>RSI(14)</th><th>最新价</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            
            <div class="legend">
                <div class="legend-item"><div class="legend-dot" style="background:#ff4d4f"></div>RSI < 20 (极度超卖)</div>
                <div class="legend-item"><div class="legend-dot" style="background:#faad14"></div>RSI 20-30 (超卖)</div>
            </div>
        </div>
        
        <div class="footer">
            <p>⚠️ 本报告仅供参考，不构成投资建议 | 数据来自AKShare</p>
            <p style="margin-top:5px;opacity:0.7">RSI < 30表示超卖，可能有技术性反弹机会</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def main():
    print("="*60)
    print("ETF RSI超卖筛选")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    print("\n📊 获取ETF数据（约需30-60秒）...")
    etf_data = get_etf_rsi()
    
    oversold = [e for e in etf_data if e['rsi'] < 30]
    print(f"✅ 检查了 {len(etf_data)} 只ETF")
    print(f"✅ 找到 {len(oversold)} 只RSI < 30的ETF")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = generate_html(etf_data, timestamp)
    
    # 保存到docs/rsi目录
    os.makedirs('docs/rsi', exist_ok=True)
    html_path = 'docs/rsi/index.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {html_path}")
    print("="*60)

if __name__ == '__main__':
    main()
