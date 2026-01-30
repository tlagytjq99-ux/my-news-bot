import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 쿼리 수정: 범위를 넓혀서 일반 웹페이지도 수집되도록 합니다.
    # (단, 최소한의 AI 관련성은 유지)
    query = 'site:whitehouse.gov (intitle:"Artificial Intelligence" OR intitle:AI)'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'whitehouse_ai_policy.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"🇺🇸 백악관 AI 종합 수집 시작 (PDF 자동 판별)...")
    final_data = []

    try:
        feed = feedparser.parse(rss_url)
        # 20개 정도 넉넉히 분석하여 웹과 PDF가 섞이게 합니다.
        entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)[:20]
        
        for entry in entries:
            title_en = entry.title.split(' - ')[0]
            if len(title_en.split()) <= 2: continue

            # 1. 링크 해독
            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # 💡 2. PDF 여부 판별 (핵심 로직)
            is_pdf = "YES" if actual_link.lower().endswith('.pdf') or ".pdf?" in actual_link.lower() else "NO"

            # 3. 날짜 및 번역
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date
            try:
                title_ko = translator.translate(title_en.strip(), dest='ko').text
            except:
                title_ko = title_en

            # 💡 4. 제목 옆에 표시 (원하신다면 제목에 [PDF]를 붙일 수도 있고, 컬럼으로만 뺄 수도 있습니다)
            display_title = f"[PDF] {title_ko}" if is_pdf == "YES" else title_ko

            final_data.append({
                "기관": "WhiteHouse",
                "발행일": pub_date,
                "제목": display_title,
                "원문": title_en,
                "PDF여부": is_pdf, # ✅ 새 컬럼
                "링크": actual_link,
                "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장 (컬럼 순서에 'PDF여부' 추가)
    fieldnames = ["기관", "발행일", "제목", "원문", "PDF여부", "링크", "수집일"]
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)
        print(f"✅ 완료! 총 {len(final_data)}건 저장 (PDF 판별 완료).")

if __name__ == "__main__":
    main()
