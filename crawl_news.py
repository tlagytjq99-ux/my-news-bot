import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

# 1. 인증 정보 및 설정
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
        if any(keyword in title for keyword in keywords):
            return category
    return "기타"

# --- 파트 1: 네이버 뉴스 수집 ---
def get_naver_news():
    url = "https://openapi.naver.com/v1/search/news.json?query=AI&display=100&sort=sim"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    res = requests.get(url, headers=headers)
    news_list = []
    if res.status_code == 200:
        items = res.json().get('items', [])
        counts = {"기업": 0, "기술": 0, "정책": 0, "산업": 0}
        for item in items:
            title = item['title'].replace("<b>","").replace("</b>","").replace("&quot;",'"').replace("&amp;","&")
            cat = classify_category(title)
            if cat in counts and counts[cat] < 2:
                news_list.append({"카테고리": cat, "기사제목": title, "발행일": item['pubDate'][:16], "링크": item['link']})
                counts[cat] += 1
    return news_list

# --- 파트 2: 과기정통부 보도자료 수집 ---
def get_msit_news():
    # 과기부 보도자료 목록 페이지
    url = "https://www.msit.go.kr/bbs/list.do?sCode=user&mPid=217&mId=113"
    # 로봇 차단을 피하기 위한 "사람 브라우저" 흉내 설정
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    msit_list = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        # 게시판 목록에서 제목 요소 찾기 (사이트 구조에 맞게 설정)
        items = soup.select('div.lst_b li') 
        count = 0
        for item in items:
            title_el = item.select_one('p.tit')
            if title_el and "AI" in title_el.text or "인공지능" in title_el.text:
                title = title_el.text.strip()
                link = "https://www.msit.go.kr" + item.select_one('a')['href']
                msit_list.append({"카테고리": "정부(과기부)", "기사제목": title, "발행일": "최근", "링크": link})
                count += 1
                if count >= 2: break
    except:
        print("과기부 사이트 접근에 실패했습니다. (보안 또는 구조 변경)")
    return msit_list

# --- 메인 실행 ---
collection_date = datetime.now().strftime("%Y-%m-%d")
all_data = get_naver_news() + get_msit_news()

if all_data:
    df = pd.DataFrame(all_data)
    df.insert(0, "수집일", collection_date) # 수집일 맨 앞에 추가
    df.to_excel("news_list.xlsx", index=False)
    print(f"✅ 수집 완료! 네이버 뉴스 및 과기부 소식이 저장되었습니다.")
else:
    print("❌ 수집된 데이터가 없습니다.")
