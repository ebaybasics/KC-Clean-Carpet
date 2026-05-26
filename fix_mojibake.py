"""
Fixes mojibake in HTML files caused by reading UTF-8 files as cp1252 then writing back as UTF-8.

The corruption: UTF-8 bytes were interpreted as individual cp1252 characters,
then each cp1252 character was re-encoded as UTF-8. This script reverses that.
"""
import os, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

htmldir = os.path.dirname(os.path.abspath(__file__))


def make_mojibake(correct_str):
    """
    Generate the mojibake string that results from reading UTF-8 bytes as cp1252.
    For each byte in the UTF-8 encoding, decode it as cp1252 to get a character.
    Those characters, written back as UTF-8, become the mojibake.
    """
    utf8_bytes = correct_str.encode('utf-8')
    result = ''
    for b in utf8_bytes:
        try:
            result += bytes([b]).decode('cp1252')
        except (UnicodeDecodeError, ValueError):
            # Bytes undefined in cp1252 (0x81, 0x8D, 0x8F, 0x90, 0x9D)
            result += bytes([b]).decode('latin-1')
    return result


# All special characters and emoji used on the site that may be corrupted
# Order matters: longer strings first to avoid partial replacement
correct_chars = [
    '\U0001f4de',  # 📞 telephone receiver (4-byte emoji)
    '✗',  # ✗ cross mark
    '✓',  # ✓ check mark
    '✔',  # ✔ heavy check mark
    '★',  # ★ black star
    '─',  # ─ box drawings light horizontal
    '→',  # → right arrow
    '≤',  # ≤ less than or equal
    '≈',  # ≈ approximately equal
    '…',  # … ellipsis
    '–',  # – en dash
    '—',  # — em dash
    '‘',  # ' left single quote
    '’',  # ' right single quote
    '“',  # " left double quote
    '”',  # " right double quote
    '•',  # • bullet
    '™',  # ™ trademark
    '®',  # ® registered
    '©',  # © copyright
]

fixes = {}
for char in correct_chars:
    moji = make_mojibake(char)
    if moji != char:
        fixes[moji] = char

print(f'Mojibake fix map ({len(fixes)} entries):')
for bad, good in sorted(fixes.items(), key=lambda x: -len(x[0])):
    print(f'  {repr(bad)} -> {repr(good)} ({good})')

print()
updated = 0
for fn in sorted(os.listdir(htmldir)):
    if not fn.endswith('.html'):
        continue
    path = os.path.join(htmldir, fn)
    with open(path, 'rb') as f:
        raw = f.read()
    had_bom = raw.startswith(b'\xef\xbb\xbf')
    if had_bom:
        raw = raw[3:]
    text = raw.decode('utf-8')
    new_text = text
    # Apply longest replacements first to avoid partial matches
    for bad, good in sorted(fixes.items(), key=lambda x: -len(x[0])):
        new_text = new_text.replace(bad, good)
    if new_text != text or had_bom:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        notes = []
        if had_bom:
            notes.append('stripped BOM')
        changes = sum(text.count(b) for b in fixes)
        if changes:
            notes.append(f'{changes} replacements')
        print(f'Fixed ({", ".join(notes)}): {fn}')
        updated += 1

print(f'\nTotal files updated: {updated}')
