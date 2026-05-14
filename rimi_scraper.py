import json
import time
import re
from playwright.sync_api import sync_playwright

CATEGORIES = {
    "dairy": "https://www.rimi.lv/e-veikals/lv/produkti/piena-produkti-un-olas/c/SH-11",
    "bread": "https://www.rimi.lv/e-veikals/lv/produkti/maize-un-konditoreja/maize/c/SH-7-2",
    "meat": "https://www.rimi.lv/e-veikals/lv/produkti/gala-un-zivs-produkti/c/SH-4",
    "vegetables": "https://www.rimi.lv/e-veikals/lv/produkti/augji-un-darzeni/darzeni/c/SH-3-2",
    "fruit": "https://www.rimi.lv/e-veikals/lv/produkti/augji-un-darzeni/augji/c/SH-3-1",
    "drinks": "https://www.rimi.lv/e-veikals/lv/produkti/dzerjieni/c/SH-6",
}

def parse_price(text):
    match = re.search(r'(\d+)[,.](\d+)', text)
    if match:
        return float(f"{match.group(1)}.{match.group(2)}")
    return None

def scrape():
    all_products = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({"Accept-Language": "lv-LV,lv;q=0.9"})
        for category, url in CATEGORIES.items():
            print(f"Scraping {category}...")
            try:
                page.goto(url, timeout=30000)
                page.wait_for_timeout(5000)
                page.wait_for_selector("li.product-grid__item", timeout=15000)
                items = page.query_selector_all("li.product-grid__item")
                count = 0
                for item in items[:15]:
                    try:
                        name = item.query_selector(".card__name")
                        price_el = item.query_selector("[class*='price']")
                        unit_el = item.query_selector("[class*='weight'], [class*='unit'], [class*='amount']")
                        if not name or not price_el:
                            continue
                        name_text = name.inner_text().strip()
                        price_text = price_el.inner_text().strip()
                        price_val = parse_price(price_text)
                        if not price_val:
                            continue
                        unit_text = unit_el.inner_text().strip() if unit_el else ""
                        all_products.append({
                            "name": name_text,
                            "unit": unit_text,
                            "category": category,
                            "store": "rimi",
                            "price": price_val
                        })
                        count += 1
                    except Exception:
                        continue
                print(f"  Found {count} products")
            except Exception as e:
                print(f"  Error: {e}")
            time.sleep(3)
        browser.close()
    with open("rimi_prices.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    print(f"\nDone! Saved {len(all_products)} products to rimi_prices.json")
    if all_products:
        print("\nSample products:")
        for p in all_products[:3]:
            print(f"  {p['name']} - €{p['price']}")

if __name__ == "__main__":
    scrape()
