import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder

def main():
    target_sources = {
        "과기정통부": 'site:msit.go.kr (인공지능 OR AI)',
        "NIA": 'site:nia.or.kr (인공지능 OR AI)',
        "NIPA": 'site:nipa.kr (인공지능 OR AI)',
        "SPRI": 'site:spri.kr (인공지능 OR AI)',
        "ETRI": 'site:etri.re.kr (인공지능 OR AI)',
        "개인정보위": 'site:pipc.go.kr (인공지능 OR AI)'
    }

    # 🛑 노이즈 및 중복 단어 필터 대폭 보강
    exclude_keywords = [
        '맨 뒤로', '직원검색', '카드뉴스', '입찰공고', '게시판 인쇄', '로그인', 
        '홈페이지', '상세보기', '사전정보공표', '누리집입니다', 'Untitled', 
        '보 도 자 료', '국가별 정보', '비공개정보', '검색결과', '목록', '직원 안내'
    ]

    file_name = 'korea_ai_policy_report.csv'
    # 초 단위 수집시간을 추가하여 GitHub Actions의 강제 업데이트 유도
    collected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_data = []

    print(f"🚀 국내 AI 정책 정밀 수집 및 제목 정제 시작...")

    for agency, query in target_sources.items():
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:25]: # 더 넓은 범위 탐색
            raw_title = entry.title.split(' - ')[0]
            
            # 1. 제목 정제: "HOME > 알림마당 > 핵심제목" 구조에서 마지막 핵심제목만 추출
            if ">" in raw_title:
                clean_title = raw_title.split(">")[-1].strip()
            else:
                clean_title = raw_title.strip()
            
            # 2. 필터링: 블랙리스트 단어 포함 시 제외
            if any(key in clean_title for key in exclude_keywords): continue
            
            # 3. 필터링: 너무 짧거나 무의미한 제목 제외
            if len(clean_title) < 5 or clean_title == "공지사항": continue

            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # 4. 필터링: 2025년 이후 최신 데이터만 유지
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else "2026-01-01"
            if pub_date < '2025-01-01': continue

            # PDF 판별 로직 (국내 기관 URL 특성 반영)
            is_pdf = "NO"
            if any(x in actual_link.lower() for x in ['.pdf', 'download', 'filedown', 'attach']):
                is_pdf = "YES"

            final_data.append({
                "기관": agency,
                "발행일": pub_date,
                "제목": f"[리포트] {clean_title}" if is_pdf == "YES" else clean_title,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "최종수집시간": collected_time
            })

    # 최신 날짜순 정렬
    final_data.sort(key=lambda x: x['발행일'], reverse=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["기관", "발행일", "제목", "PDF여부", "링크", "최종수집시간"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)

    print(f"✅ 정제 완료! 총 {len(final_data)}건 저장.")

if __name__ == "__main__":
    main()
