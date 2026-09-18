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
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu"
            ]
        )
        context = browser.new_context()
        page = context.new_page()
        
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
            previous_count = 0
            retries = 0
            max_retries = 4

            while True:
                page.evaluate('''(selector) => {
                    const feed = document.querySelector(selector);
                    if(feed) feed.scrollTo(0, feed.scrollHeight);
                }''', feed_selector)

                page.wait_for_timeout(1500)

                current_count = page.locator('a[href*="/maps/place/"]').count()
                if current_count == previous_count:
                    retries += 1
                    if retries >= max_retries:
                        break
                else:
                    retries = 0
                previous_count = current_count
        except:
            pass

        links_locator = page.locator('a[href*="/maps/place/"]')
        num_links = links_locator.count()
        print(f"Found {num_links} places.")

        feed_data = page.evaluate('''() => {
            const result = {};
            const items = document.querySelectorAll('a[href*="/maps/place/"]');
            for(const item of items) {
                const href = item.href;
                let container = item.parentElement;
                while(container && container.getAttribute('role') !== 'feed') {
                    const span = container.querySelector('span[aria-label*="stars"], span[aria-label*="étoiles"]');
                    if(span) {
                        result[href] = span.getAttribute('aria-label');
                        break;
                    }
                    container = container.parentElement;
                }
            }
            return result;
        }''')

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
                name = name_locator.first.text_content() if name_locator.count() > 0 else "N/A"

                rating = "N/A"
                reviews = "0"
                
                # MÉTHODE ULTRA-ROBUSTE POUR NOTE ET AVIS
                try:
                    f7nice = page.locator('div.F7nice').first
                    if f7nice.count() > 0:
                        text_block = f7nice.text_content()
                        
                        # Extraction de la note
                        rating_match = re.search(r'([0-9][,\.][0-9])', text_block)
                        if rating_match:
                            rating = rating_match.group(1).replace(',', '.')
                        elif "5" in text_block:
                            rating = "5.0"

                    # Extraction robuste du nombre d'avis
                    # On cible l'élément parent des étoiles qui possède l'attribut aria-label complet.
                    # Exemple: "4.7 étoiles 34 avis" ou "4.7 stars 34 reviews"
                    parent_aria = f7nice.evaluate('''element => {
                        let current = element;
                        for(let i=0; i<3; i++) {
                            if(current && current.hasAttribute('aria-label') && (current.getAttribute('aria-label').toLowerCase().includes('avis') || current.getAttribute('aria-label').toLowerCase().includes('reviews'))) {
                                return current.getAttribute('aria-label');
                            }
                            if(current) current = current.parentElement;
                        }

                        // Fallback: search globally for the star rating aria-label
                        const globalSpan = document.querySelector('span[aria-label*="avis"], span[aria-label*="reviews"]');
                        if(globalSpan) return globalSpan.getAttribute('aria-label');

                        // Fallback: search globally for a button containing reviews
                        const btns = Array.from(document.querySelectorAll('button'));
                        const reviewBtn = btns.find(b => b.textContent && (b.textContent.toLowerCase().includes('avis') || b.textContent.toLowerCase().includes('reviews')));
                        if(reviewBtn) return reviewBtn.textContent;

                        return null;
                    }''') if f7nice.count() > 0 else None

                    if not parent_aria:
                        parent_aria = page.evaluate('''() => {
                            const globalSpan = document.querySelector('span[aria-label*="avis"], span[aria-label*="reviews"]');
                            if(globalSpan) return globalSpan.getAttribute('aria-label');
                            const btns = Array.from(document.querySelectorAll('button'));
                            const reviewBtn = btns.find(b => b.textContent && (b.textContent.toLowerCase().includes('avis') || b.textContent.toLowerCase().includes('reviews')));
                            if(reviewBtn) return reviewBtn.textContent;
                            return null;
                        }''')

                    if parent_aria:
                        match = re.search(r'([\d\s,\.]+)\s*(?:avis|reviews)', parent_aria, re.IGNORECASE)
                        if match:
                            num_clean = re.sub(r'[^\d]', '', match.group(1))
                            if num_clean:
                                reviews = num_clean

                    # Si toujours 0, on cherche entre parenthèses dans le bloc note ou on utilise les données extraites depuis le feed de recherche
                    if reviews == "0":
                        if f7nice.count() > 0:
                            m = re.search(r'\(([0-9\s]+)\)', f7nice.text_content())
                            if m:
                                reviews = re.sub(r'[^0-9]', '', m.group(1))

                        if reviews == "0" and url in feed_data:
                            feed_aria = feed_data[url]
                            match = re.search(r'([\d\s,\.]+)\s*(?:avis|reviews)', feed_aria, re.IGNORECASE)
                            if match:
                                num_clean = re.sub(r'[^\d]', '', match.group(1))
                                if num_clean:
                                    reviews = num_clean

                            if reviews == "0":
                                # Cas de repli, le format de aria-label est souvent "4.7 stars 1,792 Reviews"
                                match_num = re.search(r'stars?\s+([\d\s,\.]+)', feed_aria, re.IGNORECASE)
                                if not match_num:
                                    match_num = re.search(r'étoiles?\s+([\d\s,\.]+)', feed_aria, re.IGNORECASE)
                                if match_num:
                                    num_clean = re.sub(r'[^\d]', '', match_num.group(1))
                                    if num_clean:
                                        reviews = num_clean

                except Exception as e:
                    print(f"Extraction error: {e}")

                phone_locator = page.locator('button[data-tooltip="Copier le numéro de téléphone"] div.Io6YTe')
                if phone_locator.count() == 0:
                     phone_locator = page.locator('button[data-tooltip="Copy phone number"] div.Io6YTe')
                phone = phone_locator.first.text_content() if phone_locator.count() > 0 else "N/A"

                actual_website_url = "N/A"
                website_anchor = page.locator('a[data-tooltip="Ouvrir le site Web"]')
                if website_anchor.count() == 0:
                     website_anchor = page.locator('a[data-tooltip="Open website"]')

                if website_anchor.count() > 0:
                     actual_website_url = website_anchor.first.get_attribute("href")

                email = "N/A"
                if actual_website_url != "N/A":
                    email = extract_email_from_url(actual_website_url)

                address_locator = page.locator('button[data-tooltip="Copier l\'adresse"] div.Io6YTe')
                if address_locator.count() == 0:
                     address_locator = page.locator('button[data-tooltip="Copy address"] div.Io6YTe')
                address = address_locator.first.text_content() if address_locator.count() > 0 else "N/A"

                postal_code = "N/A"
                city = "N/A"
                if address != "N/A":
                    match = re.search(r'\b(\d{5})\s+([^,]+)', address)
                    if match:
                        postal_code = match.group(1)
                        city = match.group(2).strip()
                    else:
                        # Fallback parsing or just keep full address if no match
                        city = address.split(',')[-1].strip() if ',' in address else address

                leads.append({
                    "Name": name,
                    "Rating": rating,
                    "Reviews": reviews,
                    "Phone": phone,
                    "Website": actual_website_url,
                    "Email": email,
                    "Code Postal": postal_code,
                    "Ville": city,
                    "URL_Google_Maps": url
                })
            except:
                pass

        browser.close()

    def rating_key(lead):
        try:
            return float(lead["Rating"].replace(',', '.'))
        except:
            return -1.0

    # NO FILTER OR SORT BY RATING IS APPLIED TO ENSURE WE GET ALL LEADS, INCLUDING THE LOWEST RATED ONES.

    safe_spec = re.sub(r'[^a-zA-Z0-9]', '_', specialty.lower())
    safe_loc = re.sub(r'[^a-zA-Z0-9]', '_', location.lower())
    filename = f"leads_{safe_spec}_{safe_loc}.csv"

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Rating", "Reviews", "Phone", "Website", "Email", "Code Postal", "Ville", "URL_Google_Maps"])
        writer.writeheader()
        writer.writerows(leads)

    print(f"EXPORT_FILE_NAME:{filename}")

if __name__ == "__main__":
    main()
