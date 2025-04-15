import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ..models.camera import Camera
from ..database import get_db
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_digital_camera(soup):
    """
    Determines if a camera is digital based on keywords in the page content.
    Args:
        soup (BeautifulSoup): Parsed HTML of the camera page.
    Returns:
        bool: True if the camera is digital, False otherwise.
    """
    keywords = ["digital", "sensor", "megapixel", "ccd", "cmos", "digital slr", "digital camera"]
    content = soup.select_one("div#mw-content-text")
    if content:
        text = content.get_text(strip=True).lower()
        for keyword in keywords:
            if keyword in text:
                return True
    return False

def scrape_cameras(max_cameras_per_category=10, max_categories=None, max_category_pages=1):
   
    max_categories = max_categories if max_categories is not None else 10
    max_cameras_per_category = max(max_cameras_per_category, 1) 

    film_formats = [
        "https://camera-wiki.org/wiki/Category:110_film",
        "https://camera-wiki.org/wiki/Category:126_film",
        "https://camera-wiki.org/wiki/Category:127_film",
        "https://camera-wiki.org/wiki/Category:120_film",
        "https://camera-wiki.org/wiki/Category:35mm_film",  
        "https://camera-wiki.org/wiki/Category:Medium_format",
        "https://camera-wiki.org/wiki/Category:Large_format",
        "https://camera-wiki.org/wiki/Category:Folding",  
        "https://camera-wiki.org/wiki/Category:SLR", 
        "https://camera-wiki.org/wiki/Category:Rangefinder"  #
    ]
        
    exclude_categories = [
        "Category:Digital",
        "Category:Digital_SLR",
        "Category:Mirrorless",
        "Category:Webcam"
    ]

    headers = {
        "User-Agent": "AnalogAPI-Scraper/1.0 (pablofriedmann; https://github.com/pablofriedmann/analogAPI)"
    }
    delay = 0.2  

    categories = []
    for format_url in film_formats:
        try:
            response = requests.get(format_url, headers=headers, timeout=5, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            category_name = format_url.split("/")[-1]
            if any(exclude in category_name for exclude in exclude_categories):
                print(f"Skipping excluded category: {category_name}")
                continue

            categories.append(format_url)
        except requests.RequestException as e:
            print(f"Error accessing format category {format_url}: {e}")
            continue

        time.sleep(delay)

    categories = categories[:max_categories]

    print(f"Found {len(categories)} categories: {categories}")

    all_cameras = []
    categories_processed = 0

    for category_url in categories:
        if categories_processed >= max_categories:
            break

        print(f"Scraping category: {category_url}")
        category_cameras = []
        current_url = category_url
        page_count = 0

        while current_url and len(category_cameras) < max_cameras_per_category:
            try:
                response = requests.get(current_url, headers=headers, timeout=5, verify=False)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error accessing {current_url}: {e}")
                break

            soup = BeautifulSoup(response.text, "html.parser")

            camera_links = soup.select("div#mw-pages li a")
            if not camera_links:
                print(f"No cameras found in {current_url}")
                break

            print(f"Found {len(camera_links)} camera links in {current_url}")

            for link in camera_links:
                if len(category_cameras) >= max_cameras_per_category:
                    break

                camera_url = "https://camera-wiki.org" + link["href"]
                camera_name = link.get_text(strip=True)

                name_parts = camera_name.split(" ", 1)
                brand = name_parts[0] if len(name_parts) > 0 else "Unknown"
                model = name_parts[1] if len(name_parts) > 1 else camera_name

                try:
                    camera_response = requests.get(camera_url, headers=headers, timeout=5, verify=False)
                    camera_response.raise_for_status()
                    camera_soup = BeautifulSoup(camera_response.text, "html.parser")

                    if is_digital_camera(camera_soup):
                        print(f"Skipping digital camera: {camera_name} at {camera_url}")
                        continue

                    format = "Unknown"
                    camera_type = "Unknown"
                    years = None
                    lens_mount = None

                    content = camera_soup.select_one("div#mw-content-text")
                    if content:
                        infobox = content.select_one("table.infobox")
                        if infobox:
                            rows = infobox.select("tr")
                            for row in rows:
                                cells = row.select("td")
                                if len(cells) >= 2:
                                    label = cells[0].get_text(strip=True).lower()
                                    value = cells[1].get_text(strip=True)
                                    if "format" in label:
                                        format = value
                                    if "type" in label:
                                        camera_type = value
                                    if "years" in label or "produced" in label:
                                        years = value
                                    if "lens mount" in label:
                                        lens_mount = value

                        paragraphs = content.select("p")
                        for p in paragraphs:
                            text = p.get_text(strip=True).lower()
                            # Format
                            if "format" in text and format == "Unknown":
                                if "35mm" in text:
                                    format = "35mm"
                                elif "medium format" in text:
                                    format = "Medium Format"
                                elif "large format" in text:
                                    format = "Large Format"
                                elif "110" in text:
                                    format = "110"
                                elif "126" in text:
                                    format = "126"
                                elif "127" in text:
                                    format = "127"
                                elif "120" in text:
                                    format = "120"
                            # Type
                            if ("type" in text or "camera" in text) and camera_type == "Unknown":
                                if "slr" in text:
                                    camera_type = "SLR"
                                elif "rangefinder" in text:
                                    camera_type = "Rangefinder"
                                elif "compact" in text:
                                    camera_type = "Compact"
                                elif "folding" in text:
                                    camera_type = "Folding"
                                elif "box" in text:
                                    camera_type = "Box"
                            # Years
                            if ("introduced in" in text or "produced from" in text or "released in" in text) and not years:
                                words = text.split()
                                for word in words:
                                    if word.isdigit() and 1800 <= int(word) <= 2025:
                                        years = word
                                        break
                            # Lens mount
                            if "lens mount" in text and not lens_mount:
                                pass  # We can improve this logic later

                    analog_formats = ["35mm", "110", "126", "127", "120", "Medium Format", "Large Format"]
                    if format != "Unknown" and not any(analog_format in format for analog_format in analog_formats):
                        print(f"Skipping camera with non-analog format: {camera_name} (format: {format})")
                        continue

                    camera_data = {
                        "brand": brand,
                        "model": model,
                        "format": format,
                        "type": camera_type,
                        "years": years,
                        "lens_mount": lens_mount,
                        "source_url": camera_url
                    }
                    category_cameras.append(camera_data)
                    print(f"Successfully scraped camera: {brand} {model} from {camera_url}")
                    print(f"Camera data: {camera_data}")

                except requests.RequestException as e:
                    print(f"Error scraping {camera_url}: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error while processing {camera_url}: {e}")
                    continue

                time.sleep(delay)

            next_page = soup.select_one("a[href*='pagefrom']")
            current_url = "https://camera-wiki.org" + next_page["href"] if next_page else None
            page_count += 1
            time.sleep(delay) 

        if category_cameras: 
            categories_processed += 1
        all_cameras.extend(category_cameras)
        print(f"Category {category_url} yielded {len(category_cameras)} cameras")

    print(f"Processed {categories_processed} categories with cameras")
    print(f"Total cameras scraped: {len(all_cameras)}")
    return all_cameras

def save_scraped_cameras(db: Session, cameras: list):
    try:
        print(f"Attempting to save {len(cameras)} cameras")
        for camera_data in cameras:
            try:
                print(f"Checking for existing camera: {camera_data['brand']} {camera_data['model']}")
                existing_camera = db.query(Camera).filter(
                    Camera.brand == camera_data["brand"],
                    Camera.model == camera_data["model"]
                ).first()

                if existing_camera:
                    print(f"Camera {camera_data['brand']} {camera_data['model']} already exists, skipping")
                    continue

                camera = Camera(
                    brand=camera_data["brand"],
                    model=camera_data["model"],
                    format=camera_data["format"],
                    type=camera_data["type"],
                    years=camera_data["years"],
                    lens_mount=camera_data["lens_mount"],
                    source_url=camera_data["source_url"]
                )
                print(f"Adding camera: {camera_data['brand']} {camera_data['model']}")
                db.add(camera)
            except Exception as e:
                print(f"Error adding camera {camera_data['brand']} {camera_data['model']}: {e}")
                continue

        print("Committing changes to database")
        db.commit()
        print(f"Successfully saved {len(cameras)} cameras to the database")
    except Exception as e:
        print(f"Error committing to database: {e}")
        db.rollback()
        raise