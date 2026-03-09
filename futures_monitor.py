#!/usr/bin/env python3
"""
期货异动监控脚本 - GitHub Actions 版本
获取国内期货实时行情，生成HTML报告到docs目录
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# 创建docs目录
os.makedirs('docs', exist_ok=True)

# 主要期货品种列表
MAIN_CONTRACTS = {
    '铜': '沪铜', '铝': '沪铝', '锌': '沪锌', '铅': '沪铅', '镍': '沪镍', '锡': '沪锡',
    '黄金': '沪金', '白银': '沪银', '螺纹钢': '螺纹钢', '热轧卷板': '热轧卷板',
    '燃料油': '燃料油', '沥青': '沥青', '橡胶': '橡胶', '纸浆': '纸浆',
    '不锈钢': '不锈钢', '线材': '线材',
    '铁矿石': '铁矿石', '焦炭': '焦炭', '焦煤': '焦煤', '豆粕': '豆粕', '豆油': '豆油',
    '棕榈油': '棕榈油', '玉米': '玉米', '淀粉': '玉米淀粉', '鸡蛋': '鸡蛋', '生猪': '生猪',
    '聚乙烯': '聚乙烯', '聚丙烯': '聚丙烯', 'PVC': 'PVC', '乙二醇': '乙二醇',
    '苯乙烯': '苯乙烯', '液化石油气': '液化石油气',
    'PTA': 'PTA', '甲醇': '甲醇', '菜粕': '菜粕', '菜油': '菜籽油', '棉花': '棉花',
    '白糖': '白糖', '苹果': '苹果', '红枣': '红枣', '纯碱': '纯碱', '玻璃': '玻璃',
    '动力煤': '动力煤', '硅铁': '硅铁', '锰硅': '锰硅', '短纤': '短纤', '花生': '花生',
    '尿素': '尿素', '棉纱': '棉纱',
    '工业硅': '工业硅', '碳酸锂': '碳酸锂',
    '原油': '原油', '20号胶': '20号胶', '低硫燃料油': '低硫燃料油', '国际铜': '国际铜',
}

def get_contract_realtime(name):
    """获取单个品种的实时行情"""
    try:
        df = ak.futures_zh_realtime(symbol=name)
        if df is not None and not df.empty:
            main = df.iloc[0]
            return {
                'symbol': main.get('symbol', ''),
                'name': main.get('name', name),
                'exchange': main.get('exchange', ''),
                'price': float(main.get('trade', 0) or 0),
                'change': float(main.get('change', 0) or 0),
                'change_percent': float(main.get('changepercent', 0) or 0) * 100,
                'volume': int(main.get('volume', 0) or 0),
                'open': float(main.get('open', 0) or 0),
                'high': float(main.get('high', 0) or 0),
                'low': float(main.get('low', 0) or 0),
            }
    except:
        pass
    return None

def get_all_futures():
    """获取所有主力合约行情"""
    results = []
    for key, name in MAIN_CONTRACTS.items():
        try:
            data = get_contract_realtime(name)
            if data:
                results.append(data)
        except:
            pass
    return results

def check_anomalies(data_list, threshold_pct=3.0):
    """筛选异动品种"""
    anomalies = []
    for item in data_list:
        change_pct = item.get('change_percent', 0)
        if abs(change_pct) >= threshold_pct:
            anomalies.append(item)
    anomalies.sort(key=lambda x: abs(x.get('change_percent', 0)), reverse=True)
    return anomalies

def get_exchange_name(exchange_code):
    mapping = {
        'shfe': '上期所', 'dce': '大商所', 'czce': '郑商所',
        'cffex': '中金所', 'gfex': '广期所', 'ine': '能源中心',
    }
    return mapping.get(exchange_code, exchange_code.upper())

def generate_html_report(all_data, anomalies, timestamp):
    """生成响应式HTML报告"""
    
    up_count = sum(1 for x in all_data if x['change_percent'] > 0)
    down_count = sum(1 for x in all_data if x['change_percent'] < 0)
    
    anomaly_rows = ""
    if anomalies:
        for item in anomalies:
            direction = "📈" if item['change_percent'] > 0 else "📉"
            color = "#ff4d4f" if item['change_percent'] < 0 else "#52c41a" if item['change_percent'] > 5 else "#faad14"
            anomaly_rows += f"""
            <tr>
                <td><span class="badge" style="background:{color}20;color:{color}">{get_exchange_name(item['exchange'])}</span></td>
                <td><b>{item['name']}</b></td>
                <td style="color:{color};font-weight:bold;font-size:1.1em;">{item['change_percent']:+.2f}%</td>
                <td>{item['price']:.0f}</td>
                <td>{item['volume']:,}</td>
            </tr>"""
    else:
        anomaly_rows = """
        <tr>
            <td colspan="5" style="text-align:center;padding:40px;color:#999;">
                <div style="font-size:48px;margin-bottom:10px;">✅</div>
                <div>当前无异动品种，所有合约涨跌幅均在±3%以内</div>
            </td>
        </tr>"""
    
    all_rows = ""
    for item in sorted(all_data, key=lambda x: abs(x['change_percent']), reverse=True)[:15]:
        color = "#ff4d4f" if item['change_percent'] < 0 else "#52c41a" if item['change_percent'] > 0 else "#999"
        all_rows += f"""
        <tr>
            <td><span class="badge">{get_exchange_name(item['exchange'])}</span></td>
            <td>{item['name']}</td>
            <td style="color:{color};font-weight:bold;">{item['change_percent']:+.2f}%</td>
            <td>{item['price']:.0f}</td>
        </tr>"""
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>期货异动监控 - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 30px 20px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: white;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
        .stat-label {{ font-size: 0.9em; opacity: 0.8; }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .card-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-right: 15px;
        }}
        .alert-icon {{ background: linear-gradient(135deg, #ff6b6b, #ee5a5a); }}
        .all-icon {{ background: linear-gradient(135deg, #4ecdc4, #44a08d); }}
        .card-title {{ font-size: 1.5em; color: #333; font-weight: 600; }}
        .card-subtitle {{ color: #888; font-size: 0.9em; margin-top: 5px; }}
        .badge {{
            background: #f0f0f0;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8em;
            color: #666;
        }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
        }}
        th:first-child {{ border-radius: 8px 0 0 0; }}
        th:last-child {{ border-radius: 0 8px 0 0; }}
        td {{ padding: 14px 12px; border-bottom: 1px solid #f0f0f0; }}
        tr:hover {{ background: #f8f9fa; }}
        tr:last-child td {{ border-bottom: none; }}
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.7);
            padding: 20px;
            font-size: 0.9em;
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
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8em; }}
            .card {{ padding: 15px; }}
            th, td {{ padding: 10px 8px; font-size: 0.9em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 期货异动监控</h1>
            <p>实时监控国内期货主力合约异动情况</p>
            <p style="margin-top:10px;font-size:0.95em;">{timestamp}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(all_data)}</div>
                <div class="stat-label">监控品种</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color:#52c41a">{up_count}</div>
                <div class="stat-label">上涨</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color:#ff4d4f">{down_count}</div>
                <div class="stat-label">下跌</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color:#faad14">{len(anomalies)}</div>
                <div class="stat-label">异动品种</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <div class="card-icon alert-icon">🚨</div>
                <div>
                    <div class="card-title">异动品种 | 涨跌幅 ≥ 3%</div>
                    <div class="card-subtitle">发现 {len(anomalies)} 个异动合约</div>
                </div>
            </div>
            <table>
                <thead>
                    <tr><th>交易所</th><th>品种</th><th>涨跌幅</th><th>现价</th><th>成交量</th></tr>
                </thead>
                <tbody>{anomaly_rows}</tbody>
            </table>
            <div class="legend">
                <div class="legend-item"><div class="legend-dot" style="background:#ff4d4f"></div>下跌 ≥ 3%</div>
                <div class="legend-item"><div class="legend-dot" style="background:#faad14"></div>上涨 3-5%</div>
                <div class="legend-item"><div class="legend-dot" style="background:#52c41a"></div>上涨 ≥ 5%</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <div class="card-icon all-icon">📈</div>
                <div>
                    <div class="card-title">涨跌幅排行 TOP15</div>
                    <div class="card-subtitle">按绝对涨跌幅排序</div>
                </div>
            </div>
            <table>
                <thead>
                    <tr><th>交易所</th><th>品种</th><th>涨跌幅</th><th>现价</th></tr>
                </thead>
                <tbody>{all_rows}</tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>⚠️ 本报告仅供参考，不构成投资建议 | 数据来自AKShare/东方财富</p>
            <p style="margin-top:10px;opacity:0.6">异动标准：涨跌幅绝对值 ≥ 3%</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def main():
    print("="*60)
    print("期货异动监控 - GitHub Actions 版本")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 获取行情
    print("\n📊 获取期货主力合约行情...")
    data = get_all_futures()
    
    if not data:
        print("❌ 未能获取任何数据")
        # 创建一个空报告
        data = []
    
    print(f"✅ 成功获取 {len(data)} 个品种")
    
    # 检查异动
    print("\n🔍 检查异动品种...")
    anomalies = check_anomalies(data, threshold_pct=3.0)
    print(f"发现 {len(anomalies)} 个异动品种")
    
    # 生成报告
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = generate_html_report(data, anomalies, timestamp)
    
    # 保存到docs目录
    html_path = 'docs/index.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("\n" + "="*60)
    print(f"✅ 报告已生成: {html_path}")
    print("="*60)
    print(f"\n📊 统计:")
    print(f"   监控品种: {len(data)} 个")
    print(f"   异动品种: {len(anomalies)} 个")

if __name__ == '__main__':
    main()
