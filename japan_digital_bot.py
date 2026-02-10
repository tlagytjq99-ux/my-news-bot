import requests
import re
import csv

def crawl_digital_agency_proxy():
    file_name = 'Japan_Digital_Policy_2025.csv'
    
    # 디지털청 URL을 구글 번역기 프록시 주소로 변환 (차단 우회용)
    proxy_url = "https://www.digital-go-jp.translate.goog/press?category=1&_x_tr_sl=ja&_x_tr_tl=ko"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    print(f"🚀 [프록시 우회 모드] 구글 서버를 통해 디지털청에 접속합니다...")

    try:
        # 구글 프록시를 통해 HTML 가져오기
        response = requests.get(proxy_url, headers=headers, timeout=30)
        html_content = response.text
        
        # 정규표현식으로 링크와 제목 추출
        # 구글 프록시를 타면 URL 구조가 살짝 변하므로 범용 패턴 사용
        pattern = r'href="([^"]*digital-go-jp\.translate\.goog/press/[^"]*)"[^>]*>(.*?)</a>'
        matches = re.findall(pattern, html_content)

        policy_results = []
        for link, title in matches:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            if len(clean_title) < 10: continue
            
            # 원본 주소로 복원
            original_link = link.split('?')[0].replace('.translate.goog', '').replace('-', '.')
            
            policy_results.append({
                "date": "2025/2026",
                "title": clean_title,
                "link": original_link
            })

        if policy_results:
            unique_data = list({v['link']: v for v in policy_results}.values())
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(unique_data)
            print(f"✅ 드디어 뚫었습니다! {len(unique_data)}건 수집 성공.")
        else:
            print("⚠️ 프록시 우회도 실패했습니다. 최종 수단인 '가상 브라우저'로 넘어가야 합니다.")
            # 빈 파일 생성
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        with open(file_name, 'w', encoding='utf-8-sig') as f:
            f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_digital_agency_proxy()
