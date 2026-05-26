"""
Fix BreadcrumbList JSON-LD on service pages:
1. Change "Services" item URL from homepage to /#services anchor
2. Normalise all breadcrumb URLs to https://www.kccleancarpets.com/ (add www, https)
Also fix the visible HTML breadcrumb nav to match.
"""
import json, re, os, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
htmldir = os.path.dirname(os.path.abspath(__file__))

SERVICES_URL = 'https://www.kccleancarpets.com/#services'
BASE = 'https://www.kccleancarpets.com'

SCRIPT_PATTERN = re.compile(
    r'(<script[^>]+type=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)',
    re.IGNORECASE
)

def normalise_url(url):
    """Ensure URL uses https://www."""
    if not url:
        return url
    url = url.strip()
    # Fix http:// -> https://
    url = re.sub(r'^http://', 'https://', url)
    # Fix https://kccleancarpets.com -> https://www.kccleancarpets.com
    url = re.sub(r'^https://kccleancarpets\.com', 'https://www.kccleancarpets.com', url)
    return url

def fix_breadcrumb_schema(s):
    if s.get('@type') != 'BreadcrumbList':
        return s, False
    changed = False
    for item in s.get('itemListElement', []):
        # Fix URL normalisation
        url_field = item.get('item')
        if isinstance(url_field, dict):
            old = url_field.get('@id', '')
            new = normalise_url(old)
            if old != new:
                url_field['@id'] = new
                changed = True
            # Fix Services crumb pointing to homepage
            if item.get('name') == 'Services' and new in (BASE + '/', BASE):
                url_field['@id'] = SERVICES_URL
                changed = True
        elif isinstance(url_field, str):
            new = normalise_url(url_field)
            if new != url_field:
                item['item'] = new
                changed = True
            if item.get('name') == 'Services' and new in (BASE + '/', BASE):
                item['item'] = SERVICES_URL
                changed = True
    return s, changed

def process_file(text):
    changes = []

    def replace_script(m):
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        try:
            s = json.loads(body.strip())
        except Exception:
            return m.group(0)
        new_s, changed = fix_breadcrumb_schema(s)
        if changed:
            changes.append('fixed BreadcrumbList')
            return open_tag + '\n' + json.dumps(new_s, indent=2, ensure_ascii=False) + '\n' + close_tag
        return m.group(0)

    new_text = SCRIPT_PATTERN.sub(replace_script, text)

    # Also fix visible HTML breadcrumb nav links
    # Pattern: <a href="https://kccleancarpets.com/..." or href="http://..."
    def fix_href(m):
        attr, q, url, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        new_url = normalise_url(url)
        if new_url != url:
            changes.append('normalised href URL')
            return f'{attr}={q}{new_url}{q}{rest}'
        return m.group(0)

    new_text = re.sub(
        r'(href)=(["\'])(https?://kccleancarpets\.com[^"\']*?)(["\'])',
        fix_href,
        new_text
    )

    return new_text, changes

updated = 0
for fn in sorted(os.listdir(htmldir)):
    if not fn.endswith('.html') or fn == 'googleec7c327026e992ea.html':
        continue
    path = os.path.join(htmldir, fn)
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8')
    new_text, changes = process_file(text)
    if new_text != text:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        print(f'Fixed ({", ".join(set(changes))}): {fn}')
        updated += 1
    else:
        print(f'  Skip: {fn}')

print(f'\nTotal files updated: {updated}')
