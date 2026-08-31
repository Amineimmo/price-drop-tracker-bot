import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import lxml

def scrape_books_toscrape(soup):
    article = soup.find("article", class_="product_page")
    if not article:
        return None
        
    title = article.find("h1").get_text(strip=True)
    price_str = article.find("p").get_text(strip=True).replace("£", "")
    
    img_el = article.find("img")
    img_url = img_el.get("src") if img_el else ""
    if img_url.startswith("../../"):
        img_url = img_url.replace("../../", "https://books.toscrape.com/")
        
    return {
        "title": title,
        "price": float(price_str),
        "image": img_url
    }

def scrape_ebay(soup):
    try:
        title_el = soup.find("h1") or soup.select_one(".item-title") or soup.select_one(".x-item-title__mainTitle")
        title = title_el.get_text(strip=True) if title_el else "eBay Item"

        price_el = (
            soup.select_one("span[itemprop='price']")
            or soup.select_one(".price")
            or soup.select_one(".x-price-primary")
            or soup.find("span", class_="notranslate")
            or soup.select_one(".srp-text-price")
        )

        if not price_el:
            return None

        price_raw = price_el.get_text(strip=True)
        
        if "to" in price_raw.lower():
            price_raw = price_raw.lower().split("to")[0]
        elif "-" in price_raw:
            price_raw = price_raw.split("-")[0]
            
        clean_price = "".join(char for char in price_raw if char.isdigit() or char == ".")
        
        if clean_price.count(".") > 1:
            parts = clean_price.rsplit(".", 1)
            clean_price = parts[0].replace(".", "") + "." + parts[1]

        if not clean_price:
            return None
            
        price_value = float(clean_price)
        price_in_mad = price_value * 9.3
            
        img_el = (
            soup.select_one(".ux-image-carousel-item.active img")
            or soup.select_one(".ux-image-carousel-item img")
            or soup.select_one("img[data-testid='ux-image-carousel-item']")
            or soup.select_one("#icImg")
            or soup.select_one("img[itemprop='image']")
            or soup.select_one(".image-treatment img")
            or soup.select_one("img")
        )
        
        img_url = "https://via.placeholder.com/400"
        if img_el:
            img_url = img_el.get("data-src") or img_el.get("src") or "https://via.placeholder.com/400"
            if img_url.startswith("//"):
                img_url = "https:" + img_url
        
        return {
            "title": title.replace("Details about  ", "").strip(),
            "price": round(price_in_mad, 2),
            "image": img_url
        }
    except Exception:
        return None

def scrape_jumia(soup):
    try:
        title_el = (
            soup.find("h1", class_="-fs20") 
            or soup.select_one("h1.-fs20")
            or soup.find("h1")
        )
        title = title_el.get_text(strip=True) if title_el else "Jumia Item"

        price_el = (
            soup.select_one("span.-fs24")
            or soup.select_one("div.-b.-ltr.-m span")
            or soup.select_one("span[itemprop='price']")
            or soup.select_one("span.prc")
            or soup.find(class_="-prc")
        )

        if not price_el:
            page_title = soup.title.get_text(strip=True) if soup.title else "Unknown Title"
            print(f"Jumia Debug: Could not find price. Page Title is: {page_title}")
            return None

        price_str = price_el.get_text(strip=True)
        clean_price = "".join(char for char in price_str if char.isdigit() or char == ".")
        
        if clean_price.count(".") > 1:
            parts = clean_price.rsplit(".", 1)
            clean_price = parts[0].replace(".", "") + "." + parts[1]
            
        if not clean_price:
            print("Jumia Debug: Price string was empty after cleaning.")
            return None

        img_el = (
            soup.select_one(".img-c img")
            or soup.select_one("img.-fw")
            or soup.select_one(".itm img")
            or soup.find("img")
        )
        
        img_url = "https://via.placeholder.com/400"
        if img_el:
            img_url = img_el.get("data-src") or img_el.get("src") or "https://via.placeholder.com/400"
            if img_url.startswith("//"):
                img_url = "https:" + img_url

        return {
            "title": title,
            "price": float(clean_price),
            "image": img_url
        }
    except Exception as e:
        print(f"Jumia Debug: Code crashed with error: {e}")
        return None

def scrape_amazon(soup):
    try:
        title_el = soup.find("span", id="productTitle")
        if not title_el:
            return None
            
        title = title_el.get_text(strip=True)
        
        price_el = (
            soup.select_one("span.a-price span.a-offscreen")
            or soup.find("span", id="priceblock_ourprice")
            or soup.find("span", id="priceblock_dealprice")
            or soup.select_one("div.a-section span.a-color-price")
        )
        
        if not price_el:
            return None
            
        price_str = price_el.get_text(strip=True)
        clean_price = "".join(char for char in price_str if char.isdigit() or char == ".")
        
        img_el = soup.find("img", id="landingImage") or soup.find("img", id="imgBlkFront")
        img_url = img_el.get("src") if img_el else "https://via.placeholder.com/400"
            
        return {
            "title": title,
            "price": float(clean_price),
            "image": img_url
        }
    except Exception:
        return None

async def get_web_data(url: str):
    if "ebay." in url:
        url = url.replace("www.ebay.", "m.ebay.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1" if "ebay." in url else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        
        context = await browser.new_context(
            user_agent=ua,
            viewport={"width": 390, "height": 844} if "ebay." in url else {"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            html_content = await page.content()
        except Exception:
            await browser.close()
            return "Not found!"
            
        await browser.close()
        
    soup = BeautifulSoup(html_content, "lxml")
    
    if "books.toscrape.com" in url:
        return scrape_books_toscrape(soup)
    elif "ebay." in url:
        return scrape_ebay(soup)
    elif "amazon." in url:
        return scrape_amazon(soup)
    elif "jumia.ma" in url:
        return scrape_jumia(soup)
    else:
        return "Not found!"