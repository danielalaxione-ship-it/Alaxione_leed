import csv
import re
import argparse
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup

def extract_email_from_url(url):
    try:
        response = requests.get(url, timeout=7)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if emails:
            return emails[0]
    except:
        pass
    return ""

def main():
    parser = argparse.ArgumentParser(description="Scrape medical leads from Google Maps")
    parser.add_argument("--specialty", type=str, default="ophtalmologue")
    parser.add_argument("--location", type=str, default="Marseille")
    args = parser.parse_args()

    specialty = args.specialty
    location = args.location

    search_query = f"{specialty} {location}"
    print(f"Searching for: {search_query}")

    leads = []
    place_urls = []

    with sync_playwright() as p:
        # PARAMÈTRES ANTI-CRASH MÉMOIRE POUR SERVEUR CLOUD
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage", # Essentiel pour éviter les crashs mémoire (OOM)
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu"
            ]
        )
        context = browser.new_context()
        page = context.new_page()
        
        # On bloque absolument tout ce qui est inutile (images, styles, scripts externes)
        page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "stylesheet", "font", "other"] else route.continue_())

        page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")

        try:
            page.wait_for_selector("button:has-text('Tout accepter')", timeout=3000)
            page.click("button:has-text('Tout accepter')")
        except:
            pass

        page.wait_for_timeout(2000)

        feed_selector = 'div[role="feed"]'
        try:
            page.wait_for_selector(feed_selector, timeout=5000)
            # Limite de sécurité à 4 scrolls (environ 30 à 45 leads)
            for _ in range(4):
                page.hover(feed_selector)
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(1500)
        except:
            pass

        links_locator = page.locator('a[href*="/maps/place/"]')
        num_links = links_locator.count()
        print(f"Found {num_links} places.")

        for i in range(num_links):
            try:
                href = links_locator.nth(i).get_attribute("href")
                if href and href not in place_urls:
                    place_urls.append(href)
            except:
                pass

        for i, url in enumerate(place_urls):
            print(f"Scraping place {i+1}/{len(place_urls)}...")
            try:
                page.goto(url)
                page.wait_for_timeout(1500)

                name_locator = page.locator('h1.DUwDvf')
                name = name_locator.first.inner_text() if name_locator.count() > 0 else "N/A"

                rating = "N/A"
                reviews = "0"
                try:
                    rating_elem = page.locator('div.F7nice > span > span[aria-hidden="true"]').first
                    if rating_elem.count() > 0:
                         rating = rating_elem.inner_text().strip()

                    reviews_elem = page.locator('div.F7nice > span:nth-child(2) > span > span[aria-label]').first
                    if reviews_elem.count() > 0:
                         reviews_text = reviews_elem.inner_text()
                         reviews = re.sub(r'[^0-9]', '', reviews_text)
                except:
                    pass

                phone_locator = page.locator('button[data-tooltip="Copier le numéro de téléphone"] div.Io6YTe')
                if phone_locator.count() == 0:
                     phone_locator = page.locator('button[data-tooltip="Copy phone number"] div.Io6YTe')
                phone = phone_locator.first.inner_text() if phone_locator.count() > 0 else "N/A"

                actual_website_url = "N/A"
                website_anchor = page.locator('a[data-tooltip="Ouvrir le site Web"]')
                if website_anchor.count() == 0:
                     website_anchor = page.locator('a[data-tooltip="Open website"]')

                if website_anchor.count() > 0:
                     actual_website_url = website_anchor.first.get_attribute("href")

                email = "N/A"
                if actual_website_url != "N/A":
                    email = extract_email_from_url(actual_website_url)

                leads.append({
                    "Name": name,
                    "Rating": rating,
                    "Reviews": reviews,
                    "Phone": phone,
                    "Website": actual_website_url,
                    "Email": email
                })
            except:
                pass

        browser.close()

    def rating_key(lead):
        try:
            return float(lead["Rating"].replace(',', '.'))
        except:
            return -1.0

    leads.sort(key=rating_key, reverse=True)

    filename = f"leads_{specialty.replace(' ', '_').lower()}_{location.replace(' ', '_').lower()}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Rating", "Reviews", "Phone", "Website", "Email"])
        writer.writeheader()
        writer.writerows(leads)

    print(f"EXPORT_FILE_NAME:{filename}")

if __name__ == "__main__":
    main()
