import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 쿼리 밸런스 조정: 
    # PDF뿐만 아니라 일반 'Priorities'나 'Fact Sheet'도 걸리게 범위를 살짝 넓혔습니다.
    query = 'site:whitehouse.gov (AI OR "Artificial Intelligence") -intitle:briefing -intitle:press -Cuba -Wildfire'
    
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'whitehouse_ai_policy.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"🇺🇸 백악관 AI 종합 모니터링 시작 (PDF 및 웹페이지)...")
    final_data = []

    try:
        feed = feedparser.parse(rss_url)
        # 좀 더 폭넓게 검토하기 위해 상위 20개를 살핍니다.
        entries = feed.entries[:20]
        
        for entry in entries:
            title_en = entry.title.split(' - ')[0]
            
            # AI 관련성 재검증
            if not any(kw in title_en.upper() for kw in ['AI', 'ARTIFICIAL', 'INTELLIGENCE']):
                continue

            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # PDF 판별
            is_pdf = "YES" if actual_link.lower().endswith('.pdf') or ".pdf?" in actual_link.lower() else "NO"
            
            # 우선순위 점수 (PDF에 가산점을 주어 상단 배치 유도)
            priority_score = 10 if is_pdf == "YES" else 5
            
            # 날짜 및 번역
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date
            try:
                title_ko = translator.translate(title_en.strip(), dest='ko').text
            except:
                title_ko = title_en

            final_data.append({
                "기관": "WhiteHouse",
                "발행일": pub_date,
                "제목": f"{'[PDF] ' if is_pdf == 'YES' else ''}{title_ko}",
                "원문": title_en,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "수집일": collected_date,
                "score": priority_score # 정렬용 임시 필드
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 1. 발행일순 정렬 -> 2. PDF 우선 정렬
    final_data.sort(key=lambda x: (x['발행일'], x['score']), reverse=True)

    # 💾 결과 저장 (임시 필드 score 제외)
    fieldnames = ["기관", "발행일", "제목", "원문", "PDF여부", "링크", "수집일"]
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(final_data)
        print(f"✅ 수집 완료! 총 {len(final_data)}건의 정책 문서 확보.")

if __name__ == "__main__":
    main()
