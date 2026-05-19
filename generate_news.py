import requests
import json
from datetime import datetime, timedelta

# 配置API密钥(会从GitHub Secrets中自动获取)
import os
DOUBAO_API_KEY = os.environ.get('DOUBAO_API_KEY')
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')

def search_stock_news():
    """搜索最新股市利好资讯"""
    url = "https://google.serper.dev/search"
    
    # 搜索关键词：近7天的公司利好公告、业绩增长、行业景气度
    query = """
    2026年5月 上市公司 重大利好公告 订单 技术突破 业绩预告
    上升周期行业 业绩高增长 公司 2026年Q1财报
    AI算力 光模块 半导体 新能源 最新利好
    """
    
    payload = json.dumps({
        "q": query,
        "num": 20,
        "tbs": "qdr:w"  # 只搜索最近一周的内容
    })
    
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    results = response.json()
    
    # 提取搜索结果
    news_content = ""
    for result in results.get('organic', []):
        news_content += f"标题：{result.get('title')}\n"
        news_content += f"内容：{result.get('snippet')}\n\n"
    
    return news_content

def analyze_with_ai(news_content):
    """用AI分析筛选资讯"""
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    
    prompt = f"""
    你是一位专业的财经分析师，擅长挖掘处于上升周期、业绩高增长的优质公司。
    
    请从以下最新资讯中，严格筛选出同时符合以下所有条件的公司：
    1. 近7天内发布了实质性利好公告(大额订单、技术突破、业绩超预期、政策支持等)
    2. 公司所处行业处于明确的上升周期
    3. 2026年Q1净利润同比增长超过30%
    4. 排除近1个月股价涨幅超过50%、估值过高的公司
    
    请按照以下固定格式输出，每个公司单独成段，不要添加任何额外内容：
    
    ## 【公司名称】(股票代码)
    - 最新利好：[具体利好内容，包括时间和金额]
    - 行业逻辑：[1句话说明行业景气度]
    - 业绩表现：[2026Q1营收和净利润同比增长率]
    - 核心亮点：[1-2个最核心的投资逻辑]
    
    如果没有符合所有条件的公司，请输出："今日暂无符合条件的优质公司"
    
    以下是最新资讯：
    {news_content}
    """
    
    payload = json.dumps({
        "model": "doubao-3-5-pro",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    })
    
    headers = {
        'Authorization': f'Bearer {DOUBAO_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    result = response.json()
    
    return result['choices'][0]['message']['content']

def main():
    print("开始搜索最新股市资讯...")
    news_content = search_stock_news()
    
    print("正在用AI分析筛选...")
    ai_content = analyze_with_ai(news_content)
    
    # 生成JSON文件
    output = {
        "update_time": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
        "content": ai_content.replace('\n', '<br>')
    }
    
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("资讯生成完成！")

if __name__ == "__main__":
    main()
