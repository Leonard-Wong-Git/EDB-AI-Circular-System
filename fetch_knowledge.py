#!/usr/bin/env python3
"""
fetch_knowledge.py
==================
抓取 EDB / ICAC 知識文件並儲存為 Markdown 格式
執行方式：python3 fetch_knowledge.py
輸出：dev/knowledge/ 目錄下的各知識文件
"""

import requests
from bs4 import BeautifulSoup
import time
import os
from pathlib import Path
from datetime import datetime, timezone

# ============================================================
# 知識來源設定
# ============================================================
SOURCES = {
    "all_roles": [
        {
            "id": "sch_admin_guide",
            "title": "學校行政指引",
            "url": "https://www.edb.gov.hk/tc/sch-admin/regulations/sch-admin-guide/index.html",
            "roles": ["principal", "vice_principal", "department_head", "teacher", "eo_admin"],
            "depth": 1,  # 抓子頁面
        },
        {
            "id": "fin_management",
            "title": "學校財務管理",
            "url": "https://www.edb.gov.hk/tc/sch-admin/fin-management/about-fin-management/index.html",
            "roles": ["principal", "vice_principal", "department_head", "teacher", "eo_admin"],
            "depth": 1,
        },
        {
            "id": "curriculum_guides",
            "title": "課程發展指引",
            "url": "https://www.edb.gov.hk/tc/curriculum-development/renewal/guides.html",
            "roles": ["principal", "vice_principal", "department_head", "teacher", "eo_admin"],
            "depth": 0,
        },
        {
            "id": "sch_activities",
            "title": "學校活動指引",
            "url": "https://www.edb.gov.hk/tc/sch-admin/admin/about-activities/sch-activities-guidelines/index.html",
            "roles": ["principal", "vice_principal", "department_head", "teacher", "eo_admin"],
            "depth": 0,
        },
        {
            "id": "press_releases",
            "title": "教育局新聞稿",
            "url": "https://www.edb.gov.hk/tc/about-edb/press/press-releases/index.html",
            "roles": ["principal", "vice_principal", "department_head", "teacher", "eo_admin"],
            "depth": 0,
        },
        {
            "id": "kpm",
            "title": "學校表現指標 (KPM)",
            "url": "https://www.edb.gov.hk/tc/sch-admin/sch-quality-assurance/performance-indicators/kpm/index.html",
            "roles": ["principal", "vice_principal", "department_head", "teacher", "eo_admin"],
            "depth": 0,
        },
    ],
    "supplier": [
        {
            "id": "fin_management_supplier",
            "title": "學校財務管理（供應商視角）",
            "url": "https://www.edb.gov.hk/tc/sch-admin/fin-management/about-fin-management/index.html",
            "roles": ["supplier"],
            "depth": 1,
        },
        {
            "id": "icac_reference",
            "title": "廉政公署採購參考資料",
            "url": "https://www.icac.org.hk/icac/pb/tc/reference.html",
            "roles": ["supplier"],
            "depth": 0,
        },
        {
            "id": "press_releases_supplier",
            "title": "教育局新聞稿（供應商）",
            "url": "https://www.edb.gov.hk/tc/about-edb/press/press-releases/index.html",
            "roles": ["supplier"],
            "depth": 0,
        },
    ],
}

# ============================================================
# HTTP 設定
# ============================================================
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
DELAY = 1.5  # seconds between requests
TIMEOUT = 15


# ============================================================
# 抓取單頁並提取文字
# ============================================================
def fetch_page(url: str) -> tuple[str, BeautifulSoup | None]:
    """Returns (text_content, soup) or (error_msg, None)"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            return f"[HTTP {resp.status_code}]", None
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove scripts, styles, nav
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True), soup
    except Exception as e:
        return f"[Error: {e}]", None


def extract_links(soup: BeautifulSoup, base_url: str) -> list[dict]:
    """Extract internal links from a page"""
    from urllib.parse import urljoin, urlparse
    links = []
    base_domain = urlparse(base_url).netloc
    seen = set()
    if not soup:
        return links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc != base_domain:
            continue
        if full_url in seen:
            continue
        seen.add(full_url)
        text = a.get_text(strip=True)
        if text and len(text) > 3:
            links.append({"url": full_url, "text": text})
    return links[:30]  # Limit sub-links


# ============================================================
# 主抓取函數
# ============================================================
def fetch_source(source: dict, output_dir: Path) -> dict:
    """Fetch a source and return result metadata"""
    print(f"\n{'='*60}")
    print(f"📥 {source['title']}")
    print(f"   {source['url']}")

    text, soup = fetch_page(source["url"])
    result = {
        "id": source["id"],
        "title": source["title"],
        "url": source["url"],
        "roles": source["roles"],
        "success": soup is not None,
        "char_count": len(text),
        "sub_pages": [],
    }

    # Build markdown content
    md_lines = [
        f"# {source['title']}",
        f"",
        f"**來源 URL：** {source['url']}",
        f"**抓取時間：** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**適用角色：** {', '.join(source['roles'])}",
        f"",
        f"---",
        f"",
        f"## 主頁內容",
        f"",
    ]

    if soup is None:
        md_lines.append(f"> ⚠️ 抓取失敗：{text}")
        print(f"   ❌ Failed: {text}")
    else:
        md_lines.append(text[:8000])  # Cap main page content
        print(f"   ✅ {len(text):,} chars")

        # Optionally fetch sub-pages
        if source.get("depth", 0) > 0 and soup:
            links = extract_links(soup, source["url"])
            print(f"   📎 Found {len(links)} sub-links, fetching top 5...")
            time.sleep(DELAY)

            for i, link in enumerate(links[:5]):
                sub_text, _ = fetch_page(link["url"])
                if sub_text and not sub_text.startswith("["):
                    result["sub_pages"].append(link["url"])
                    md_lines += [
                        f"",
                        f"---",
                        f"",
                        f"## 子頁：{link['text']}",
                        f"**URL：** {link['url']}",
                        f"",
                        sub_text[:4000],
                    ]
                    print(f"   ↳ [{i+1}] {link['text'][:50]} — {len(sub_text):,} chars")
                time.sleep(DELAY)

    # Write markdown file
    fname = output_dir / f"{source['id']}.md"
    fname.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"   💾 Saved → dev/knowledge/{source['id']}.md")
    return result


# ============================================================
# 生成 ROLE_KNOWLEDGE_INDEX.md
# ============================================================
def write_index(all_results: list[dict], output_dir: Path):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    success = [r for r in all_results if r["success"]]
    failed  = [r for r in all_results if not r["success"]]

    lines = [
        "# 角色知識庫索引 (ROLE_KNOWLEDGE_INDEX)",
        "",
        f"**生成時間：** {now}",
        f"**知識來源：** {len(all_results)} 個  |  成功：{len(success)}  |  失敗：{len(failed)}",
        "",
        "---",
        "",
        "## 知識文件清單",
        "",
        "| 文件 | 標題 | 適用角色 | 狀態 |",
        "|------|------|----------|------|",
    ]

    for r in all_results:
        status = "✅" if r["success"] else "❌"
        roles  = " / ".join(r["roles"])
        lines.append(f"| [{r['id']}.md](./{r['id']}.md) | {r['title']} | {roles} | {status} |")

    lines += [
        "",
        "---",
        "",
        "## 角色 → 知識文件對照",
        "",
    ]
    role_map = {}
    for r in all_results:
        for role in r["roles"]:
            role_map.setdefault(role, []).append(r)

    role_labels = {
        "principal": "👔 校長",
        "vice_principal": "🏫 副校長",
        "department_head": "📚 科主任",
        "teacher": "🧑‍🏫 教師",
        "eo_admin": "📋 行政主任",
        "supplier": "🏢 供應商",
    }
    for role_key, label in role_labels.items():
        docs = role_map.get(role_key, [])
        lines += [
            f"### {label}",
            "",
        ]
        for d in docs:
            lines.append(f"- [{d['title']}](./{d['id']}.md) — {d['url']}")
        lines.append("")

    if failed:
        lines += [
            "---",
            "",
            "## ⚠️ 抓取失敗的來源",
            "",
        ]
        for r in failed:
            lines.append(f"- **{r['title']}**: {r['url']}")
        lines += [
            "",
            "> 請手動訪問以上 URL，複製內容後替換對應 .md 檔案中的佔位文字。",
        ]

    idx_path = output_dir / "ROLE_KNOWLEDGE_INDEX.md"
    idx_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📋 Index saved → dev/knowledge/ROLE_KNOWLEDGE_INDEX.md")


# ============================================================
# ENTRY POINT
# ============================================================
def main():
    # Determine output directory relative to this script
    script_dir = Path(__file__).parent
    output_dir = script_dir / "dev" / "knowledge"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")

    all_results = []
    all_sources = SOURCES["all_roles"] + SOURCES["supplier"]

    for source in all_sources:
        result = fetch_source(source, output_dir)
        all_results.append(result)
        time.sleep(DELAY)

    write_index(all_results, output_dir)

    # Summary
    success = sum(1 for r in all_results if r["success"])
    print(f"\n{'='*60}")
    print(f"✅ 完成！成功：{success}/{len(all_results)} 個知識來源")
    print(f"📁 所有文件已儲存至：{output_dir}")
    print(f"\n下一步：")
    print(f"  1. 檢查 dev/knowledge/ 目錄下的 .md 文件")
    print(f"  2. 如有抓取失敗的來源，請手動補充內容")
    print(f"  3. 告知 AI Agent 讀取 dev/knowledge/ROLE_KNOWLEDGE_INDEX.md")


if __name__ == "__main__":
    main()
