# -*- coding: utf-8 -*-
"""Extrait des RIOFE du SDIS 78 (PDF d'origine dans modeles/riofe/) :
- les fonds de page des fiches (docs/app/forms/riofe-*.png, 200 dpi, numéro d'annexe masqué),
- la géométrie mesurée de chaque fiche (lignes, cases à cocher, champs, colonnes MSP) en mm,
- le contenu : blocs, compétences associées, savoirs-agir, descripteurs NA / ECA / A, niveau minimal requis.
Sortie : data/riofe.json. Usage : python3 tools/riofe.py"""
import json, os, re
import pdfplumber
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..')
P = lambda *a: os.path.join(ROOT, *a)
MM = 25.4 / 72
FORMS = P('docs', 'app', 'forms')
SRC = {'TRA': P('modeles', 'riofe', 'RIOFE_EQ_SPV_MODULE_TRANSVERSE.pdf'), 'SUAP': P('modeles', 'riofe', 'RIOFE_EQ_SPV_SUAP.pdf')}

def mm(v):
    return round(v * MM, 2)

def words_in(page, x0, y0, x1, y1):
    ws = [w for w in page.extract_words(keep_blank_chars=False)
          if x0 <= (w['x0'] + w['x1']) / 2 <= x1 and y0 <= (w['top'] + w['bottom']) / 2 <= y1]
    ws.sort(key=lambda w: (round(w['top'] / 3), w['x0']))
    t = ' '.join(w['text'] for w in ws)
    return re.sub(r'\s+', ' ', t).replace(' ,', ',').replace(' .', '.').strip()

def uniq(vals, tol=1.5):
    out = []
    for v in sorted(vals):
        if not out or v - out[-1] > tol:
            out.append(v)
    return out

def render(pdf_path, pn, key, mask=None):
    """Fond de page à 200 dpi, palette 48 couleurs ; mask = zone (en points) blanchie (titre d'annexe)."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[pn - 1]
        img = page.to_image(resolution=200).original.convert('RGB')
    if mask:
        k = 200 / 72
        ImageDraw.Draw(img).rectangle([mask[0] * k, mask[1] * k, mask[2] * k, mask[3] * k], fill='white')
    img.quantize(colors=48, method=Image.Quantize.MEDIANCUT).save(os.path.join(FORMS, key + '.png'), optimize=True)

def vlines(page, xmin=0, xmax=10_000, minh=6, ymax=10_000):
    """Traits verticaux fins (rectangles de 0,5 pt de large) : {x arrondi : [rectangles]}."""
    d = {}
    for r in page.rects:
        if r['x1'] - r['x0'] < 1.5 and r['bottom'] - r['top'] > minh and xmin <= r['x0'] <= xmax and r['top'] < ymax:
            d.setdefault(round(r['x0'], 1), []).append(r)
    return d

def grid_bottom(page):
    w = find_word(page, 'OBSERVATIONS') or find_word(page, 'A=acquis')
    return w['top'] if w else page.height

def box_columns(page):
    """Les 3 colonnes de cases à cocher (après NA, ECA, A) : paires de traits verticaux distants de 11 à 21 pt
    qui partagent les mêmes lignes (dans la zone de la grille, au-dessus des observations)."""
    d = vlines(page, 150, ymax=grid_bottom(page))
    xs = sorted(x for x, v in d.items() if len(v) >= 3)
    tops = {x: {round(r['top']) for r in v} for x, v in d.items()}
    pairs = []
    for i, a in enumerate(xs):
        for b in xs[i + 1:]:
            if 10.5 < b - a < 21 and len(d[b]) >= 3 and len(tops[a] & tops[b]) >= 3:
                if not pairs or a - pairs[-1][0] > 20:
                    pairs.append((a, b))
                break
    pairs = pairs[-3:]
    return [(a, b, d[a]) for a, b in pairs]

def rows_from(rects, minh=6):
    spans = uniq([round(r['top'], 1) for r in rects if r['bottom'] - r['top'] > minh], 2)
    rows = []
    for t in spans:
        b = max(r['bottom'] for r in rects if abs(r['top'] - t) <= 2 and r['bottom'] - r['top'] > minh)
        rows.append((t, b))
    return rows

def find_word(page, text, after_y=0):
    for w in page.extract_words():
        if w['text'].startswith(text) and w['top'] >= after_y:
            return w
    return None

def formative_pages(pdf_path, pns, has_header=True):
    """Fiche formative (autoévaluation ou critériée) : 2 pages. Retourne géométrie + lignes avec descripteurs."""
    sheet = {'pages': [], 'rows': []}
    with pdfplumber.open(pdf_path) as pdf:
        for i, pn in enumerate(pns):
            page = pdf.pages[pn - 1]
            cols = box_columns(page)
            (b1x0, b1x1, b1r), (b2x0, b2x1, _), (b3x0, b3x1, _) = cols
            rows = rows_from(b1r)
            # en-tête de colonnes (« NON ACQUIS ») : ligne d'en-tête à ignorer
            hdr = find_word(page, 'NON')
            if hdr:
                rows = [r for r in rows if not (r[0] - 2 <= hdr['top'] <= r[1])]
            vs = sorted({round(e['x0'], 1) for e in page.edges if e['orientation'] == 'v' and e['bottom'] - e['top'] > 8})
            left = [v for v in vs if v < b1x0 - 30]
            # colonnes : compétence associée | savoir-agir | NA | case | ECA | case | A | case
            sa_x1 = max(v for v in vs if v < b1x0 - 60)
            sa_x0 = max(v for v in vs if v < sa_x1 - 30)
            comp_x0 = min(v for v in vs if v > 22)
            na = (sa_x1 + 4, b1x0 - 4)
            eca = (b1x1 + 4, b2x0 - 4)
            ac = (b2x1 + 4, b3x0 - 4)
            # groupes « compétence associée » (cellules fusionnées de la 1re colonne)
            comp_x1 = min(v for v in vs if v > comp_x0 + 40)
            dv = vlines(page, comp_x1 - 3, comp_x1 + 1.5, ymax=grid_bottom(page))
            groups = rows_from([r for v in dv.values() for r in v])
            pg = {'n': pn, 'boxes': [[mm(b1x0), mm(b1x1)], [mm(b2x0), mm(b2x1)], [mm(b3x0), mm(b3x1)]], 'rows': []}
            for (t, b) in rows:
                g = next((gg for gg in groups if gg[0] - 2 <= (t + b) / 2 <= gg[1] + 2), None)
                row = {'sa': words_in(page, sa_x0, t, sa_x1, b),
                       'NA': words_in(page, na[0], t, na[1], b), 'ECA': words_in(page, eca[0], t, eca[1], b), 'A': words_in(page, ac[0], t, ac[1], b),
                       'comp': words_in(page, comp_x0, g[0], sa_x0, g[1]) if g else '', 'page': i}
                sheet['rows'].append(row)
                pg['rows'].append([mm(t), mm(b)])
            # champs d'en-tête (1re page) et blocs observations / signatures (dernière page)
            f = {}
            for key, label in [('nom', 'Nom'), ('prenom', 'Prénom'), ('cis', 'CIS'), ('date', 'Date')]:
                w = find_word(page, label)
                if w and w['top'] < 200:
                    f[key] = [mm(w['x1'] + (36 if key == 'date' else 8)), mm((w['top'] + w['bottom']) / 2)]
            th = find_word(page, 'Thème')
            if th and th['top'] < 220:
                mi = find_word(page, 'Missions')
                rf = find_word(page, 'Réf.')
                theme_rects = [r for r in page.rects if r['x0'] > 100 and r['x0'] < 200 and r['top'] < th['bottom'] + 2 and r['bottom'] > th['top'] - 2 and r['bottom'] - r['top'] > 8]
                tr = max(theme_rects, key=lambda r: r['x1'] - r['x0']) if theme_rects else None
                if tr:
                    f['theme'] = [mm(tr['x0']), mm(tr['top']), mm(tr['x1']), mm(tr['bottom'])]
                    mrects = [r for r in page.rects if abs(r['x0'] - tr['x0']) < 3 and r['top'] >= tr['bottom'] - 2 and r['bottom'] - r['top'] > 8]
                    if mrects:
                        m = min(mrects, key=lambda r: r['top'])
                        f['missions'] = [mm(m['x0']), mm(m['top']), mm(m['x1']), mm(m['bottom'])]
                if rf:
                    f['ref'] = [mm(rf['x0'] - 4), mm(rf['bottom'] + 2), mm(rf['x0'] + 56), mm(rf['bottom'] + 30)]
            po = find_word(page, 'Points')
            if po and po['top'] > 200:
                ws = [w for w in page.extract_words() if w['text'] == 'Points']
                gr = [w for w in page.extract_words() if w['text'].startswith('Grade')]
                da = [w for w in page.extract_words() if w['text'] == 'Date' and w['top'] > (gr[0]['top'] if gr else 0)]
                bottom_obs = gr[0]['top'] - 12 if gr else po['top'] + 150
                f['pos'] = [mm(ws[0]['x0']), mm(ws[0]['bottom'] + 2), mm(ws[1]['x0'] - 8), mm(bottom_obs)]
                f['neg'] = [mm(ws[1]['x0']), mm(ws[1]['bottom'] + 2), mm(574), mm(bottom_obs)]
                if gr:
                    f['form'] = [mm(gr[0]['x0']), mm(gr[0]['bottom'] + 4), mm(gr[1]['x0'] - 8), mm(da[0]['top'] - 6) if da else mm(gr[0]['bottom'] + 50)]
                    f['app'] = [mm(gr[1]['x0']), mm(gr[1]['bottom'] + 4), mm(574), f['form'][3]]
                if da:
                    f['dform'] = [mm(da[0]['x0']), mm(da[0]['bottom'] + 4), f['form'][2], mm(da[0]['bottom'] + 60)]
                    f['dapp'] = [f['app'][0], mm(da[0]['bottom'] + 4), mm(574), mm(da[0]['bottom'] + 60)]
            pg['fields'] = f
            sheet['pages'].append(pg)
    return sheet

def sommative_page(pdf_path, pn, start_after=0, stop_before=10_000):
    """Grille sommative : colonnes MSP1..MSPn (centrées sur leurs intitulés), lignes repérées par le niveau minimal requis
    (« A » ou « ECA »), bornées par les traits horizontaux ; intertitres (compétences associées)."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[pn - 1]
        W = [w for w in page.extract_words() if start_after <= w['top'] < stop_before]
        niv = next(w for w in W if w['text'].startswith('Niveau'))
        msp = sorted([w for w in W if re.fullmatch(r'MS ?P?\d*', w['text']) and abs(w['top'] - niv['top']) < 12], key=lambda w: w['x0'])
        cx = [(w['x0'] + w['x1']) / 2 for w in msp]
        step = (cx[-1] - cx[0]) / (len(cx) - 1)
        cols = [[c - step / 2, c + step / 2] for c in cx]
        lvl_x0, lvl_x1 = niv['x0'] - 25, cols[0][0]
        left = min(e['x0'] for e in page.edges if e['orientation'] == 'v' and start_after <= e['top'] < stop_before)
        right = cols[-1][1]
        cover = {}
        for e in page.edges:
            if e['orientation'] == 'h' and e['x1'] - e['x0'] > 2:
                cover.setdefault(round(e['top'] * 2) / 2, []).append((e['x0'], e['x1']))
        def covered(segs):
            segs, tot, cur = sorted(segs), 0, None
            for a, b in segs:
                if cur is None or a > cur[1]:
                    if cur: tot += cur[1] - cur[0]
                    cur = [a, b]
                else:
                    cur[1] = max(cur[1], b)
            return tot + (cur[1] - cur[0] if cur else 0)
        H = sorted(y for y, s in cover.items() if covered(s) > (right - left) * .9)
        head_rects = [r for r in page.rects if r['x1'] - r['x0'] > (cols[-1][1] - left) * .8 and 6 < r['bottom'] - r['top'] < 22]
        in_head = lambda w: any(r['top'] - 1 <= (w['top'] + w['bottom']) / 2 <= r['bottom'] + 1 for r in head_rects)
        rows = []
        for w in W:
            if w['text'] in ('A', 'ECA') and lvl_x0 < (w['x0'] + w['x1']) / 2 < lvl_x1 and w['top'] > niv['bottom'] and not in_head(w):
                yc = (w['top'] + w['bottom']) / 2
                up = max([h for h in H if h < yc - 3] or [w['top'] - 8])
                dn = min([h for h in H if h > yc + 3] or [w['bottom'] + 8])
                rows.append({'sa': words_in(page, left, up, lvl_x0, dn), 'min': w['text'], 'y': [mm(up), mm(dn)]})
        rows.sort(key=lambda r: r['y'][0])
        heads, seen = [], set()
        for r in page.rects:
            if r['x1'] - r['x0'] > (cols[-1][1] - left) * .8 and 6 < r['bottom'] - r['top'] < 22 and niv['bottom'] < r['top'] < stop_before:
                tx = words_in(page, r['x0'], r['top'], r['x1'], r['bottom'])
                if tx and tx not in seen and 'MSP' not in tx and 'acquis' not in tx:
                    seen.add(tx)
                    heads.append([mm(r['top']), tx])
        heads.sort()
        f = {}
        for key, label in [('nom', 'Nom'), ('prenom', 'Prénom'), ('cis', 'CIS'), ('date', 'Date')]:
            w = next((w for w in page.extract_words() if w['text'].startswith(label) and w['top'] < 160), None)
            if w:
                f[key] = [mm(w['x1'] + (36 if key == 'date' else 8)), mm((w['top'] + w['bottom']) / 2)]
        return {'n': pn, 'cols': [[mm(a), mm(b)] for a, b in cols], 'rows': rows, 'heads': heads, 'fields': f}

def main():
    os.makedirs(FORMS, exist_ok=True)
    out = {}
    # ---- Équipier SUAP (RIOFE SUAP : fiches p.28-35) ----
    s = {}
    s['auto'] = formative_pages(SRC['SUAP'], [28, 29])
    s['crit'] = formative_pages(SRC['SUAP'], [30, 31])
    s['trans'] = formative_pages(SRC['SUAP'], [32, 33])
    s['somm'] = [sommative_page(SRC['SUAP'], 34), sommative_page(SRC['SUAP'], 35)]
    for key, pn in [('auto', 28), ('auto', 29), ('crit', 30), ('crit', 31), ('trans', 32), ('trans', 33)]:
        render(SRC['SUAP'], pn, f'riofe-suap-{key}-{pn}', mask=(70, 15, 520, 46) if pn in (28, 30, 32) else None)
    render(SRC['SUAP'], 34, 'riofe-suap-somm-34', mask=(70, 15, 520, 46))
    render(SRC['SUAP'], 35, 'riofe-suap-somm-35')
    out['SUAP'] = s
    # ---- Prompt Secours (RIOFE module transverse : fiches p.28-31, sommative PS p.33) ----
    t = {}
    t['auto'] = formative_pages(SRC['TRA'], [28, 29])
    t['crit'] = formative_pages(SRC['TRA'], [30, 31])
    t['somm'] = [sommative_page(SRC['TRA'], 33, 0, 520), sommative_page(SRC['TRA'], 33, 520)]
    for key, pn in [('auto', 28), ('auto', 29), ('crit', 30), ('crit', 31)]:
        render(SRC['TRA'], pn, f'riofe-ps-{key}-{pn}', mask=(70, 15, 520, 40) if pn in (28, 30) else None)
    render(SRC['TRA'], 33, 'riofe-ps-somm-33')
    out['PS'] = t
    # attestations d'assiduité (page scannée : champs mesurés à la main, en points, communs aux deux RIOFE)
    render(SRC['SUAP'], 26, 'riofe-suap-attest', mask=(70, 15, 520, 46))
    render(SRC['TRA'], 26, 'riofe-ps-attest', mask=(70, 15, 520, 46))
    json.dump(out, open(P('data', 'riofe.json'), 'w'), ensure_ascii=False, indent=1)
    for k, v in out.items():
        for sk in ('auto', 'crit', 'trans'):
            if sk in v:
                print(k, sk, 'lignes :', len(v[sk]['rows']))
        print(k, 'sommative :', [len(p['rows']) for p in v['somm']])

if __name__ == '__main__':
    main()
