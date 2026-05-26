"""
Schema LLM/RAG enhancements:
1. Add foundingDate + founder to LocalBusiness on index.html
2. Add HowTo schema blocks to service pages
3. Add about (City) + mentions (Service) to all BlogPosting schemas
4. Add serviceOutput to all Service schemas
"""
import json, re, os, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
htmldir = os.path.dirname(os.path.abspath(__file__))

SCRIPT_PATTERN = re.compile(
    r'(\s*<script[^>]+type=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)',
    re.IGNORECASE
)

# --- Task 1: LocalBusiness additions ---
FOUNDING_DATE = "2021-06"
FOUNDER = {"@type": "Person", "name": "Roland Smith"}

# --- Task 2: HowTo schemas ---
HOW_TO_SCHEMAS = {
    'carpet-cleaning.html': {
        "name": "How to Deep Clean Carpet with Hot Water Extraction",
        "description": "KC Clean Carpets' professional hot water extraction carpet cleaning process used in Kansas City homes and businesses.",
        "totalTime": "PT2H",
        "step": [
            {"@type": "HowToStep", "name": "Pre-Inspection", "text": "Technician assesses fiber type, soiling level, and problem areas before any cleaning begins."},
            {"@type": "HowToStep", "name": "Pre-Treatment", "text": "Specialized pre-spray is applied to break down embedded dirt, oils, and stains in carpet fibers."},
            {"@type": "HowToStep", "name": "Hot Water Extraction", "text": "High-pressure hot water is injected deep into carpet fibers and immediately extracted along with dirt, allergens, and residue."},
            {"@type": "HowToStep", "name": "Post-Grooming", "text": "Carpet fibers are groomed to restore pile direction, improve appearance, and speed up drying time."},
            {"@type": "HowToStep", "name": "Final Inspection", "text": "Technician walks through results with the customer to confirm satisfaction before leaving."},
        ]
    },
    'hardwood-cleaning.html': {
        "name": "How to Deep Clean Hardwood Floors Without Damage",
        "description": "KC Clean Carpets' professional hardwood floor deep cleaning process using pH-balanced solutions safe for all wood species.",
        "totalTime": "PT3H",
        "step": [
            {"@type": "HowToStep", "name": "Floor Inspection", "text": "Technician inspects finish type, wood species, and any problem areas such as staining, buildup, or finish damage."},
            {"@type": "HowToStep", "name": "Dry Debris Removal", "text": "Loose dirt, grit, and debris are carefully removed before wet cleaning to prevent scratching."},
            {"@type": "HowToStep", "name": "pH-Balanced Cleaning Solution Applied", "text": "A professional-grade, pH-neutral cleaner formulated for hardwood is applied to break down oils, grime, and embedded residue."},
            {"@type": "HowToStep", "name": "Machine Scrubbing", "text": "Low-moisture cleaning machine agitates the solution into grooves and grain without saturating the wood."},
            {"@type": "HowToStep", "name": "Extraction and Dry Buff", "text": "Cleaning solution and loosened soil are extracted. Floor is buffed dry to a streak-free finish."},
        ]
    },
    'upholstery-cleaning.html': {
        "name": "How to Clean Upholstery Professionally",
        "description": "KC Clean Carpets' fabric-safe upholstery cleaning process for sofas, chairs, and other upholstered furniture.",
        "totalTime": "PT1H30M",
        "step": [
            {"@type": "HowToStep", "name": "Fabric Code Check", "text": "Technician checks the manufacturer fabric code (W, S, WS, or X) to select the safe cleaning method."},
            {"@type": "HowToStep", "name": "Pre-Vacuum", "text": "Loose debris, pet hair, and dry soil are vacuumed from all surfaces before wet cleaning."},
            {"@type": "HowToStep", "name": "Pre-Spot Treatment", "text": "Stains and high-soil areas are pre-treated with the appropriate spotter for the fabric type."},
            {"@type": "HowToStep", "name": "Low-Moisture Cleaning", "text": "Fabric is cleaned with a low-moisture method appropriate for the fabric code to prevent shrinkage, bleeding, or watermarks."},
            {"@type": "HowToStep", "name": "Speed Drying", "text": "Air movers are used to accelerate drying so furniture can be used again quickly."},
        ]
    },
    'tile-grout-cleaning.html': {
        "name": "How to Clean Tile and Grout Professionally",
        "description": "KC Clean Carpets' tile and grout deep cleaning process to restore discolored grout lines and grimy tile surfaces.",
        "totalTime": "PT2H",
        "step": [
            {"@type": "HowToStep", "name": "Surface Inspection", "text": "Technician assesses grout type, tile material, and degree of soiling or discoloration."},
            {"@type": "HowToStep", "name": "Pre-Treatment Application", "text": "Alkaline or acid pre-spray is applied based on soil type to dissolve soap scum, grease, and mineral deposits."},
            {"@type": "HowToStep", "name": "High-Pressure Rotary Scrubbing", "text": "A turbo cleaning tool applies high-pressure hot water while simultaneously scrubbing and extracting soil from grout lines."},
            {"@type": "HowToStep", "name": "Detail Scrubbing", "text": "Edges, corners, and tight areas are hand-scrubbed to ensure complete cleaning."},
            {"@type": "HowToStep", "name": "Rinse and Extract", "text": "All cleaning solution and loosened soil are thoroughly rinsed and extracted, leaving tile and grout clean and nearly dry."},
        ]
    },
    'commercial-carpet-cleaning.html': {
        "name": "How Commercial Carpet Cleaning Works",
        "description": "KC Clean Carpets' commercial carpet cleaning process designed to minimize business disruption while delivering deep extraction results.",
        "totalTime": "PT4H",
        "step": [
            {"@type": "HowToStep", "name": "Walkthrough and Scheduling", "text": "Technician assesses traffic patterns, soil levels, and high-use zones. Cleaning is scheduled during off-hours to minimize disruption."},
            {"@type": "HowToStep", "name": "Furniture and Equipment Moving", "text": "Movable items are relocated to protect them and allow full carpet access."},
            {"@type": "HowToStep", "name": "Pre-Treatment of High-Traffic Zones", "text": "Heavily soiled pathways and spots are pre-sprayed with commercial-grade traffic lane cleaner."},
            {"@type": "HowToStep", "name": "Hot Water Extraction", "text": "Truck-mounted hot water extraction removes deep soil, allergens, and residue from carpet fibers throughout the space."},
            {"@type": "HowToStep", "name": "Speed Drying Setup", "text": "Air movers are positioned to accelerate drying so the space is back in service as quickly as possible."},
        ]
    },
    'sandless-refinishing.html': {
        "name": "How Sandless Hardwood Floor Refinishing Works",
        "description": "KC Clean Carpets' one-day sandless refinishing process that renews dull hardwood floors without the dust, mess, or downtime of traditional sanding.",
        "totalTime": "PT6H",
        "step": [
            {"@type": "HowToStep", "name": "Floor Assessment", "text": "Technician inspects the existing finish for compatibility with the sandless process, checking for wax coatings, deep scratches, or finish failure."},
            {"@type": "HowToStep", "name": "Deep Cleaning", "text": "Floor is thoroughly cleaned to remove all dirt, oils, and residue that would prevent adhesion of the new finish coat."},
            {"@type": "HowToStep", "name": "Light Abrasion", "text": "The existing finish is lightly abraded using a floor machine to create a mechanical bond without removing significant material."},
            {"@type": "HowToStep", "name": "New Finish Coat Application", "text": "A fresh coat of polyurethane or aluminum oxide finish is applied evenly across the floor."},
            {"@type": "HowToStep", "name": "Cure Time", "text": "Floor is left to cure for several hours before light foot traffic is allowed. Full cure takes 24–48 hours."},
        ]
    },
    'wax-removal.html': {
        "name": "How to Remove Wax Buildup from Hardwood Floors",
        "description": "KC Clean Carpets' wax removal process to strip built-up wax from hardwood floors before refinishing or applying a new protective coat.",
        "totalTime": "PT4H",
        "step": [
            {"@type": "HowToStep", "name": "Wax Identification", "text": "Technician confirms wax presence and type (paste wax, liquid wax, or mop-and-shine buildup) to select the correct solvent."},
            {"@type": "HowToStep", "name": "Wax Solvent Application", "text": "A mineral spirits or commercial wax stripper is applied in sections to dissolve the wax layer without damaging the wood beneath."},
            {"@type": "HowToStep", "name": "Mechanical Scrubbing", "text": "A floor machine with a stripping pad agitates the solvent to lift and loosen wax from the wood grain."},
            {"@type": "HowToStep", "name": "Wax Residue Removal", "text": "Dissolved wax and stripper are thoroughly removed with clean cloths and extraction, leaving bare wood surface."},
            {"@type": "HowToStep", "name": "Surface Preparation for Refinishing", "text": "Floor is inspected and confirmed clean and dry, ready for sandless refinishing or a new protective finish coat."},
        ]
    },
}

# --- Task 3: Blog post cities ---
BLOG_CITIES = {
    'blog-raytown-carpet-cleaning.html':         {"name": "Raytown",         "addressRegion": "MO"},
    'blog-kansas-city-carpet-cleaning.html':     {"name": "Kansas City",     "addressRegion": "MO"},
    'blog-lees-summit-carpet-cleaning.html':     {"name": "Lee's Summit",   "addressRegion": "MO"},
    'blog-overland-park-carpet-cleaning.html':   {"name": "Overland Park",   "addressRegion": "KS"},
    'blog-leawood-carpet-cleaning.html':         {"name": "Leawood",         "addressRegion": "KS"},
    'blog-liberty-carpet-cleaning.html':         {"name": "Liberty",         "addressRegion": "MO"},
    'blog-independence-carpet-cleaning.html':    {"name": "Independence",    "addressRegion": "MO"},
    'blog-gladstone-carpet-cleaning.html':       {"name": "Gladstone",       "addressRegion": "MO"},
    'blog-grandview-carpet-cleaning.html':       {"name": "Grandview",       "addressRegion": "MO"},
    'blog-north-kansas-city-carpet-cleaning.html': {"name": "North Kansas City", "addressRegion": "MO"},
    'blog-blue-springs-carpet-cleaning.html':    {"name": "Blue Springs",    "addressRegion": "MO"},
    'blog-olathe-carpet-cleaning.html':          {"name": "Olathe",          "addressRegion": "KS"},
}

# --- Task 4: Service output descriptions ---
SERVICE_OUTPUTS = {
    'carpet-cleaning.html':          "Deeply cleaned carpet free of dirt, allergens, pet odors, and stains with fast dry time",
    'hardwood-cleaning.html':        "Restored hardwood floors with pH-balanced deep clean and no residue",
    'upholstery-cleaning.html':      "Clean, refreshed upholstery safe for all fabric types",
    'tile-grout-cleaning.html':      "Restored grout lines and tile surfaces free of buildup and discoloration",
    'commercial-carpet-cleaning.html': "Clean commercial carpet with minimal disruption and fast dry time",
    'sandless-refinishing.html':     "Refinished hardwood floors with renewed shine, completed in one day without sanding",
    'wax-removal.html':              "Hardwood floors free of wax buildup, ready for refinishing or a new protective coat",
}


def inject_script_block(html, schema_obj):
    """Inject a new JSON-LD script block before </body>."""
    block = '\n<script type="application/ld+json">\n' + json.dumps(schema_obj, indent=2, ensure_ascii=False) + '\n</script>\n'
    return html.replace('</body>', block + '</body>', 1)


def process_index(text):
    changes = []

    def replace_script(m):
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        try:
            schema = json.loads(body.strip())
        except Exception:
            return m.group(0)
        if schema.get('@type') == 'LocalBusiness':
            modified = False
            if 'foundingDate' not in schema:
                schema['foundingDate'] = FOUNDING_DATE
                modified = True
                changes.append('added foundingDate')
            if 'founder' not in schema:
                schema['founder'] = FOUNDER
                modified = True
                changes.append('added founder')
            if modified:
                return open_tag + '\n' + json.dumps(schema, indent=2, ensure_ascii=False) + '\n' + close_tag
        return m.group(0)

    new_text = SCRIPT_PATTERN.sub(replace_script, text)
    return new_text, changes


def process_service_page(fn, text):
    changes = []

    def replace_script(m):
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        try:
            schema = json.loads(body.strip())
        except Exception:
            return m.group(0)
        if schema.get('@type') == 'Service' and fn in SERVICE_OUTPUTS:
            if 'serviceOutput' not in schema:
                schema['serviceOutput'] = {"@type": "Thing", "name": SERVICE_OUTPUTS[fn]}
                changes.append('added serviceOutput')
                return open_tag + '\n' + json.dumps(schema, indent=2, ensure_ascii=False) + '\n' + close_tag
        return m.group(0)

    new_text = SCRIPT_PATTERN.sub(replace_script, text)

    # Inject HowTo block if not already present
    if fn in HOW_TO_SCHEMAS:
        how_to_type = '{"@type": "HowTo"'
        if how_to_type not in new_text and '"HowTo"' not in new_text:
            schema_obj = {"@context": "https://schema.org", "@type": "HowTo"}
            schema_obj.update(HOW_TO_SCHEMAS[fn])
            new_text = inject_script_block(new_text, schema_obj)
            changes.append('added HowTo schema')

    return new_text, changes


def process_blog_page(fn, text):
    changes = []
    city_info = BLOG_CITIES[fn]

    def replace_script(m):
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        try:
            schema = json.loads(body.strip())
        except Exception:
            return m.group(0)
        if schema.get('@type') == 'BlogPosting':
            modified = False
            if 'about' not in schema:
                schema['about'] = {
                    "@type": "City",
                    "name": city_info['name'],
                    "addressRegion": city_info['addressRegion'],
                    "addressCountry": "US"
                }
                modified = True
                changes.append('added about (City)')
            if 'mentions' not in schema:
                schema['mentions'] = [
                    {"@type": "Service", "name": "Carpet Cleaning", "provider": {"@type": "LocalBusiness", "name": "KC Clean Carpets"}}
                ]
                modified = True
                changes.append('added mentions')
            if modified:
                return open_tag + '\n' + json.dumps(schema, indent=2, ensure_ascii=False) + '\n' + close_tag
        return m.group(0)

    new_text = SCRIPT_PATTERN.sub(replace_script, text)
    return new_text, changes


updated = 0
for fn in sorted(os.listdir(htmldir)):
    if not fn.endswith('.html') or fn == 'googleec7c327026e992ea.html':
        continue
    path = os.path.join(htmldir, fn)
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8')
    changes = []

    if fn == 'index.html':
        new_text, changes = process_index(text)
    elif fn in SERVICE_OUTPUTS or fn in HOW_TO_SCHEMAS:
        new_text, changes = process_service_page(fn, text)
    elif fn in BLOG_CITIES:
        new_text, changes = process_blog_page(fn, text)
    else:
        new_text = text

    if new_text != text:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        print(f'Fixed ({", ".join(changes)}): {fn}')
        updated += 1
    else:
        print(f'  Skip: {fn}')

print(f'\nTotal files updated: {updated}')
