"""
Gartner Newsroom Crawler
가트너 뉴스룸에서 최신 10개 기사를 크롤링합니다.
"""

import json
import csv
import time
from datetime import datetime
from playwright.sync_api import sync_playwright


NEWSROOM_URL = "https://www.gartner.com/en/newsroom"


def crawl_gartner_newsroom() -> list[dict]:
    """가트너 뉴스룸에서 최신 10개 기사를 크롤링합니다."""
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        print(f"[{datetime.now()}] 가트너 뉴스룸 접속 중...")
        page.goto(NEWSROOM_URL, wait_until="networkidle", timeout=60_000)

        # 쿠키 동의 팝업 처리 (있는 경우)
        try:
            page.click("button#onetrust-accept-btn-handler", timeout=5_000)
            print("쿠키 동의 완료")
            time.sleep(1)
        except Exception:
            pass

        # 뉴스 카드가 로드될 때까지 대기
        print("뉴스 카드 로딩 대기 중...")
        page.wait_for_selector(
            "article, .newsroom-article, [class*='article-card'], [class*='news-card']",
            timeout=30_000,
        )
        time.sleep(2)

        # ── 여러 CSS 선택자를 순서대로 시도 ──────────────────────────────────
        selectors_to_try = [
            # 가장 일반적인 패턴
            "article",
            "[class*='article-card']",
            "[class*='news-card']",
            "[class*='newsroom-card']",
            ".card",
            "li[class*='item']",
        ]

        article_elements = []
        used_selector = ""
        for sel in selectors_to_try:
            els = page.query_selector_all(sel)
            if len(els) >= 3:
                article_elements = els
                used_selector = sel
                break

        print(f"선택자 '{used_selector}'로 {len(article_elements)}개 요소 발견")

        # 최신 10개만 처리
        for idx, el in enumerate(article_elements[:10], start=1):
            try:
                # 제목
                title = ""
                for title_sel in ["h1", "h2", "h3", "h4", "[class*='title']"]:
                    t_el = el.query_selector(title_sel)
                    if t_el:
                        title = t_el.inner_text().strip()
                        if title:
                            break

                # URL
                url = ""
                link_el = el.query_selector("a")
                if link_el:
                    href = link_el.get_attribute("href") or ""
                    url = href if href.startswith("http") else f"https://www.gartner.com{href}"

                # 날짜
                date = ""
                for date_sel in ["time", "[class*='date']", "[class*='time']", "[datetime]"]:
                    d_el = el.query_selector(date_sel)
                    if d_el:
                        date = (
                            d_el.get_attribute("datetime")
                            or d_el.inner_text().strip()
                        )
                        if date:
                            break

                # 카테고리 / 태그
                category = ""
                for cat_sel in [
                    "[class*='category']",
                    "[class*='tag']",
                    "[class*='topic']",
                    "[class*='label']",
                ]:
                    c_el = el.query_selector(cat_sel)
                    if c_el:
                        category = c_el.inner_text().strip()
                        if category:
                            break

                # 요약문 (description / summary)
                summary = ""
                for sum_sel in [
                    "p",
                    "[class*='description']",
                    "[class*='summary']",
                    "[class*='excerpt']",
                ]:
                    s_el = el.query_selector(sum_sel)
                    if s_el:
                        summary = s_el.inner_text().strip()
                        if summary:
                            break

                article = {
                    "rank": idx,
                    "title": title,
                    "url": url,
                    "date": date,
                    "category": category,
                    "summary": summary,
                    "crawled_at": datetime.now().isoformat(),
                }
                results.append(article)
                print(f"  [{idx}] {title[:60]}{'...' if len(title) > 60 else ''}")

            except Exception as e:
                print(f"  [{idx}] 파싱 오류: {e}")

        browser.close()

    return results


def save_results(data: list[dict]) -> None:
    """크롤링 결과를 JSON / CSV 두 가지 형식으로 저장합니다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON 저장
    json_path = f"gartner_news_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nJSON 저장 완료: {json_path}")

    # CSV 저장
    csv_path = f"gartner_news_{timestamp}.csv"
    if data:
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"CSV  저장 완료: {csv_path}")

    # GitHub Actions summary 출력
    summary_lines = [
        "## 🗞️ Gartner Newsroom – 최신 10개 기사\n",
        f"크롤링 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "| # | 제목 | 날짜 | 카테고리 |",
        "|---|------|------|----------|",
    ]
    for item in data:
        title_link = f"[{item['title'][:50]}]({item['url']})" if item["url"] else item["title"][:50]
        summary_lines.append(
            f"| {item['rank']} | {title_link} | {item['date']} | {item['category']} |"
        )

    summary_md = "\n".join(summary_lines)

    # $GITHUB_STEP_SUMMARY 에 기록 (GitHub Actions 환경)
    import os
    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        with open(gh_summary, "a", encoding="utf-8") as f:
            f.write(summary_md + "\n")
        print("GitHub Actions 스텝 요약 기록 완료")
    else:
        print("\n" + summary_md)


if __name__ == "__main__":
    articles = crawl_gartner_newsroom()

    if articles:
        print(f"\n총 {len(articles)}개 기사 크롤링 성공")
        save_results(articles)
    else:
        print("크롤링된 데이터가 없습니다. 사이트 구조 변경 여부를 확인하세요.")
        raise SystemExit(1)
