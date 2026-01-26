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
    title_str = str(title)
    for category, keywords in categories.items():
        if any(keyword in title_str for keyword in keywords):
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

def get_msit_news():
    msit_list = []
    # 보도자료 게시판 URL
    url = "https://www.msit.go.kr/bbs/list.do?sCode=user&mPid=217&mId=113"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # 제목이 들어있는 모든 태그를 더 유연하게 검색
            elements = soup.select('.lst_b p.tit') or soup.select('td.left a') or soup.select('.tit')
            
            # 검색 키워드 확장
            target_keywords = ["AI", "인공지능", "디지털", "데이터", "ICT", "반도체", "전략", "기술"]
            
            count = 0
            for el in elements:
                title = el.get_text().strip()
                # 키워드 중 하나라도 포함되어 있는지 확인
                if any(k in title for k in target_keywords):
                    # 링크 찾기 (부모 태그나 본인 태그에서)
                    link_tag = el if el.name == 'a' else el.find_parent('a') or el.select_one('a')
                    if not link_tag:
                        # p.tit 같은 경우 바로 옆이나 부모 근처에 a태그가 있음
                        link_tag = el.find_previous('a') or el.find_next('a')

                    if link_tag and link_tag.has_attr('href'):
                        href = link_tag['href']
                        full_link = "https://www.msit.go.kr" + href if href.startswith('/') else href
                        msit_list.append({"카테고리": "정부(과기부)", "기사제목": title, "발행일": "최근", "링크": full_link})
                        count += 1
                        if count >= 2: break
    except Exception as e:
        print(f"과기부 상세 오류: {e}")
    return msit_list

# --- 메인 실행 ---
collection_date = datetime.now().strftime("%Y-%m-%d")
all_data = get_naver_news() + get_msit_news()

if all_data:
    df = pd.DataFrame(all_data)
    df.insert(0, "수집일", collection_date)
    df.to_excel("news_list.xlsx", index=False)
    print(f"✅ 수집 완료! 총 {len(all_data)}건 (과기부: {len([d for d in all_data if d['카테고리'] == '정부(과기부)'])}건)")
