import requests
from bs4 import BeautifulSoup
import csv
import os
import time  # 재시도를 위한 시간 지연용
from datetime import datetime
from googletrans import Translator

def main():
    target_url = "https://www.mckinsey.com/capabilities/quantumblack/our-insights"
    file_name = 'mckinsey_ai_report.csv'
    translator = Translator()
    
    print(f"📡 [McKinsey] AI 리포트 수집 시작 (인내심 모드 가동)...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    # 💡 최대 3번까지 다시 시도합니다.
    for attempt in range(3):
        try:
            # 💡 timeout을 60초로 넉넉하게 늘렸습니다.
            response = requests.get(target_url, headers=headers, timeout=60)
            response.raise_for_status() # 연결 오류 확인
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all(['h3', 'h4'], limit=20)
            
            new_data = []
            for item in articles:
                title_en = item.get_text().strip()
                link_tag = item.find_parent('a') or item.find('a') or item.find_previous('a')
                
                if len(title_en) > 20 and link_tag:
                    href = link_tag.get('href', '')
                    full_url = f"https://www.mckinsey.com{href}" if href.startswith('/') else href
                    
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
                    if len(new_data) >= 10: break

            if new_data:
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["기관", "발행일", "제목", "원문", "링크"])
                    writer.writeheader()
                    writer.writerows(new_data)
                print(f"🎉 드디어 성공! {len(new_data)}건 저장 완료.")
                return # 성공했으니 함수 종료

        except Exception as e:
            print(f"⚠️ {attempt+1}번째 시도 실패: {e}")
            if attempt < 2:
                print("   5초 후 다시 시도합니다...")
                time.sleep(5)
            else:
                print("❌ 모든 시도가 실패했습니다.")

if __name__ == "__main__":
    main()
