"""
Gartner Newsroom Crawler v2
- 기사 링크 URL 패턴(/newsroom/press-releases/, /newsroom/announcements/ 등)으로 필터링
- 페이지가 완전히 렌더링될 때까지 명시적으로 대기
"""

import json
import csv
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

NEWSROOM_URL = "https://www.gartner.com/en/newsroom"

# 가트너 기사 URL에 포함되는 경로 패턴
ARTICLE_PATH_KEYWORDS = [
    "/newsroom/press-releases/",
    "/newsroom/announcements/",
    "/newsroom/q-and-a/",
    "/newsroom/conference-highlights/",
]


def is_article_url(href: str) -> bool:
    """가트너 뉴스 기사 URL인지 판별합니다."""
    return any(kw in href for kw in ARTICLE_PATH_KEYWORDS)


def crawl_gartner_newsroom(max_articles: int = 10) -> list[dict]:
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
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        # ── 1. 페이지 접속 ─────────────────────────────────────────────────
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 가트너 뉴스룸 접속 중...")
        page.goto(NEWSROOM_URL, wait_until="domcontentloaded", timeout=60_000)

        # ── 2. 쿠키 팝업 처리 ─────────────────────────────────────────────
        for btn_sel in [
            "#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('Agree')",
        ]:
            try:
                page.click(btn_sel, timeout=4_000)
                print("  쿠키 동의 완료")
                time.sleep(1)
                break
            except Exception:
                pass

        # ── 3. 기사 링크가 나타날 때까지 대기 ─────────────────────────────
        print("  뉴스 기사 링크 로딩 대기 중...")
        try:
            page.wait_for_selector(
                "a[href*='/newsroom/press-releases/'], "
                "a[href*='/newsroom/announcements/'], "
                "a[href*='/newsroom/q-and-a/']",
                timeout=30_000,
            )
        except PwTimeout:
            print("  ⚠️  기사 링크 대기 시간 초과. 현재 로드된 내용으로 진행합니다.")

        # 동적 렌더링 완료를 위한 추가 대기
        time.sleep(3)

        # ── 4. 모든 <a> 태그 수집 후 기사 URL 필터링 ──────────────────────
        all_links = page.query_selector_all("a[href]")
        print(f"  전체 링크 수: {len(all_links)}개")

        seen_urls: set[str] = set()
        article_links = []

        for link in all_links:
            href = link.get_attribute("href") or ""
            if not is_article_url(href):
                continue

            full_url = href if href.startswith("http") else f"https://www.gartner.com{href}"
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            article_links.append((link, full_url))

        print(f"  기사 링크 필터링 결과: {len(article_links)}개")

        if not article_links:
            # 디버그용: 현재 페이지 HTML 저장
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("  ❌ 기사 링크를 찾지 못했습니다. debug_page.html을 확인하세요.")
            browser.close()
            return []

        # ── 5. 각 링크에서 제목·날짜·카테고리·요약 추출 ──────────────────
        for idx, (link_el, full_url) in enumerate(article_links[:max_articles], start=1):
            try:
                # ① 제목: 링크 텍스트 우선
                title = link_el.inner_text().strip()

                # 링크 텍스트가 너무 짧으면 부모 컨테이너에서 제목 태그 탐색
                if len(title) < 10:
                    parent = link_el.evaluate_handle(
                        "el => el.closest('article, li, div[class*=\"card\"], div[class*=\"item\"]')"
                    )
                    parent_el = parent.as_element() if parent else None
                    if parent_el:
                        for h in ["h1", "h2", "h3", "h4"]:
                            h_el = parent_el.query_selector(h)
                            if h_el:
                                t = h_el.inner_text().strip()
                                if t:
                                    title = t
                                    break

                # ② 카드(컨테이너) 탐색
                card_handle = link_el.evaluate_handle(
                    "el => el.closest('article, li, section, "
                    "div[class*=\"card\"], div[class*=\"item\"], div[class*=\"result\"]')"
                )
                card_el = card_handle.as_element() if card_handle else None

                # ③ 날짜
                date = ""
                if card_el:
                    for date_sel in ["time[datetime]", "time", "[class*='date']", "[class*='time']"]:
                        d = card_el.query_selector(date_sel)
                        if d:
                            date = d.get_attribute("datetime") or d.inner_text().strip()
                            if date:
                                break

                # ④ 카테고리
                category = ""
                if card_el:
                    for cat_sel in ["[class*='category']", "[class*='topic']", "[class*='tag']", "[class*='label']"]:
                        c = card_el.query_selector(cat_sel)
                        if c:
                            category = c.inner_text().strip()
                            if category:
                                break

                # ⑤ 요약
                summary = ""
                if card_el:
                    for sum_sel in ["p", "[class*='description']", "[class*='summary']", "[class*='excerpt']"]:
                        s = card_el.query_selector(sum_sel)
                        if s:
                            text = s.inner_text().strip()
                            if text and text != title:
                                summary = text
                                break

                article = {
                    "rank": idx,
                    "title": title,
                    "url": full_url,
                    "date": date,
                    "category": category,
                    "summary": summary,
                    "crawled_at": datetime.now().isoformat(),
                }
                results.append(article)
                print(f"  [{idx:02d}] {title[:70]}{'...' if len(title) > 70 else ''}")
                print(f"        날짜: {date or '(없음)'}  |  카테고리: {category or '(없음)'}")

            except Exception as e:
                print(f"  [{idx}] 파싱 오류: {e}")

        browser.close()

    return results


def save_results(data: list[dict]) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON
    json_path = f"gartner_news_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON 저장: {json_path}")

    # CSV (UTF-8 BOM → Excel 한글 깨짐 방지)
    csv_path = f"gartner_news_{timestamp}.csv"
    if data:
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ CSV  저장: {csv_path}")

    # GitHub Actions Step Summary
    lines = [
        "## 🗞️ Gartner Newsroom – 최신 기사\n",
        f"크롤링 시각: {datetime.now():%Y-%m-%d %H:%M:%S}\n",
        "| # | 제목 | 날짜 | 카테고리 |",
        "|---|------|------|----------|",
    ]
    for item in data:
        linked_title = (
            f"[{item['title'][:60]}]({item['url']})"
            if item["url"] else item["title"][:60]
        )
        lines.append(
            f"| {item['rank']} | {linked_title} | {item['date']} | {item['category']} |"
        )

    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        with open(gh_summary, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("✅ GitHub Actions 스텝 요약 기록 완료")
    else:
        print("\n" + "\n".join(lines))


if __name__ == "__main__":
    articles = crawl_gartner_newsroom(max_articles=10)

    if articles:
        print(f"\n총 {len(articles)}개 기사 크롤링 성공")
        save_results(articles)
    else:
        print("\n❌ 크롤링된 데이터가 없습니다.")
        raise SystemExit(1)
