import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 쿼리 설정: 2025년 전체 문서 대상
    query = 'site:whitehouse.gov after:2025-01-01'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    # 2. 사진 속 46개 카테고리 및 키워드 데이터베이스화
    category_db = {
        "1. 5G/6G Network": ["5G standardization", "Open RAN", "Terahertz communication", "Satellite-5G integration", "Network slicing"],
        "2. Cloud Computing": ["Cloud 3.0", "Multi-cloud", "Sovereign cloud", "Serverless architecture", "Cloud native AI"],
        "3. IoT": ["Industrial IoT", "Matter protocol", "Edge AI sensors", "Digital twins", "IoT security"],
        "4. AI": ["Agentic AI", "Multiagent systems", "Domain-specific LLM", "AI ethics & governance", "On-device AI"],
        "5. Big Data": ["Data mesh", "Vector database", "Real-time analytics", "Data fabric", "Privacy computing"],
        "6. Blockchain": ["Web3 infrastructure", "Asset tokenization", "Zero-knowledge proofs", "CBDC", "Layer 2 scaling"],
        "7. Robotics": ["Humanoid robots", "Physical AI", "Collaborative robots", "Robot-as-a-Service", "Autonomous mobile robots"],
        "8. Connect Car": ["V2X communication", "SDV", "In-vehicle infotainment", "Level 4 autonomy", "EV infrastructure"],
        "9. XR/AR/VR": ["Spatial computing", "Mixed Reality", "Metaverse enterprise", "Haptic feedback", "Lightweight AR glasses"],
        "10. Healthcare": ["Digital therapeutics", "AI diagnostics", "Telemedicine platforms", "Genomic data", "Wearable health tech"],
        "11. 3D Printing": ["Additive manufacturing", "Bioprinting", "Metal 3D printing", "4D printing materials", "On-demand parts"],
        "12. Software": ["Low-code/No-code", "DevOps automation", "Microservices", "SaaS market trends", "Open source security"],
        "13. Application": ["Super-apps", "Progressive Web Apps", "UX/UI design trends", "Mobile app security", "Cross-platform dev"],
        "14. IT Service": ["DX consulting", "Managed services", "IT outsourcing", "Infrastructure management", "Cybersecurity services"],
        "15. Hardware": ["Next-gen semiconductors", "GPU clusters", "Quantum processors", "Sustainable electronics", "Edge computing hardware"],
        "16. Mobile Device": ["Foldable smartphones", "Wearable tech", "Mobile SoC benchmarks", "5G ready devices", "Battery innovation"],
        "17. Mobile Wireless": ["Wi-Fi 7", "Private 5G", "Spectrum allocation", "LPWAN", "Satellite-to-mobile"],
        "18. Broadband/IPTV": ["FTTH", "10G broadband", "IPTV streaming", "Next-gen broadcasting", "Content delivery network"],
        "19. Telecom Equipment": ["Core network gear", "5G base stations", "Fiber optic cables", "NFV", "Telecom supply chain"],
        "20. Telecom SVCs": ["B2B telecom", "MVNO market", "Data roaming", "5G subscription", "Service bundling"],
        "21. Regulation": ["AI Act compliance", "Data privacy laws", "Tech antitrust", "Platform accountability", "Digital services act"],
        "22. Publication/e-book": ["Digital publishing", "Audiobook market", "Subscription models", "Self-publishing platforms", "DRM technology"],
        "23. Comic/Webtoon": ["Webtoon monetization", "Transmedia IP", "AI-assisted creation", "Webtoon globalization", "Digital comic platforms"],
        "24. Music": ["Music streaming", "AI-generated music", "High-res audio", "Digital royalties", "Live streaming concerts"],
        "25. Game": ["Cloud gaming", "Unreal Engine 5", "eSports industry", "Mobile gaming revenue", "AAA game development"],
        "26. Movie/Animation": ["Virtual production", "AI in animation", "Digital distribution", "CGI technology", "Streaming box office"],
        "27. TV/Radio": ["Connected TV", "Podcasting trends", "Digital radio", "FAST channels", "Broadcast technology"],
        "28. Advertising": ["Programmatic ads", "Retail media networks", "Privacy-first ads", "AdTech trends", "Social media marketing"],
        "29. E-Learning": ["EdTech platforms", "Gamified learning", "LMS technology", "Online certification", "Virtual classrooms"],
        "30. Content Platform": ["Creator economy", "User-generated content", "Short-form video", "Content moderation AI", "Algorithm trends"],
        "31. Immersive Content": ["360-degree video", "Spatial audio", "Interactive stories", "Holographic displays", "Immersive marketing"],
        "32. OTT/Streaming SVCs": ["SVOD vs AVOD", "Original content", "Churn rate analysis", "Multi-device streaming", "Global expansion"],
        "33. Copyright": ["IP protection", "Copyright in AI", "Digital watermarking", "Piracy tracking", "Fair use doctrine"],
        "34. Automotive/Aviation": ["Electric Vehicles", "Urban Air Mobility", "eVTOL technology", "Connected aircraft", "Hydrogen fuel cells"],
        "35. Logistics/Shipping": ["Smart warehousing", "Last-mile delivery", "Supply chain visibility", "Autonomous trucking", "Logistics automation"],
        "36. Chemicals/Gas": ["Specialty chemicals", "Green hydrogen", "Carbon capture", "Digital oilfield", "Supply chain resilience"],
        "37. Energy/Utility": ["Smart grid", "Renewable energy", "Energy storage", "Virtual power plants", "Green energy IT"],
        "38. Metals": ["Rare earth elements", "Green steel", "Recycling technology", "Mining automation", "Battery materials"],
        "39. Construction/Defense": ["BIM", "Smart construction", "Military AI", "Unmanned systems", "Defense tech trends"],
        "40. Government": ["GovTech", "Smart city", "Digital ID", "E-government", "Public sector AI"],
        "41. Machines": ["Industrial automation", "Machine vision", "Predictive maintenance", "CNC technology", "Smart tools"],
        "42. Manufacturing": ["Industry 4.0", "Digital twins", "Smart factories", "MES", "Flexible manufacturing"],
        "43. Wood, Plastics & Textiles": ["Sustainable materials", "Smart textiles", "Recycled plastics", "Engineered wood", "Manufacturing tech"],
        "44. Pharmacy": ["Drug discovery", "Biopharmaceuticals", "Clinical trial tech", "Pharmacy automation", "Personalized medicine"],
        "45. Food": ["FoodTech", "Alternative proteins", "Vertical farming", "Food safety tracking", "Precision agriculture"],
        "46. Education": ["STEM education", "Adaptive learning", "Higher ed trends", "Skill-based learning", "EdTech policy"]
    }

    print(f"📡 2025년 백악관 정책 분류 스캔 시작... (유형: 46개)")

    try:
        feed = feedparser.parse(rss_url)
        results = []

        for entry in feed.entries:
            try:
                pub_date = datetime(*entry.published_parsed[:3])
                if pub_date.year == 2025:
                    title = entry.title.split(' - ')[0].strip()
                    
                    matched_categories = []
                    matched_keywords = []

                    # 사진 기반 데이터베이스 매칭
                    for cat, kws in category_db.items():
                        for kw in kws:
                            if kw.lower() in title.lower():
                                matched_categories.append(cat)
                                matched_keywords.append(kw)
                    
                    # 2025년 문서라면 데이터 보존 (유형이 없으면 General Policy)
                    try:
                        decoded = gnewsdecoder(entry.link)
                        actual_url = decoded.get('decoded_url', entry.link)
                    except:
                        actual_url = entry.link

                    results.append({
                        "발행일": pub_date.strftime('%Y-%m-%d'),
                        "유형(Category)": ", ".join(set(matched_categories)) if matched_categories else "General Policy",
                        "매칭키워드": ", ".join(set(matched_keywords)) if matched_keywords else "N/A",
                        "제목": title,
                        "원문링크": actual_url
                    })
                time.sleep(0.05)
            except: continue

        # 3. CSV 저장
        file_name = 'whitehouse_2025_tech_report.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "유형(Category)", "매칭키워드", "제목", "원문링크"])
            writer.writeheader()
            if results:
                results.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(results)
                print(f"✅ 완료: 총 {len(results)}건의 데이터를 46개 카테고리로 분류했습니다.")
            else:
                print("⚠️ 매칭 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
