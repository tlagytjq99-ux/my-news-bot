import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 쿼리 고도화: 
    # 1. AI와 함께 'Strategy', 'Report', 'Framework', 'Policy' 같은 단어를 결합
    # 2. 노이즈(Cuba, Wildfire, School Choice 등)를 일으키는 정치 키워드 강제 제외 (-)
    query = 'site:whitehouse.gov (AI OR "Artificial Intelligence") (Report OR Strategy OR Framework OR Policy OR "Executive Order") -Cuba -Wildfire -School -Recovery'
    
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'whitehouse_ai_policy.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"🇺🇸 백악관 AI 정책 리포트 정밀 수집 시작...")
    final_data = []

    try:
        feed = feedparser.parse(rss_url)
        # 중요도가 높은 순으로 15개를 먼저 살핍니다.
        entries = feed.entries[:15]
        
        for entry in entries:
            title_en = entry.title.split(' - ')[0]
            
            # 💡 [필터 추가] 제목에 AI 관련 핵심어가 없으면 과감히 패스
            ai_keywords = ['AI', 'ARTIFICIAL', 'INTELLIGENCE', 'ALGORITHM', 'TECHNOLOGY']
            if not any(kw in title_en.upper() for kw in ai_keywords):
                continue

            # 링크 해독
            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # 💡 [PDF 판별]
            is_pdf = "YES" if actual_link.lower().endswith('.pdf') or ".pdf?" in actual_link.lower() else "NO"
            display_prefix = "[PDF] " if is_pdf == "YES" else ""

            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date

            try:
                title_ko = translator.translate(title_en.strip(), dest='ko').text
            except:
                title_ko = title_en

            final_data.append({
                "기관": "WhiteHouse",
                "발행일": pub_date,
                "제목": f"{display_prefix}{title_ko}",
                "원문": title_en,
                "PDF여부": is_pdf,
                "링크": actual_link,
                "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 최신순 정렬 후 저장
    final_data.sort(key=lambda x: x['발행일'], reverse=True)

    fieldnames = ["기관", "발행일", "제목", "원문", "PDF여부", "링크", "수집일"]
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)
        print(f"✅ 정밀 수집 완료! {len(final_data)}건의 AI 관련 정책 확보.")

if __name__ == "__main__":
    main()
