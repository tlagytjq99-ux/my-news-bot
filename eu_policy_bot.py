import requests
import csv
from xml.etree import ElementTree

def fetch_eu_cellar_atom_2025():
    # 1. 더욱 가벼운 Atom 피드 엔드포인트 사용
    url = "http://publications.europa.eu/webapi/notification/ingestion"
    
    # 서버 부담을 줄이기 위해 한 번에 50개씩 끊어서 가져오도록 설정
    params = {
        "startDate": "2025-01-01",
        "type": "CREATE",
        "wemiClasses": "work",
        "pageSize": "50",
        "page": "1"
    }
    
    # 가이드에 따라 Atom 피드 형식 요청
    headers = {
        "Accept": "application/atom+xml",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Intelligence-Bot"
    }

    print(f"📡 Cellar Atom 피드 접속 중... (서버 응답 대기 시간을 120초로 연장합니다)", flush=True)
    
    file_name = 'EU_Policy_2025_Full.csv'
    collected_data = []

    try:
        # [핵심] timeout을 120초로 대폭 늘려 서버 지연에 대비합니다.
        response = requests.get(url, params=params, headers=headers, timeout=120)
        
        if response.status_code == 200:
            # Atom XML 파싱
            root = ElementTree.fromstring(response.content)
            # Atom 네임스페이스 정의
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'notifEntry': 'http://publications.europa.eu/rss/notificationEntry'
            }
            
            entries = root.findall('atom:entry', ns)

            for entry in entries:
                cellar_id_tag = entry.find('notifEntry:cellarId', ns)
                date_tag = entry.find('notifEntry:date', ns)
                title_tag = entry.find('atom:title', ns)
                
                cellar_id = cellar_id_tag.text if cellar_id_tag is not None else "N/A"
                date = date_tag.text[:10] if date_tag is not None else "2025"
                title = title_tag.text if title_tag is not None else "EU Document"
                
                uuid = cellar_id.replace('cellar:', '')
                link = f"https://publications.europa.eu/resource/cellar/{uuid}"

                collected_data.append({
                    "date": date,
                    "title": title,
                    "link": link
                })
            
            print(f"✅ 수집 성공! 2025년 신규 정책 {len(collected_data)}건을 확보했습니다.", flush=True)
        else:
            print(f"❌ 서버 응답 에러: {response.status_code}", flush=True)

    except requests.exceptions.Timeout:
        print("⚠️ EU 서버가 너무 느려 응답 시간을 초과했습니다. 잠시 후 다시 시도됩니다.", flush=True)
    except Exception as e:
        print(f"❌ 기타 오류: {e}", flush=True)

    # 결과 저장 (파일이 있어야 Git Push 에러가 안 납니다)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            writer.writerow({"date": "2025-02-09", "title": "Monitoring Mode: Waiting for Cellar server response", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_cellar_atom_2025()
