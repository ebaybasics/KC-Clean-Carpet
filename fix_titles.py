"""
Update title tags and meta descriptions on service pages for CTR optimization.
"""
import re, os, sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
htmldir = os.path.dirname(os.path.abspath(__file__))

UPDATES = {
    'carpet-cleaning.html': {
        'title': 'Carpet Cleaning Kansas City | From $45/Room · 5-Star Rated',
        'meta': '5-star hot water extraction in Kansas City & Raytown. Pet stains, odors & allergens removed. Rooms from $45. Call KC Clean Carpets at (816) 715-1130.',
    },
    'hardwood-cleaning.html': {
        'title': 'Hardwood Floor Cleaning Kansas City | No Damage, No Residue',
        'meta': 'pH-balanced deep clean and buff for hardwood floors in Kansas City. Removes years of grime and restores shine — without warping or dulling your finish. 5-star rated. Call (816) 715-1130.',
    },
    'wax-removal.html': {
        'title': 'Hardwood Wax Removal Kansas City | Strip Old Wax, Restore Shine',
        'meta': 'Professional wax removal for hardwood floors in Kansas City. Strip yellowed, dulling buildup and prep your floors for refinishing. Call KC Clean Carpets at (816) 715-1130.',
    },
    'sandless-refinishing.html': {
        'title': 'Sandless Floor Refinishing Kansas City | Restore Like-New for Less',
        'meta': 'Restore most hardwood floors to brand-new condition in one day — no dust, no sanding, at a fraction of traditional refinishing cost. KC Clean Carpets, Kansas City. Call (816) 715-1130.',
    },
    'upholstery-cleaning.html': {
        'title': 'Upholstery & Couch Cleaning Kansas City | Safe for All Fabrics',
        'meta': 'Professional sofa, couch & chair cleaning in Kansas City. Fabric-code checked before every job — no shrinkage, no watermarks. Stains & odors removed. Call (816) 715-1130.',
    },
    'tile-grout-cleaning.html': {
        'title': 'Tile & Grout Cleaning Kansas City | Restore Discolored Grout Lines',
        'meta': 'High-pressure tile and grout cleaning in Kansas City. Restore discolored grout lines and grimy tile surfaces to like-new. Overland Park, Leawood & KC metro. Call (816) 715-1130.',
    },
    'commercial-carpet-cleaning.html': {
        'title': 'Commercial Carpet Cleaning Kansas City | After-Hours Scheduling',
        'meta': 'Professional commercial carpet cleaning in Kansas City. After-hours scheduling for offices, hotels, retail & medical facilities — minimal business disruption. Call (816) 715-1130.',
    },
}

title_pat = re.compile(r'(<title>)(.*?)(</title>)', re.IGNORECASE | re.DOTALL)
meta_dq = re.compile(r'(<meta\s+name="description"\s+content=")([^"]*?)(")', re.IGNORECASE)
meta_sq = re.compile(r"(<meta\s+name='description'\s+content=')([^']*?)(')", re.IGNORECASE)

updated = 0
for fn, changes in UPDATES.items():
    path = os.path.join(htmldir, fn)
    with open(path, 'rb') as f:
        text = f.read().decode('utf-8')

    new_text = text
    applied = []

    # Update title
    new_text, n = title_pat.subn(lambda m: m.group(1) + changes['title'] + m.group(3), new_text, count=1)
    if n:
        applied.append('title')

    # Update meta description (try double quotes first, then single)
    new_text, n = meta_dq.subn(lambda m: m.group(1) + changes['meta'] + m.group(3), new_text, count=1)
    if n:
        applied.append('meta')
    else:
        new_text, n = meta_sq.subn(lambda m: m.group(1) + changes['meta'] + m.group(3), new_text, count=1)
        if n:
            applied.append('meta')

    if new_text != text:
        with open(path, 'wb') as f:
            f.write(new_text.encode('utf-8'))
        print(f'Updated ({", ".join(applied)}): {fn}')
        updated += 1
    else:
        print(f'  No change: {fn}')

print(f'\nTotal files updated: {updated}')
