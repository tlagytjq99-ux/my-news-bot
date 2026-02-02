import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 타겟 기관 최적화 (개인정보위 제외)
    target_sources = {
        "과기정통부": 'site:msit.go.kr (인공지능 OR AI)',
        "NIA": 'site:nia.or.kr (인공지능 OR AI)',
        "NIPA": 'site:nipa.kr (인공지능 OR AI)',
        "SPRI": 'site:spri.kr (인공지능 OR AI)',
        "ETRI": 'site:etri.re.kr (인공지능 OR AI)'
    }

    exclude_keywords = [
        '맨 뒤로', '직원검색', '카드뉴스', '입찰공고', '게시판 인쇄', '로그인', 
        '홈페이지', '상세보기', '사전정보공표', '누리집입니다', 'Untitled', 
        '보 도 자 료', '국가별 정보', '비공개정보', '검색결과', '목록', '직원 안내'
    ]

    file_name = 'korea_ai_policy_report.csv'
    collected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_data = []

    print(f"🚀 국내 AI 정책 정밀 수집 (기관별 2건 제한) 시작...")

    for agency, query in target_sources.items():
        print(f"🔍 {agency} 최신 데이터 필터링 중...")
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        agency_count = 0 # 기관별 카운트 변수
        
        for entry in feed.entries:
            if agency_count >= 2: break # 🚀 기관당 2개 수집 완료 시 다음 기관으로 패스
            
            raw_title = entry.title.split(' - ')[0]
            
            # 제목 정제 (Breadcrumb 제거)
            clean_title = raw_title.split(">")[-1].strip() if ">" in raw_title else raw_title.strip()
            
            # 노이즈 필터링
            if any(key in clean_title for key in exclude_keywords): continue
            if len(clean_title) < 5 or clean_title == "공지사항": continue

            # 링크 해독
            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # 날짜 필터링 (2025년 이후)
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else "2026-01-01"
            if pub_date < '2025-01-01': continue

            # PDF 판별
            is_pdf = "YES" if any(x in actual_link.lower() for x in ['.pdf', 'download', 'filedown', 'attach']) else "NO"

            final_data.append({
                "기관": agency,
                "발행일": pub_date,
                "제목": f"[리포트] {clean_title}" if is_pdf == "YES" else clean_title,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "최종수집시간": collected_time
            })
            
            agency_count += 1 # 성공적으로 추가된 경우에만 카운트 증가

    # 최신 날짜순 정렬
    final_data.sort(key=lambda x: x['발행일'], reverse=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["기관", "발행일", "제목", "PDF여부", "링크", "최종수집시간"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)

    print(f"✅ 정제 완료! 기관별 최대 2건, 총 {len(final_data)}건 저장.")

if __name__ == "__main__":
    main()
