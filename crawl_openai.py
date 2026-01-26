import requests
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET

def get_openai_news_rss():
    print("🌐 OpenAI RSS 피드 수집 시작...")
    news_list = []
    
    # OpenAI의 공식 RSS 피드 주소
    rss_url = "https://openai.com/news/rss.xml"
    
    try:
        # 헤더 설정 (일반 브라우저처럼 보이게 함)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.get(rss_url, headers=headers, timeout=20)
        
        if res.status_code == 200:
            # XML 데이터 파싱
            root = ET.fromstring(res.content)
            # RSS 내의 item 태그들을 찾음
            items = root.findall('.//item')
            
            print(f"🔎 발견된 아이템 개수: {len(items)}개")
            
            for item in items[:5]: # 최신 5개
                title = item.find('title').text if item.find('title') is not None else "제목 없음"
                link = item.find('link').text if item.find('link') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                
                # 날짜 형식 깔끔하게 정리 (선택 사항)
                # 예: Mon, 20 Jan 2026 12:00:00 +0000 -> 2026-01-20
                
                news_list.append({
                    "카테고리": "글로벌(OpenAI)",
                    "기사제목": title.strip(),
                    "발행일": pub_date,
                    "링크": link
                })
        else:
            print(f"❌ 접속 실패 (상태 코드: {res.status_code})")
            
    except Exception as e:
        print(f"❌ RSS 수집 중 오류 발생: {e}")
        
    return news_list

if __name__ == "__main__":
    results = get_openai_news_rss()
    
    if not results:
        print("⚠️ 데이터가 없어 빈 파일을 생성합니다.")
        df = pd.DataFrame(columns=["수집일", "카테고리", "기사제목", "발행일", "링크"])
    else:
        df = pd.DataFrame(results)
        df.insert(0, "수집일", datetime.now().strftime("%Y-%m-%d"))
        print(f"✅ {len(results)}건 수집 완료!")

    # 파일 저장 (이름은 그대로 유지)
    df.to_excel("openai_news.xlsx", index=False)
