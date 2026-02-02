import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 과기정통부 쿼리를 더 포괄적으로 수정 (site 제한을 조금 완화하거나 검색어 보강)
    target_sources = {
        "과기정통부": '과기정통부 (인공지능 OR AI) "보도자료"', # 'site' 대신 기관명+보도자료 조합으로 뉴스탭 공략
        "NIA": 'site:nia.or.kr (인공지능 OR AI)',
        "NIPA": 'site:nipa.kr (인공지능 OR AI)',
        "SPRI": 'site:spri.kr (인공지능 OR AI)',
        "ETRI": 'site:etri.re.kr (인공지능 OR AI)'
    }

    exclude_keywords = [
        '맨 뒤로', '직원검색', '카드뉴스', '입찰공고', '게시판 인쇄', '로그인', 
        '홈페이지', '상세보기', '사전정보공표', '누리집입니다', 'Untitled', 
        '보 도 자 료', '국가별 정보', '비공개정보', '검색결과', '목록', '직원 안내', '인사', '동정'
    ]

    file_name = 'korea_ai_policy_report.csv'
    collected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_data = []

    print(f"🚀 [보강 버전] 국내 AI 정책 수집 시작...")

    for agency, query in target_sources.items():
        print(f"🔍 {agency} 데이터 탐색 중...")
        encoded_query = urllib.parse.quote(query)
        # 과기정통부는 뉴스 결과가 더 정확하므로 q={query}를 최적화
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        agency_count = 0
        
        for entry in feed.entries:
            if agency_count >= 2: break 
            
            raw_title = entry.title.split(' - ')[0]
            clean_title = raw_title.split(">")[-1].strip() if ">" in raw_title else raw_title.strip()
            
            if any(key in clean_title for key in exclude_keywords): continue
            if len(clean_title) < 5: continue

            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # 과기정통부의 경우 날짜가 없으면 현재 시간으로 일단 수집
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else datetime.now().strftime('%Y-%m-%d')
            
            # 너무 옛날 데이터는 제외 (2025년 이후)
            if pub_date < '2025-01-01': continue

            is_pdf = "YES" if any(x in actual_link.lower() for x in ['.pdf', 'download', 'filedown', 'attach']) else "NO"

            final_data.append({
                "기관": agency,
                "발행일": pub_date,
                "제목": f"[리포트] {clean_title}" if is_pdf == "YES" else clean_title,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "최종수집시간": collected_time
            })
            agency_count += 1

    final_data.sort(key=lambda x: x['발행일'], reverse=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["기관", "발행일", "제목", "PDF여부", "링크", "최종수집시간"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)

    print(f"✅ 보강 완료! 과기정통부 포함 총 {len(final_data)}건 확인.")

if __name__ == "__main__":
    main()
