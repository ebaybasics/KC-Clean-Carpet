"""
Fix Rich Results schema issues:
1. Remove incomplete LocalBusiness blocks from service pages
   (they reference the homepage entity via @id but lack required fields)
   The Service schema already has provider->@id pointing to the full LocalBusiness.
2. Add missing 'name' to Service schemas (required by schema.org)
3. Ensure BlogPosting image is a full URL (not relative)
"""
import json, re, os, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
htmldir = os.path.dirname(os.path.abspath(__file__))

# Service pages that have the incomplete LocalBusiness pattern
SERVICE_PAGES = {
    'carpet-cleaning.html', 'upholstery-cleaning.html', 'hardwood-cleaning.html',
    'tile-grout-cleaning.html', 'commercial-carpet-cleaning.html',
    'sandless-refinishing.html', 'wax-removal.html', 'carpet-cleaning-cost.html',
}

SCRIPT_PATTERN = re.compile(
    r'(\s*<script[^>]+type=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)',
    re.IGNORECASE
)

BASE_URL = 'https://www.kccleancarpets.com'


def process_file(fn, text):
    changes = []
    new_text = text

    def replace_script(m):
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        try:
            schema = json.loads(body.strip())
        except Exception:
            return m.group(0)  # leave unparseable blocks alone

        t = schema.get('@type', '')
        modified = False

        # Fix 1: Remove incomplete LocalBusiness from service pages
        # An incomplete one has @id referencing #business but no address/telephone
        if fn in SERVICE_PAGES and t == 'LocalBusiness':
            has_id = schema.get('@id', '').endswith('#business')
            has_address = bool(schema.get('address'))
            if has_id and not has_address:
                changes.append('removed incomplete LocalBusiness')
                return ''  # drop this entire script block

        # Fix 2: Add name to Service schemas if missing
        if t == 'Service' and not schema.get('name'):
            service_type = schema.get('serviceType', '')
            if service_type:
                schema['name'] = service_type
                modified = True
                changes.append(f'added Service.name="{service_type}"')

        # Fix 3: Ensure BlogPosting image is absolute URL
        if t == 'BlogPosting':
            img = schema.get('image', '')
            if img and not img.startswith('http'):
                schema['image'] = BASE_URL + ('/' if not img.startswith('/') else '') + img
                modified = True
                changes.append('made BlogPosting image URL absolute')

        if modified:
            new_body = '\n' + json.dumps(schema, indent=2, ensure_ascii=False) + '\n'
            return open_tag + new_body + close_tag
        return m.group(0)

    new_text = SCRIPT_PATTERN.sub(replace_script, new_text)
    # Clean up any double blank lines left by removed blocks
    new_text = re.sub(r'\n{3,}', '\n\n', new_text)

    return new_text, changes


updated = 0
for fn in sorted(os.listdir(htmldir)):
    if not fn.endswith('.html') or fn == 'googleec7c327026e992ea.html':
        continue
    path = os.path.join(htmldir, fn)
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8')

    new_text, changes = process_file(fn, text)

    if new_text != text:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        print(f'Fixed ({", ".join(changes)}): {fn}')
        updated += 1
    else:
        print(f'  Skip: {fn}')

print(f'\nTotal files updated: {updated}')
