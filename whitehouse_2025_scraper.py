import feedparser
import csv
import urllib.parse
import requests
from bs4 import BeautifulSoup
from googlenewsdecoder import gnewsdecoder
import time

def get_whitehouse_content(url):
    """백악관 원문 본문을 가져오는 함수"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            content = soup.find('section', class_='body-content')
            return content.get_text(strip=True).lower() if content else ""
    except:
        return ""
    return ""

def main():
    # 1. 사진 속 ICT 유형 및 키워드 데이터베이스 구축
    ICT_DATABASE = {
        "Intelligent Services": ["Artificial Intelligence", "Machine Learning", "AI Education", "AI Governance", "AI Stack"],
        "Data": ["Information Silo", "Data Privacy", "Fraud Detection", "Data Sharing", "Digital Assets"],
        "Network": ["Connectivity", "Cybersecurity", "Spectrum", "Infrastructure", "Comm. Security"],
        "Security": ["National Security", "Threat Mitigation", "Critical Infra", "Cyber Defense", "Risk Assessment"],
        "Cloud": ["Efficiency", "Digital Sovereignty", "Cloud Hosting", "Government IT", "Modernization"],
        "SW/System": ["SW Innovation", "Defense Acquisition", "Interoperability", "Digital Transformation", "Open Source"],
        "Computing": ["High-Performance", "Semiconductor", "Quantum Tech", "Processing Power", "Hardware Security"]
    }

    # 구글 검색용 통합 키워드 생성
    all_keywords = []
    for kws in ICT_DATABASE.values():
        all_keywords.extend(kws)
    search_query_str = " OR ".join([f'"{k}"' for k in all_keywords[:10]]) # 검색 효율을 위해 주요 키워드 조합

    target_site = "whitehouse.gov/presidential-actions/"
    query = f"site:{target_site} {search_query_str} after:2025-01-01 before:2026-01-01"
    rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"

    print(f"📡 사진 기반 2025 ICT 정책 딥 스캔 시작...")

    feed = feedparser.parse(rss_url)
    results = []

    for entry in feed.entries:
        try:
            decoded = gnewsdecoder(entry.link)
            actual_url = decoded.get('decoded_url', entry.link)
            
            # 본문 데이터 확보
            full_text = get_whitehouse_content(actual_url)
            title = entry.title.split(' - ')[0].strip().lower()

            # 사진 속 키워드 매칭 검사
            matched_types = []
            matched_keywords = []

            for ict_type, keywords in ICT_DATABASE.items():
                for kw in keywords:
                    if kw.lower() in title or kw.lower() in full_text:
                        if ict_type not in matched_types:
                            matched_types.append(ict_type)
                        matched_keywords.append(kw)

            if matched_types:
                results.append({
                    "발행일": entry.published if 'published' in entry else "2025",
                    "ICT 유형": ", ".join(matched_types),
                    "매칭 키워드": ", ".join(list(set(matched_keywords))),
                    "제목": entry.title.split(' - ')[0].strip(),
                    "원문링크": actual_url
                })
                print(f"✅ 매칭 발견: [{matched_types[0]}] {entry.title[:30]}")
                time.sleep(1)
        except:
            continue

    # CSV 저장
    file_name = 'whitehouse_ict_2025_report.csv'
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["발행일", "ICT 유형", "매칭 키워드", "제목", "원문링크"])
        writer.writeheader()
        writer.writerows(results)

    print(f"🏁 분석 완료! 파일명: {file_name}")

if __name__ == "__main__":
    main()
