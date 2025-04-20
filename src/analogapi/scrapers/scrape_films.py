import requests
import re
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ..models.film import Film
from ..database import get_db
import time
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_films(max_films=100):
    
    max_films = max(max_films, 1)

    url = "https://en.wikipedia.org/wiki/List_of_photographic_films"
    headers = {
        "User-Agent": "AnalogAPI-Scraper/1.0 (pablofriedmann; https://github.com/pablofriedmann/analogAPI)"
    }
    delay = 1 

    all_films = []

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")
        return all_films

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table", class_="wikitable")

    film_count = 0
    for table in tables:
        rows = table.find_all("tr")[1:]
        for row in rows:
            if film_count >= max_films:
                break

            cells = row.find_all("td")
            if len(cells) < 8:
                continue

            try:
                extracted_maker = cells[0].get_text(strip=True)
                extracted_film_name = cells[1].get_text(strip=True)
             
                type_film = cells[4].get_text(strip=True).lower()
                process = cells[5].get_text(strip=True)
                iso = cells[6].get_text(strip=True)
                formats = cells[7].get_text(strip=True).lower() 
                grain = cells[8].get_text(strip=True).lower() if len(cells) > 8 else "Unknown" 

                print(f"Extracted maker: {extracted_maker}")
                print(f"Extracted film_name: {extracted_film_name}")
                print(f"Type: {type_film}")
                print(f"Process: {process}")
                print(f"ISO: {iso}")
                print(f"Formats: {formats}")
                print(f"Grain: {grain}")

                brand = extracted_maker if extracted_maker else "Unknown"
                name = extracted_film_name if extracted_film_name else "Unknown"

                brand = brand.strip().title()
                brand_corrections = {
                    "Fujifilm": ["Fujifilm", "Fuji", "Fujicolor"],
                    "Agfa": ["Agfa", "Agfa Photo", "Agfaphoto"],
                    "Ilford": ["Ilford", "Ilford Photo"],
                    "Adox": ["Adox"],
                    "Foma": ["Foma"],
                    "Konica": ["Konica"],
                    "Orwo": ["Orwo", "Original Wolfen", "Wolfen"],
                    "Polaroid": ["Polaroid"],
                    "Kodak": ["Kodak"],
                    "Cinestill": ["Cinestill"],
                    "Dubblefilm": ["Dubblefilm"],
                    "Film Washi": ["Film Washi"],
                    "Flic Film": ["Flic Film", "Flicfilm"],
                    "Harman": ["Harman"],
                    "Holga": ["Holga"],
                    "Jch": ["Jch"],
                    "Kentmere": ["Kentmere"],
                    "Kono!": ["Kono!", "Kono"],
                    "Kosmo Foto": ["Kosmo Foto"],
                    "Lomography": ["Lomography"],
                    "Lucky": ["Lucky"],
                    "Oriental": ["Oriental"],
                    "Rera": ["Rera"],
                    "Revolog": ["Revolog", "Revelog"],
                    "Rollei": ["Rollei"],
                    "Sfl": ["Sfl"],
                    "Shanghai": ["Shanghai"],
                    "Silberra": ["Silberra"],
                    "Spur": ["Spur"],
                    "Svema": ["Svema"],
                    "Tasma": ["Tasma"],
                    "Ultrafine": ["Ultrafine"],
                    "Vibe": ["Vibe"],
                    "Yodica": ["Yodica"],
                }

                normalized_brand = "Unknown"
                for known_brand, aliases in brand_corrections.items():
                    if any(alias.lower() in brand.lower() for alias in aliases):
                        normalized_brand = known_brand
                        break
                brand = normalized_brand
                if brand == "Unknown":
                    brand = extracted_maker.strip().title()

                print(f"Assigned brand: {brand}")
                print(f"Assigned name: {name}")

                color = "Unknown"
                name_cleaned = name.replace(" ", "").lower()
                type_film_cleaned = type_film.replace(" ", "").lower()
                process_cleaned = process.replace(" ", "").lower()
                print(f"type_film_cleaned: {type_film_cleaned}")
                print(f"process_cleaned: {process_cleaned}")
                if ("colornegative" in type_film_cleaned or 
                    "colorreversal" in type_film_cleaned or 
                    "colorslide" in type_film_cleaned or 
                    "color" in type_film_cleaned or 
                    "color" in name_cleaned or 
                    "c-41" in process_cleaned or 
                    "e-6" in process_cleaned):
                    color = "Color"
                elif ("blackandwhite" in type_film_cleaned or 
                      "b&w" in type_film_cleaned or 
                      "b/w" in type_film_cleaned or 
                      "monochrome" in type_film_cleaned or 
                      "b&w" in name_cleaned or 
                      "b/w" in name_cleaned or 
                      "b&w" in process_cleaned or 
                      "b/w" in process_cleaned):
                    color = "Black and White"

                if "slidefilm" in type_film_cleaned or "slide" in name_cleaned:
                    color = "Slide Film"
                elif "cinefilm" in type_film_cleaned or "cine" in name_cleaned or "motionpicture" in type_film_cleaned or "motionpicture" in name_cleaned:
                    color = "Cine Film"

                if color == "Unknown":
                    link = cells[0].find("a") 
                    if link and "href" in link.attrs:
                        brand_page_url = "https://en.wikipedia.org" + link["href"]
                        try:
                            brand_page_response = requests.get(brand_page_url, headers=headers, timeout=5)
                            brand_page_response.raise_for_status()
                            brand_soup = BeautifulSoup(brand_page_response.text, "html.parser")
                            brand_page_text = brand_soup.get_text().replace(" ", "").lower()
                            print(f"Searching color in brand page text: {brand_page_text[:100]}...")
                            if "colornegative" in brand_page_text or "colorreversal" in brand_page_text or "colorslide" in brand_page_text or "color" in brand_page_text or "c-41" in brand_page_text or "e-6" in brand_page_text:
                                color = "Color"
                            elif "blackandwhite" in brand_page_text or "b&w" in brand_page_text or "b/w" in brand_page_text or "monochrome" in brand_page_text:
                                color = "Black and White"
                        except Exception as e:
                            print(f"Error accessing brand page {brand_page_url}: {e}")

                iso_value = "Unknown"
                iso_match = re.search(r'\d+', iso)
                if iso_match:
                    iso_value = iso_match.group()

                if iso_value == "Unknown":
                    formats_cleaned = formats.replace(" ", "").lower()
                    iso_match = re.search(r'iso\s*(\d+)', formats_cleaned)
                    if iso_match:
                        iso_value = iso_match.group(1)

                if iso_value == "Unknown":
                    name_cleaned = name.replace(" ", "").lower()
                    iso_match = re.search(r'\d+', name_cleaned)
                    if iso_match:
                        iso_value = iso_match.group()

                if iso_value == "Unknown":
                    link = cells[0].find("a") 
                    if link and "href" in link.attrs:
                        brand_page_url = "https://en.wikipedia.org" + link["href"]
                        try:
                            brand_page_response = requests.get(brand_page_url, headers=headers, timeout=5)
                            brand_page_response.raise_for_status()
                            brand_soup = BeautifulSoup(brand_page_response.text, "html.parser")
                            brand_page_text = brand_soup.get_text().replace(" ", "").lower()
                            iso_match = re.search(r'iso\s*(\d+)', brand_page_text)
                            if iso_match:
                                iso_value = iso_match.group(1)
                        except Exception as e:
                            print(f"Error accessing brand page for ISO {brand_page_url}: {e}")

                format_value = "Unknown"
                format_list = [f.strip() for f in formats.split(",")]
                desired_formats = ["35mm", "120", "110", "126", "127", "Instant"]
                for fmt in format_list:
                    fmt_cleaned = fmt.replace(" ", "").lower()
                    print(f"Checking format: {fmt_cleaned}")
                    if "35mm" in fmt_cleaned or "35 mm" in fmt_cleaned:
                        format_value = "35mm"
                        break
                    elif "120" in fmt_cleaned:
                        format_value = "120"
                        break
                    elif "110" in fmt_cleaned:
                        format_value = "110"
                        break
                    elif "126" in fmt_cleaned:
                        format_value = "126"
                        break
                    elif "127" in fmt_cleaned:
                        format_value = "127"
                        break
                    elif "instant" in fmt_cleaned or "polaroid" in fmt_cleaned:
                        format_value = "Instant"
                        break
                    elif "sheetfilm" in fmt_cleaned or "largeformat" in fmt_cleaned:
                        format_value = "Large Format"
                        break

                if format_value == "Unknown":
                    formats_cleaned = formats.replace(" ", "").lower()
                    if "35mm" in formats_cleaned or "35 mm" in formats_cleaned:
                        format_value = "35mm"
                    elif "120" in formats_cleaned:
                        format_value = "120"
                    elif "110" in formats_cleaned:
                        format_value = "110"
                    elif "126" in formats_cleaned:
                        format_value = "126"
                    elif "127" in formats_cleaned:
                        format_value = "127"
                    elif "instant" in formats_cleaned or "polaroid" in formats_cleaned:
                        format_value = "Instant"
                    elif "sheetfilm" in formats_cleaned or "largeformat" in formats_cleaned:
                        format_value = "Large Format"

                if format_value == "Unknown":
                    link = cells[0].find("a")  
                    if link and "href" in link.attrs:
                        brand_page_url = "https://en.wikipedia.org" + link["href"]
                        try:
                            brand_page_response = requests.get(brand_page_url, headers=headers, timeout=5)
                            brand_page_response.raise_for_status()
                            brand_soup = BeautifulSoup(brand_page_response.text, "html.parser")
                            brand_page_text = brand_soup.get_text().replace(" ", "").lower()
                            print(f"Searching format in brand page text: {brand_page_text[:100]}...")
                            if "35mm" in brand_page_text or "35 mm" in brand_page_text:
                                format_value = "35mm"
                            elif "120" in brand_page_text:
                                format_value = "120"
                            elif "110" in brand_page_text:
                                format_value = "110"
                            elif "126" in brand_page_text:
                                format_value = "126"
                            elif "127" in brand_page_text:
                                format_value = "127"
                            elif "instant" in brand_page_text or "polaroid" in brand_page_text:
                                format_value = "Instant"
                            elif "sheetfilm" in brand_page_text or "largeformat" in brand_page_text:
                                format_value = "Large Format"
                        except Exception as e:
                            print(f"Error accessing brand page {brand_page_url}: {e}")

                grain_value = "Unknown"
                if "fine" in grain or "very fine" in grain:
                    grain_value = "Fine"
                elif "medium" in grain or "medium-fine" in grain:
                    grain_value = "Medium"
                elif "coarse" in grain:
                    grain_value = "Coarse"

                if format_value == "Unknown":
                    format_value = "Unknown"

                if color == "Unknown":
                    color = "Unknown"

                film_data = {
                    "brand": brand,   
                    "name": name,         
                    "format": format_value,
                    "color": color,
                    "iso": iso_value,
                    "grain": grain_value,
                    "source_url": url
                }
                all_films.append(film_data)
                film_count += 1
                print(f"Successfully scraped film: {film_data['brand']} {film_data['name']} from {url}")
                print(f"Film data: {film_data}")

            except Exception as e:
                print(f"Error processing film row: {e}")
                continue

            time.sleep(delay)

        if film_count >= max_films:
            break

    print(f"Total films scraped: {len(all_films)}")
    return all_films

def save_scraped_films(db: Session, films: list):
    valid_formats = ["35mm", "120", "110", "126", "127", "Instant", "Large Format", "Unknown"]
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