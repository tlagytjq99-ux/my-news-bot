import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

# 1. 인증 정보
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

# --- 파트 1: 네이버 뉴스 수집 ---
def get_naver_news():
    url = "https://openapi.naver.com/v1/search/news.json?query=AI&display=100&sort=sim"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    news_list = []
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            items = res.json().get('items', [])
            counts = {"기업": 0, "기술": 0, "정책": 0, "산업": 0}
            for item in items:
                title = item['title'].replace("<b>","").replace("</b>","").replace("&quot;",'"').replace("&amp;","&")
                cat = classify_category(title)
                if cat in counts and counts[cat] < 2:
                    news_list.append({"카테고리": cat, "기사제목": title, "발행일": item['pubDate'][:16], "링크": item['link']})
                    counts[cat] += 1
    except Exception as e:
        print(f"네이버 API 수집 중 오류: {e}")
    return news_list

# --- 파트 2: 과기정통부 보도자료 수집 ---
def get_msit_news():
    url = "https://www.msit.go.kr/bbs/list.do?sCode=user&mPid=217&mId=113"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    msit_list = []
    try:
        res = requests.get(url, headers=headers, timeout=15) # 타임아웃 연장
        res.raise_for_status() # 접속 실패 시 에러 발생
        
        # lxml 대신 기본 html.parser 사용 (설치 문제 방지)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 과기부 사이트의 실제 제목 태그를 더 정밀하게 타겟팅
        items = soup.find_all('div', class_='lst_b') # 혹은 soup.select('tr') 등으로 시도
        
        # 만약 위 태그로 안 잡힐 경우를 대비한 유연한 수집
        rows = soup.select('div.lst_b li') or soup.select('tr')
        
        count = 0
        for row in rows:
            title_el = row.select_one('p.tit') or row.select_one('td.left a')
            if title_el:
                title_text = title_el.get_text().strip()
                if "AI" in title_text or "인공지능" in title_text or "디지털" in title_text:
                    link_el = row.select_one('a')
                    link = "https://www.msit.go.kr" + link_el['href'] if link_el else url
                    msit_list.append({"카테고리": "정부(과기부)", "기사제목": title_text, "발행일": "최근", "링크": link})
                    count += 1
                    if count >= 2: break
    except Exception as e:
        print(f"과기부 수집 건너뜀 (원인: {e})") # 에러가 나도 전체 프로세스는 멈추지 않게 함
    return msit_list

# --- 메인 실행 ---
collection_date = datetime.now().strftime("%Y-%m-%d")
all_data = get_naver_news() + get_msit_news()

if all_data:
    df = pd.DataFrame(all_data)
    if '수집일' not in df.columns:
        df.insert(0, "수집일", collection_date)
    df.to_excel("news_list.xlsx", index=False)
    print(f"✅ 수집 완료! (총 {len(all_data)}건)")
else:
    print("❌ 수집된 데이터가 없습니다.")
