import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 '보도자료' 키워드를 빼고, 기관명과 연도 위주로 검색 범위를 다시 넓힙니다.
    target_sources = {
        "과기정통부": '과기정통부 (인공지능 OR AI) 2026',
        "NIA": 'site:nia.or.kr (인공지능 OR AI) 2026',
        "NIPA": 'site:nipa.kr (인공지능 OR AI) 2026',
        "SPRI": 'site:spri.kr (인공지능 OR AI) 2026',
        "ETRI": 'site:etri.re.kr (인공지능 OR AI) 2026'
    }

    exclude_keywords = [
        '맨 뒤로', '직원검색', '카드뉴스', '입찰공고', '게시판 인쇄', '로그인', 
        '홈페이지', '상세보기', '사전정보공표', '누리집입니다', 'Untitled', 
        '국가별 정보', '비공개정보', '검색결과', '목록', '직원 안내'
    ]

    file_name = 'korea_ai_policy_report.csv'
    collected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_data = []

    # 🗓️ 2026년 데이터 필터 (기관별 상황에 따라 2025년 12월부터로 살짝 넓힘)
    # 2026년 초반이라 데이터가 적을 수 있으니 기준을 조금 유연하게 잡았습니다.
    BASE_DATE = "2025-12-15" 

    print(f"🚀 [2026 최신 통합] 데이터 수집 시작...")

    for agency, query in target_sources.items():
        print(f"📡 {agency} 최신 소식 탐색 중...")
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        agency_count = 0
        
        for entry in feed.entries:
            if agency_count >= 2: break 
            
            raw_title = entry.title.split(' - ')[0]
            clean_title = raw_title.split(">")[-1].strip() if ">" in raw_title else raw_title.strip()
            
            # 노이즈 필터링 (보도자료 단어 유무와 상관없이 내용 위주)
            if any(key in clean_title for key in exclude_keywords): continue
            if len(clean_title) < 5: continue

            # 날짜 추출
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else datetime.now().strftime('%Y-%m-%d')
            
            # 지정된 날짜 이전 자료는 과감히 제외
            if pub_date < BASE_DATE: continue

            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            is_pdf = "YES" if any(x in actual_link.lower() for x in ['.pdf', 'download', 'filedown', 'attach']) else "NO"

            final_data.append({
                "기관": agency,
                "발행일": pub_date,
                "제목": clean_title,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "최종수집시간": collected_time
            })
            agency_count += 1

    # 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["기관", "발행일", "제목", "PDF여부", "링크", "최종수집시간"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)

    print(f"✅ 완료! {BASE_DATE} 이후 최신 데이터 총 {len(final_data)}건 수집.")

if __name__ == "__main__":
    main()
