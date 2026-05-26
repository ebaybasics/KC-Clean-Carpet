"""
Round 2 W3C fixes:
1. Remove duplicate <meta name="description"> tags (keep first)
2. Fix h2->h4 heading skips (change h4->h3 in card sections)
3. Fix <h1> inside <button> in schedule.html (change to <span>)
"""
import os, re, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
htmldir = os.path.dirname(os.path.abspath(__file__))


def remove_duplicate_meta_description(text):
    """Keep only the first <meta name="description"> tag."""
    pattern = re.compile(r'<meta\s+name="description"[^>]+>', re.IGNORECASE)
    matches = list(pattern.finditer(text))
    if len(matches) <= 1:
        return text
    # Remove all but the first
    for m in reversed(matches[1:]):
        # Remove the tag and its trailing newline if present
        start = m.start()
        end = m.end()
        if end < len(text) and text[end] == '\n':
            end += 1
        # Also remove leading whitespace on the same line
        while start > 0 and text[start-1] in (' ', '\t'):
            start -= 1
        text = text[:start] + text[end:]
    return text


def fix_h4_to_h3_in_cards(text, filename):
    """Change h4->h3 for card subheadings that skip h3 under h2 sections."""
    # Files and their specific card section patterns
    # Strategy: find all h4 tags that appear after an h2 with no intervening h3,
    # and change them to h3. Only in the main content, not footer.

    # For all affected files: replace <h4> and </h4> with <h3> and </h3>
    # But only within card/benefit/symptom/problem component divs
    card_classes = r'benefit-card|symptom-card|symptom-row|problem-item|danger-card|next-card'

    def replace_h4_in_card(m):
        tag_content = m.group(0)
        return tag_content.replace('<h4>', '<h3>').replace('</h4>', '</h3>')

    # Match card divs and replace h4 inside them
    text = re.sub(
        r'(<div\s+class="(?:' + card_classes + r')"[^>]*>[\s\S]*?</div>\s*</div>)',
        replace_h4_in_card,
        text
    )
    return text


def fix_h1_in_button(text):
    """Replace <h1> inside <button> with a styled <span>."""
    # Find <h1>...</h1> inside a <button>...</button>
    def replace_h1(m):
        inner = m.group(1)  # content inside h1
        # Use a span with display:block and the same visual weight
        return f'<span style="display:block; font-size:inherit; font-weight:inherit; line-height:inherit; margin:0;">{inner}</span>'

    # Only replace h1 that's inside a button context
    # Find button blocks and replace h1 inside them
    def fix_button(m):
        btn = m.group(0)
        btn = re.sub(r'<h1>([\s\S]*?)</h1>', replace_h1, btn)
        return btn

    text = re.sub(
        r'<button\b[^>]*>[\s\S]*?</button>',
        fix_button,
        text
    )
    return text


# Files needing heading fixes
heading_fix_files = {
    'blog-overland-park-carpet-cleaning.html',
    'sandless-refinishing-landing.html',
    'sandless-refinishing.html',
    'wax-removal-landing.html',
    'wax-removal.html',
}

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

    # Fix 1: duplicate meta description
    t = remove_duplicate_meta_description(new_text)
    if t != new_text:
        changes.append('removed duplicate meta description')
        new_text = t

    # Fix 2: h4->h3 in card sections
    if fn in heading_fix_files:
        t = fix_h4_to_h3_in_cards(new_text, fn)
        if t != new_text:
            changes.append('h4->h3 in cards')
            new_text = t

    # Fix 3: h1 inside button (schedule.html)
    if fn == 'schedule.html':
        t = fix_h1_in_button(new_text)
        if t != new_text:
            changes.append('h1->span in button')
            new_text = t

    if new_text != text:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        print(f'Fixed ({", ".join(changes)}): {fn}')
        updated += 1
    else:
        print(f'  Skip: {fn}')

print(f'\nTotal files updated: {updated}')
