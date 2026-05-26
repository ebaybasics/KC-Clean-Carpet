"""
Fix W3C validation errors across all HTML files:
1. URL-encode spaces in src/href attribute paths (%20)
2. Move <style> from inside <main> to before </head> (index.html)
3. Move iframe width/height percentages to CSS (index.html)
"""
import os, re, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
htmldir = os.path.dirname(os.path.abspath(__file__))


def encode_spaces_in_paths(text):
    """URL-encode spaces in src and href attribute values (local file paths only)."""
    def encode_attr(m):
        attr = m.group(1)   # src or href
        quote = m.group(2)  # " or '
        value = m.group(3)  # the path value
        # Only encode if it contains a space and looks like a local path (no protocol)
        if ' ' in value and '://' not in value and not value.startswith('//'):
            value = value.replace(' ', '%20')
        return f'{attr}={quote}{value}{quote}'

    return re.sub(
        r'(src|href)=(["\'])([^"\']+)\2',
        encode_attr,
        text
    )


def fix_style_in_main(text):
    """Move any <style> blocks inside <main> to before </head>."""
    # Find all <style>...</style> blocks that appear after <main>
    main_start = text.find('<main')
    if main_start == -1:
        return text

    # Find style blocks inside main
    style_pattern = re.compile(r'(\n?<style>[\s\S]*?</style>\n?)', re.DOTALL)
    styles_to_move = []

    def collect_styles(m):
        if m.start() > main_start:
            styles_to_move.append(m.group(1))
            return ''  # remove from current location
        return m.group(0)  # leave in place

    new_text = style_pattern.sub(collect_styles, text)

    if styles_to_move:
        # Inject before </head>
        inject = '\n' + '\n'.join(s.strip() for s in styles_to_move) + '\n'
        new_text = new_text.replace('</head>', inject + '</head>', 1)

    return new_text


def fix_iframe_percent_dimensions(text):
    """Move width/height percentage attributes on iframes to inline CSS."""
    def fix_iframe(m):
        tag = m.group(0)
        # Remove width="100%" and height="100%" attributes
        tag = re.sub(r'\s*width="100%"', '', tag)
        tag = re.sub(r'\s*height="100%"', '', tag)
        # Add to existing style="" or create one
        if 'style="' in tag:
            tag = tag.replace('style="', 'style="width:100%; height:100%; ')
        else:
            tag = tag.replace('<iframe', '<iframe style="width:100%; height:100%;"')
        return tag

    return re.sub(
        r'<iframe\b[^>]*width="100%"[^>]*>|<iframe\b[^>]*height="100%"[^>]*>',
        fix_iframe,
        text,
        flags=re.DOTALL
    )


updated = 0
for fn in sorted(os.listdir(htmldir)):
    if not fn.endswith('.html') or fn == 'googleec7c327026e992ea.html':
        continue
    path = os.path.join(htmldir, fn)
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8')
    new_text = text
    changes = []

    # Fix 1: URL-encode spaces in paths (all pages)
    t = encode_spaces_in_paths(new_text)
    if t != new_text:
        changes.append('encoded spaces in paths')
        new_text = t

    # Fix 2: Move <style> out of <main> (mainly index.html)
    t = fix_style_in_main(new_text)
    if t != new_text:
        changes.append('moved style from main to head')
        new_text = t

    # Fix 3: iframe percent dimensions → CSS (index.html)
    t = fix_iframe_percent_dimensions(new_text)
    if t != new_text:
        changes.append('iframe dimensions to CSS')
        new_text = t

    if new_text != text:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        print(f'Fixed ({", ".join(changes)}): {fn}')
        updated += 1
    else:
        print(f'  Skip: {fn}')

print(f'\nTotal files updated: {updated}')
