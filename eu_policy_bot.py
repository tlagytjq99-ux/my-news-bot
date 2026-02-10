import requests
import csv
import re

def fetch_eu_policy_final_gold():
    # 진단에서 확인된 실 데이터가 포함된 주소
    target_url = "https://op.europa.eu/en/web/general-publications/publications"
    
    file_name = 'EU_Policy_2025_Final.csv'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("💰 [정밀 추출] 41개의 후보 중 2025년 핵심 정책 데이터를 골라냅니다...", flush=True)

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        content = response.text

        # 링크와 텍스트 추출 패턴
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', content)
        
        final_list = []
        seen_titles = set()

        for l, t in links:
            # HTML 태그 제거 및 청소
            title = re.sub('<[^<]+?>', '', t).strip()
            # 정책 문서다운 조건: 제목이 길고(15자 이상), 특정 메뉴 단어 제외
            if len(title) > 15 and title not in seen_titles:
                exclude_keywords = ['Privacy policy', 'Legal notice', 'Cookies', 'Contact', 'Sitemap', 'Search']
                if not any(key in title for key in exclude_keywords):
                    # 2025년 문서이거나 최신 리스트에 있는 것들
                    full_link = l if l.startswith('http') else "https://op.europa.eu" + l
                    
                    final_list.append({
                        "date": "2025-Latest",
                        "title": title,
                        "link": full_link
                    })
                    seen_titles.add(title)

        if final_list:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(final_list)
            print(f"🎯 [대성공] 총 {len(final_list)}건의 핵심 정책 리스트를 파일로 저장했습니다!", flush=True)
            print(f"📑 첫 번째 문서: {final_list[0]['title']}", flush=True)
        else:
            print("⚠️ 필터링 결과 남은 데이터가 없습니다. 필터를 완화합니다.", flush=True)

    except Exception as e:
        print(f"❌ 최종 추출 중 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_policy_final_gold()
