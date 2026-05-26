"""
Fixes three Lighthouse accessibility issues across the site:
1. mob-svc-label: gold (#FFB300) text on white mobile drawer → change to navy (all pages)
2. related-posts h4: gold text on light gray background (blog pages) → change to navy
3. Blog body links: no underlines = distinguishable by color only → add underlines
4. svc-card links: img tags missing closing > and links lack aria-label (service pages)
"""
import os, re, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

htmldir = os.path.dirname(os.path.abspath(__file__))

def fix_mob_svc_label(text):
    """Change mob-svc-label color from gold to navy (passes contrast on white background)."""
    # Match the .mob-svc-label rule (single or multi-line) and swap only its color
    return re.sub(
        r'(\.mob-svc-label\s*\{[^}]*?)color:\s*var\(--kc-gold\)',
        r'\1color: var(--kc-blue-dark)',
        text,
        flags=re.DOTALL
    )

def fix_related_posts_h4(text):
    """Change related-posts h4 color from gold to navy (gold on #f5f7fb fails contrast)."""
    return re.sub(
        r'(\.related-posts\s+h4\s*\{[^}]*?)color:\s*var\(--kc-gold\)',
        r'\1color: var(--kc-blue-dark)',
        text,
        flags=re.DOTALL
    )

def add_post_body_link_underline(text):
    """Add underline rule for links in blog post body so they're not color-only."""
    # Only add if not already present
    if '.post-body a {' in text or '.post-body a{' in text:
        return text
    # Insert after the last .post-body rule block
    return re.sub(
        r'(\.post-body [^{]+\{[^}]+\})',
        lambda m: m.group(0),
        text
    ).replace(
        '.post-body .callout strong {',
        '.post-body a { color: var(--kc-blue); text-decoration: underline; }\n        .post-body .callout strong {'
    )

def fix_svc_card_links(text):
    """
    Fix svc-card links: add missing > to img tags and add aria-label to <a> tags.
    Pattern: <a href="..." class="svc-card"> wraps an img and an overlay with the label.
    """
    # Step 1: Fix missing > on img tags inside svc-cards
    # Pattern: alt="SOMETHING"\n (spaces) <div class="svc-card-overlay"
    text = re.sub(
        r'(alt="[^"]*")(\s*\n\s+<div\s+class="svc-card-overlay")',
        r'\1>\2',
        text
    )

    # Step 2: Add aria-label to svc-card <a> tags using the label text from svc-card-label span
    def add_aria_label(m):
        full = m.group(0)
        a_open = m.group(1)  # <a href="..." class="svc-card">
        label_text = m.group(2)  # text inside svc-card-label span
        # Unescape &amp; etc for the aria-label value
        label_clean = label_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
        # Only add if aria-label not already present
        if 'aria-label' in a_open:
            return full
        new_a = a_open.replace('class="svc-card"', f'class="svc-card" aria-label="{label_clean}"')
        return full.replace(a_open, new_a)

    text = re.sub(
        r'(<a\s+href="[^"]*"\s+class="svc-card">)'  # group 1: opening a tag
        r'[\s\S]*?'
        r'<span\s+class="svc-card-label">([^<]+)</span>',  # group 2: label text
        add_aria_label,
        text
    )
    return text

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

    # Fix 1: mob-svc-label color (all pages)
    t = fix_mob_svc_label(new_text)
    if t != new_text:
        changes.append('mob-svc-label color')
        new_text = t

    # Fix 2: related-posts h4 color (blog pages)
    if 'related-posts' in new_text:
        t = fix_related_posts_h4(new_text)
        if t != new_text:
            changes.append('related-posts h4 color')
            new_text = t

    # Fix 3: post-body link underlines (blog pages)
    if 'post-body' in new_text:
        t = add_post_body_link_underline(new_text)
        if t != new_text:
            changes.append('post-body link underlines')
            new_text = t

    # Fix 4: svc-card links (service pages)
    if 'svc-card' in new_text:
        t = fix_svc_card_links(new_text)
        if t != new_text:
            changes.append('svc-card links')
            new_text = t

    if new_text != text:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        print(f'Fixed ({", ".join(changes)}): {fn}')
        updated += 1
    else:
        print(f'  Skip: {fn}')

print(f'\nTotal files updated: {updated}')
