import os
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

# 1. 네이버 API 인증 정보 (GitHub Secrets)
client_id = os.environ.get('NAVER_CLIENT_ID')
client_secret = os.environ.get('NAVER_CLIENT_SECRET')

def classify_category(title):
    """뉴스 제목에 따른 카테고리 분류"""
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
    """네이버 뉴스 API 수집 (각 카테고리별 2개씩 총 8개)"""
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
                    news_list.append({
                        "카테고리": cat, 
                        "기사제목": title, 
                        "발행일": item['pubDate'][:16], 
                        "링크": item['link']
                    })
                    counts[cat] += 1
    except: pass
    return news_list

def get_msit_via_google():
    """구글 RSS를 통한 과기부 보도자료 수집 (메뉴명 필터링 포함)"""
    msit_list = []
    # 검색 쿼리: 과기부 사이트 내에서 'AI' 또는 '인공지능' 제목 검색
    rss_url = "https://news.google.com/rss/search?q=site:msit.go.kr+intitle:AI+OR+intitle:인공지능&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        res = requests.get(rss_url, timeout=15)
        # lxml 설치 유무와 상관없이 작동하도록 html.parser 사용
        soup = BeautifulSoup(res.text, 'html.parser') 
        items = soup.find_all('item')
        
        count = 0
        for item in items:
            title_tag = item.find('title')
            link_tag = item.find('link')
            date_tag = item.find('pubdate')
            
            if title_tag and link_tag:
                full_title = title_tag.get_text().split(' - ')[0]
                
                # [중요] 불필요한 사이트 메뉴명 걸러내기
                trash_keywords = ["직원검색", "게시판", "기관소개", "소속유관기관", "인쇄", "과학기술정보통신부", "공지사항"]
                # 제목이 너무 짧거나 메뉴 키워드가 포함되면 제외
                if any(k == full_title.strip() for k in trash_keywords) or len(full_title) < 12:
                    continue

                link = link_tag.get_text()
                # 날짜 형식 정리
                pub_date = date_tag.get_text()[:16] if date_tag else "최근"
                
                msit_list.append({
                    "카테고리": "정부(과기부)",
                    "기사제목": full_title,
                    "발행일": pub_date,
                    "링크": link
                })
                count += 1
                if count >= 5: break # 최신 정책 5개까지만
    except Exception as e:
        print(f"⚠️ 과기부 수집 중 참고: {e}")
    return msit_list

# --- 메인 실행부 ---
if __name__ == "__main__":
    collection_date = datetime.now().strftime("%Y-%m-%d")
    
    # 두 데이터 합치기
    naver_data = get_naver_news()
    msit_data = get_msit_via_google()
    all_data = naver_data + msit_data

    if all_data:
        df = pd.DataFrame(all_data)
        # 수집일 컬럼을 맨 앞에 추가
        df.insert(0, "수집일", collection_date)
        
        # 엑셀 파일로 저장
        df.to_excel("news_list.xlsx", index=False)
        
        msit_count = len(msit_data)
        print(f"✅ 수집 완료! (네이버: {len(naver_data)}건, 과기부: {msit_count}건)")
    else:
        print("❌ 수집된 데이터가 없어 파일을 생성하지 않았습니다.")
