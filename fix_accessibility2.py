"""
Round 2 accessibility fixes:
1. Remove aria-label from svc-card links (caused label-content-name-mismatch)
2. Fix sticky-fab opacity (0.65 → 1) to pass non-text contrast requirements
3. Add text-decoration:underline to breadcrumb links on blog pages
"""
import os, re, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
htmldir = os.path.dirname(os.path.abspath(__file__))


def remove_svc_card_aria_label(text):
    """Remove aria-label from svc-card links — the img alt text is sufficient."""
    return re.sub(
        r'(<a\s+href="[^"]*"\s+class="svc-card")\s+aria-label="[^"]*"',
        r'\1',
        text
    )


def fix_sticky_fab_opacity(text):
    """Replace opacity:.65 on sticky-fab links with opacity:1 (full opacity)."""
    # Match the .sticky-fab a rule and change opacity
    text = re.sub(
        r'(\.sticky-fab a\s*\{[^}]*?)opacity:\s*\.65',
        r'\1opacity: 1',
        text,
        flags=re.DOTALL
    )
    # Remove redundant opacity:1 from hover since it's now the default
    text = re.sub(
        r'(\.sticky-fab a:hover\s*\{[^}]*?)opacity:\s*1;\s*',
        r'\1',
        text,
        flags=re.DOTALL
    )
    return text


def add_breadcrumb_underline(text):
    """Add text-decoration:underline to breadcrumb links."""
    if 'text-decoration: underline' in text and '.breadcrumb a' in text:
        # Check if breadcrumb already has underline
        m = re.search(r'\.breadcrumb a\s*\{([^}]+)\}', text)
        if m and 'underline' in m.group(1):
            return text
    # Add underline to breadcrumb a rule
    return re.sub(
        r'(\.breadcrumb a\s*\{[^}]*?)(color:\s*var\(--kc-blue\);)',
        r'\1\2 text-decoration: underline;',
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

    # Fix 1: Remove aria-label from svc-cards (service pages)
    if 'svc-card" aria-label=' in new_text:
        t = remove_svc_card_aria_label(new_text)
        if t != new_text:
            changes.append('removed svc-card aria-label')
            new_text = t

    # Fix 2: sticky-fab opacity (all pages)
    if 'sticky-fab' in new_text and 'opacity: .65' in new_text:
        t = fix_sticky_fab_opacity(new_text)
        if t != new_text:
            changes.append('sticky-fab opacity→1')
            new_text = t

    # Fix 3: breadcrumb underline (blog pages and service pages with breadcrumb)
    if '.breadcrumb a' in new_text:
        t = add_breadcrumb_underline(new_text)
        if t != new_text:
            changes.append('breadcrumb underline')
            new_text = t

    if new_text != text:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        print(f'Fixed ({", ".join(changes)}): {fn}')
        updated += 1
    else:
        print(f'  Skip: {fn}')

print(f'\nTotal files updated: {updated}')
