import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 아카이브 페이지를 거르기 위한 키워드 조합 쿼리
    # 'Executive Order on'을 넣어 공식 문서 제목 형식을 강제하고, 
    # 대표님이 주신 기술 키워드들을 결합합니다.
    tech_keywords = "(AI OR Semiconductor OR Energy OR Quantum OR Infrastructure OR Defense OR Efficiency)"
    target_path = "whitehouse.gov/presidential-actions/executive-orders/"
    
    # "Executive Order on"이 제목에 포함된 것만 찾아서 아카이브 페이지 유입 차단
    query = f'site:{target_path} "Executive Order on" {tech_keywords} after:2025-01-01'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    # 2. 사진 속 46개 카테고리 분류 DB
    category_db = {
        "1. 5G/6G Network": ["5G", "6G", "Open RAN", "Terahertz", "Network slicing"],
        "2. Cloud Computing": ["Cloud 3.0", "Multi-cloud", "Sovereign cloud", "Serverless", "Cloud native"],
        "3. IoT": ["Industrial IoT", "Matter protocol", "Edge AI", "Digital twin", "IoT security"],
        "4. AI": ["Agentic AI", "Multiagent", "LLM", "AI ethics", "On-device AI", "Artificial Intelligence"],
        "5. Big Data": ["Data mesh", "Vector database", "Real-time analytics", "Data fabric", "Privacy computing"],
        "6. Blockchain": ["Web3", "Asset tokenization", "RWA", "Zero-knowledge proofs", "CBDC"],
        "7. Robotics": ["Humanoid", "Physical AI", "Collaborative robot", "Robot-as-a-Service", "Autonomous mobile"],
        "8. Connect Car": ["V2X", "SDV", "In-vehicle infotainment", "Level 4 autonomy", "EV infrastructure"],
        "9. XR/AR/VR": ["Spatial computing", "Mixed Reality", "Metaverse", "Haptic feedback", "AR glasses"],
        "10. Healthcare": ["Digital therapeutics", "AI diagnostics", "Telemedicine", "Genomic data", "Wearable health"],
        "11. 3D Printing": ["Additive manufacturing", "Bioprinting", "Metal 3D printing", "4D printing"],
        "12. Software": ["Low-code", "DevOps", "Microservices", "SaaS", "Open source security"],
        "13. Application": ["Super-apps", "Progressive Web Apps", "UX/UI", "Mobile app security"],
        "14. IT Service": ["DX consulting", "Managed services", "IT outsourcing", "Infrastructure management"],
        "15. Hardware": ["Semiconductor", "GPU", "Quantum processor", "Sustainable electronics"],
        "16. Mobile Device": ["Foldable", "Wearable", "SoC", "Battery innovation"],
        "17. Mobile Wireless": ["Wi-Fi 7", "Private 5G", "Spectrum", "LPWAN"],
        "18. Broadband/IPTV": ["FTTH", "10G broadband", "IPTV", "Broadcasting"],
        "19. Telecom Equipment": ["Core network", "Base stations", "Fiber optic", "NFV"],
        "20. Telecom SVCs": ["B2B telecom", "MVNO", "Roaming", "5G subscription"],
        "21. Regulation": ["AI Act", "Data privacy", "Antitrust", "Platform accountability"],
        "22. Publication/e-book": ["Digital publishing", "Audiobook", "DRM"],
        "23. Comic/Webtoon": ["Webtoon", "Transmedia IP", "AI-assisted creation"],
        "24. Music": ["Music streaming", "AI-generated music", "Digital royalties"],
        "25. Game": ["Cloud gaming", "Unreal Engine", "eSports", "Mobile gaming"],
        "26. Movie/Animation": ["Virtual production", "AI in animation", "Digital distribution"],
        "27. TV/Radio": ["Connected TV", "Podcasting", "Digital radio", "FAST channels"],
        "28. Advertising": ["Programmatic ads", "Retail media", "Privacy-first ads"],
        "29. E-Learning": ["EdTech", "Gamified learning", "LMS", "Virtual classroom"],
        "30. Content Platform": ["Creator economy", "UGC", "Short-form video", "Algorithm"],
        "31. Immersive Content": ["360-degree video", "Spatial audio", "Holographic"],
        "32. OTT/Streaming SVCs": ["SVOD", "AVOD", "Churn rate", "Multi-device"],
        "33. Copyright": ["IP protection", "Copyright in AI", "Watermarking"],
        "34. Automotive/Aviation": ["Electric Vehicle", "UAM", "eVTOL", "Hydrogen fuel"],
        "35. Logistics/Shipping": ["Smart warehouse", "Last-mile delivery", "Autonomous trucking"],
        "36. Chemicals/Gas": ["Specialty chemicals", "Green hydrogen", "Carbon capture"],
        "37. Energy/Utility": ["Smart grid", "Renewable energy", "Energy storage", "SMR", "Nuclear"],
        "38. Metals": ["Rare earth", "Green steel", "Recycling", "Mining automation"],
        "39. Construction/Defense": ["BIM", "Military AI", "UAV", "Drone", "Defense tech"],
        "40. Government": ["GovTech", "Smart city", "Digital ID", "E-government", "Public sector AI"],
        "41. Machines": ["Industrial automation", "Machine vision", "Predictive maintenance"],
        "42. Manufacturing": ["Industry 4.0", "Digital twins", "Smart factories", "MES"],
        "43. Wood, Plastics & Textiles": ["Sustainable materials", "Smart textiles", "Recycled plastics"],
        "44. Pharmacy": ["Drug discovery", "Biopharmaceutical", "Clinical trial"],
        "45. Food": ["FoodTech", "Alternative protein", "Vertical farming"],
        "46. Education": ["STEM education", "Adaptive learning", "Skill-based learning"]
    }

    print(f"📡 백악관 개별 행정명령 정밀 스캔 시작 (노이즈 제거 모드)...")

    try:
        feed = feedparser.parse(rss_url)
        results = []

        for entry in feed.entries:
            try:
                title = entry.title.split(' - ')[0].strip()
                
                # 'Archives'나 'Page'가 들어간 목록 페이지는 가차없이 버립니다.
                if any(word in title for word in ["Archives", "Page", "Presidential Actions"]):
                    continue

                # 구글 우회 디코딩
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_url = decoded.get('decoded_url', entry.link)
                except:
                    actual_url = entry.link

                # 카테고리 매칭
                matched_cats = []
                for cat, kws in category_db.items():
                    if any(kw.lower() in title.lower() for kw in kws):
                        matched_cats.append(cat)

                results.append({
                    "발행일": datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d'),
                    "유형(Category)": ", ".join(matched_cats) if matched_cats else "Executive Order",
                    "제목": title,
                    "원문링크": actual_url
                })
                time.sleep(0.1)
            except: continue

        # 3. CSV 저장
        file_name = 'whitehouse_eo_2025_only.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "유형(Category)", "제목", "원문링크"])
            writer.writeheader()
            if results:
                results.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(results)
                print(f"✅ 성공: {len(results)}건의 '진짜' 행정명령 문서를 찾았습니다.")
            else:
                print("⚠️ 개별 문서 인덱싱을 찾지 못했습니다. 쿼리를 더 단순화해 보겠습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
