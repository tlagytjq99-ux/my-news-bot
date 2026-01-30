import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder

def main():
    target_sources = {
        "과기정통부": 'site:msit.go.kr (인공지능 OR AI) -intitle:직원 -intitle:검색',
        "NIA": 'site:nia.or.kr (인공지능 OR AI) -intitle:이동 -intitle:공고',
        "SPRI": 'site:spri.kr (인공지능 OR AI)',
        "개인정보위": 'site:pipc.go.kr (인공지능 OR AI)'
    }

    # 🛑 노이즈 제거를 위한 블랙리스트 키워드
    exclude_keywords = ['맨 뒤로', '직원검색', '카드뉴스', '입찰공고', '게시판 인쇄', '로그인', '홈페이지']

    file_name = 'korea_ai_policy_clean.csv'
    collected_date = datetime.now().strftime("%Y-%m-%d")
    final_data = []

    for agency, query in target_sources.items():
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:15]: # 더 많이 훑고 필터링
            title = entry.title.split(' - ')[0]
            
            # 1. 노이즈 필터링 (블랙리스트 단어가 제목에 있으면 제외)
            if any(key in title for key in exclude_keywords):
                continue
            
            # 2. 너무 짧은 제목 제외 (정상적인 제목은 보통 10자 이상)
            if len(title) < 5:
                continue

            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
            
            # 3. 최신 데이터만 수집 (예: 2025년 이후 데이터만)
            if pub_date < '2025-01-01':
                continue

            is_pdf = "YES" if "Download" in actual_link or actual_link.lower().endswith('.pdf') or "FileDown" in actual_link else "NO"

            final_data.append({
                "기관": agency,
                "발행일": pub_date,
                "제목": f"[리포트] {title}" if is_pdf == "YES" else title,
                "PDF여부": is_pdf,
                "링크": actual_link
            })

    # 저장 로직 (최신순)
    final_data.sort(key=lambda x: x['발행일'], reverse=True)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "PDF여부", "링크"])
        writer.writeheader()
        writer.writerows(final_data)

if __name__ == "__main__":
    main()
