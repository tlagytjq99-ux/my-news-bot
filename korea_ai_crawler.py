import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 쿼리에 2026년과 '보도자료' 키워드 직접 주입
    target_sources = {
        "과기정통부": '과기정통부 "보도자료" 2026 (인공지능 OR AI)',
        "NIA": 'site:nia.or.kr "보도자료" 2026 (인공지능 OR AI)',
        "NIPA": 'site:nipa.kr "보도자료" 2026 (인공지능 OR AI)',
        "SPRI": 'site:spri.kr (인공지능 OR AI) 2026',
        "ETRI": 'site:etri.re.kr "보도자료" 2026 (인공지능 OR AI)'
    }

    exclude_keywords = [
        '맨 뒤로', '직원검색', '카드뉴스', '입찰공고', '게시판 인쇄', '로그인', 
        '홈페이지', '상세보기', '사전정보공표', '누리집입니다', 'Untitled', 
        '보 도 자 료', '국가별 정보', '비공개정보', '검색결과', '목록', '직원 안내'
    ]

    file_name = 'korea_ai_policy_report.csv'
    collected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_data = []

    # 🗓️ 2026년 데이터가 아니면 절대 수집하지 않음
    BASE_DATE = "2026-01-01"

    print(f"🚀 [2026 보도자료 핀포인트] 수집 시작...")

    for agency, query in target_sources.items():
        print(f"📡 {agency} 최신 보도자료 탐색 중...")
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        agency_count = 0
        
        for entry in feed.entries:
            if agency_count >= 2: break 
            
            raw_title = entry.title.split(' - ')[0]
            clean_title = raw_title.split(">")[-1].strip() if ">" in raw_title else raw_title.strip()
            
            if any(key in clean_title for key in exclude_keywords): continue

            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else datetime.now().strftime('%Y-%m-%d')
            
            # 🔥 강력한 필터: 2026년 자료가 아니면 즉시 탈락
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
                "제목": f"[보도자료] {clean_title}" if "보도자료" not in clean_title else clean_title,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "최종수집시간": collected_time
            })
            agency_count += 1

    # 💾 저장
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["기관", "발행일", "제목", "PDF여부", "링크", "최종수집시간"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)

    print(f"✅ 완료! 2026년 최신 보도자료 위주로 {len(final_data)}건 수집되었습니다.")

if __name__ == "__main__":
    main()
