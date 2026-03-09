#!/usr/bin/env python3
"""
期货枢轴点计算 - 基于实时数据近似
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# 监控品种
SYMBOLS = {
    '沪铜': '沪铜', '沪铝': '沪铝', '沪锌': '沪锌', '沪铅': '沪铅',
    '沪镍': '沪镍', '沪锡': '沪锡', '沪金': '沪金', '沪银': '沪银',
    '螺纹钢': '螺纹钢', '热轧卷板': '热轧卷板', '铁矿石': '铁矿石',
    '焦炭': '焦炭', '焦煤': '焦煤', '豆粕': '豆粕', '豆油': '豆油',
    '棕榈油': '棕榈油', '原油': '原油', 'PTA': 'PTA', '甲醇': '甲醇',
    '纯碱': '纯碱', '玻璃': '玻璃',
}

def calculate_pivot_points(high, low, close):
    """计算枢轴点"""
    pp = (high + low + close) / 3
    r1 = 2 * pp - low
    s1 = 2 * pp - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)
    return {
        'pp': round(pp, 2),
        'r1': round(r1, 2), 'r2': round(r2, 2),
        's1': round(s1, 2), 's2': round(s2, 2),
    }

def main():
    print("="*60)
    print("期货枢轴点计算 - 基于实时数据")
    beijing_time = datetime.utcnow() + timedelta(hours=8)
    print(f"时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    os.makedirs('docs/pivot', exist_ok=True)
    results = []
    
    print(f"\n📊 开始计算 {len(SYMBOLS)} 个品种...")
    
    for name in SYMBOLS.values():
        try:
            print(f"  {name}...", end=' ')
            df = ak.futures_zh_realtime(symbol=name)
            if df is not None and not df.empty:
                data = df.iloc[0]
                high = float(data.get('high', 0))
                low = float(data.get('low', 0))
                close = float(data.get('settlement', data.get('trade', 0)))
                
                if high > 0 and low > 0 and close > 0:
                    pivot = calculate_pivot_points(high, low, close)
                    pivot['name'] = name
                    pivot['price'] = float(data.get('trade', 0))
                    results.append(pivot)
                    print("✓")
                else:
                    print("-")
            else:
                print("×")
        except:
            print("失败")
            continue
    
    # 生成简单HTML
    timestamp = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    
    rows = ""
    for r in results:
        rows += f"""
        <tr>
            <td>{r['name']}</td>
            <td>{r['price']:.0f}</td>
            <td style='color:#ff4d4f'>{r['s2']}</td>
            <td style='color:#ff4d4f'>{r['s1']}</td>
            <td style='font-weight:bold'>{r['pp']}</td>
            <td style='color:#52c41a'>{r['r1']}</td>
            <td style='color:#52c41a'>{r['r2']}</td>
        </tr>"""
    
    html = f"""
<!DOCTYPE html>
<html><head><meta charset='UTF-8'>
<title>期货枢轴点 - {timestamp}</title>
<style>
body{{font-family:Arial,sans-serif;padding:20px;background:#f5f5f5}}
.container{{max-width:1000px;margin:0 auto;background:white;padding:20px;border-radius:8px}}
h1{{color:#333}}table{{width:100%;border-collapse:collapse;margin-top:20px}}
th{{background:#1e3c72;color:white;padding:10px;text-align:center}}
td{{padding:10px;text-align:center;border-bottom:1px solid #ddd}}
.footer{{text-align:center;color:#999;margin-top:20px}}
</style></head><body>
<div class='container'>
<h1>📊 期货枢轴点分析</h1>
<p>基于今日实时行情计算 | {timestamp}</p>
<p style="color:#ff6b6b;font-size:0.9em;">⚠️ 注意：本报告使用当日已产生的最高/最低/结算价计算，非前一交易日数据。GitHub Actions 环境无法稳定获取历史日K。</p>
<table>
<tr><th>品种</th><th>现价</th><th style='color:#ffccc7'>S2</th><th style='color:#ffccc7'>S1</th><th>PP</th><th style='color:#d4edda'>R1</th><th style='color:#d4edda'>R2</th></tr>
{rows}
</table>
<p class='footer'>⚠️ 本报告仅供参考，不构成投资建议 | 数据来自AKShare</p>
</div></body></html>
"""
    
    with open('docs/pivot/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 报告已生成: {len(results)} 个品种")
    print("="*60)

if __name__ == '__main__':
    main()
