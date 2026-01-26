import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

# 1. 인증 정보 (GitHub Secrets 확인 필수)
client_id = os.environ.get('NAVER_CLIENT_ID')
client_secret = os.environ.get('NAVER_CLIENT_SECRET')

def classify_category(title):
    categories = {
        "기업": ["투자", "유치", "인수", "합병", "M&A", "실적", "상장", "IPO", "파트너십", "협력", "삼성", "네이버", "구글", "오픈AI"],
        "기술": ["모델", "LLM", "성능", "출시", "특허", "논문", "칩", "반도체", "HBM", "Sora", "GPT", "알고리즘"],
        "정책": ["정부", "법안", "규제", "가이드라인", "예산", "지원", "국회", "과기부", "EU", "조약", "윤리"],
        "산업": ["시장", "전망", "도입", "사례", "금융", "의료", "제조", "일자리", "확산", "트렌드", "인력"]
    }
    title_str = str(title)
    for category, keywords in categories.items():
        if any(keyword in title_str for keyword in keywords):
            return category
    return "기타"

# --- 파트 1: 네이버 뉴스 수집 ---
def get_naver_news():
    news_list = []
    if not client_id or not client_secret:
        print("⚠️ 네이버 API 키가 설정되지 않았습니다.")
        return news_list
        
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
    except Exception as e:
        print(f"⚠️ 네이버 API 수집 중 건너뜀: {e}")
    return news_list

# --- 파트 2: 과기정통부 보도자료 수집 ---
def get_msit_news():
    msit_list = []
    url = "https://www.msit.go.kr/bbs/list.do?sCode=user&mPid=217&mId=113"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 가장 범용적인 태그 탐색
            items = soup.find_all('li') or soup.find_all('tr')
            count = 0
            for item in items:
                text = item.get_text()
                if ("AI" in text or "인공지능" in text) and count < 2:
                    link_tag = item.find('a')
                    if link_tag and link_tag.has_attr('href'):
                        href = link_tag['href']
                        link = "https://www.msit.go.kr" + href if not href.startswith('http') else href
                        title = link_tag.get_text().strip() or "과기부 보도자료"
                        msit_list.append({"카테고리": "정부(과기부)", "기사제목": title, "발행일": "최근", "링크": link})
                        count += 1
    except Exception as e:
        print(f"⚠️ 과기부 수집 중 건너뜀: {e}")
    return msit_list

# --- 메인 실행 ---
try:
    collection_date = datetime.now().strftime("%Y-%m-%d")
    all_data = get_naver_news() + get_msit_news()

    if all_data:
        df = pd.DataFrame(all_data)
        df.insert(0, "수집일", collection_date)
        df.to_excel("news_list.xlsx", index=False)
        print(f"✅ 성공: {len(all_data)}개의 데이터를 저장했습니다.")
    else:
        # 빈 데이터라도 엑셀은 만들어야 에러가 안 남
        df = pd.DataFrame(columns=["수집일", "카테고리", "기사제목", "발행일", "링크"])
        df.to_excel("news_list.xlsx", index=False)
        print("⚠️ 수집된 데이터가 없어 빈 파일을 생성했습니다.")
except Exception as e:
    print(f"❌ 최종 실행 오류: {e}")
