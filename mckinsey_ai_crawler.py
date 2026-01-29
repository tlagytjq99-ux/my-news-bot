import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
from googletrans import Translator

def main():
    # 🎯 타겟: 맥킨지 AI & 테크 인사이트
    target_url = "https://www.mckinsey.com/capabilities/quantumblack/our-insights"
    file_name = 'mckinsey_ai_report.csv'
    translator = Translator()
    
    print(f"📡 [McKinsey] AI 리포트 수집 및 번역 시작...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 맥킨지 리포트 제목과 링크 추출
        # 사이트 구조에 맞춰 제목이 포함된 태그들을 훑습니다.
        articles = soup.find_all(['h3', 'h4'], limit=15)
        
        new_data = []
        count = 0

        for item in articles:
            title_en = item.get_text().strip()
            # 주변에 링크(a tag)가 있는지 탐색
            link_tag = item.find_parent('a') or item.find('a') or item.find_previous('a')
            
            if len(title_en) > 20 and link_tag:
                href = link_tag.get('href', '')
                full_url = f"https://www.mckinsey.com{href}" if href.startswith('/') else href
                
                # 💡 영어 -> 한국어 번역
                try:
                    translated = translator.translate(title_en, src='en', dest='ko')
                    title_ko = translated.text
                except:
                    title_ko = title_en

                print(f"   ✅ 수집 완료: {title_ko[:30]}...")
                
                new_data.append({
                    "기관": "McKinsey",
                    "발행일": datetime.now().strftime("%Y-%m-%d"),
                    "제목": title_ko,
                    "원문": title_en,
                    "링크": full_url
                })
                count += 1
                if count >= 10: break

        # 💾 CSV 저장
        if new_data:
            file_exists = os.path.exists(file_name)
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크"])
                writer.writeheader()
                writer.writerows(new_data)
            print(f"🎉 성공! 총 {len(new_data)}건의 리포트를 저장했습니다.")
        else:
            print("❌ 데이터를 찾지 못했습니다. 사이트 구조를 다시 확인해야 합니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    main()
