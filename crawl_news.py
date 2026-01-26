import os
import requests
import pandas as pd
from datetime import datetime

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

def get_naver_news_general():
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

def get_msit_news_via_api():
    msit_list = []
    url = "https://openapi.naver.com/v1/search/news.json?query=과학기술정보통신부+AI&display=50&sort=date"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        res = requests.get(res_url, headers=headers, timeout=10) if (res := requests.get(url, headers=headers)) else None
        if res and res.status_code == 200:
            for item in res.json().get('items', []):
                title = item['title'].replace("<b>","").replace("</b>","").replace("&quot;",'"').replace("&amp;","&")
                msit_list.append({"카테고리": "정부(과기부)", "기사제목": title, "발행일": item['pubDate'][:16], "링크": item['link']})
    except: pass
    return msit_list

# --- 메인 실행부 ---
if __name__ == "__main__":
    collection_date = datetime.now().strftime("%Y-%m-%d")
    all_data = get_naver_news_general() + get_msit_news_via_api()

    if all_data:
        df = pd.DataFrame(all_data)

        # [고급 중복 제거] 
        # 제목의 앞 15자가 겹치면 동일 기사로 판단 (언론사별 미세한 제목 차이 무시)
        df['temp_title'] = df['기사제목'].str.slice(0, 15)
        df = df.drop_duplicates(subset=['temp_title'], keep='first').drop(columns=['temp_title'])
        
        # 완전 중복도 한 번 더 체크
        df = df.drop_duplicates(subset=['기사제목'], keep='first')

        df.insert(0, "수집일", collection_date)
        df.to_excel("news_list.xlsx", index=False)
        print(f"✅ 지능형 중복 제거 완료! 총 {len(df)}건 저장")
