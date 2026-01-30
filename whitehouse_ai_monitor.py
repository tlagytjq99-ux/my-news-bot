import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 쿼리에 filetype:pdf를 명시적으로 넣지는 않되(모든 형태 수집 위해), 
    # 수집 후 PDF 여부를 판별하는 전략을 사용합니다.
    query = 'site:whitehouse.gov (intitle:"Artificial Intelligence" OR intitle:AI OR "Executive Order") -intitle:briefing'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'whitehouse_ai_policy.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"🇺🇸 백악관 AI 정책 및 PDF 문서 분석 시작...")
    final_data = []

    try:
        feed = feedparser.parse(rss_url)
        entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)[:10]
        
        for entry in entries:
            title_en = entry.title.split(' - ')[0]
            if len(title_en.split()) <= 3: continue

            # 💡 [핵심] 링크 해독
            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # 💡 [PDF 판별 로직]
            # 링크가 .pdf로 끝나거나 제목에 PDF가 포함된 경우
            is_pdf = "NO"
            display_prefix = ""
            if actual_link.lower().endswith('.pdf') or ".pdf?" in actual_link.lower() or "[PDF]" in title_en.upper():
                is_pdf = "YES"
                display_prefix = "[PDF] "

            # 날짜 및 번역
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date
            try:
                # 번역 시 PDF 태그는 제외하고 텍스트만 번역
                title_ko = translator.translate(title_en.strip(), dest='ko').text
            except:
                title_ko = title_en

            final_data.append({
                "기관": "WhiteHouse",
                "발행일": pub_date,
                "제목": f"{display_prefix}{title_ko}", # 제목 앞에 [PDF] 표시
                "원문": title_en,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장 (PDF여부 컬럼 추가)
    fieldnames = ["기관", "발행일", "제목", "원문", "PDF여부", "링크", "수집일"]
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)
        print(f"✅ 분석 완료! PDF 포함 {len(final_data)}건 저장.")

if __name__ == "__main__":
    main()
