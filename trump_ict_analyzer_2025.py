import requests
import csv
import time

def main():
    # 
    
    # 1. 46개 카테고리 데이터 (기존 동일)
    ICT_DATABASE = {
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
        "42. Manufacturing": ["Industry 4.0", "Digital twins", "Smart factories"],
        "43. Wood, Plastics & Textiles": ["Sustainable materials", "Smart textiles", "Recycled plastics"],
        "44. Pharmacy": ["Drug discovery", "Biopharmaceutical", "Clinical trial"],
        "45. Food": ["FoodTech", "Alternative protein", "Vertical farming"],
        "46. Education": ["STEM education", "Adaptive learning", "Skill-based learning"]
        # ... (나머지 카테고리 포함)
    }

    results = []
    page = 1
    
    print("🚀 2025년 전체 데이터 정밀 스캔 시작 (모든 페이지 수집)...")

    while True:
        api_url = "https://www.federalregister.gov/api/v1/documents.json"
        params = {
            "conditions[publication_date][year]": "2025",
            "conditions[presidential_document_type][]": ["executive_order", "determination", "memorandum", "proclamation"],
            "conditions[president]": "donald-trump",
            "order": "newest",
            "per_page": 100,
            "page": page,  # 페이지 번호 추가
            "fields[]": ["title", "publication_date", "html_url", "raw_text_url", "type"]
        }

        response = requests.get(api_url, params=params)
        if response.status_code != 200: break
        
        data = response.json()
        docs = data.get('results', [])
        
        if not docs: break # 더 이상 가져올 데이터가 없으면 중단

        print(f"📄 {page}페이지 분석 중... ({len(docs)}건)")

        for doc in docs:
            title = doc.get('title', '')
            raw_url = doc.get('raw_text_url')
            full_text = ""
            
            # 본문 텍스트 딥 스캔
            if raw_url:
                try:
                    full_text = requests.get(raw_url).text.lower()
                except: pass

            matched_cats = []
            found_kws = []
            for cat, kws in ICT_DATABASE.items():
                for kw in kws:
                    if kw.lower() in title.lower() or kw.lower() in full_text:
                        if cat not in matched_cats: matched_cats.append(cat)
                        found_kws.append(kw)

            results.append({
                "Date": doc.get('publication_date'),
                "Type": doc.get('type'),
                "ICT_Category": ", ".join(matched_cats) if matched_cats else "General",
                "Keywords": ", ".join(list(set(found_kws))),
                "Title": title,
                "Link": doc.get('html_url')
            })
        
        page += 1
        time.sleep(0.5) # 서버 부하 방지

    # 3. CSV 저장
    if results:
        with open('Trump_ICT_Full_Report_2025.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "Type", "ICT_Category", "Keywords", "Title", "Link"])
            writer.writeheader()
            writer.writerows(results)
        print(f"🏁 수집 완료! 총 {len(results)}건의 데이터를 저장했습니다.")
    else:
        print("⚠️ 수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
