# src/analogapi/scrapers/scrape_films.py
import requests
import re
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ..models.film import Film
from ..database import get_db
import time
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_not_a_film(film_name, film_url):
    """
    Determines if the page is not a specific film stock (e.g., a category, camera, or unrelated page).
    """
    name_lower = film_name.lower()
    url_lower = film_url.lower()
    # Excluir páginas que son categorías o contienen palabras relacionadas con cámaras
    if any(keyword in name_lower for keyword in ["camera", "category", "template", "format", "encoding", "instamatic", "box", "flex", "reflex", "bessa", "brownie"]):
        return True
    if any(keyword in url_lower for keyword in ["camera", "category"]):
        return True
    # Excluir nombres que no parezcan películas (e.g., solo números o sin "film")
    if name_lower.isdigit() or ("film" not in name_lower and "color" not in name_lower and "negative" not in name_lower):
        return True
    return False

def scrape_films(max_films_per_category=10, max_categories=None, max_category_pages=1):
    """
    Scrapes analog films from specific brand categories on Camera-wiki.org.
    Args:
        max_films_per_category (int): Maximum number of films to scrape per category.
        max_categories (int): Maximum number of categories to scrape.
        max_category_pages (int): Maximum number of subcategory pages to process.
    Returns:
        list: List of dictionaries with the scraped film data.
    """
    max_categories = max_categories if max_categories is not None else 10
    max_films_per_category = max(max_films_per_category, 1)

    # Define categories based on film brands
    film_categories = [
        "https://camera-wiki.org/wiki/Category:Kodak",
        "https://camera-wiki.org/wiki/Category:Ilford",
        "https://camera-wiki.org/wiki/Category:Fujifilm",
        "https://camera-wiki.org/wiki/Category:Agfa",
        "https://camera-wiki.org/wiki/Category:Foma",
        "https://camera-wiki.org/wiki/Category:Konica",
        "https://camera-wiki.org/wiki/Category:Orwo",
        "https://camera-wiki.org/wiki/Category:Adox",
    ]

    headers = {
        "User-Agent": "AnalogAPI-Scraper/1.0 (pablofriedmann; https://github.com/pablofriedmann/analogAPI)"
    }
    delay = 1  # Delay between requests

    categories = []
    for category_url in film_categories:
        try:
            response = requests.get(category_url, headers=headers, timeout=5, verify=False)
            response.raise_for_status()
            categories.append(category_url)
        except requests.RequestException as e:
            print(f"Error accessing category {category_url}: {e}")
            continue
        time.sleep(delay)

    categories = categories[:max_categories]
    print(f"Found {len(categories)} categories: {categories}")

    all_films = []
    categories_processed = 0
    known_brands = ["Kodak", "Ilford", "Fujifilm", "Polaroid", "Agfa", "Foma", "Konica", "Orwo", "Adox"]

    for category_url in categories:
        if categories_processed >= max_categories:
            break

        print(f"Scraping category: {category_url}")
        category_films = []
        current_url = category_url
        page_count = 0

        while current_url and len(category_films) < max_films_per_category and page_count < max_category_pages:
            try:
                response = requests.get(current_url, headers=headers, timeout=5, verify=False)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error accessing {current_url}: {e}")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            film_links = soup.select("div#mw-pages li a")
            if not film_links:
                print(f"No films found in {current_url}")
                break

            print(f"Found {len(film_links)} film links in {current_url}")

            for link in film_links:
                if len(category_films) >= max_films_per_category:
                    break

                film_url = "https://camera-wiki.org" + link["href"]
                film_name = link.get_text(strip=True)

                if is_not_a_film(film_name, film_url):
                    print(f"Skipping non-film page: {film_name} ({film_url})")
                    continue

                try:
                    film_response = requests.get(film_url, headers=headers, timeout=5, verify=False)
                    film_response.raise_for_status()
                    film_soup = BeautifulSoup(film_response.text, "html.parser")

                    format = "Unknown"
                    color = "Unknown"
                    iso = None
                    grain = "Unknown"

                    # Intentar inferir el formato desde el nombre o URL
                    name_lower = film_name.lower()
                    if "35mm" in name_lower or "35mm" in film_url.lower():
                        format = "35mm"
                    elif "120" in name_lower or "120" in film_url.lower():
                        format = "120"
                    elif "110" in name_lower or "110" in film_url.lower():
                        format = "110"
                    elif "126" in name_lower or "126" in film_url.lower():
                        format = "126"
                    elif "127" in name_lower or "127" in film_url.lower():
                        format = "127"
                    elif "instant" in name_lower or "polaroid" in name_lower or "sx-70" in name_lower:
                        format = "Instant"

                    content = film_soup.select_one("div#mw-content-text")
                    if content:
                        infobox = content.select_one("table.infobox")
                        if infobox:
                            rows = infobox.select("tr")
                            for row in rows:
                                cells = row.select("td")
                                if len(cells) >= 2:
                                    label = cells[0].get_text(strip=True).lower()
                                    value = cells[1].get_text(strip=True).lower()
                                    if "format" in label and format == "Unknown":
                                        if "35mm" in value:
                                            format = "35mm"
                                        elif "120" in value:
                                            format = "120"
                                        elif "110" in value:
                                            format = "110"
                                        elif "126" in value:
                                            format = "126"
                                        elif "127" in value:
                                            format = "127"
                                        elif "instant" in value:
                                            format = "Instant"
                                    if "type" in label or "color" in label:
                                        if "color" in value:
                                            color = "Color"
                                        elif "black and white" in value or "b&w" in value or "monochrome" in value:
                                            color = "Black and White"
                                    if "iso" in label or "speed" in label:
                                        iso = int(re.search(r'\d+', value).group()) if re.search(r'\d+', value) else None
                                    if "grain" in label:
                                        grain = value.title()

                        paragraphs = content.select("p")
                        for p in paragraphs:
                            text = p.get_text(strip=True).lower()
                            if "format" in text and format == "Unknown":
                                if "35mm" in text:
                                    format = "35mm"
                                elif "medium format" in text or "120" in text:
                                    format = "120"
                                elif "110" in text:
                                    format = "110"
                                elif "126" in text:
                                    format = "126"
                                elif "127" in text:
                                    format = "127"
                                elif "instant" in text or "polaroid" in text or "sx-70" in text:
                                    format = "Instant"
                            if ("type" in text or "color" in text) and color == "Unknown":
                                if "color" in text:
                                    color = "Color"
                                elif "black and white" in text or "b&w" in text or "monochrome" in text:
                                    color = "Black and White"
                            if ("iso" in text or "speed" in text) and not iso:
                                iso_match = re.search(r'iso\s+(\d+)', text)
                                if iso_match:
                                    iso = int(iso_match.group(1))
                            if "grain" in text and grain == "Unknown":
                                if "fine" in text:
                                    grain = "Fine"
                                elif "medium" in text:
                                    grain = "Medium"
                                elif "coarse" in text:
                                    grain = "Coarse"

                    desired_formats = ["35mm", "120", "110", "126", "127", "Instant"]
                    if format != "Unknown" and not any(desired_format in format for desired_format in desired_formats):
                        print(f"Skipping film with non-desired format: {film_name} (format: {format})")
                        continue

                    name_parts = film_name.split(" ", 1)
                    brand = name_parts[0] if name_parts[0] in known_brands else "Unknown"
                    name = name_parts[1] if len(name_parts) > 1 and name_parts[0] in known_brands else film_name

                    if brand.isdigit() or "camera" in name.lower():
                        print(f"Skipping film with invalid brand or name: {film_name} ({film_url})")
                        continue

                    if not iso:
                        print(f"Skipping film without ISO: {film_name} ({film_url})")
                        continue

                    film_data = {
                        "brand": brand,
                        "name": name,
                        "format": format,
                        "color": color,
                        "iso": iso,
                        "grain": grain,
                        "source_url": film_url
                    }
                    category_films.append(film_data)
                    print(f"Successfully scraped film: {brand} {name} from {film_url}")
                    print(f"Film data: {film_data}")

                except requests.RequestException as e:
                    print(f"Error scraping {film_url}: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error while processing {film_url}: {e}")
                    continue

                time.sleep(delay)

            next_page = soup.select_one("a[href*='pagefrom']")
            current_url = "https://camera-wiki.org" + next_page["href"] if next_page else None
            page_count += 1
            time.sleep(delay)

        if category_films:
            categories_processed += 1
        all_films.extend(category_films)
        print(f"Category {category_url} yielded {len(category_films)} films")

    print(f"Processed {categories_processed} categories with films")
    print(f"Total films scraped: {len(all_films)}")
    return all_films

def save_scraped_films(db: Session, films: list):
    valid_formats = ["35mm", "120", "110", "126", "127", "Instant"]
    saved_films = 0
    try:
        print(f"Attempting to save {len(films)} films")
        for film_data in films:
            try:
                if film_data["format"] not in valid_formats:
                    print(f"Skipping film with invalid format: {film_data['brand']} {film_data['name']} (format: {film_data['format']})")
                    continue

                existing_film = db.query(Film).filter(
                    Film.brand.ilike(film_data["brand"]),
                    Film.name.ilike(film_data["name"].replace(" ", ""))
                ).first()

                if existing_film:
                    print(f"Film {film_data['brand']} {film_data['name']} already exists, skipping")
                    continue

                film = Film(
                    brand=film_data["brand"],
                    name=film_data["name"],
                    format=film_data["format"],
                    color=film_data["color"],
                    iso=film_data["iso"],
                    grain=film_data["grain"],
                    source_url=film_data["source_url"]
                )
                print(f"Adding film: {film_data['brand']} {film_data['name']}")
                db.add(film)
                db.commit()
                print(f"Successfully added film: {film_data['brand']} {film_data['name']}")
                saved_films += 1
            except Exception as e:
                print(f"Error adding film {film_data['brand']} {film_data['name']}: {e}")
                db.rollback()
                raise
        print(f"Successfully saved {saved_films} films to the database")
    except Exception as e:
        print(f"Error committing to database: {e}")
        db.rollback()
        raise