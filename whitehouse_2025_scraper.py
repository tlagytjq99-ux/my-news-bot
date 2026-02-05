import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 2025년 전체 문서 타겟팅
    query = 'site:whitehouse.gov after:2025-01-01'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    # 2. 사진 기반 카테고리별 키워드 매핑 사전 (핵심 키워드 추출)
    # 키워드가 발견되면 해당 key(유형)를 결과에 출력합니다.
    category_map = {
        "5G/6G Network": ["5G", "6G", "Open RAN", "Terahertz", "Network slicing"],
        "Cloud Computing": ["Cloud 3.0", "Multi-cloud", "Sovereign cloud", "Serverless", "Cloud native"],
        "IoT": ["Industrial IoT", "Matter protocol", "Edge AI", "Digital twin", "IoT security"],
        "AI": ["Agentic AI", "Multiagent", "LLM", "AI ethics", "On-device AI", "Artificial Intelligence"],
        "Big Data": ["Data mesh", "Vector database", "Real-time analytics", "Data fabric", "Privacy computing"],
        "Blockchain": ["Web3", "Tokenization", "RWA", "Zero-knowledge proofs", "CBDC", "Layer 2"],
        "Robotics": ["Humanoid", "Physical AI", "Collaborative robot", "Robot-as-a-Service", "Autonomous mobile"],
        "Connect Car": ["V2X", "SDV", "In-vehicle infotainment", "Level 4 autonomy", "EV infrastructure"],
        "XR/AR/VR": ["Spatial computing", "Mixed Reality", "Metaverse", "Haptic feedback", "Lightweight AR"],
        "Healthcare": ["Digital therapeutics", "AI diagnostics", "Telemedicine", "Genomic data", "Wearable health"],
        "Hardware": ["Next-gen semiconductors", "GPU clusters", "Quantum processors", "Sustainable electronics"],
        "Cybersecurity": ["Zero Trust", "Threat Intelligence", "Post-quantum cryptography", "Cyber defense"],
        "Energy/Sustainability": ["Smart grid", "Renewable energy", "SMR", "Nuclear", "Hydrogen", "Carbon capture"],
        "Fintech": ["Digital payment", "Stablecoin", "DeFi", "Smart contract"],
        "Space/Defense": ["SpaceX", "Lunar", "Military AI", "UAV", "Drone", "Defense tech"]
    }

    print(f"📡 2025년 백악관 정책 매칭 시작... (대상 유형: {len(category_map)}개)")

    try:
        feed = feedparser.parse(rss_url)
        results = []

        for entry in feed.entries:
            try:
                pub_date = datetime(*entry.published_parsed[:3])
                if pub_date.year == 2025:
                    title = entry.title.split(' - ')[0].strip()
                    
                    matched_types = []
                    matched_keywords = []

                    # 유형별 키워드 검사
                    for category, keywords in category_map.items():
                        for kw in keywords:
                            if kw.lower() in title.lower():
                                matched_types.append(category)
                                matched_keywords.append(kw)
                    
                    if matched_types:
                        try:
                            decoded = gnewsdecoder(entry.link)
                            actual_url = decoded.get('decoded_url', entry.link)
                        except:
                            actual_url = entry.link

                        results.append({
                            "발행일": pub_date.strftime('%Y-%m-%d'),
                            "유형(Category)": ", ".join(set(matched_types)),
                            "감지키워드": ", ".join(set(matched_keywords)),
                            "제목": title,
                            "원문링크": actual_url
                        })
                time.sleep(0.05)
            except: continue

        # 3. CSV 저장
        file_name = 'whitehouse_2025_tech_report.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "유형(Category)", "감지키워드", "제목", "원문링크"])
            writer.writeheader()
            if results:
                results.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(results)
                print(f"✅ 완료: 총 {len(results)}건의 정책을 유형별로 분류했습니다.")
            else:
                print("⚠️ 매칭되는 기술 정책이 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
