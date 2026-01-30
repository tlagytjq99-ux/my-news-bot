import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 국내 핵심 정책 기관 리스트 (site: 연산자로 공식 도메인만 타겟팅)
    target_sources = {
        "과기정통부": 'site:msit.go.kr (인공지능 OR AI)',
        "NIA(지능정보사회진흥원)": 'site:nia.or.kr (인공지능 OR AI)',
        "NIPA(정보통신산업진흥원)": 'site:nipa.kr (인공지능 OR AI)',
        "SPRI(소프트웨어정책연구소)": 'site:spri.kr (인공지능 OR AI)',
        "ETRI(전자통신연구원)": 'site:etri.re.kr (인공지능 OR AI)',
        "개인정보보호위원회": 'site:pipc.go.kr (인공지능 OR AI)'
    }

    file_name = 'korea_ai_policy_report.csv'
    collected_date = datetime.now().strftime("%Y-%m-%d")
    final_data = []

    print(f"🇰🇷 국내 AI 정책 데이터 수집 시작...")

    for agency, query in target_sources.items():
        print(f"🔍 {agency} 분석 중...")
        
        # 한국어(ko) 및 한국 지역(KR) 설정
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        try:
            feed = feedparser.parse(rss_url)
            # 기관별 최신 5~7건 추출
            entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)[:7]
            
            for entry in entries:
                title = entry.title.split(' - ')[0]
                
                # 1. 구글 암호 링크 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except:
                    actual_link = entry.link

                # 2. PDF 여부 판별 (파일 확장자 체크)
                is_pdf = "YES" if actual_link.lower().endswith('.pdf') or ".pdf?" in actual_link.lower() else "NO"
                
                # 3. 날짜 및 제목 구성
                pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date
                display_title = f"[PDF] {title}" if is_pdf == "YES" else title

                final_data.append({
                    "기관": agency,
                    "발행일": pub_date,
                    "제목": display_title,
                    "원문제목": title,
                    "PDF여부": is_pdf,
                    "링크": actual_link,
                    "수집일": collected_date
                })

        except Exception as e:
            print(f"❌ {agency} 수집 중 오류: {e}")

    # 최신 날짜순 정렬 후 CSV 저장 (utf-8-sig로 한글 깨짐 방지)
    final_data.sort(key=lambda x: x['발행일'], reverse=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["기관", "발행일", "제목", "원문제목", "PDF여부", "링크", "수집일"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)

    print(f"✅ 수집 완료! {len(final_data)}건 저장됨.")

if __name__ == "__main__":
    main()
