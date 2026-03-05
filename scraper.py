import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# Ai2 모델 호출 함수 (Hugging Face API 이용)
def ask_ai2(text):
    api_url = "https://api-inference.huggingface.co/models/allenai/OLMo-7B-Instruct"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    # AI에게 내리는 정교한 명령 (프롬프트)
    prompt = f"당신은 ICT 산업 분석가입니다. 다음 영문 뉴스를 한국어로 제목을 번역하고, 핵심 내용을 3줄로 요약하세요.\n\n내용: {text}\n\n형식:\n번역제목: \n요약: "
    
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": prompt})
        result = response.json()
        # AI 답변 추출 (비개발자분들을 위해 예외처리를 간단히 함)
        return result[0]['generated_text'].split("형식:")[1]
    except:
        return "번역/요약 처리 중 오류 발생"

def run_platform():
    url = "https://www.whitehouse.gov/news/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data_list = []
    # 최신 뉴스 3개만 샘플링
    articles = soup.find_all('article', limit=3)
    
    for article in articles:
        title_tag = article.find('a')
        original_title = title_tag.get_text(strip=True)
        link = title_tag['href']
        pub_date = article.find('time').get_text(strip=True) if article.find('time') else "N/A"
        
        # --- Ai2 모델 가동 ---
        ai_response = ask_ai2(original_title)
        # 결과에서 제목과 요약 분리 (간단한 로직)
        translated_title = ai_response.split("요약:")[0].replace("번역제목:", "").strip()
        summary = ai_response.split("요약:")[1].strip()
        # -------------------

        data_list.append({
            "1)기관명": "미국 백악관",
            "2)발행일": pub_date,
            "3)번역된 제목": translated_title,
            "4)원문": original_title,
            "5)요약내용": summary,
            "6)링크 (URL)": link,
            "7)수집일": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    df = pd.DataFrame(data_list)
    df.to_excel("whitehouse_ai_report.xlsx", index=False)

if __name__ == "__main__":
    run_platform()
