import asyncio
import csv
import os
from datetime import datetime
from crawl4ai import AsyncWebCrawler
from googletrans import Translator

async def main():
    target_url = "https://www.cao.go.jp/houdou/houdou.html"
    file_name = 'japan_ai_report.csv'
    translator = Translator()

    print(f"📡 [일본 내각부] Crawl4AI 가동 - 지능형 데이터 추출 시작...")

    async with AsyncWebCrawler() as crawler:
        # 1. 페이지 크롤링 (브라우저 실행 및 마크다운 변환)
        result = await crawler.arun(url=target_url)

        # 2. 결과물(마크다운)에서 링크와 텍스트 추출
        # Crawl4AI가 정리해준 데이터에서 제목이 긴 것들만 추립니다.
        content = result.markdown
        lines = content.split('\n')
        
        new_data = []
        count = 0
        
        for line in lines:
            # 마크다운 링크 패턴 추출: [제목](링크)
            if '[' in line and '](' in line:
                try:
                    title_ja = line.split('[')[1].split(']')[0].strip()
                    link = line.split('(')[1].split(')')[0].strip()
                    
                    # 💡 지능형 필터링: 뉴스 제목처럼 긴 것만
                    if len(title_ja) > 20 and ('.html' in link or '.pdf' in link):
                        # 한국어 번역
                        translated = translator.translate(title_ja, src='ja', dest='ko')
                        title_ko = translated.text
                        
                        # 절대 경로 보정
                        full_url = link if link.startswith('http') else f"https://www.cao.go.jp{link}"

                        print(f"   ✅ 발견 & 번역: {title_ko[:35]}...")
                        new_data.append({
                            "기관": "일본 내각부(CAO)",
                            "발행일": datetime.now().strftime("%Y-%m-%d"),
                            "제목": title_ko,
                            "원문제목": title_ja,
                            "링크": full_url,
                            "수집일": datetime.now().strftime("%Y-%m-%d")
                        })
                        count += 1
                        if count >= 10: break
                except:
                    continue

        # 💾 CSV 저장
        if new_data:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문제목", "링크", "수집일"])
                writer.writeheader()
                writer.writerows(new_data)
            print(f"🎉 성공! Crawl4AI가 {len(new_data)}건을 완벽하게 낚아냈습니다.")
        else:
            print("❌ Crawl4AI로도 데이터를 찾지 못했습니다. URL을 다시 확인해봐야 합니다.")

if __name__ == "__main__":
    asyncio.run(main())
