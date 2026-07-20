"""Apify Actor entry — Seller Pilot — HEB US Scraper."""
from __future__ import annotations

from apify import Actor

from .scraper import scrape_product


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        url = str(actor_input.get("url") or actor_input.get("productId") or "").strip()
        region = str(actor_input.get("region") or "USA").strip() or "USA"
        proxy_urls = actor_input.get("proxyUrls") or []
        if isinstance(proxy_urls, str):
            proxy_urls = [p.strip() for p in proxy_urls.split(",") if p.strip()]
        timeout_secs = int(actor_input.get("timeoutSecs") or 45)
        max_retries = int(actor_input.get("maxRetries") or 2)
        if not url:
            await Actor.fail(status_message="Input field `url` is required.")
            return
        Actor.log.info("Scraping vendor=hebus region=%s url=%s", region, url[:120])
        result = scrape_product(
            url=url,
            region=region,
            vendor="hebus",
            proxy_urls=list(proxy_urls),
            timeout_secs=timeout_secs,
            max_retries=max_retries,
            actor_input=actor_input,
        )
        await Actor.push_data(result)
        await Actor.set_value("OUTPUT", result)
