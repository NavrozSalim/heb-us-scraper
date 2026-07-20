"""HEB.com product page scraper (US)."""
from __future__ import annotations

import re
from typing import Any

from .helpers import fail, fetch_html, ok, parse_money, soup


def scrape_product(
    *,
    url: str,
    region: str,
    vendor: str,
    proxy_urls: list[str],
    timeout_secs: int,
    max_retries: int,
    actor_input: dict[str, Any],
) -> dict:
    if url.isdigit():
        url = f"https://www.heb.com/product-detail/{url}"

    last_err = "unknown"
    for attempt in range(max(1, max_retries + 1)):
        try:
            html, status = fetch_html(url, proxy_urls=proxy_urls, timeout_secs=timeout_secs)
            if status >= 400:
                last_err = f"HTTP {status}"
                continue
            doc = soup(html)
            title_el = (
                doc.select_one("h1")
                or doc.select_one("[data-qe-id=productTitle]")
                or doc.select_one("meta[property='og:title']")
            )
            if title_el and title_el.name == "meta":
                title = title_el.get("content")
            else:
                title = title_el.get_text(strip=True) if title_el else None

            price = None
            for sel in (
                "[data-qe-id=productPrice]",
                ".product-price",
                "span.price",
                "meta[itemprop=price]",
            ):
                el = doc.select_one(sel)
                if el:
                    price = parse_money(el.get("content") or el.get_text())
                    if price is not None:
                        break
            if price is None:
                m = re.search(r'"price"\s*:?\s*"?([0-9]+(?:\.[0-9]+)?)"?', html)
                if m:
                    price = float(m.group(1))

            stock = None
            text = doc.get_text(" ", strip=True).lower()
            if "out of stock" in text or "unavailable" in text:
                stock = 0
            elif "add to cart" in text or "in stock" in text:
                stock = 10

            if price is None and not title:
                last_err = "parse_failed"
                continue

            return ok(
                price,
                stock,
                title,
                vendor=vendor,
                region=region,
                url=url,
                host="heb.com",
                attempt=attempt + 1,
            )
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
    return fail("heb_scrape_failed", last_err, vendor=vendor, region=region, url=url)
