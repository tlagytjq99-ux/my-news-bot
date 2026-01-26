import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

# 1. 네이버 API 인증 정보
client_id = os.environ.get('NAVER_CLIENT_ID')
client_secret = os.environ.get('NAVER_CLIENT_SECRET')

def classify_category(title):
    categories = {
        "기업": ["투자", "유치", "인수", "합병", "M&A", "실적", "상장", "IPO", "파트너십", "협력", "삼성", "네이버", "구글", "오픈AI"],
        "기술": ["모델", "LLM", "성능", "출시", "특허", "논문", "칩", "반도체", "HBM", "Sora", "GPT", "알고리즘"],
        "정책": ["정부", "법안", "규제", "가이드라인", "예산", "지원", "국회", "과기부", "EU", "조약", "윤리"],
        "산업": ["시장", "전망", "도입", "사례", "금융", "의료", "제조", "일자리", "확산", "트렌드", "인력"]
    }
    for category, keywords in categories.items():
        if any(keyword in str(title) for keyword in keywords):
            return category
    return "기타"

def get_naver_news():
    news_list = []
    if not client_id or not client_secret: return news_list
    url = "https://openapi.naver.com/v1/search/news.json?query=AI&display=100&sort=sim"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            items = res.json().get('items', [])
            counts = {"기업": 0, "기술": 0, "정책": 0, "산업": 0}
            for item in items:
                title = item['title'].replace("<b>","").replace("</b>","").replace("&quot;",'"').replace("&amp;","&")
                cat = classify_category(title)
                if cat in counts and counts[cat] < 2:
                    news_list.append({"카테고리": cat, "기사제목": title, "발행일": item['pubDate'][:16], "링크": item['link']})
                    counts[cat] += 1
    except: pass
    return news_list

def get_msit_via_google():
    """과기부 사이트 직접 접속 대신 구글 뉴스 RSS를 통해 우회 수집"""
    msit_list = []
    # 검색어: site:msit.go.kr AI
    rss_url = "https://news.google.com/rss/search?q=site:msit.go.kr+AI&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        res = requests.get(rss_url, timeout=15)
        # xml 파서 에러를 피하기 위해 기본 html.parser 사용
        soup = BeautifulSoup(res.text, 'html.parser') 
        items = soup.find_all('item')
        
        for item in items[:5]: # 최신 5개
            title_tag = item.find('title')
            link_tag = item.find('link')
            date_tag = item.find('pubdate')
            
            if title_tag and link_tag:
                title = title_tag.get_text().split(' - ')[0]
                link = link_tag.get_text()
                pub_date = date_tag.get_text()[:16] if date_tag else "최근"
                
                msit_list.append({
                    "카테고리": "정부(과기부)",
                    "기사제목": title,
                    "발행일": pub_date,
                    "링크": link
                })
    except Exception as e:
        print(f"⚠️ 과기부 우회 수집 중 참고용 메시지: {e}")
    return msit_list

# --- 메인 실행 ---
collection_date = datetime.now().strftime("%Y-%m-%d")
all_data = get_naver_news() + get_msit_via_google()

if all_data:
    df = pd.DataFrame(all_data)
    df.insert(0, "수집일", collection_date)
    df.to_excel("news_list.xlsx", index=False)
    msit_count = len([d for d in all_data if d['카테고리'] == '정부(과기부)'])
    print(f"✅ 수집 완료! (네이버: {len(all_data)-msit_count}건, 과기부: {msit_count}건)")
else:
    print("❌ 수집된 데이터가 없습니다.")
