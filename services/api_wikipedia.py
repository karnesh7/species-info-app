import wikipedia
import wikipediaapi

def get_wikipedia_info(species_name):
    result = {
        "summary": "Not available",
        "image": None,
        "url": None,
        "sections": {}
    }

    # First: Try to get summary, URL, and image using 'wikipedia'
    try:
        wikipedia.set_lang("en")
        page = wikipedia.page(species_name)
        result["summary"] = page.summary
        result["url"] = page.url

        for img in page.images:
            if img.lower().endswith((".jpg", ".jpeg", ".png")) and not any(kw in img.lower() for kw in ["icon", "logo", "flag", "map"]):
                result["image"] = img
                break
    except Exception as e:
        print(f"[Wikipedia summary/image error] {e}")

    # Second: Use wikipediaapi to extract structured sections
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,  # Safe for now
            user_agent='SpeciesInfoApp/1.0 (contact@example.com)'
        )
        page = wiki_wiki.page(species_name)

        print(f"\n[Wikipedia API Debug] Page exists: {page.exists()}")
        print(f"Title: {page.title}")
        print(f"Top-level sections: {len(page.sections)}")

        if page.exists():
            section_map = {
                "conservation": "Conservation Status",
                "status": "Conservation Status",
                "threat": "Conservation Status",

                "habitat": "Habitat / Distribution",
                "distribution": "Habitat / Distribution",
                "range": "Habitat / Distribution",
                "location": "Habitat / Distribution",
                "region": "Habitat / Distribution",

                "diet": "Diet",
                "feeding": "Diet",
                "food": "Diet",
                "foraging": "Diet",

                "behavior": "Behavior",
                "behaviour": "Behavior",
                "reproduction": "Behavior",
                "breeding": "Behavior",
                "nesting": "Behavior",

                "also known": "Also Known As",
                "other names": "Also Known As",
                "common names": "Also Known As",
                "etymology": "Also Known As",
                "name": "Also Known As"
            }


            def extract_sections(section):
                for subsection in section.sections:
                    title_lower = subsection.title.lower()
                    print(f"Found section: {subsection.title}")
                    for key, display in section_map.items():
                        if key in title_lower and subsection.text.strip():
                            # Clean up raw WIKI text into a single paragraph
                            clean_text = " ".join(subsection.text.strip().split())
                            result["sections"].setdefault(display, []).append(clean_text)
                    extract_sections(subsection)

            extract_sections(page)

            # Join multiple subsections for each category cleanly
            for key in result["sections"]:
                result["sections"][key] = "\n\n".join(result["sections"][key])
    except Exception as e:
        print(f"[Wikipedia API section error] {e}")

    return result
