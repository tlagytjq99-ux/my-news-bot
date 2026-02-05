import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 백악관 행정명령 섹션 2025년 정밀 타겟팅
    target_site = "whitehouse.gov/presidential-actions/executive-orders/"
    query = f"site:{target_site} after:2025-01-01"
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    # 2. 사진 속 46개 카테고리 및 세부 키워드 전수 이식
    category_db = {
        "1. 5G/6G Network": ["5G", "6G", "Open RAN", "Terahertz", "Network slicing"],
        "2. Cloud Computing": ["Cloud 3.0", "Multi-cloud", "Sovereign cloud", "Serverless", "Cloud native"],
        "3. IoT": ["Industrial IoT", "Matter protocol", "Edge AI", "Digital twin", "IoT security"],
        "4. AI": ["Agentic AI", "Multiagent", "LLM", "AI ethics", "On-device AI", "Artificial Intelligence"],
        "5. Big Data": ["Data mesh", "Vector database", "Real-time analytics", "Data fabric", "Privacy computing"],
        "6. Blockchain": ["Web3", "Asset tokenization", "RWA", "Zero-knowledge proofs", "CBDC", "Layer 2"],
        "7. Robotics": ["Humanoid", "Physical AI", "Collaborative robot", "Robot-as-a-Service", "Autonomous mobile"],
        "8. Connect Car": ["V2X", "SDV", "In-vehicle infotainment", "Level 4 autonomy", "EV infrastructure"],
        "9. XR/AR/VR": ["Spatial computing", "Mixed Reality", "Metaverse", "Haptic feedback", "AR glasses"],
        "10. Healthcare": ["Digital therapeutics", "AI diagnostics", "Telemedicine", "Genomic data", "Wearable health"],
        "11. 3D Printing": ["Additive manufacturing", "Bioprinting", "Metal 3D printing", "4D printing"],
        "12. Software": ["Low-code", "No-code", "DevOps", "Microservices", "SaaS", "Open source"],
        "13. Application": ["Super-apps", "PWA", "UX/UI", "Mobile app security"],
        "14. IT Service": ["DX consulting", "Managed services", "IT outsourcing", "Infrastructure management"],
        "15. Hardware": ["Semiconductor", "GPU", "HBM", "Quantum processor", "Sustainable electronics"],
        "16. Mobile Device": ["Foldable", "Wearable", "SoC", "Battery innovation"],
        "17. Mobile Wireless": ["Wi-Fi 7", "Private 5G", "Spectrum", "LPWAN"],
        "18. Broadband/IPTV": ["FTTH", "10G broadband", "IPTV", "CDN"],
        "19. Telecom Equipment": ["Core network", "Base station", "Fiber optic", "NFV"],
        "20. Telecom SVCs": ["B2B telecom", "MVNO", "Roaming", "5G subscription"],
        "21. Regulation": ["AI Act", "Data privacy", "Antitrust", "Accountability"],
        "22. Publication/e-book": ["Digital publishing", "Audiobook", "DRM"],
        "23. Comic/Webtoon": ["Webtoon", "Transmedia", "IP creation"],
        "24. Music": ["Streaming", "AI music", "Royalties"],
        "25. Game": ["Cloud gaming", "Unreal Engine", "eSports", "AAA game"],
        "26. Movie/Animation": ["Virtual production", "CGI", "Distribution"],
        "27. TV/Radio": ["Connected TV", "Podcast", "Digital radio", "FAST"],
        "28. Advertising": ["Programmatic", "Retail media", "AdTech"],
        "29. E-Learning": ["EdTech", "LMS", "Virtual classroom"],
        "30. Content Platform": ["Creator economy", "UGC", "Short-form", "Algorithm"],
        "31. Immersive Content": ["360-degree", "Spatial audio", "Holographic"],
        "32. OTT/Streaming SVCs": ["SVOD", "AVOD", "Churn rate"],
        "33. Copyright": ["IP protection", "Watermarking", "Fair use"],
        "34. Automotive/Aviation": ["Electric Vehicle", "UAM", "eVTOL", "Hydrogen fuel"],
        "35. Logistics/Shipping": ["Smart warehouse", "Last-mile", "Autonomous trucking"],
        "36. Chemicals/Gas": ["Specialty chemicals", "Green hydrogen", "Carbon capture"],
        "37. Energy/Utility": ["Smart grid", "Renewable", "Energy storage", "SMR", "Nuclear"],
        "38. Metals": ["Rare earth", "Green steel", "Mining automation"],
        "39. Construction/Defense": ["BIM", "Military AI", "UAV", "Drone", "Defense tech"],
        "40. Government": ["GovTech", "Smart city", "Digital ID", "E-government"],
        "41. Machines": ["Industrial automation", "Machine vision", "Predictive maintenance"],
        "42. Manufacturing": ["Industry 4.0", "Digital twins", "Smart factory", "MES"],
        "43. Wood, Plastics & Textiles": ["Sustainable materials", "Smart textiles", "Recycled plastics"],
        "44. Pharmacy": ["Drug discovery", "Biopharmaceutical", "Clinical trial"],
        "45. Food": ["FoodTech", "Alternative protein", "Vertical farming"],
        "46. Education": ["STEM", "Adaptive learning", "Skill-based"]
    }

    print(f"📡 백악관 행정명령 섹션 정밀 분석 시작...")

    try:
        feed = feedparser.parse(rss_url)
        # 데이터가 적으면 상위 섹션까지 확장
        if len(feed.entries) < 3:
            print("💡 특정 섹션 데이터 부족으로 Presidential Actions 전체로 확장합니다.")
            query = "site:whitehouse.gov/presidential-actions after:2025-01-01"
            rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(rss_url)

        results = []
        for entry in feed.entries:
            try:
                title = entry.title.split(' - ')[0].strip()
                
                # 유형 분류 로직
                matched_cats = []
                for cat, kws in category_db.items():
                    if any(kw.lower() in title.lower() for kw in kws):
                        matched_cats.append(cat)
                
                # 링크 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_url = decoded.get('decoded_url', entry.link)
                except:
                    actual_url = entry.link

                results.append({
                    "발행일": entry.published[:16] if 'published' in entry else "2025",
                    "유형(Category)": ", ".join(matched_cats) if matched_cats else "General Tech Policy",
                    "제목": title,
                    "원문링크": actual_url
                })
                time.sleep(0.1)
            except: continue

        # CSV 저장
        file_name = 'whitehouse_eo_tech_2025.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "유형(Category)", "제목", "원문링크"])
            writer.writeheader()
            writer.writerows(results)
            print(f"✅ 성공: 총 {len(results)}건의 행정명령 데이터를 분류 완료했습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
