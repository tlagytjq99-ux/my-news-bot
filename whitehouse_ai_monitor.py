import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 검색 필터를 최소화하여 '모든 AI 관련 페이지'를 수집합니다.
    # 특정 단어(Report 등)를 강제하지 않아야 일반 웹 뉴스도 걸러지지 않습니다.
    query = 'site:whitehouse.gov (AI OR "Artificial Intelligence") -intitle:briefing -intitle:press'
    
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'whitehouse_ai_policy.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"🇺🇸 백악관 AI 종합 수집 시작 (웹페이지 & PDF 통합)...")
    final_data = []

    try:
        feed = feedparser.parse(rss_url)
        # 다양한 형태를 보기 위해 상위 20개를 분석합니다.
        entries = feed.entries[:20]
        
        for entry in entries:
            title_en = entry.title.split(' - ')[0]
            
            # AI 키워드가 제목에 포함되어 있는지 확인
            if not any(kw in title_en.upper() for kw in ['AI', 'ARTIFICIAL', 'INTELLIGENCE']):
                continue

            # 링크 해독
            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # 💡 [핵심] PDF 여부만 판별 (수집을 제한하지 않음)
            is_pdf = "YES" if actual_link.lower().endswith('.pdf') or ".pdf?" in actual_link.lower() else "NO"
            
            # 발행일 및 번역
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date
            try:
                title_ko = translator.translate(title_en.strip(), dest='ko').text
            except:
                title_ko = title_en

            # 💡 제목 옆에 표시를 원하셨으니 제목 앞에만 [PDF]를 붙이고 
            # 일반 페이지(NO)는 깔끔하게 제목만 나갑니다.
            display_title = f"[PDF] {title_ko}" if is_pdf == "YES" else title_ko

            final_data.append({
                "기관": "WhiteHouse",
                "발행일": pub_date,
                "제목": display_title,
                "원문": title_en,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 최신순 정렬
    final_data.sort(key=lambda x: x['발행일'], reverse=True)

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "PDF여부", "링크", "수집일"])
        writer.writeheader()
        writer.writerows(final_data)
        print(f"✅ 완료! 총 {len(final_data)}건의 혼합 문서 저장.")

if __name__ == "__main__":
    main()
