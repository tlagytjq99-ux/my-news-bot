import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

# 1. 인증 정보 (네이버 API)
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

# --- 파트 1: 네이버 뉴스 수집 (기존 동일) ---
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

# --- 파트 2: 과기부 AI 검색 결과 수집 (최신 5개) ---
def get_msit_search_results():
    msit_list = []
    # 사용자님이 주신 AI 검색 결과 URL
    url = "https://www.msit.go.kr/bbs/list.do?sCode=user&mId=307&mPid=208&pageIndex=1&bbsSeqNo=94&nttSeqNo=&searchOpt=ALL&searchTxt=ai"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://www.msit.go.kr/"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 과기부 게시판 리스트의 제목 부분 탐색
            items = soup.select('div.lst_b li')
            
            for item in items[:5]: # 최신 자료 5개만
                title_el = item.select_one('p.tit')
                if title_el:
                    title = title_el.get_text(strip=True)
                    # 상세페이지 링크 추출
                    link_el = item.select_one('a')
                    href = link_el['href'] if link_el else ""
                    full_link = "https://www.msit.go.kr" + href if href.startswith('/') else url
                    
                    msit_list.append({
                        "카테고리": "정부(과기부)",
                        "기사제목": title,
                        "발행일": "최근",
                        "링크": full_link
                    })
    except Exception as e:
        print(f"⚠️ 과기부 검색 수집 중 오류: {e}")
    return msit_list

# --- 메인 실행 ---
collection_date = datetime.now().strftime("%Y-%m-%d")
all_data = get_naver_news() + get_msit_search_results()

if all_data:
    df = pd.DataFrame(all_data)
    df.insert(0, "수집일", collection_date)
    df.to_excel("news_list.xlsx", index=False)
    print(f"✅ 수집 완료! (총 {len(all_data)}건 / 과기부 AI 소식 {len([d for d in all_data if d['카테고리'] == '정부(과기부)'])}건)")
else:
    print("❌ 수집된 데이터가 없습니다.")
