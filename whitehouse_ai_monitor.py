import feedparser
import csv
import urllib.parse
from datetime import datetime
from googletrans import Translator
from googlenewsdecoder import gnewsdecoder

def main():
    # 🎯 백악관 정밀 타겟팅 쿼리
    # 행정명령(Executive Order), 팩트시트(Fact Sheet), 전략(Strategy) 등 핵심 문서 위주
    query = 'site:whitehouse.gov (intitle:"Artificial Intelligence" OR intitle:AI OR "Executive Order on AI") -intitle:briefing -intitle:press'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    file_name = 'whitehouse_ai_policy.csv'
    translator = Translator()
    collected_date = datetime.now().strftime("%Y-%m-%d")

    print(f"🇺🇸 백악관 AI 핵심 정책 수집 시작...")
    final_data = []

    try:
        feed = feedparser.parse(rss_url)
        # 최신순 정렬 후 상위 10개 분석 (백악관은 중요도가 높으니 10개까지 봅니다)
        entries = sorted(feed.entries, key=lambda x: x.get('published_parsed'), reverse=True)[:10]
        
        for entry in entries:
            title_en = entry.title.split(' - ')[0]
            
            # 1. 너무 짧은 제목(단순 카테고리 등) 제외
            if len(title_en.split()) <= 3:
                continue

            print(f"🔑 링크 해독 및 분석 중: {title_en[:40]}...")
            
            # 2. 암호 해독기로 원본 링크 추출 (성공의 핵심)
            try:
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link

            # 3. 날짜 처리
            pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d') if hasattr(entry, 'published_parsed') else collected_date

            # 4. 한국어 번역
            try:
                title_ko = translator.translate(title_en.strip(), dest='ko').text
            except:
                title_ko = title_en

            final_data.append({
                "기관": "WhiteHouse",
                "발행일": pub_date,
                "제목": title_ko,
                "원문": title_en,
                "링크": actual_link,
                "수집일": collected_date
            })

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 💾 결과 저장 (인코딩: utf-8-sig로 엑셀 한글 깨짐 방지)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크", "수집일"])
        writer.writeheader()
        if final_data:
            writer.writerows(final_data)
            print(f"✅ 완료! 백악관 핵심 정책 {len(final_data)}건 저장 완료.")
        else:
            print("⚠️ 조건에 맞는 최신 정책 문서가 발견되지 않았습니다.")

if __name__ == "__main__":
    main()
