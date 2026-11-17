# -*- coding: utf-8 -*-
"""Produit toutes les images de marque de FORSSUAP 78 à partir de brand/logo-sdis78-source.png :
en-tête des PDF, symbole, icônes de l'application web, icônes et écrans de démarrage Android.
Remplacer le fichier source par le logo officiel en haute définition, puis relancer : python3 tools/brand.py"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..')
P = lambda *a: os.path.join(ROOT, *a)
src = Image.open(P('brand', 'logo-sdis78-source.png')).convert('RGBA')

def disc(size, scale=1.0, bg=(255, 255, 255, 255)):
    """Logo rond centré sur un carré (fond blanc), réduit de « scale »."""
    canvas = Image.new('RGBA', (size, size), bg)
    s = max(1, int(size * scale))
    lg = src.resize((s, s), Image.LANCZOS)
    mask = Image.new('L', (s, s), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
    canvas.paste(lg, ((size - s) // 2, (size - s) // 2), mask)
    return canvas

# En-tête des PDF (format 480 x 297 attendu par les fiches) et symbole de la barre du haut
head = Image.new('RGB', (480, 297), 'white')
lg = disc(280).convert('RGB')
head.paste(lg, ((480 - 280) // 2, (297 - 280) // 2))
head.save(P('brand', 'logo-480.jpg'), quality=92)
disc(96).save(P('brand', 'symbole-96.png'))

# Application web
icons = P('docs', 'app', 'icons')
for name, size, scale in [('icon-1024.png', 1024, .96), ('icon-512.png', 512, .96), ('icon-192.png', 192, .96),
                          ('apple-touch-icon.png', 180, .9), ('maskable-512.png', 512, .72)]:
    disc(size, scale).convert('RGB').save(os.path.join(icons, name))
disc(512, .96).convert('RGB').save(P('docs', 'icon.png'))

# Android : icônes (anciennes et adaptatives) et écrans de démarrage, aux tailles déjà présentes
res = P('mobile', 'android', 'app', 'src', 'main', 'res')
for d in os.listdir(res):
    for f in os.listdir(os.path.join(res, d)):
        path = os.path.join(res, d, f)
        if not f.endswith('.png'):
            continue
        w, h = Image.open(path).size
        if f.startswith('ic_launcher_foreground'):
            disc(w, .62, bg=(0, 0, 0, 0)).save(path)          # zone sûre des icônes adaptatives
        elif f.startswith('ic_launcher'):
            disc(w, .94).save(path)
        elif f.startswith('splash'):
            img = Image.new('RGB', (w, h), 'white')
            s = int(min(w, h) * .45)
            img.paste(disc(s).convert('RGB'), ((w - s) // 2, (h - s) // 2))
            img.save(path)
print('Images FORSSUAP 78 produites.')
