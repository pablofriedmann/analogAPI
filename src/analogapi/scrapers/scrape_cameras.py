import requests
import re
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from ..models.camera import Camera
from ..database import get_db
import time
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_digital_camera(soup):
    keywords = ["digital camera", "digital slr", "megapixel", "ccd sensor", "cmos sensor"]
    content = soup.select_one("div#mw-content-text")
    if content:
        text = content.get_text(strip=True).lower()
        for keyword in keywords:
            if keyword in text:
                return True
    return False

def is_not_a_camera(camera_name, camera_url):
    name_lower = camera_name.lower()
    url_lower = camera_url.lower()
    if any(keyword in name_lower for keyword in ["film", "category", "template", "format", "cartridge", "encoding"]):
        return True
    if any(keyword in url_lower for keyword in ["category", "film", "cartridge"]):
        return True
    if name_lower in ["110 film", "126 film", "127 film", "120 film", "35mm film", "instant film", "dx encoding"]:
        return True
    if "led" in name_lower:
        return True
    if name_lower.isdigit() or name_lower in ["126", "110"]:
        return True
    return False

def scrape_cameras(max_cameras_per_category=10, max_categories=None, max_category_pages=1):
    max_categories = max_categories if max_categories is not None else 10
    max_cameras_per_category = max(max_cameras_per_category, 1)

    film_formats = [
        "https://camera-wiki.org/wiki/Category:35mm_film",
        "https://camera-wiki.org/wiki/Category:120_film",
        "https://camera-wiki.org/wiki/Category:127_film",
        "https://camera-wiki.org/wiki/Category:110_film",
        "https://camera-wiki.org/wiki/Category:126_film",
        "https://camera-wiki.org/wiki/Category:Large_format",
        "https://camera-wiki.org/wiki/Category:APS",
        "https://camera-wiki.org/wiki/Category:Disc_film",
        "https://camera-wiki.org/wiki/Category:Instant",
        "https://camera-wiki.org/wiki/Category:Minox",
    ]

    exclude_categories = ["Category:Digital", "Category:Digital_SLR", "Category:Mirrorless", "Category:Webcam"]
    headers = {"User-Agent": "AnalogAPI-Scraper/1.0 (pablofriedmann; https://github.com/pablofriedmann/analogAPI)"}
    delay = 1

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
    known_brands = [
        "Canon", "Nikon", "Hasselblad", "Pentax", "Mamiya", "Kodak", "Fujifilm", "Ilford", "Minox", "Polaroid",
        "Ricoh", "Agfa", "Argus", "Ansco", "Agilux", "Acro", "Adler", "Firstline", "Capital", "Accuraflex"
    ]

    for category_url in categories:
        if categories_processed >= max_categories:
            break

        print(f"Scraping category: {category_url}")
        category_cameras = []
        current_url = category_url
        page_count = 0

        while current_url and len(category_cameras) < max_cameras_per_category and page_count < max_category_pages:
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

                if is_not_a_camera(camera_name, camera_url):
                    print(f"Skipping non-camera page: {camera_name} ({camera_url})")
                    continue

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

                    # Inferir el formato desde la categoría
                    category_name = category_url.split("/")[-1].lower()
                    if "35mm_film" in category_name:
                        format = "35mm"
                    elif "120_film" in category_name:
                        format = "120"
                    elif "127_film" in category_name:
                        format = "127"
                    elif "110_film" in category_name:
                        format = "110"
                    elif "126_film" in category_name:
                        format = "126"
                    elif "large_format" in category_name:
                        format = "Large Format"
                    elif "aps" in category_name:
                        format = "APS"
                    elif "disc_film" in category_name:
                        format = "Disc Film"
                    elif "instant" in category_name:
                        format = "Instant"
                    elif "minox" in category_name:
                        format = "Minox"

                    content = camera_soup.select_one("div#mw-content-text")
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
                                        elif "medium format" in value or "120" in value:
                                            format = "120"
                                        elif "large format" in value:
                                            format = "Large Format"
                                        elif "110" in value:
                                            format = "110"
                                        elif "126" in value:
                                            format = "126"
                                        elif "127" in value:
                                            format = "127"
                                        elif "aps" in value:
                                            format = "APS"
                                        elif "disc film" in value:
                                            format = "Disc Film"
                                        elif "instant" in value or "polaroid" in value:
                                            format = "Instant"
                                        elif "minox" in value:
                                            format = "Minox"
                                        else:
                                            format = value
                                    if "type" in label:
                                        camera_type = value.title()
                                    if "years" in label or "produced" in label:
                                        years = value
                                    if "lens mount" in label:
                                        lens_mount = value.title()

                        paragraphs = content.select("p")
                        for p in paragraphs:
                            text = p.get_text(strip=True).lower()
                            # Extraer formato
                            if "format" in text and format == "Unknown":
                                if "35mm" in text:
                                    format = "35mm"
                                elif "medium format" in text or "120" in text:
                                    format = "120"
                                elif "large format" in text:
                                    format = "Large Format"
                                elif "110" in text:
                                    format = "110"
                                elif "126" in text:
                                    format = "126"
                                elif "127" in text:
                                    format = "127"
                                elif "aps" in text:
                                    format = "APS"
                                elif "disc film" in text:
                                    format = "Disc Film"
                                elif "instant" in text or "polaroid" in text:
                                    format = "Instant"
                                elif "minox" in text:
                                    format = "Minox"
                            if format == "Unknown":
                                if "35mm" in text:
                                    format = "35mm"
                                elif "medium format" in text or "120" in text:
                                    format = "120"
                                elif "large format" in text:
                                    format = "Large Format"
                                elif "110" in text:
                                    format = "110"
                                elif "126" in text:
                                    format = "126"
                                elif "127" in text:
                                    format = "127"
                                elif "aps" in text:
                                    format = "APS"
                                elif "disc film" in text:
                                    format = "Disc Film"
                                elif "instant" in text or "polaroid" in text:
                                    format = "Instant"
                                elif "minox" in text:
                                    format = "Minox"
                            # Extraer tipo
                            if ("type" in text or "camera" in text) and camera_type == "Unknown":
                                if "slr" in text:
                                    camera_type = "SLR"
                                elif "rangefinder" in text:
                                    camera_type = "Rangefinder"
                                elif "compact" in text or "point and shoot" in text:
                                    camera_type = "Point and Shoot"
                                elif "folding" in text:
                                    camera_type = "Folding"
                                elif "box" in text:
                                    camera_type = "Box"
                                elif "instant" in text or "polaroid" in text:
                                    camera_type = "Instant"
                                elif "tlr" in text:
                                    camera_type = "TLR"
                                elif "view camera" in text:
                                    camera_type = "View Camera"
                            # Extraer años
                            year_match = re.search(r"(introduced in|produced from|released in|made from)\s+(\d{4})", text)
                            if year_match and not years:
                                years = year_match.group(2)
                            range_match = re.search(r"(produced from|made from)\s+(\d{4})\s+to\s+(\d{4})", text)
                            if range_match and not years:
                                years = f"{range_match.group(2)}-{range_match.group(3)}"
                            if not years:
                                year_solo = re.search(r"\b(19\d{2}|20\d{2})\b", text)
                                if year_solo:
                                    years = year_solo.group(1)
                            # Extraer montura de lente
                            if "lens mount" in text and not lens_mount:
                                mount_match = re.search(r"lens mount\s*[:\s]*([a-zA-Z0-9\s-]+)(?=\s*(?:\.|$|\n))", text)
                                if mount_match:
                                    lens_mount = mount_match.group(1).strip().title()[:50]
                            elif "mount" in text and not lens_mount:
                                mount_match = re.search(r"mount\s*[:\s]*([a-zA-Z0-9\s-]+)(?=\s*(?:\.|$|\n))", text)
                                if mount_match:
                                    lens_mount = mount_match.group(1).strip().title()[:50]
                            if not lens_mount:
                                known_mounts = [
                                    "canon fd", "canon ef", "nikon f", "pentax k", "hasselblad v", "mamiya rb",
                                    "leica m", "minolta sr", "olympus om", "contax g", "zeiss zf", "m42", "k mount",
                                    "exakta", "praktica b", "rollei sl", "voigtlander bessamatic"
                                ]
                                for mount in known_mounts:
                                    if mount in text:
                                        lens_mount = mount.title()
                                        break
                            if not lens_mount:
                                mount_patterns = [
                                    r"\b(m\d+|fd|ef|f|k|v|rb|sr|om|g|zf)\b",
                                    r"\b(leica|canon|nikon|pentax|hasselblad|mamiya|minolta|olympus|contax|zeiss)\s+[a-z0-9-]+\b"
                                ]
                                for pattern in mount_patterns:
                                    mount_match = re.search(pattern, text)
                                    if mount_match:
                                        lens_mount = mount_match.group(0).title()
                                        break
                            if not lens_mount and camera_type in ["Folding", "Box", "TLR"]:
                                lens_mount = "Fixed Lens"

                    desired_formats = ["35mm", "110", "126", "127", "120", "Large Format", "APS", "Disc Film", "Instant", "Minox"]
                    if format != "Unknown" and not any(desired_format in format for desired_format in desired_formats):
                        print(f"Skipping camera with non-desired format: {camera_name} (format: {format})")
                        continue

                    name_parts = camera_name.split(" ", 1)
                    brand = name_parts[0] if name_parts[0] in known_brands else "Unknown"
                    model = name_parts[1] if len(name_parts) > 1 and name_parts[0] in known_brands else camera_name

                    if brand.isdigit() or "film" in model.lower():
                        print(f"Skipping camera with invalid brand or model: {camera_name} ({camera_url})")
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
    valid_formats = ["35mm", "120", "Large Format", "110", "126", "127", "APS", "Disc Film", "Instant", "Minox"]
    try:
        print(f"Attempting to save {len(cameras)} cameras")
        for camera_data in cameras:
            try:
                if camera_data["format"] not in valid_formats:
                    print(f"Skipping camera with invalid format: {camera_data['brand']} {camera_data['model']} (format: {camera_data['format']})")
                    continue

                existing_camera = db.query(Camera).filter(
                    Camera.brand.ilike(camera_data["brand"]),
                    Camera.model.ilike(camera_data["model"].replace(" ", ""))
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
                db.commit()
                print(f"Successfully added camera: {camera_data['brand']} {camera_data['model']}")
            except Exception as e:
                print(f"Error adding camera {camera_data['brand']} {camera_data['model']}: {e}")
                db.rollback()
                continue
        print(f"Successfully saved {len(cameras)} cameras to the database")
    except Exception as e:
        print(f"Error committing to database: {e}")
        db.rollback()
        raise