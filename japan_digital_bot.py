import requests
import re
import csv
import urllib3

# SSL 경고 메시지 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def crawl_digital_agency_final_attempt():
    file_name = 'Japan_Digital_Policy_2025.csv'
    # 원본 URL로 복귀하되, SSL 검증을 끕니다.
    url = "https://www.digital.go.jp/press?category=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ja-JP,ja;q=0.9,ko-KR;q=0.8,ko;q=0.7,en-US;q=0.6,en;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }

    print(f"🚀 [최종 보정 모드] SSL 검증을 우회하여 {url}에 접속합니다...")

    try:
        # verify=False로 SSL 인증서 에러를 강제로 통과합니다.
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        html_content = response.text
        
        # 정규표현식: /press/ 뒤에 영문/숫자/대시가 붙은 모든 링크 추출
        # <a ... href="/press/xxxx"> 제목 </a> 형태 타겟팅
        pattern = r'href="(/press/[^"]+)"[^>]*>(.*?)</a>'
        matches = re.findall(pattern, html_content)

        policy_results = []
        for link, title in matches:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            # 메뉴나 너무 짧은 텍스트 필터링
            if len(clean_title) < 10 or "一覧" in clean_title: continue
            
            policy_results.append({
                "date": "2025/2026",
                "title": clean_title,
                "link": "https://www.digital.go.jp" + link if link.startswith('/') else link
            })

        if policy_results:
            unique_data = list({v['link']: v for v in policy_results}.values())
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(unique_data)
            print(f"✅ 드디어 성공! {len(unique_data)}건의 데이터를 확보했습니다.")
        else:
            print("⚠️ 데이터를 찾지 못했습니다. 사이트 구조가 정적이지 않을 수 있습니다.")
            # 빈 파일 생성
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                f.write("date,title,link\n")

    except Exception as e:
        print(f"❌ 치명적 오류: {e}")
        with open(file_name, 'w', encoding='utf-8-sig') as f:
            f.write("date,title,link\n")

if __name__ == "__main__":
    crawl_digital_agency_final_attempt()
