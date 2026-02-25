"""
Gartner Newsroom Crawler v3
전략:
  1순위 - 공식 RSS 피드 (www.gartner.com/newsroom/rss) → 봇 차단 없이 안정적
  2순위 - Playwright 헤드리스 브라우저 → RSS 실패 시 백업
"""

import csv
import json
import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

NEWSROOM_URL = "https://www.gartner.com/en/newsroom"
RSS_URL = "https://www.gartner.com/newsroom/rss"
MAX_ARTICLES = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# 기사 URL 판별 패턴
ARTICLE_PATH_KEYWORDS = [
    "/newsroom/press-releases/",
    "/newsroom/announcements/",
    "/newsroom/q-and-a/",
    "/newsroom/conference-highlights/",
]


# ─────────────────────────────────────────────────────────────────────────────
# 전략 1: RSS 피드
# ─────────────────────────────────────────────────────────────────────────────

def crawl_via_rss() -> list[dict]:
    """가트너 공식 RSS 피드를 파싱합니다."""
    print(f"\n[RSS] {RSS_URL} 요청 중...")
    try:
        resp = requests.get(RSS_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[RSS] 요청 실패: {e}")
        return []

    content_type = resp.headers.get("Content-Type", "")
    print(f"[RSS] 응답 상태: {resp.status_code} | Content-Type: {content_type}")

    # HTML이 반환되면 RSS가 아님
    text = resp.text.strip()
    if text.startswith("<!DOCTYPE") or text.startswith("<html"):
        print("[RSS] RSS가 아닌 HTML이 반환됨 → 백업 전략으로 전환")
        return []

    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        print(f"[RSS] XML 파싱 실패: {e}")
        return []

    # RSS 네임스페이스 처리
    ns = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "content": "http://purl.org/rss/1.0/modules/content/",
        "media": "http://search.yahoo.com/mrss/",
    }

    # <channel> → <item> 탐색 (RSS 2.0 / Atom 공통 처리)
    items = root.findall(".//item")
    if not items:
        # Atom 피드 형식
        atom_ns = "http://www.w3.org/2005/Atom"
        items = root.findall(f".//{{{atom_ns}}}entry")

    print(f"[RSS] 피드 아이템 수: {len(items)}")
    if not items:
        print("[RSS] 아이템 없음 → 백업 전략으로 전환")
        return []

    results = []
    for idx, item in enumerate(items[:MAX_ARTICLES], start=1):
        def _text(tag, default=""):
            el = item.find(tag) or item.find(f"dc:{tag}", ns)
            return el.text.strip() if el is not None and el.text else default

        title    = _text("title")
        url      = _text("link") or _text("guid")
        date     = _text("pubDate") or _text("dc:date", ns) or _text("published")
        category = _text("category")
        summary  = _text("description") or _text("summary")

        # HTML 태그 제거 (요약에 마크업 포함될 수 있음)
        import re
        summary = re.sub(r"<[^>]+>", "", summary).strip()

        article = {
            "rank": idx,
            "title": title,
            "url": url,
            "date": date,
            "category": category,
            "summary": summary[:300],
            "crawled_at": datetime.now().isoformat(),
        }
        results.append(article)
        print(f"  [{idx:02d}] {title[:70]}{'...' if len(title) > 70 else ''}")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# 전략 2: Playwright (백업)
# ─────────────────────────────────────────────────────────────────────────────

def crawl_via_playwright() -> list[dict]:
    """Playwright로 가트너 뉴스룸을 직접 렌더링합니다."""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
    except ImportError:
        print("[Playwright] playwright 패키지가 없습니다.")
        return []

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1280,900",
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
            # 자바스크립트 활성화 명시
            java_script_enabled=True,
        )
        page = context.new_page()

        # ── 접속 ──────────────────────────────────────────────────────────
        print(f"\n[Playwright] {NEWSROOM_URL} 접속 중...")
        try:
            page.goto(NEWSROOM_URL, wait_until="networkidle", timeout=90_000)
        except PwTimeout:
            print("[Playwright] networkidle 타임아웃 → domcontentloaded로 재시도")
            page.goto(NEWSROOM_URL, wait_until="domcontentloaded", timeout=60_000)

        # ── 쿠키 팝업 처리 ─────────────────────────────────────────────────
        for btn in ["#onetrust-accept-btn-handler", "button:has-text('Accept All')", "button:has-text('Accept')"]:
            try:
                page.click(btn, timeout=4_000)
                print("[Playwright] 쿠키 동의 완료")
                time.sleep(1)
                break
            except Exception:
                pass

        # ── 스크롤로 레이지 로드 유도 ──────────────────────────────────────
        print("[Playwright] 페이지 스크롤 중 (레이지 로드 유도)...")
        for _ in range(5):
            page.evaluate("window.scrollBy(0, 600)")
            time.sleep(0.8)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        # ── 기사 링크 대기 ─────────────────────────────────────────────────
        selector_css = ", ".join(
            f"a[href*='{kw}']" for kw in ARTICLE_PATH_KEYWORDS
        )
        try:
            page.wait_for_selector(selector_css, timeout=20_000)
            print("[Playwright] 기사 링크 발견!")
        except PwTimeout:
            print("[Playwright] 기사 링크 대기 시간 초과")
            # 디버그용 HTML 저장 (아티팩트로 확인 가능)
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("[Playwright] debug_page.html 저장 완료")

        # ── 링크 수집 및 필터링 ────────────────────────────────────────────
        all_links = page.query_selector_all("a[href]")
        print(f"[Playwright] 전체 링크 수: {len(all_links)}")

        seen: set[str] = set()
        article_links = []
        for link in all_links:
            href = link.get_attribute("href") or ""
            if not any(kw in href for kw in ARTICLE_PATH_KEYWORDS):
                continue
            full_url = href if href.startswith("http") else f"https://www.gartner.com{href}"
            if full_url in seen:
                continue
            seen.add(full_url)
            article_links.append((link, full_url))

        print(f"[Playwright] 기사 URL 필터링 결과: {len(article_links)}개")

        # ── 각 기사에서 메타데이터 추출 ───────────────────────────────────
        import re
        for idx, (link_el, full_url) in enumerate(article_links[:MAX_ARTICLES], start=1):
            try:
                title = link_el.inner_text().strip()

                # 제목이 짧으면 부모 컨테이너에서 탐색
                if len(title) < 10:
                    card_handle = link_el.evaluate_handle(
                        "el => el.closest('article, li, div[class*=\"card\"], div[class*=\"item\"]')"
                    )
                    card_el = card_handle.as_element() if card_handle else None
                    if card_el:
                        for h in ["h1", "h2", "h3", "h4"]:
                            h_el = card_el.query_selector(h)
                            if h_el:
                                t = h_el.inner_text().strip()
                                if t:
                                    title = t
                                    break

                card_handle = link_el.evaluate_handle(
                    "el => el.closest('article, li, section, "
                    "div[class*=\"card\"], div[class*=\"item\"], div[class*=\"result\"]')"
                )
                card_el = card_handle.as_element() if card_handle else None

                date = category = summary = ""
                if card_el:
                    for sel, attr in [("time[datetime]", "datetime"), ("time", None), ("[class*='date']", None)]:
                        d = card_el.query_selector(sel)
                        if d:
                            date = (d.get_attribute("datetime") if attr else None) or d.inner_text().strip()
                            if date:
                                break

                    for sel in ["[class*='category']", "[class*='topic']", "[class*='tag']", "[class*='label']"]:
                        c = card_el.query_selector(sel)
                        if c:
                            category = c.inner_text().strip()
                            if category:
                                break

                    for sel in ["p", "[class*='description']", "[class*='summary']", "[class*='excerpt']"]:
                        s = card_el.query_selector(sel)
                        if s:
                            text = re.sub(r"\s+", " ", s.inner_text().strip())
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

            except Exception as e:
                print(f"  [{idx}] 파싱 오류: {e}")

        browser.close()

    return results


# ─────────────────────────────────────────────────────────────────────────────
# 저장
# ─────────────────────────────────────────────────────────────────────────────

def save_results(data: list[dict]) -> None:
    import re
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = f"gartner_news_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON 저장: {json_path}")

    csv_path = f"gartner_news_{timestamp}.csv"
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
        linked = f"[{item['title'][:60]}]({item['url']})" if item["url"] else item["title"][:60]
        lines.append(f"| {item['rank']} | {linked} | {item['date']} | {item['category']} |")

    gh = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh:
        with open(gh, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("✅ GitHub Actions 스텝 요약 기록 완료")
    else:
        print("\n" + "\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Gartner Newsroom Crawler v3")
    print("=" * 60)

    # 1순위: RSS
    articles = crawl_via_rss()

    # 2순위: Playwright
    if not articles:
        print("\n[!] RSS 실패 → Playwright 백업 전략 실행")
        articles = crawl_via_playwright()

    if articles:
        print(f"\n총 {len(articles)}개 기사 크롤링 성공")
        save_results(articles)
    else:
        print("\n❌ 모든 전략 실패. 가트너 사이트 접근 정책을 확인하세요.")
        raise SystemExit(1)
