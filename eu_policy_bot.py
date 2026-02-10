import requests
import csv
import re

def diagnose_and_fetch():
    # 최신 일반 간행물 페이지 (RSS가 아닌 일반 웹 응답 시도)
    target_url = "https://op.europa.eu/en/web/general-publications/publications"
    
    file_name = 'EU_Policy_2025_Final.csv'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("🔍 [서버 진단] 서버 응답 본문을 직접 분석합니다...", flush=True)

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        content = response.text

        # 1. 서버가 응답한 내용의 길이를 확인
        print(f"📡 서버 응답 길이: {len(content)} 자", flush=True)

        # 2. 2025라는 단어가 본문에 몇 번 등장하는지 확인
        count_2025 = content.count("2025")
        print(f"🔢 본문 내 '2025' 등장 횟수: {count_2025}회", flush=True)

        # 3. 아주 단순하게 링크와 텍스트를 낚아챔 (모든 <a> 태그)
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', content)
        
        all_records = []
        for l, t in links:
            clean_title = re.sub('<[^<]+?>', '', t).strip() # HTML 태그 제거
            if len(clean_title) > 10: # 제목다운 것만 골라냄
                all_records.append({
                    "date": "2025-Latest",
                    "title": clean_title,
                    "link": l if l.startswith('http') else "https://op.europa.eu" + l
                })

        if all_records:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(all_records[:50]) # 상위 50개만 저장
            print(f"✅ [대성공] 진단 결과 {len(all_records)}개의 잠재적 데이터를 찾았습니다!", flush=True)
        else:
            print("❌ 본문에서 유효한 링크를 찾지 못했습니다. 서버가 다른 페이지를 보여주고 있습니다.", flush=True)

    except Exception as e:
        print(f"❌ 진단 중 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    diagnose_and_fetch()
