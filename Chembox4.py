import pygame
import math
import sys
import random

pygame.init()

# ═══════════════════════════════════════════════════════════════════════════════
# KONSTANTY A NASTAVENÍ
# ═══════════════════════════════════════════════════════════════════════════════
WIDTH, HEIGHT = 1600, 900
is_fullscreen = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("ChemSandbox Ultimate - Kvantovy Simulator Molekul")
clock = pygame.time.Clock()

def toggle_fullscreen():
    global screen, is_fullscreen, WIDTH, HEIGHT
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        info = pygame.display.Info()
        WIDTH, HEIGHT = info.current_w, info.current_h
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        WIDTH, HEIGHT = 1600, 900
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("ChemSandbox Ultimate - Kvantovy Simulator Molekul")
    return screen

# ─── BAREVNÁ PALETA (Premium Dark Neon) ───────────────────────────────────────
BG_COLOR      = (8, 10, 18)
BG_CANVAS     = (12, 15, 24)
GRID_COLOR    = (22, 26, 38)
UI_BG         = (14, 18, 28)
UI_PANEL      = (22, 28, 42)
UI_HOVER      = (38, 48, 72)
UI_ACTIVE     = (55, 120, 235)
UI_BORDER     = (40, 50, 75)
UI_SEPARATOR  = (32, 38, 58)
TEXT_COLOR    = (210, 218, 232)
TEXT_DIM      = (100, 110, 138)
TEXT_BRIGHT   = (240, 245, 255)
WHITE         = (255, 255, 255)
BLACK         = (0, 0, 0)
BOND_COLOR    = (140, 155, 175)
HIGHLIGHT     = (255, 210, 60)

# Specializované barvy
E_FREE_COLOR  = (255, 240, 80)     # Žlutá – volné valenční elektrony
E_BOND_COLOR  = (60, 230, 255)     # Tyrkysová – vazebné elektrony
ORBITAL_SP    = (70, 140, 255, 45) # Modrá – sp orbitaly
ORBITAL_SP2   = (60, 220, 140, 40) # Zelená – sp2
ORBITAL_SP3   = (170, 100, 255, 38)# Fialová – sp3
ORBITAL_P     = (255, 150, 60, 35) # Oranžová – p orbitaly
ORBITAL_S     = (200, 200, 255, 30)# Světlá – s orbital
H_BOND_COLOR  = (255, 200, 50)     # Vodíkové můstky
ALERT_BG      = (180, 40, 40)
ALERT_COLOR   = (255, 255, 255)

# Neon glow barvy
NEON_BLUE     = (40, 120, 255)
NEON_CYAN     = (0, 220, 255)
NEON_GREEN    = (0, 255, 140)
NEON_PURPLE   = (160, 80, 255)
NEON_ORANGE   = (255, 160, 40)
NEON_RED      = (255, 60, 80)
NEON_YELLOW   = (255, 230, 50)

# ─── FONTY ────────────────────────────────────────────────────────────────────
def get_font(size, bold=False):
    try:
        return pygame.font.SysFont("segoeui", size, bold=bold)
    except:
        return pygame.font.Font(None, size)

font_tiny    = get_font(12)
font_small   = get_font(14)
font_medium  = get_font(18)
font_large   = get_font(24, bold=True)
font_element = get_font(22, bold=True)
font_title   = get_font(32, bold=True)
font_huge    = get_font(42, bold=True)
font_desc    = get_font(15)

# ═══════════════════════════════════════════════════════════════════════════════
# DATABÁZE PRVKŮ
# Format: (barva, valence, hmotnost, český_název, max_vazeb, elektronegativita)
# ═══════════════════════════════════════════════════════════════════════════════
ELEMENTS = {
    #      barva             val  M      nazev        max_bonds  EN
    'H':  ((240, 240, 240), 1, 1.0,   'Vodík',      1, 2.20),
    'He': ((200, 255, 255), 2, 4.0,   'Helium',     0, 0.00),
    'Li': ((200, 100, 255), 1, 6.9,   'Lithium',    1, 0.98),
    'Be': ((150, 255, 150), 2, 9.0,   'Beryllium',  2, 1.57),
    'B':  ((255, 200, 150), 3, 10.8,  'Bor',        3, 2.04),  # BF3
    'C':  ((100, 100, 100), 4, 12.0,  'Uhlík',      4, 2.55),  # CH4
    'N':  ((80, 130, 255),  5, 14.0,  'Dusík',      3, 3.04),  # NH3 (3 vazby + 1 volny par)
    'O':  ((255, 65, 65),   6, 16.0,  'Kyslík',     2, 3.44),  # H2O (2 vazby + 2 volne pary)
    'F':  ((130, 255, 130), 7, 19.0,  'Fluor',      1, 3.98),  # HF
    'Ne': ((200, 255, 255), 8, 20.1,  'Neon',       0, 0.00),
    'Na': ((160, 100, 255), 1, 23.0,  'Sodík',      1, 0.93),
    'Mg': ((100, 200, 100), 2, 24.3,  'Hořčík',     2, 1.31),
    'Al': ((200, 200, 200), 3, 27.0,  'Hliník',     3, 1.61),  # AlCl3
    'Si': ((150, 150, 150), 4, 28.1,  'Křemík',     4, 1.90),  # SiH4
    'P':  ((255, 150, 50),  5, 31.0,  'Fosfor',     3, 2.19),  # PH3 (3 vazby + 1 volny par)
    'S':  ((255, 240, 50),  6, 32.1,  'Síra',       2, 2.58),  # H2S (2 vazby + 2 volne pary)
    'Cl': ((100, 255, 100), 7, 35.4,  'Chlor',      1, 3.16),  # HCl (1 vazba + 3 volne pary)
    'Ar': ((200, 255, 255), 8, 39.9,  'Argon',      0, 0.00),
    'K':  ((180, 120, 255), 1, 39.1,  'Draslík',    1, 0.82),
    'Ca': ((120, 220, 120), 2, 40.1,  'Vápník',     2, 1.00),
    'Ti': ((180, 180, 190), 4, 47.8,  'Titan',      4, 1.54),  # TiCl4
    'Fe': ((200, 100, 50),  8, 55.8,  'Železo',     6, 1.83),  # Fe(CN)6
    'Cu': ((255, 150, 100), 11,63.5,  'Měď',        4, 1.90),  # Cu komplexy
    'Zn': ((180, 180, 200), 2, 65.4,  'Zinek',      4, 1.65),  # Zn komplexy
    'Br': ((150, 50, 50),   7, 79.9,  'Brom',       1, 2.96),  # HBr
    'Ag': ((220, 220, 220), 1, 107.8, 'Stříbro',    2, 1.93),
    'I':  ((120, 50, 160),  7, 126.9, 'Jod',        1, 2.66),  # HI
    'Au': ((255, 215, 0),   11,196.9, 'Zlato',      4, 2.54),
    'Pt': ((210, 210, 220), 10,195.0, 'Platina',    6, 2.28),
    'Pb': ((100, 100, 120), 4, 207.2, 'Olovo',      4, 2.33),
    '*':  ((130, 130, 140), 1, 5.0,   'Zbytek (R)', 1, 2.50),
}

# Kategorie prvků pro periodickou tabulku
ELEMENT_CATEGORIES = {
    'H': 'nekov', 'He': 'vz_plyn', 'Li': 'alk_kov', 'Be': 'kov',
    'B': 'polokov', 'C': 'nekov', 'N': 'nekov', 'O': 'nekov',
    'F': 'halogen', 'Ne': 'vz_plyn', 'Na': 'alk_kov', 'Mg': 'kov',
    'Al': 'kov', 'Si': 'polokov', 'P': 'nekov', 'S': 'nekov',
    'Cl': 'halogen', 'Ar': 'vz_plyn', 'K': 'alk_kov', 'Ca': 'kov',
    'Ti': 'trans_kov', 'Fe': 'trans_kov', 'Cu': 'trans_kov',
    'Zn': 'trans_kov', 'Br': 'halogen', 'Ag': 'trans_kov',
    'I': 'halogen', 'Au': 'trans_kov', 'Pt': 'trans_kov',
    'Pb': 'kov', '*': 'special',
}

CATEGORY_COLORS = {
    'nekov':     (50, 180, 120),
    'kov':       (80, 140, 220),
    'alk_kov':   (180, 100, 255),
    'halogen':   (220, 180, 50),
    'vz_plyn':   (100, 200, 220),
    'polokov':   (180, 150, 100),
    'trans_kov': (200, 120, 80),
    'special':   (120, 120, 130),
}

# ═══════════════════════════════════════════════════════════════════════════════
# CHEMICKÉ POPISY A VYSVĚTLENÍ
# ═══════════════════════════════════════════════════════════════════════════════
HYBRIDIZATION_DESC = {
    's':     "Čistý s-orbital: Sféricky symetrický oblak.\nAtom nemá vazby, elektrony jsou v základním stavu.",
    'sp':    "Lineární geometrie (180°).\n2 sp-orbitaly + 2 nezkřížené p-orbitaly.\nPříklad: CO₂, C₂H₂ (acetylen).",
    'sp2':   "Trigonálně planární (120°).\n3 sp²-orbitaly v rovině + 1 p-orbital kolmý.\nPříklad: BF₃, ethylen (C₂H₄), grafen.",
    'sp3':   "Tetraedrická geometrie (109.5°).\n4 ekvivalentní sp³-orbitaly.\nPříklad: CH₄ (metan), H₂O, NH₃.",
    'sp3d':  "Trigonálně bipyramidální (90°/120°).\n5 orbitalů s d-účastí.\nPříklad: PCl₅, SF₄.",
    'sp3d2': "Oktaedrická geometrie (90°).\n6 ekvivalentních orbitalů.\nPříklad: SF₆, XeF₄.",
}

BOND_TYPE_DESC = {
    1: "Jednoduchá σ-vazba: Sdílení jednoho páru elektronů.\nVolná rotace kolem osy vazby.",
    2: "Dvojná vazba (σ + π): Sdílení dvou párů.\nBlokovaná rotace – planární geometrie.",
    3: "Trojná vazba (σ + 2π): Sdílení tří párů.\nNejkratší a nejsilnější kovalentní vazba.",
}

REACTION_DESCRIPTIONS = {
    'ionic_attraction': "IONTOVA INTERAKCE\nOpacne naboje se pritahuji Coulombovym zakonem:\nF = k*q1*q2/r2\nVznika iontova vazba (NaCl, KBr).",
    'h_bond': "VODIKOVY MUSTEK\nH vazany na F/O/N je silne d+.\nPritahuje volny e- par na sousednim F/O/N.\nKlicovy pro DNA, proteiny, vodu!",
    'polar_bond': "POLARNI KOVALENTNI VAZBA\nRozdil EN > 0.4: elektrony se presouvaji\nk elektronegativnejsimu atomu.\nVznika dipolovy moment d+...d-.",
    'nonpolar_bond': "NEPOLARNI KOVALENTNI VAZBA\nRozdil EN < 0.4: elektrony jsou sdileny\nrovnomerne. Symetricka distribuce naboje.",
    'electrophilic': "ELEKTROFILNI CENTRUM\nAtom s kladnym nabojem (d+ nebo kation).\nHleda elektronovy par - nukleofilni atak!\nPriklad: C v C=O skupine, H+.",
    'nucleophilic': "NUKLEOFILNI CENTRUM\nAtom se zapornym nabojem nebo volnym parem.\nNabizi elektrony elektrofilum.\nPriklad: O v H2O, N v NH3, Cl-.",
    'noble_gas': "VZACNY PLYN\nPlny valencni obal - maximalni stabilita.\nNetvori vazby za normalnich podminek.\nOktetove pravidlo je splneno.",
    'octet_complete': "OKTET KOMPLETNI\nAtom dosahl konfigurace vzacneho plynu.\n8 elektronu ve valencnim obalu.\nMaximalni termodynamicka stabilita.",
    'octet_incomplete': "NEKOMPLETNI OKTET\nAtom nema plny valencni obal.\nJe reaktivni - hleda elektrony nebo partnera\npro tvorbu vazby.",
}

# ═══════════════════════════════════════════════════════════════════════════════
# PŘEDDEFINOVANÉ MOLEKULY
# ═══════════════════════════════════════════════════════════════════════════════
PREDEF_MOLECULES = {
    'H₂O': {
        'atoms': [('O', 0, 0), ('H', -50, 40), ('H', 50, 40)],
        'bonds': [(0, 1, 1), (0, 2, 1)],
        'desc': 'Voda – základní rozpouštědlo života'
    },
    'CO₂': {
        'atoms': [('C', 0, 0), ('O', -70, 0), ('O', 70, 0)],
        'bonds': [(0, 1, 2), (0, 2, 2)],
        'desc': 'Oxid uhličitý – lineární, nepolární'
    },
    'NH₃': {
        'atoms': [('N', 0, 0), ('H', -45, 40), ('H', 45, 40), ('H', 0, -50)],
        'bonds': [(0, 1, 1), (0, 2, 1), (0, 3, 1)],
        'desc': 'Amoniak – pyramidální, zásada'
    },
    'CH₄': {
        'atoms': [('C', 0, 0), ('H', -50, -35), ('H', 50, -35), ('H', -50, 35), ('H', 50, 35)],
        'bonds': [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)],
        'desc': 'Metan – dokonalý tetraedr'
    },
    'NaCl': {
        'atoms': [('Na', -40, 0), ('Cl', 40, 0)],
        'bonds': [(0, 1, 1)],
        'ions': [(0, 1), (1, -1)],
        'desc': 'Chlorid sodný – iontová vazba'
    },
    'C₂H₄': {
        'atoms': [('C', -35, 0), ('C', 35, 0), ('H', -70, -35), ('H', -70, 35), ('H', 70, -35), ('H', 70, 35)],
        'bonds': [(0, 1, 2), (0, 2, 1), (0, 3, 1), (1, 4, 1), (1, 5, 1)],
        'desc': 'Ethylen – sp² hybridizace, planární'
    },
    'HCl': {
        'atoms': [('H', -35, 0), ('Cl', 35, 0)],
        'bonds': [(0, 1, 1)],
        'desc': 'Kyselina chlorovodíková – silná kyselina'
    },
    'O₂': {
        'atoms': [('O', -30, 0), ('O', 30, 0)],
        'bonds': [(0, 1, 2)],
        'desc': 'Molekulární kyslík – dvojná vazba'
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# POMOCNÉ FUNKCE
# ═══════════════════════════════════════════════════════════════════════════════
TOOL_CURSOR   = 0
TOOL_PAN      = 1
TOOL_ADD_ATOM = 2
TOOL_ADD_BOND = 3
TOOL_IONIZE   = 4

MODE_2D = 0
MODE_3D = 1

def get_bond_order(b_type):
    if b_type == 2: return 2
    if b_type == 3: return 3
    return 1

def get_en_color(en):
    """Barva podle elektronegativity: modrá (nízká) → bílá (střed) → červená (vysoká)."""
    if en == 0: return (120, 120, 120)
    if en < 2.0:
        t = max(0.0, en / 2.0)
        return (int(60 + 140*t), int(80 + 120*t), int(255 - 55*t))
    elif en < 3.0:
        t = (en - 2.0) / 1.0
        return (int(200 + 55*t), int(200 - 50*t), int(200 - 130*t))
    else:
        t = min(1.0, (en - 3.0) / 1.0)
        return (255, int(150 - 100*t), int(70 - 40*t))

def lerp_color(c1, c2, t):
    """Lineární interpolace barev."""
    t = max(0.0, min(1.0, t))
    return (int(c1[0] + (c2[0]-c1[0])*t),
            int(c1[1] + (c2[1]-c1[1])*t),
            int(c1[2] + (c2[2]-c1[2])*t))

def point_line_distance(px, py, x1, y1, x2, y2):
    l2 = (x1 - x2)**2 + (y1 - y2)**2
    if l2 == 0: return math.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1)*(x2 - x1) + (py - y1)*(y2 - y1)) / l2))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return math.hypot(px - proj_x, py - proj_y)

def draw_glow_circle(surface, color, pos, radius, intensity=1.0):
    """Vykreslí kruh s neonovým glow efektem."""
    for i in range(4):
        r = radius + i * 4
        alpha = int(max(5, min(80, 60 * intensity / (i + 1))))
        glow_surf = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (color[0], color[1], color[2], alpha),
                          (r+1, r+1), r)
        surface.blit(glow_surf, (int(pos[0] - r - 1), int(pos[1] - r - 1)))

def draw_soft_glow(surface, color, pos, radius):
    """Jemný glow pro elektrony."""
    for i in range(3):
        r = radius + i * 3
        alpha = max(5, 50 - i * 18)
        s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (color[0], color[1], color[2], alpha), (r+1, r+1), r)
        surface.blit(s, (int(pos[0] - r - 1), int(pos[1] - r - 1)))

def rotate_3d(x, y, z, angle_x, angle_y, angle_z=0):
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y1 = y * cos_x - z * sin_x
    z1 = y * sin_x + z * cos_x
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x2 = x * cos_y + z1 * sin_y
    z2 = -x * sin_y + z1 * cos_y
    return x2, y1, z2

# ═══════════════════════════════════════════════════════════════════════════════
# UI RENDERING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_ui_button(surface, rect, label, font, is_active=False, is_hovered=False,
                   accent_color=None, icon_char=None, time_val=0):
    """Premium UI tlačítko s glassmorphism efektem."""
    # Stín
    shadow = pygame.Surface((rect.width + 2, rect.height + 3), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 35))
    surface.blit(shadow, (rect.x, rect.y + 2))

    # Pozadí
    if is_active:
        bg = (42, 85, 190)
    elif is_hovered:
        bg = UI_HOVER
    else:
        bg = (20, 26, 40)
    pygame.draw.rect(surface, bg, rect, border_radius=8)

    # Horní lesk (glassmorphism)
    sheen_h = max(1, rect.height // 2 - 3)
    sheen = pygame.Surface((rect.width - 4, sheen_h), pygame.SRCALPHA)
    alpha = 30 if is_active else (20 if is_hovered else 8)
    sheen.fill((255, 255, 255, alpha))
    surface.blit(sheen, (rect.x + 2, rect.y + 2))

    # Levý akcentový proužek
    ac = accent_color if accent_color else (UI_ACTIVE if is_active else None)
    if ac:
        pygame.draw.rect(surface, ac,
                        pygame.Rect(rect.x + 3, rect.y + 6, 3, rect.height - 12),
                        border_radius=2)
    
    # Pulse efekt při hoveru
    if is_hovered and not is_active:
        pulse = abs(math.sin(time_val * 3)) * 0.3 + 0.7
        border_c = lerp_color((50, 60, 90), NEON_CYAN, pulse * 0.4)
    elif is_active:
        border_c = (80, 140, 255)
    else:
        border_c = (32, 40, 60)
    pygame.draw.rect(surface, border_c, rect, width=1, border_radius=8)

    # Ikona
    text_x = rect.x + 12
    if icon_char:
        icon_surf = font.render(icon_char, True, ac if ac else TEXT_DIM)
        surface.blit(icon_surf, (rect.x + 10, rect.y + (rect.height - icon_surf.get_height()) // 2))
        text_x = rect.x + 30

    # Text
    text_c = WHITE if (is_active or is_hovered) else TEXT_DIM
    txt_surf = font.render(label, True, text_c)
    ty = rect.y + (rect.height - txt_surf.get_height()) // 2
    surface.blit(txt_surf, (text_x, ty))

# ═══════════════════════════════════════════════════════════════════════════════
# VYLEPŠENÉ ORBITALY
# ═══════════════════════════════════════════════════════════════════════════════
def draw_hybridization_orbitals(surface, atom, sx, sy, radius, time):
    """Vykreslí hybridizační orbitaly s vylepšenou grafikou."""
    hyb = atom.hybridization

    # Vybrat barvu podle hybridizace
    if hyb == 's':     color = ORBITAL_S
    elif hyb == 'sp':  color = ORBITAL_SP
    elif hyb == 'sp2': color = ORBITAL_SP2
    elif hyb == 'sp3': color = ORBITAL_SP3
    else:              color = ORBITAL_SP3

    p_color = ORBITAL_P
    length = radius * 3.5

    # Pulzování (simulace vlnové funkce "dýchání")
    breath = 1.0 + math.sin(time * 1.5) * 0.08

    def draw_orbital_lobe(angle, col, scale=1.0):
        """Vykreslí jeden lalok orbitalu s gradientem průhlednosti."""
        l = length * scale * breath
        points = []
        steps = 28
        for i in range(steps):
            t = (i / steps) * 2 * math.pi
            # Tvar p-orbitalu (kapkovitý)
            shape_r = (math.cos(t) + 1) * (l / 2)
            shape_y = math.sin(t) * (l * 0.28)
            rx = shape_r * math.cos(angle) - shape_y * math.sin(angle)
            ry = shape_r * math.sin(angle) + shape_y * math.cos(angle)
            points.append((sx + rx, sy + ry))
        
        if len(points) > 2:
            # Vnější obal
            pygame.draw.polygon(surface, col, points)
            # Vnitřní jádro (silnější barva)
            inner_points = []
            for i in range(steps):
                t = (i / steps) * 2 * math.pi
                shape_r = (math.cos(t) + 1) * (l * 0.3)
                shape_y = math.sin(t) * (l * 0.16)
                rx = shape_r * math.cos(angle) - shape_y * math.sin(angle)
                ry = shape_r * math.sin(angle) + shape_y * math.cos(angle)
                inner_points.append((sx + rx, sy + ry))
            inner_col = (col[0], col[1], col[2], min(255, col[3] + 30))
            pygame.draw.polygon(surface, inner_col, inner_points)
            # Obrys
            outline_col = (col[0], col[1], col[2], min(255, col[3] + 60))
            pygame.draw.polygon(surface, outline_col, points, 1)

    # S-orbital jádro (pulzující kružnice)
    s_r = int(radius * 1.3 * breath)
    s_col = (color[0], color[1], color[2], 20)
    pygame.draw.circle(surface, s_col, (int(sx), int(sy)), s_r)
    pygame.draw.circle(surface, (color[0], color[1], color[2], 50),
                      (int(sx), int(sy)), s_r, 1)

    base_rot = time * 0.4

    if hyb == 'sp3':
        # Tetraedrické rozložení (2D projekce)
        angles = [0, math.pi/2, math.pi, 3*math.pi/2]
        for i, ang in enumerate(angles):
            draw_orbital_lobe(base_rot + ang, color, 0.9)
    elif hyb == 'sp2':
        # 3 sp2 v rovině + p kolmé
        for i in range(3):
            draw_orbital_lobe(base_rot + i * (2*math.pi/3), color)
        # p-orbital (kolmý – naznačen vertikálně)
        draw_orbital_lobe(base_rot + math.pi/2, p_color, 0.7)
        draw_orbital_lobe(base_rot - math.pi/2, p_color, 0.7)
    elif hyb == 'sp':
        # 2 sp lineárně + 2 p kolmé
        draw_orbital_lobe(base_rot, color, 1.1)
        draw_orbital_lobe(base_rot + math.pi, color, 1.1)
        draw_orbital_lobe(base_rot + math.pi/2, p_color, 0.65)
        draw_orbital_lobe(base_rot - math.pi/2, p_color, 0.65)
    elif hyb == 's':
        # Čistý s-orbital – jen zvětšená koule
        s2_r = int(length * 0.6 * breath)
        pygame.draw.circle(surface, color, (int(sx), int(sy)), s2_r)
        pygame.draw.circle(surface, (color[0], color[1], color[2], 60),
                          (int(sx), int(sy)), s2_r, 1)
    else:
        # sp3d, sp3d2
        count = 5 if hyb == 'sp3d' else 6
        for i in range(count):
            draw_orbital_lobe(base_rot + i * (2*math.pi/count), color, 0.85)

# ═══════════════════════════════════════════════════════════════════════════════
# ATOM
# ═══════════════════════════════════════════════════════════════════════════════
class Atom:
    def __init__(self, x, y, symbol):
        self.x, self.y, self.z = x, y, 0.0
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
        self.symbol = symbol
        data = ELEMENTS[symbol]
        self.color = data[0]
        self.base_valence = data[1]
        self.mass = max(1.0, data[2])
        self.max_bonds = data[4]
        self.en = data[5]
        self.en_eff = self.en
        self.delta_charge = 0.0
        self.base_radius = 18 + (self.mass ** 0.3) * 2.5
        self.ion_charge = 0
        self.is_dragged = False
        self.hybridization = "s"
        self.lone_pairs = 0
        self.steric_number = 0

        # Data pro orbity elektronů
        self.e_data = []
        for _ in range(8):
            self.e_data.append({
                'rot_x': random.uniform(0, 6.28),
                'rot_y': random.uniform(0, 6.28),
                'angle': random.uniform(0, 6.28),
                'speed': random.uniform(0.04, 0.10),
                'trail': [],  # Historie pozic pro trail efekt
            })

    @property
    def valence(self):
        return max(0, self.base_valence - self.ion_charge)

    @property
    def radius(self):
        return max(5, self.base_radius - (self.ion_charge * 4))

    def get_screen_pos(self, cam_x, cam_y, mode, view_rot_x, view_rot_y):
        if mode == MODE_2D:
            return self.x - cam_x, self.y - cam_y, self.radius, 0
        else:
            cx, cy, cz = self.x - cam_x, self.y - cam_y, self.z
            cos_x, sin_x = math.cos(view_rot_x), math.sin(view_rot_x)
            y1 = cy * cos_x - cz * sin_x
            z1 = cy * sin_x + cz * cos_x
            cos_y, sin_y = math.cos(view_rot_y), math.sin(view_rot_y)
            x2 = cx * cos_y + z1 * sin_y
            z2 = -cx * sin_y + z1 * cos_y
            z_dist = z2 + 800
            if z_dist < 10: z_dist = 10
            f = 800 / z_dist
            sx = x2 * f + WIDTH // 2
            sy = y1 * f + HEIGHT // 2
            return sx, sy, self.radius * f, z2

# ═══════════════════════════════════════════════════════════════════════════════
# BOND
# ═══════════════════════════════════════════════════════════════════════════════
class Bond:
    def __init__(self, atom1, atom2, b_type=1):
        self.a1 = atom1
        self.a2 = atom2
        self.type = b_type
        self.rest_length = self.a1.radius + self.a2.radius + 50

# ═══════════════════════════════════════════════════════════════════════════════
# SANDBOX – HLAVNÍ ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
class Sandbox:
    def __init__(self):
        self.atoms = []
        self.bonds = []
        self.cam_x, self.cam_y = 0, 0
        self.current_tool = TOOL_ADD_ATOM
        self.selected_symbol = 'C'
        self.ptable_open = False
        self.predef_open = False

        self.mode = MODE_2D
        self.show_electrons = True
        self.show_orbitals = False
        self.show_skeletal = False

        self.view_rot_x, self.view_rot_y = 0.0, 0.0
        self.dragging_atom = None
        self.bonding_start_atom = None
        self.hovered_atom = None
        self.hovered_bond = None
        self.panning = False
        self.last_mouse_pos = (0, 0)

        self.alert_message = ""
        self.alert_timer = 0

        self.h_bonds = []
        self.chem_descriptions = []  # Aktuální chemické popisy pro pravý panel
        self.event_log = []          # Historie dějů
        self.energy_history = []     # Historie energie pro graf

        # Layout konstanty
        self.SIDEBAR_W = 170
        self.DIAG_W = 310

        # ─── Tlačítka levého panelu ───
        btn_y = 72
        btn_h = 34
        btn_gap = 6
        bw = self.SIDEBAR_W - 20

        self.ui_buttons = []
        self.ui_labels = ["Kurzor", "Kamera", "Pridat Atom", "Vazba", "Ionizator"]
        self.ui_tools = [TOOL_CURSOR, TOOL_PAN, TOOL_ADD_ATOM, TOOL_ADD_BOND, TOOL_IONIZE]
        for i in range(5):
            self.ui_buttons.append(pygame.Rect(10, btn_y + i*(btn_h + btn_gap), bw, btn_h))

        sep1_y = btn_y + 5*(btn_h + btn_gap) + 4

        # Akční tlačítka
        self.btn_auto_h  = pygame.Rect(10, sep1_y + 18, bw, btn_h)
        self.btn_clear   = pygame.Rect(10, sep1_y + 18 + btn_h + btn_gap, bw, btn_h)
        self.btn_predef  = pygame.Rect(10, sep1_y + 18 + 2*(btn_h + btn_gap), bw, btn_h)

        sep2_y = sep1_y + 18 + 3*(btn_h + btn_gap) + 8

        # Zobrazení
        self.btn_mode      = pygame.Rect(10, sep2_y + 18, bw, btn_h)
        self.btn_skeletal  = pygame.Rect(10, sep2_y + 18 + (btn_h+btn_gap), bw, btn_h)
        self.btn_electrons = pygame.Rect(10, sep2_y + 18 + 2*(btn_h+btn_gap), bw, btn_h)
        self.btn_orbitals  = pygame.Rect(10, sep2_y + 18 + 3*(btn_h+btn_gap), bw, btn_h)

        sep3_y = sep2_y + 18 + 4*(btn_h + btn_gap) + 8

        # Prvek (periodická tabulka)
        self.btn_ptable = pygame.Rect(10, sep3_y + 18, bw, 88)

        sep4_y = sep3_y + 18 + 88 + 8

        # Nastavení
        self.btn_fullscreen = pygame.Rect(10, sep4_y + 18, bw, btn_h)

        # Umožníme scrollování, pokud se nevejde
        self.sep1_y = sep1_y
        self.sep2_y = sep2_y
        self.sep3_y = sep3_y
        self.sep4_y = sep4_y

    def show_alert(self, text):
        self.alert_message = text
        self.alert_timer = 220

    def log_event(self, text):
        self.event_log.append(text)
        if len(self.event_log) > 50:
            self.event_log.pop(0)

    # ─────────────── CHEMIE ───────────────────────────────────────────────────
    def calculate_chemistry(self):
        """Výpočet efektivní EN, parciálních nábojů, hybridizace a VSEPR."""
        for a in self.atoms:
            a.en_eff = a.en + (a.ion_charge * 1.5)

        for _ in range(3):
            temp_en = {a: a.en_eff for a in self.atoms}
            for a in self.atoms:
                if a.en == 0: continue
                shift = 0.0
                for b in self.bonds:
                    neighbor = b.a2 if b.a1 == a else (b.a1 if b.a2 == a else None)
                    if neighbor and neighbor.en != 0:
                        shift += (temp_en[neighbor] - temp_en[a]) * 0.25
                a.en_eff = a.en + (a.ion_charge * 1.5) + shift

        for a in self.atoms:
            a.delta_charge = (a.en_eff - a.en) if a.en != 0 else 0.0

            neighbors_count = 0
            bond_orders_sum = 0
            for b in self.bonds:
                if b.a1 == a or b.a2 == a:
                    neighbors_count += 1
                    bond_orders_sum += get_bond_order(b.type)

            lp = (a.valence - bond_orders_sum) / 2.0
            a.lone_pairs = max(0, math.floor(lp))
            a.steric_number = neighbors_count + a.lone_pairs

            if neighbors_count == 0:   a.hybridization = "s"
            elif a.steric_number <= 2: a.hybridization = "sp"
            elif a.steric_number == 3: a.hybridization = "sp2"
            elif a.steric_number == 4: a.hybridization = "sp3"
            elif a.steric_number == 5: a.hybridization = "sp3d"
            else:                      a.hybridization = "sp3d2"

    def generate_descriptions(self):
        """Generuje kontextové popisy chemických dějů."""
        self.chem_descriptions.clear()

        if not self.atoms:
            self.chem_descriptions.append(("Pridej atomy", "Klikni na platno pro pridani\natomu a zacni stavet molekulu.",
                                            NEON_CYAN))
            return

        # Analýza molekulárních vlastností
        total_mass = sum(a.mass for a in self.atoms)
        formula_parts = {}
        for a in self.atoms:
            if a.symbol != '*':
                formula_parts[a.symbol] = formula_parts.get(a.symbol, 0) + 1

        formula = ""
        # Hillova notace: C první, pak H, pak abecedně
        order = sorted(formula_parts.keys(), key=lambda s: (s != 'C', s != 'H', s))
        for sym in order:
            count = formula_parts[sym]
            formula += sym + (str(count) if count > 1 else "")

        if formula:
            self.chem_descriptions.append(("Sumarni vzorec",
                                            f"{formula}\nM = {total_mass:.1f} g/mol",
                                            TEXT_COLOR))

        # Analýza polarity
        if self.bonds:
            max_en_diff = 0
            most_polar = None
            for b in self.bonds:
                diff = abs(b.a1.en - b.a2.en)
                if diff > max_en_diff:
                    max_en_diff = diff
                    most_polar = b

            if max_en_diff > 1.7:
                self.chem_descriptions.append(("Iontovy charakter",
                    f"dEN = {max_en_diff:.2f} (>{1.7})\nVazba {most_polar.a1.symbol}-{most_polar.a2.symbol}\nje prevazne iontova.",
                    NEON_RED))
            elif max_en_diff > 0.4:
                self.chem_descriptions.append(("Polarni vazba",
                    f"dEN = {max_en_diff:.2f}\nVazba {most_polar.a1.symbol}-{most_polar.a2.symbol}\nvykazuje dipolovy moment.",
                    NEON_YELLOW))
            elif max_en_diff > 0 and self.bonds:
                self.chem_descriptions.append(("Nepolarni vazba",
                    f"dEN = {max_en_diff:.2f} (<0.4)\nElektrony jsou sdileny\nrovnomerne.",
                    NEON_GREEN))

        # Vodíkové můstky
        if self.h_bonds:
            self.chem_descriptions.append(("H-mustky aktivni",
                f"Detekovano {len(self.h_bonds)} vodikovych\nmustku. Stabilizuji strukturu\n(klicove pro H2O, DNA, proteiny).",
                H_BOND_COLOR))

        # Ionty
        cations = [a for a in self.atoms if a.ion_charge > 0]
        anions = [a for a in self.atoms if a.ion_charge < 0]
        if cations or anions:
            ion_text = ""
            if cations:
                ion_text += f"Kationty: {', '.join(a.symbol+'+' for a in cations[:3])}\n"
            if anions:
                ion_text += f"Anionty: {', '.join(a.symbol+'-' for a in anions[:3])}\n"
            if cations and anions:
                ion_text += "Coulombovská přitažlivost aktivní!"
            self.chem_descriptions.append(("Iontove interakce", ion_text.strip(), NEON_PURPLE))

        # Hovered atom detaily
        if self.hovered_atom and self.hovered_atom.symbol != '*':
            ha = self.hovered_atom
            hyb_desc = HYBRIDIZATION_DESC.get(ha.hybridization, "")
            self.chem_descriptions.append((f"{ha.symbol} - {ha.hybridization}",
                                            hyb_desc, NEON_CYAN))

            # Reaktivita
            tot_charge = ha.delta_charge + ha.ion_charge
            if tot_charge > 0.15:
                self.chem_descriptions.append(("Elektrofil",
                    REACTION_DESCRIPTIONS['electrophilic'], NEON_RED))
            elif tot_charge < -0.15:
                self.chem_descriptions.append(("Nukleofil",
                    REACTION_DESCRIPTIONS['nucleophilic'], (100, 150, 255)))

        # Hovered bond detaily
        if self.hovered_bond:
            hb = self.hovered_bond
            desc = BOND_TYPE_DESC.get(hb.type, "")
            en_diff = abs(hb.a1.en - hb.a2.en)
            bond_name = f"{hb.a1.symbol}–{hb.a2.symbol}"
            extra = f"\nΔEN({bond_name}) = {en_diff:.2f}"
            if en_diff > 0.4:
                extra += f"\nδ+ na {hb.a1.symbol if hb.a1.en < hb.a2.en else hb.a2.symbol}"
                extra += f", δ- na {hb.a2.symbol if hb.a1.en < hb.a2.en else hb.a1.symbol}"
            self.chem_descriptions.append((f"Vazba {bond_name}", desc + extra, NEON_ORANGE))

    # ─────────────── FYZIKA ───────────────────────────────────────────────────
    def apply_physics(self):
        self.calculate_chemistry()
        self.h_bonds.clear()

        # Vodíkové můstky
        for a1 in self.atoms:
            if a1.symbol in ['O', 'N', 'F']:
                for a2 in self.atoms:
                    if a2.symbol == 'H' and a1 != a2:
                        is_polarized = False
                        for b in self.bonds:
                            if ((b.a1 == a2 and b.a2.symbol in ['O','N','F']) or
                                (b.a2 == a2 and b.a1.symbol in ['O','N','F'])):
                                is_polarized = True; break
                        if is_polarized:
                            is_cov = any((b.a1==a1 and b.a2==a2) or (b.a1==a2 and b.a2==a1)
                                        for b in self.bonds)
                            if not is_cov:
                                dx = a2.x - a1.x; dy = a2.y - a1.y; dz = a2.z - a1.z
                                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                                if dist < 150 and dist > 0.1:
                                    self.h_bonds.append((a1, a2))
                                    force = (150 - dist) * 0.05
                                    fx = (dx/dist)*force; fy = (dy/dist)*force; fz = (dz/dist)*force
                                    if not a1.is_dragged:
                                        a1.vx += fx/a1.mass; a1.vy += fy/a1.mass; a1.vz += fz/a1.mass
                                    if not a2.is_dragged:
                                        a2.vx -= fx/a2.mass; a2.vy -= fy/a2.mass; a2.vz -= fz/a2.mass

        # Repulze + Coulomb
        for i in range(len(self.atoms)):
            for j in range(i+1, len(self.atoms)):
                a1, a2 = self.atoms[i], self.atoms[j]
                dx = a2.x-a1.x; dy = a2.y-a1.y; dz = a2.z-a1.z
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                if dist < 0.1: dist = 0.1

                min_dist = a1.radius + a2.radius + 30
                force = 0.0
                if dist < min_dist:
                    force = (min_dist - dist) * 0.2

                tc1 = a1.delta_charge + a1.ion_charge
                tc2 = a2.delta_charge + a2.ion_charge
                charge_factor = tc1 * tc2 * 300
                if abs(charge_factor) > 0.01 and dist < min_dist + 200:
                    c_force = charge_factor / dist
                    if c_force < -1.5: c_force = -1.5
                    force += c_force

                if force != 0.0:
                    fx = (dx/dist)*force; fy = (dy/dist)*force; fz = (dz/dist)*force
                    if not a1.is_dragged:
                        a1.vx -= fx/a1.mass; a1.vy -= fy/a1.mass; a1.vz -= fz/a1.mass
                    if not a2.is_dragged:
                        a2.vx += fx/a2.mass; a2.vy += fy/a2.mass; a2.vz += fz/a2.mass

        # VSEPR úhlové síly
        for a in self.atoms:
            neighbors = []
            for b in self.bonds:
                if b.a1 == a: neighbors.append(b.a2)
                elif b.a2 == a: neighbors.append(b.a1)

            n_count = len(neighbors)
            if n_count < 2: continue

            if a.hybridization == "sp":     base_angle = math.pi
            elif a.hybridization == "sp2":  base_angle = math.pi * 2/3
            elif a.hybridization == "sp3":  base_angle = math.radians(109.5)
            elif a.hybridization == "sp3d": base_angle = math.pi / 2
            else:                           base_angle = math.pi / 2

            target_angle = base_angle - math.radians(a.lone_pairs * 2.5)

            for i_n in range(n_count):
                for j_n in range(i_n+1, n_count):
                    n1, n2 = neighbors[i_n], neighbors[j_n]
                    L1 = a.radius + n1.radius + 50
                    L2 = a.radius + n2.radius + 50
                    ideal_dist = math.sqrt(L1**2 + L2**2 - 2*L1*L2*math.cos(target_angle))

                    dx = n2.x-n1.x; dy = n2.y-n1.y; dz = n2.z-n1.z
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if dist < 0.1: dist = 0.1

                    diff = dist - ideal_dist
                    force = diff * 0.08
                    fx = (dx/dist)*force; fy = (dy/dist)*force; fz = (dz/dist)*force
                    if not n1.is_dragged:
                        n1.vx += fx/n1.mass; n1.vy += fy/n1.mass; n1.vz += fz/n1.mass
                    if not n2.is_dragged:
                        n2.vx -= fx/n2.mass; n2.vy -= fy/n2.mass; n2.vz -= fz/n2.mass

        # Pružiny vazeb
        for bond in self.bonds:
            a1, a2 = bond.a1, bond.a2
            dx = a2.x-a1.x; dy = a2.y-a1.y; dz = a2.z-a1.z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < 0.1: dist = 0.1
            force = (dist - bond.rest_length) * 0.1
            fx = (dx/dist)*force; fy = (dy/dist)*force; fz = (dz/dist)*force
            if not a1.is_dragged:
                a1.vx += fx/a1.mass; a1.vy += fy/a1.mass; a1.vz += fz/a1.mass
            if not a2.is_dragged:
                a2.vx -= fx/a2.mass; a2.vy -= fy/a2.mass; a2.vz -= fz/a2.mass

        # Pohyb + tlumení
        total_ke = 0.0
        for a in self.atoms:
            if not a.is_dragged:
                a.x += a.vx; a.y += a.vy; a.z += a.vz
            if self.mode == MODE_2D and not a.is_dragged:
                a.z *= 0.95
            a.vx *= 0.8; a.vy *= 0.8; a.vz *= 0.8
            total_ke += 0.5 * a.mass * (a.vx**2 + a.vy**2 + a.vz**2)

        self.energy_history.append(total_ke)
        if len(self.energy_history) > 200:
            self.energy_history.pop(0)

    # ─────────────── AUTO VODÍKY ──────────────────────────────────────────────
    def auto_hydrogen(self):
        new_atoms = []
        new_bonds = []
        for a in self.atoms:
            if a.symbol in ['H', '*', 'He', 'Ne', 'Ar', 'Kr', 'Xe']: continue
            current = sum(get_bond_order(b.type) for b in self.bonds if b.a1 == a or b.a2 == a)
            target = a.max_bonds
            free = max(0, target - current)
            for k in range(free):
                angle = k * (2*math.pi / max(1, free)) + random.uniform(-0.3, 0.3)
                hx = a.x + 55 * math.cos(angle)
                hy = a.y + 55 * math.sin(angle)
                h = Atom(hx, hy, 'H')
                new_atoms.append(h)
                new_bonds.append(Bond(a, h, 1))
        self.atoms.extend(new_atoms)
        self.bonds.extend(new_bonds)
        self.show_alert("Auto-vodíky doplněny dle oktetového pravidla.")
        self.log_event(f"Doplněno {len(new_atoms)} vodíků.")

    # ─────────────── PŘEDDEFINOVANÉ MOLEKULY ──────────────────────────────────
    def spawn_molecule(self, key):
        mol = PREDEF_MOLECULES[key]
        cx = WIDTH // 2 + self.cam_x
        cy = HEIGHT // 2 + self.cam_y

        new_atoms = []
        for sym, ox, oy in mol['atoms']:
            new_atoms.append(Atom(cx + ox, cy + oy, sym))
        for i1, i2, bt in mol['bonds']:
            self.bonds.append(Bond(new_atoms[i1], new_atoms[i2], bt))

        if 'ions' in mol:
            for idx, charge in mol['ions']:
                new_atoms[idx].ion_charge = charge

        self.atoms.extend(new_atoms)
        self.show_alert(f"Vytvořeno: {key} – {mol['desc']}")
        self.log_event(f"Molekula {key} přidána.")

    # ─────────────── EVENTS ───────────────────────────────────────────────────
    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Tlačítka režimů
                if self.btn_mode.collidepoint(mx, my):
                    self.mode = MODE_3D if self.mode == MODE_2D else MODE_2D
                    if self.mode == MODE_3D and len(self.atoms) > 0:
                        cx = sum(a.x for a in self.atoms) / len(self.atoms)
                        cy = sum(a.y for a in self.atoms) / len(self.atoms)
                        self.cam_x, self.cam_y = cx, cy
                        for a in self.atoms: a.vz += random.uniform(-8.0, 8.0)
                    elif self.mode == MODE_2D and len(self.atoms) > 0:
                        self.cam_x = sum(a.x for a in self.atoms)/len(self.atoms) - WIDTH//2
                        self.cam_y = sum(a.y for a in self.atoms)/len(self.atoms) - HEIGHT//2
                    return

                if self.btn_electrons.collidepoint(mx, my):
                    self.show_electrons = not self.show_electrons; return
                if self.btn_orbitals.collidepoint(mx, my):
                    self.show_orbitals = not self.show_orbitals; return
                if self.btn_skeletal.collidepoint(mx, my):
                    self.show_skeletal = not self.show_skeletal; return
                if self.btn_auto_h.collidepoint(mx, my):
                    self.auto_hydrogen(); return
                if self.btn_clear.collidepoint(mx, my):
                    self.atoms.clear(); self.bonds.clear(); self.h_bonds.clear()
                    self.energy_history.clear()
                    self.show_alert("Prostor vycisten."); return
                if self.btn_predef.collidepoint(mx, my):
                    self.predef_open = not self.predef_open; return
                if self.btn_fullscreen.collidepoint(mx, my):
                    toggle_fullscreen()
                    return

                if self.mode == MODE_2D:
                    world_x = mx + self.cam_x
                    world_y = my + self.cam_y

                    # Předdefinované molekuly popup
                    if self.predef_open:
                        popup_x = self.SIDEBAR_W + 10
                        popup_y = 50
                        keys = list(PREDEF_MOLECULES.keys())
                        for i, key in enumerate(keys):
                            r = pygame.Rect(popup_x, popup_y + i * 42, 260, 38)
                            if r.collidepoint(mx, my):
                                self.spawn_molecule(key)
                                self.predef_open = False
                                return
                        self.predef_open = False
                        return

                    # Periodická tabulka popup
                    if self.ptable_open:
                        cols = 6
                        pt_ox = self.SIDEBAR_W + 10
                        pt_oy = 10
                        for i, key in enumerate(ELEMENTS.keys()):
                            rx = pt_ox + 15 + (i % cols) * 115
                            ry = pt_oy + 40 + (i // cols) * 82
                            if pygame.Rect(rx, ry, 108, 74).collidepoint(mx, my):
                                self.selected_symbol = key
                                self.ptable_open = False
                                self.current_tool = TOOL_ADD_ATOM
                                return
                        self.ptable_open = False
                        return

                    # Tlačítka nástrojů
                    for i, rect in enumerate(self.ui_buttons):
                        if rect.collidepoint(mx, my):
                            self.current_tool = self.ui_tools[i]
                            self.bonding_start_atom = None
                            return

                    if self.btn_ptable.collidepoint(mx, my):
                        self.ptable_open = not self.ptable_open; return

                    # Canvas interakce
                    if mx > self.SIDEBAR_W and mx < WIDTH - self.DIAG_W:
                        if self.current_tool == TOOL_PAN:
                            self.panning = True
                        elif self.current_tool == TOOL_ADD_ATOM:
                            if not self.hovered_atom:
                                if ELEMENTS[self.selected_symbol][4] == 0:
                                    self.show_alert(f"{ELEMENTS[self.selected_symbol][3]} je vzácný plyn – netvoří vazby!")
                                self.atoms.append(Atom(world_x, world_y, self.selected_symbol))
                                self.log_event(f"Přidán {self.selected_symbol}")
                        elif self.current_tool == TOOL_CURSOR:
                            if self.hovered_atom:
                                self.dragging_atom = self.hovered_atom
                                self.dragging_atom.is_dragged = True
                        elif self.current_tool == TOOL_ADD_BOND:
                            if self.hovered_atom:
                                self.bonding_start_atom = self.hovered_atom
                        elif self.current_tool == TOOL_IONIZE:
                            if self.hovered_atom:
                                self.hovered_atom.ion_charge += 1
                                self.show_alert(f"Odebran e- -> {self.hovered_atom.symbol}+ (kation)")
                                self.log_event(f"{self.hovered_atom.symbol} ionizovan na kation (+{self.hovered_atom.ion_charge})")

                elif self.mode == MODE_3D:
                    self.panning = True

            elif event.button == 3 and self.mode == MODE_2D:
                if self.current_tool == TOOL_IONIZE:
                    if self.hovered_atom:
                        self.hovered_atom.ion_charge -= 1
                        self.show_alert(f"Pridan e- -> {self.hovered_atom.symbol}- (anion)")
                        self.log_event(f"{self.hovered_atom.symbol} redukovam na anion ({self.hovered_atom.ion_charge})")
                else:
                    if self.hovered_atom:
                        self.bonds = [b for b in self.bonds
                                     if b.a1 != self.hovered_atom and b.a2 != self.hovered_atom]
                        sym = self.hovered_atom.symbol
                        self.atoms.remove(self.hovered_atom)
                        self.log_event(f"Smazán {sym}")
                    else:
                        world_x = mx + self.cam_x
                        world_y = my + self.cam_y
                        to_remove = None
                        for b in self.bonds:
                            if point_line_distance(world_x, world_y, b.a1.x, b.a1.y, b.a2.x, b.a2.y) < 25:
                                to_remove = b; break
                        if to_remove:
                            self.bonds.remove(to_remove)
                            self.log_event("Vazba odstraněna")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.panning = False
                if self.dragging_atom:
                    self.dragging_atom.is_dragged = False
                    self.dragging_atom = None

                if (self.mode == MODE_2D and self.current_tool == TOOL_ADD_BOND
                    and self.bonding_start_atom):
                    if self.hovered_atom and self.hovered_atom != self.bonding_start_atom:
                        start_a = self.bonding_start_atom
                        target = self.hovered_atom

                        existing_bond = None
                        for b in self.bonds:
                            if ((b.a1 == start_a and b.a2 == target) or
                                (b.a2 == start_a and b.a1 == target)):
                                existing_bond = b; break

                        orders1 = sum(get_bond_order(b.type) for b in self.bonds
                                     if b.a1 == start_a or b.a2 == start_a)
                        orders2 = sum(get_bond_order(b.type) for b in self.bonds
                                     if b.a1 == target or b.a2 == target)

                        if existing_bond:
                            next_type = existing_bond.type + 1
                            if next_type > 5:
                                self.bonds.remove(existing_bond)
                                self.log_event(f"Vazba {start_a.symbol}-{target.symbol} odstraněna")
                            else:
                                diff = get_bond_order(next_type) - get_bond_order(existing_bond.type)
                                if (orders1 + diff > start_a.max_bonds or
                                    orders2 + diff > target.max_bonds):
                                    self.show_alert("Překročena maximální valence!")
                                else:
                                    existing_bond.type = next_type
                                    self.log_event(f"Vazba {start_a.symbol}-{target.symbol} → řád {next_type}")
                        else:
                            if start_a.max_bonds == 0 or target.max_bonds == 0:
                                self.show_alert("Vzácné plyny netvoří vazby!")
                            elif orders1 + 1 > start_a.max_bonds or orders2 + 1 > target.max_bonds:
                                self.show_alert("Překročena maximální valence!")
                            else:
                                self.bonds.append(Bond(start_a, target))
                                self.log_event(f"Vazba {start_a.symbol}-{target.symbol} vytvořena")
                    self.bonding_start_atom = None

        elif event.type == pygame.MOUSEMOTION:
            if self.panning:
                dx = mx - self.last_mouse_pos[0]
                dy = my - self.last_mouse_pos[1]
                if self.mode == MODE_2D:
                    self.cam_x -= dx; self.cam_y -= dy
                else:
                    self.view_rot_y += dx * 0.01
                    self.view_rot_x -= dy * 0.01
            elif self.dragging_atom and self.mode == MODE_2D:
                self.dragging_atom.x = mx + self.cam_x
                self.dragging_atom.y = my + self.cam_y
                self.dragging_atom.z = 0

            # Hover detection
            self.hovered_atom = None
            self.hovered_bond = None
            if self.mode == MODE_2D:
                wx, wy = mx + self.cam_x, my + self.cam_y
                for a in reversed(self.atoms):
                    if math.hypot(a.x - wx, a.y - wy) <= a.radius + 10:
                        self.hovered_atom = a; break
                if not self.hovered_atom:
                    for b in self.bonds:
                        if point_line_distance(wx, wy, b.a1.x, b.a1.y, b.a2.x, b.a2.y) < 15:
                            self.hovered_bond = b; break

        self.last_mouse_pos = (mx, my)

    # ═════════════════════════════════════════════════════════════════════════
    # RENDERING
    # ═════════════════════════════════════════════════════════════════════════
    def draw(self, surface, time):
        surface.fill(BG_COLOR)

        canvas_left = self.SIDEBAR_W
        canvas_right = WIDTH - self.DIAG_W

        # Mřížka v canvas oblasti
        if self.mode == MODE_2D:
            gs = 80
            for x in range(int((-self.cam_x + canvas_left) % gs) + canvas_left, canvas_right, gs):
                pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
            for y in range(int(-self.cam_y % gs), HEIGHT, gs):
                pygame.draw.line(surface, GRID_COLOR, (canvas_left, y), (canvas_right, y))

        render_queue = []

        for a in self.atoms:
            sx, sy, sr, z = a.get_screen_pos(self.cam_x, self.cam_y, self.mode,
                                              self.view_rot_x, self.view_rot_y)
            render_queue.append({'type': 'atom', 'obj': a, 'sx': sx, 'sy': sy, 'r': sr, 'z': z})

            # Volné elektrony
            if self.show_electrons and not self.show_skeletal:
                used_val = sum(get_bond_order(b.type) for b in self.bonds if b.a1 == a or b.a2 == a)
                free_val = max(0, a.valence - used_val)
                for i in range(free_val):
                    ed = a.e_data[i]
                    ed['angle'] += ed['speed']

                    orbit_r = a.radius + 14
                    lx = orbit_r * math.cos(ed['angle'])
                    ly = orbit_r * math.sin(ed['angle'])
                    rx, ry, rz = rotate_3d(lx, ly, 0, ed['rot_x'], ed['rot_y'])
                    wx, wy, wz = a.x + rx, a.y + ry, a.z + rz

                    if self.mode == MODE_2D:
                        esx = wx - self.cam_x; esy = wy - self.cam_y; e_r = 4; e_z = 0
                    else:
                        crx, cry, crz = rotate_3d(wx-self.cam_x, wy-self.cam_y, wz,
                                                  self.view_rot_x, self.view_rot_y)
                        z_d = crz + 800
                        if z_d < 10: z_d = 10
                        f = 800 / z_d
                        esx = crx*f + WIDTH//2; esy = cry*f + HEIGHT//2; e_r = 4*f; e_z = crz

                    # Trail
                    ed['trail'].append((esx, esy))
                    if len(ed['trail']) > 6:
                        ed['trail'].pop(0)

                    render_queue.append({'type': 'electron', 'sx': esx, 'sy': esy,
                                        'r': e_r, 'z': e_z, 'color': E_FREE_COLOR,
                                        'trail': list(ed['trail'])})

        # Vazby
        for b in self.bonds:
            sx1, sy1, _, z1 = b.a1.get_screen_pos(self.cam_x, self.cam_y, self.mode,
                                                    self.view_rot_x, self.view_rot_y)
            sx2, sy2, _, z2 = b.a2.get_screen_pos(self.cam_x, self.cam_y, self.mode,
                                                    self.view_rot_x, self.view_rot_y)
            render_queue.append({'type': 'bond', 'obj': b, 'sx1': sx1, 'sy1': sy1,
                                'sx2': sx2, 'sy2': sy2, 'z': (z1+z2)/2})

            # Vazebné elektrony
            if self.show_electrons and not self.show_skeletal:
                order = get_bond_order(b.type)
                en_diff = b.a2.en_eff - b.a1.en_eff
                center_shift = max(-0.4, min(0.4, en_diff * 0.15))

                for i in range(order * 2):
                    osc = (math.sin(time * 4 + i * (math.pi / order)) + 1) / 2
                    t_pos = max(0.1, min(0.9, 0.2 + osc * 0.6 + center_shift))
                    wx = b.a1.x + (b.a2.x - b.a1.x) * t_pos
                    wy = b.a1.y + (b.a2.y - b.a1.y) * t_pos
                    wz = b.a1.z + (b.a2.z - b.a1.z) * t_pos

                    # Offset do strany
                    bdx = b.a2.x - b.a1.x; bdy = b.a2.y - b.a1.y
                    bl = math.hypot(bdx, bdy)
                    if bl > 0:
                        side = (i % 2 - 0.5) * 10
                        wx += (-bdy/bl) * side
                        wy += (bdx/bl) * side

                    if self.mode == MODE_2D:
                        esx = wx - self.cam_x; esy = wy - self.cam_y; e_r = 3.5; e_z = 0
                    else:
                        crx, cry, crz = rotate_3d(wx-self.cam_x, wy-self.cam_y, wz,
                                                  self.view_rot_x, self.view_rot_y)
                        z_d = crz + 800
                        f = 800 / max(10, z_d)
                        esx = crx*f + WIDTH//2; esy = cry*f + HEIGHT//2; e_r = 3.5*f; e_z = crz

                    render_queue.append({'type': 'electron', 'sx': esx, 'sy': esy,
                                        'r': e_r, 'z': e_z, 'color': E_BOND_COLOR,
                                        'trail': []})

        # Vodíkové můstky
        for hb in self.h_bonds:
            sx1, sy1, _, z1 = hb[0].get_screen_pos(self.cam_x, self.cam_y, self.mode,
                                                     self.view_rot_x, self.view_rot_y)
            sx2, sy2, _, z2 = hb[1].get_screen_pos(self.cam_x, self.cam_y, self.mode,
                                                     self.view_rot_x, self.view_rot_y)
            render_queue.append({'type': 'h_bond', 'p1': (sx1, sy1), 'p2': (sx2, sy2),
                                'z': (z1+z2)/2})

        # Z-sorting
        render_queue.sort(key=lambda item: item['z'], reverse=True)

        # Alpha surface pro glow efekty
        alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for item in render_queue:
            if item['type'] == 'h_bond':
                # Tečkovaná čára s glow
                p1, p2 = item['p1'], item['p2']
                dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                steps = max(2, int(dist / 8))
                for i in range(steps):
                    if i % 2 == 0:
                        t1 = i / steps; t2 = min(1.0, (i+1) / steps)
                        x1 = p1[0] + (p2[0]-p1[0])*t1; y1 = p1[1] + (p2[1]-p1[1])*t1
                        x2 = p1[0] + (p2[0]-p1[0])*t2; y2 = p1[1] + (p2[1]-p1[1])*t2
                        pygame.draw.line(surface, H_BOND_COLOR, (x1, y1), (x2, y2), 2)
                        # Soft glow na můstku
                        mx_h = (x1+x2)/2; my_h = (y1+y2)/2
                        draw_soft_glow(alpha_surf, H_BOND_COLOR, (mx_h, my_h), 5)

            elif item['type'] == 'bond':
                b = item['obj']
                x1, y1, x2, y2 = item['sx1'], item['sy1'], item['sx2'], item['sy2']

                is_hovered_b = (b == self.hovered_bond)

                if not self.show_skeletal:
                    # Glow kolem vazby
                    glow_color = (80, 150, 255, 25) if not is_hovered_b else (120, 200, 255, 45)
                    pygame.draw.line(alpha_surf, glow_color, (x1, y1), (x2, y2), 22)

                dx, dy = x2 - x1, y2 - y1
                length = math.hypot(dx, dy)
                if length > 0:
                    nx, ny = -dy/length, dx/length
                    b_color = WHITE if self.show_skeletal else BOND_COLOR
                    b_width = 3 if self.show_skeletal else 4

                    if is_hovered_b:
                        b_color = NEON_CYAN
                        b_width += 1

                    if b.type == 1 or b.type > 3:
                        pygame.draw.line(surface, b_color, (x1, y1), (x2, y2), b_width)
                    elif b.type == 2:
                        off = 4
                        pygame.draw.line(surface, b_color, (x1+nx*off, y1+ny*off),
                                        (x2+nx*off, y2+ny*off), max(1, b_width-1))
                        pygame.draw.line(surface, b_color, (x1-nx*off, y1-ny*off),
                                        (x2-nx*off, y2-ny*off), max(1, b_width-1))
                    elif b.type == 3:
                        off = 6
                        pygame.draw.line(surface, b_color, (x1+nx*off, y1+ny*off),
                                        (x2+nx*off, y2+ny*off), max(1, b_width-2))
                        pygame.draw.line(surface, b_color, (x1, y1), (x2, y2), b_width)
                        pygame.draw.line(surface, b_color, (x1-nx*off, y1-ny*off),
                                        (x2-nx*off, y2-ny*off), max(1, b_width-2))

                    # Polaritní šipka na polárních vazbách
                    if not self.show_skeletal and abs(b.a1.en - b.a2.en) > 0.4:
                        mid_x = (x1+x2)/2; mid_y = (y1+y2)/2
                        if b.a1.en < b.a2.en:
                            delta_label = "δ+"
                            delta_pos = (x1, y1)
                            delta2_label = "δ-"
                            delta2_pos = (x2, y2)
                        else:
                            delta_label = "δ-"
                            delta_pos = (x1, y1)
                            delta2_label = "δ+"
                            delta2_pos = (x2, y2)
                        # Vykreslení δ+ a δ- značek
                        dt1 = font_tiny.render(delta_label, True, (255, 200, 100))
                        dt2 = font_tiny.render(delta2_label, True, (255, 200, 100))
                        off_x = ny * 18; off_y = -nx * 18
                        surface.blit(dt1, (delta_pos[0]+off_x-8, delta_pos[1]+off_y-6))
                        surface.blit(dt2, (delta2_pos[0]+off_x-8, delta2_pos[1]+off_y-6))

            elif item['type'] == 'atom':
                a = item['obj']
                sx, sy, r = int(item['sx']), int(item['sy']), max(5, int(item['r']))
                darken = max(0.4, min(1.0, 1.0 - (item['z'] / 800.0)))

                # Barva podle ionizace
                base_c = a.color
                if a.ion_charge > 0:
                    base_c = lerp_color(a.color, (255, 80, 80), min(1.0, a.ion_charge * 0.4))
                elif a.ion_charge < 0:
                    base_c = lerp_color(a.color, (80, 80, 255), min(1.0, abs(a.ion_charge) * 0.4))

                c = (int(base_c[0]*darken), int(base_c[1]*darken), int(base_c[2]*darken))

                # Orbitaly
                if self.show_orbitals and a.symbol != '*' and not self.show_skeletal:
                    draw_hybridization_orbitals(alpha_surf, a, sx, sy, r, time)

                # Nábojová aura
                tot_charge = a.delta_charge + a.ion_charge
                if abs(tot_charge) > 0.05 and not self.show_skeletal:
                    intensity = min(150, int(abs(tot_charge) * 180))
                    if tot_charge < 0:
                        aura_c = (50, 100, 255, intensity)
                    else:
                        aura_c = (255, 50, 50, intensity)
                    aura_r = int(r * 2.0)
                    pygame.draw.circle(alpha_surf, aura_c, (sx, sy), aura_r)

                # Atom vykreslení
                is_hov = (a == self.hovered_atom)
                txt_str = "R" if a.symbol == '*' else a.symbol

                if self.show_skeletal:
                    pygame.draw.circle(surface, BG_COLOR, (sx, sy), 15)
                    txt = font_element.render(txt_str, True, WHITE)
                else:
                    if a.symbol == '*':
                        obrys_c = (180, 180, 180) if is_hov else (70, 70, 70)
                        pygame.draw.circle(surface, obrys_c, (sx, sy), r + 2, 2)
                    else:
                        # Vnější ring s glow při hoveru
                        if is_hov:
                            draw_glow_circle(alpha_surf, NEON_CYAN, (sx, sy), r + 4, 0.8)
                            pygame.draw.circle(surface, (200, 220, 255), (sx, sy), r + 3, 2)
                        else:
                            pygame.draw.circle(surface, (30, 30, 30), (sx, sy), r + 2)

                        # Gradient na atomu (3D efekt)
                        pygame.draw.circle(surface, c, (sx, sy), r)
                        # Highlight (lesk)
                        if r > 8:
                            hl_r = max(2, r // 3)
                            hl_x = sx - r // 4
                            hl_y = sy - r // 4
                            hl_c = (min(255, c[0]+80), min(255, c[1]+80), min(255, c[2]+80))
                            hl_s = pygame.Surface((hl_r*2, hl_r*2), pygame.SRCALPHA)
                            pygame.draw.circle(hl_s, (*hl_c, 80), (hl_r, hl_r), hl_r)
                            surface.blit(hl_s, (hl_x - hl_r, hl_y - hl_r))

                    txt_c = (20, 20, 20) if sum(c) > 350 else (230, 235, 245)
                    txt = font_element.render(txt_str, True, txt_c)

                surface.blit(txt, (sx - txt.get_width()//2, sy - txt.get_height()//2))

                # Iontový náboj jako exponent
                if a.ion_charge != 0:
                    sign = "+" if a.ion_charge > 0 else "-"
                    num = str(abs(a.ion_charge)) if abs(a.ion_charge) > 1 else ""
                    ion_c = NEON_RED if a.ion_charge > 0 else NEON_CYAN
                    ion_txt = font_small.render(num + sign, True, ion_c)
                    surface.blit(ion_txt, (sx + r - 4, sy - r - 2))

                # EN hodnota pod atomem
                if self.mode == MODE_2D and a.en > 0 and a.symbol != '*' and not self.show_skeletal:
                    en_txt = font_tiny.render(f"{a.en:.2f}", True, get_en_color(a.en))
                    surface.blit(en_txt, (sx - en_txt.get_width()//2, sy + r + 3))

            elif item['type'] == 'electron':
                esx, esy = int(item['sx']), int(item['sy'])
                e_r = max(1, int(item['r']))
                e_color = item['color']

                # Trail efekt
                trail = item.get('trail', [])
                if len(trail) > 1:
                    for ti in range(len(trail) - 1):
                        alpha_t = int(40 * (ti + 1) / len(trail))
                        t_color = (e_color[0], e_color[1], e_color[2], alpha_t)
                        t_r = max(1, int(e_r * (ti + 1) / len(trail)))
                        pygame.draw.circle(alpha_surf, t_color,
                                          (int(trail[ti][0]), int(trail[ti][1])), t_r)

                # Glow kolem elektronu
                draw_soft_glow(alpha_surf, e_color, (esx, esy), e_r + 2)

                # Elektron samotný
                pygame.draw.circle(surface, WHITE, (esx, esy), e_r + 1)
                pygame.draw.circle(surface, e_color, (esx, esy), e_r)

        # Blit alpha surface
        surface.blit(alpha_surf, (0, 0))

        # Čára vazby při tažení
        if self.mode == MODE_2D and self.current_tool == TOOL_ADD_BOND and self.bonding_start_atom:
            mx, my = pygame.mouse.get_pos()
            sx, sy, _, _ = self.bonding_start_atom.get_screen_pos(self.cam_x, self.cam_y,
                                                                    self.mode, 0, 0)
            pygame.draw.line(surface, NEON_CYAN, (int(sx), int(sy)), (mx, my), 2)

        # ═════════════════════════════════════════════════════════════════════
        # UI: LEVÝ SIDEBAR
        # ═════════════════════════════════════════════════════════════════════
        mx, my = pygame.mouse.get_pos()

        # Sidebar pozadí
        sidebar_surf = pygame.Surface((self.SIDEBAR_W, HEIGHT), pygame.SRCALPHA)
        sidebar_surf.fill((UI_BG[0], UI_BG[1], UI_BG[2], 240))
        surface.blit(sidebar_surf, (0, 0))

        # Jemný horní záblesk
        glow_s = pygame.Surface((self.SIDEBAR_W, 90), pygame.SRCALPHA)
        glow_s.fill((55, 115, 235, 10))
        surface.blit(glow_s, (0, 0))

        # Pravý okraj sidebaru
        pygame.draw.line(surface, UI_SEPARATOR, (self.SIDEBAR_W, 0), (self.SIDEBAR_W, HEIGHT), 2)

        # ── Header ────────────────────────────────────
        # Animovaný atom v logu
        logo_cx, logo_cy = 22, 26
        # Jádro
        pygame.draw.circle(surface, NEON_BLUE, (logo_cx, logo_cy), 10)
        pygame.draw.circle(surface, (100, 180, 255), (logo_cx, logo_cy), 6)
        # Orbita elektronu
        e_angle = time * 3.0
        ex = logo_cx + int(14 * math.cos(e_angle))
        ey = logo_cy + int(8 * math.sin(e_angle))
        pygame.draw.circle(surface, NEON_CYAN, (ex, ey), 3)
        pygame.draw.ellipse(surface, (60, 100, 180), (logo_cx-14, logo_cy-8, 28, 16), 1)

        surface.blit(font_large.render("ChemBox", True, TEXT_BRIGHT), (40, 12))
        surface.blit(font_tiny.render("Ultimate v4.0", True, TEXT_DIM), (40, 36))
        pygame.draw.line(surface, UI_SEPARATOR, (8, 52), (self.SIDEBAR_W - 8, 52), 1)

        # ── Sekce: Nástroje ───────────────────────────
        surface.blit(font_tiny.render("NÁSTROJE", True, TEXT_DIM), (10, 58))
        for i, rect in enumerate(self.ui_buttons):
            accent = None
            if self.ui_tools[i] == TOOL_IONIZE:
                accent = NEON_PURPLE
            draw_ui_button(surface, rect, self.ui_labels[i], font_medium,
                          self.current_tool == self.ui_tools[i],
                          rect.collidepoint(mx, my), accent, time_val=time)

        pygame.draw.line(surface, UI_SEPARATOR, (8, self.sep1_y), (self.SIDEBAR_W - 8, self.sep1_y), 1)

        # ── Sekce: Akce ───────────────────────────────
        surface.blit(font_tiny.render("AKCE", True, TEXT_DIM), (10, self.sep1_y + 4))
        draw_ui_button(surface, self.btn_auto_h, "Auto-Vodíky +H", font_medium,
                      False, self.btn_auto_h.collidepoint(mx, my),
                      NEON_GREEN, time_val=time)
        draw_ui_button(surface, self.btn_clear, "Vymazat Vse", font_medium,
                      False, self.btn_clear.collidepoint(mx, my),
                      NEON_RED, time_val=time)
        draw_ui_button(surface, self.btn_predef, "Molekuly", font_medium,
                      self.predef_open, self.btn_predef.collidepoint(mx, my),
                      NEON_ORANGE, time_val=time)

        pygame.draw.line(surface, UI_SEPARATOR, (8, self.sep2_y), (self.SIDEBAR_W - 8, self.sep2_y), 1)

        # ── Sekce: Zobrazení ──────────────────────────
        surface.blit(font_tiny.render("ZOBRAZENÍ", True, TEXT_DIM), (10, self.sep2_y + 4))

        mode_label = "<- Zpet 2D" if self.mode == MODE_3D else "-> 3D Pohled"
        draw_ui_button(surface, self.btn_mode, mode_label, font_medium,
                      self.mode == MODE_3D, self.btn_mode.collidepoint(mx, my),
                      NEON_PURPLE, time_val=time)

        skel_label = "Skeletarni ON" if self.show_skeletal else "Skeletarni"
        draw_ui_button(surface, self.btn_skeletal, skel_label, font_medium,
                      self.show_skeletal, self.btn_skeletal.collidepoint(mx, my),
                      NEON_ORANGE if self.show_skeletal else None, time_val=time)

        e_label = "Elektrony ON" if self.show_electrons else "Elektrony"
        draw_ui_button(surface, self.btn_electrons, e_label, font_medium,
                      self.show_electrons, self.btn_electrons.collidepoint(mx, my),
                      NEON_YELLOW if self.show_electrons else None, time_val=time)

        orb_label = "Orbitaly ON" if self.show_orbitals else "Orbitaly"
        draw_ui_button(surface, self.btn_orbitals, orb_label, font_medium,
                      self.show_orbitals, self.btn_orbitals.collidepoint(mx, my),
                      NEON_PURPLE if self.show_orbitals else None, time_val=time)

        pygame.draw.line(surface, UI_SEPARATOR, (8, self.sep3_y), (self.SIDEBAR_W - 8, self.sep3_y), 1)

        # ── Sekce: Prvek ──────────────────────────────
        surface.blit(font_tiny.render("AKTIVNÍ PRVEK", True, TEXT_DIM), (10, self.sep3_y + 4))
        edata = ELEMENTS[self.selected_symbol]
        is_pt_hov = self.btn_ptable.collidepoint(mx, my)
        pt_bg = (35, 25, 60) if self.ptable_open else (UI_HOVER if is_pt_hov else (20, 26, 40))
        pygame.draw.rect(surface, pt_bg, self.btn_ptable, border_radius=8)

        # Rámeček podle kategorie
        cat = ELEMENT_CATEGORIES.get(self.selected_symbol, 'special')
        cat_color = CATEGORY_COLORS.get(cat, (100, 100, 100))
        pygame.draw.rect(surface, cat_color, self.btn_ptable, width=1, border_radius=8)

        # Barevný kroužek
        pygame.draw.circle(surface, edata[0],
                          (self.btn_ptable.x + 22, self.btn_ptable.y + 22), 13)
        pygame.draw.circle(surface, WHITE,
                          (self.btn_ptable.x + 22, self.btn_ptable.y + 22), 13, 1)
        sym_disp = "R" if self.selected_symbol == '*' else self.selected_symbol
        surface.blit(font_large.render(sym_disp, True, TEXT_BRIGHT),
                    (self.btn_ptable.x + 42, self.btn_ptable.y + 5))
        if self.selected_symbol != '*':
            surface.blit(font_tiny.render(edata[3], True, TEXT_DIM),
                        (self.btn_ptable.x + 8, self.btn_ptable.y + 46))
            surface.blit(font_tiny.render(f"EN {edata[5]:.2f} | Val {edata[1]}",
                                          True, get_en_color(edata[5])),
                        (self.btn_ptable.x + 8, self.btn_ptable.y + 60))
        arrow = "^ Zavrit" if self.ptable_open else "v Tabulka"
        surface.blit(font_tiny.render(arrow, True, TEXT_DIM),
                    (self.btn_ptable.x + 42, self.btn_ptable.y + 74))

        pygame.draw.line(surface, UI_SEPARATOR, (8, self.sep4_y), (self.SIDEBAR_W - 8, self.sep4_y), 1)

        # -- Sekce: Nastaveni -----
        surface.blit(font_tiny.render("NASTAVENI", True, TEXT_DIM), (10, self.sep4_y + 4))
        fs_label = "Windowed" if is_fullscreen else "Fullscreen"
        draw_ui_button(surface, self.btn_fullscreen, fs_label, font_medium,
                      is_fullscreen, self.btn_fullscreen.collidepoint(mx, my),
                      NEON_CYAN, time_val=time)

        # ═════════════════════════════════════════════════════════════════════
        # POPUPY
        # ═════════════════════════════════════════════════════════════════════

        # Periodická tabulka
        if self.ptable_open and self.mode == MODE_2D:
            cols = 6
            pt_ox = self.SIDEBAR_W + 10
            keys = list(ELEMENTS.keys())
            rows = (len(keys) + cols - 1) // cols
            pt_w = cols * 115 + 30
            pt_h = rows * 82 + 55
            pt_oy = 10

            # Pozadí
            popup_bg = pygame.Surface((pt_w, pt_h), pygame.SRCALPHA)
            popup_bg.fill((10, 14, 24, 235))
            surface.blit(popup_bg, (pt_ox, pt_oy))
            pygame.draw.rect(surface, UI_BORDER,
                            pygame.Rect(pt_ox, pt_oy, pt_w, pt_h), width=2, border_radius=10)

            title_t = font_medium.render("Periodická Tabulka Prvků", True, TEXT_BRIGHT)
            surface.blit(title_t, (pt_ox + (pt_w - title_t.get_width())//2, pt_oy + 10))

            for i, (sym, data) in enumerate(ELEMENTS.items()):
                rx = pt_ox + 15 + (i % cols) * 115
                ry = pt_oy + 40 + (i // cols) * 82
                rect = pygame.Rect(rx, ry, 108, 74)

                is_sel = (sym == self.selected_symbol)
                is_hov = rect.collidepoint(mx, my)

                cat = ELEMENT_CATEGORIES.get(sym, 'special')
                cat_c = CATEGORY_COLORS.get(cat, (100, 100, 100))

                if is_sel:
                    bg_c = (42, 85, 190)
                elif is_hov:
                    bg_c = (cat_c[0]//3, cat_c[1]//3, cat_c[2]//3)
                else:
                    bg_c = UI_PANEL

                pygame.draw.rect(surface, bg_c, rect, border_radius=6)
                border_c = cat_c if (is_sel or is_hov) else (30, 38, 55)
                pygame.draw.rect(surface, border_c, rect, width=1, border_radius=6)

                # Barevný pruh nahoře
                pygame.draw.rect(surface, cat_c,
                                pygame.Rect(rx+2, ry+2, rect.width-4, 3), border_radius=6)

                pygame.draw.circle(surface, data[0], (rx + 18, ry + 24), 9)
                disp = "R" if sym == '*' else sym
                surface.blit(font_element.render(disp, True, TEXT_BRIGHT), (rx + 34, ry + 12))
                surface.blit(font_tiny.render(data[3], True, TEXT_DIM), (rx + 6, ry + 40))
                if sym != '*':
                    surface.blit(font_tiny.render(f"EN {data[5]:.2f}",
                                                  True, get_en_color(data[5])), (rx + 6, ry + 54))

        # Předdefinované molekuly popup
        if self.predef_open and self.mode == MODE_2D:
            popup_x = self.SIDEBAR_W + 10
            popup_y = 50
            keys = list(PREDEF_MOLECULES.keys())
            pw = 270
            ph = len(keys) * 42 + 14

            popup_bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
            popup_bg.fill((10, 14, 24, 235))
            surface.blit(popup_bg, (popup_x, popup_y))
            pygame.draw.rect(surface, NEON_ORANGE,
                            pygame.Rect(popup_x, popup_y, pw, ph), width=1, border_radius=10)

            for i, key in enumerate(keys):
                r = pygame.Rect(popup_x + 6, popup_y + 6 + i*42, pw - 12, 38)
                is_hov = r.collidepoint(mx, my)
                bg = UI_HOVER if is_hov else (20, 26, 40)
                pygame.draw.rect(surface, bg, r, border_radius=6)
                if is_hov:
                    pygame.draw.rect(surface, NEON_ORANGE, r, width=1, border_radius=6)

                surface.blit(font_medium.render(key, True, TEXT_BRIGHT), (r.x + 10, r.y + 3))
                desc_t = font_tiny.render(PREDEF_MOLECULES[key]['desc'][:35], True, TEXT_DIM)
                surface.blit(desc_t, (r.x + 10, r.y + 22))

        # ═════════════════════════════════════════════════════════════════════
        # UI: PRAVÝ DIAGNOSTICKÝ PANEL
        # ═════════════════════════════════════════════════════════════════════
        diag_x = WIDTH - self.DIAG_W

        # Pozadí
        diag_bg = pygame.Surface((self.DIAG_W, HEIGHT), pygame.SRCALPHA)
        diag_bg.fill((UI_BG[0], UI_BG[1], UI_BG[2], 240))
        surface.blit(diag_bg, (diag_x, 0))
        pygame.draw.line(surface, UI_SEPARATOR, (diag_x, 0), (diag_x, HEIGHT), 2)

        # Header
        surface.blit(font_large.render("Diagnostika", True, TEXT_BRIGHT), (diag_x + 15, 12))
        pygame.draw.line(surface, UI_SEPARATOR, (diag_x + 10, 42), (diag_x + self.DIAG_W - 10, 42))

        # Generovat popisy
        self.generate_descriptions()

        # Energetický mini-graf
        if len(self.energy_history) > 2:
            graph_x = diag_x + 15
            graph_y = 52
            graph_w = self.DIAG_W - 30
            graph_h = 50
            pygame.draw.rect(surface, (15, 18, 28), (graph_x, graph_y, graph_w, graph_h),
                            border_radius=4)
            pygame.draw.rect(surface, (30, 38, 55), (graph_x, graph_y, graph_w, graph_h),
                            width=1, border_radius=4)

            max_e = max(self.energy_history) if max(self.energy_history) > 0 else 1
            pts = []
            for i, e in enumerate(self.energy_history):
                px = graph_x + int(i * graph_w / len(self.energy_history))
                py = graph_y + graph_h - 4 - int((e / max_e) * (graph_h - 8))
                pts.append((px, py))
            if len(pts) > 1:
                pygame.draw.lines(surface, NEON_GREEN, False, pts, 1)

            surface.blit(font_tiny.render("Kinetická energie", True, TEXT_DIM),
                        (graph_x + 4, graph_y + 2))
            desc_y_start = graph_y + graph_h + 12
        else:
            desc_y_start = 55

        # Chemické popisy
        dy = desc_y_start
        for title, desc, color in self.chem_descriptions:
            if dy > HEIGHT - 80: break

            # Záhlaví
            title_surf = font_medium.render(title, True, color)
            surface.blit(title_surf, (diag_x + 15, dy))
            dy += 22

            # Popis po řádcích
            for line in desc.split('\n'):
                if dy > HEIGHT - 50: break
                line_surf = font_desc.render(line, True, TEXT_DIM)
                surface.blit(line_surf, (diag_x + 18, dy))
                dy += 17
            dy += 10

            # Separator
            if dy < HEIGHT - 60:
                pygame.draw.line(surface, (30, 36, 52),
                                (diag_x + 15, dy), (diag_x + self.DIAG_W - 15, dy))
                dy += 8

        # Event log (spodní část)
        if self.event_log:
            log_y = max(dy + 10, HEIGHT - 140)
            pygame.draw.line(surface, UI_SEPARATOR,
                            (diag_x + 10, log_y - 5), (diag_x + self.DIAG_W - 10, log_y - 5))
            surface.blit(font_tiny.render("HISTORIE DĚJŮ", True, TEXT_DIM), (diag_x + 15, log_y))
            log_y += 16
            for entry in reversed(self.event_log[-6:]):
                if log_y > HEIGHT - 40: break
                surface.blit(font_tiny.render("• " + entry, True, (80, 90, 110)),
                            (diag_x + 15, log_y))
                log_y += 15

        # ═════════════════════════════════════════════════════════════════════
        # 3D BANNER
        # ═════════════════════════════════════════════════════════════════════
        if self.mode == MODE_3D:
            bw = 380
            ban = pygame.Surface((bw, 36), pygame.SRCALPHA)
            ban.fill((12, 16, 32, 210))
            bx = self.SIDEBAR_W + (canvas_right - self.SIDEBAR_W - bw) // 2
            surface.blit(ban, (bx, 12))
            pygame.draw.rect(surface, NEON_BLUE,
                            pygame.Rect(bx, 12, bw, 36), width=1, border_radius=8)
            surface.blit(font_medium.render("3D PROSTOROVÝ POHLED  —  Tažením otáčej",
                                            True, (130, 185, 255)), (bx + 14, 20))

        # ═════════════════════════════════════════════════════════════════════
        # ALERT
        # ═════════════════════════════════════════════════════════════════════
        if self.alert_timer > 0:
            fade = min(1.0, self.alert_timer / 30.0)
            alert_surf = font_large.render(self.alert_message, True, WHITE)
            aw = alert_surf.get_width() + 40
            ah = 46
            ax = (canvas_left + canvas_right) // 2 - aw // 2
            ay = 20

            al_bg = pygame.Surface((aw, ah), pygame.SRCALPHA)
            al_bg.fill((ALERT_BG[0], ALERT_BG[1], ALERT_BG[2], int(220 * fade)))
            surface.blit(al_bg, (ax, ay))
            pygame.draw.rect(surface, (255, 100, 100),
                            pygame.Rect(ax, ay, aw, ah), width=2, border_radius=8)
            surface.blit(alert_surf, (ax + 20, ay + (ah - alert_surf.get_height())//2))
            self.alert_timer -= 1

        # ═════════════════════════════════════════════════════════════════════
        # STATUS BAR (spodní lišta)
        # ═════════════════════════════════════════════════════════════════════
        sb_y = HEIGHT - 28
        pygame.draw.rect(surface, UI_BG, (0, sb_y, WIDTH, 28))
        pygame.draw.line(surface, UI_SEPARATOR, (0, sb_y), (WIDTH, sb_y))

        tool_names = {TOOL_CURSOR: "Kurzor", TOOL_PAN: "Kamera",
                     TOOL_ADD_ATOM: "Atom", TOOL_ADD_BOND: "Vazba", TOOL_IONIZE: "Ion"}
        sym_sb = "R" if self.selected_symbol == '*' else self.selected_symbol

        sb_items = [
            (f" {'2D' if self.mode == MODE_2D else '3D'} ", NEON_BLUE),
            (f" | {tool_names.get(self.current_tool, '?')} ", TEXT_DIM),
            (f" | {sym_sb} ({ELEMENTS[self.selected_symbol][3]}) ", TEXT_COLOR),
            (f" | Atomy: {len(self.atoms)} ", TEXT_DIM),
            (f" | Vazby: {len(self.bonds)} ", TEXT_DIM),
        ]
        if self.h_bonds:
            sb_items.append((f" | H-mustky: {len(self.h_bonds)} ", H_BOND_COLOR))

        xpos = 8
        for text, col in sb_items:
            t = font_small.render(text, True, col)
            surface.blit(t, (xpos, sb_y + (28 - t.get_height())//2))
            xpos += t.get_width()

        hints = "PKM = Smazat | Vazba = tah | Ionizator: L=+, P=-"
        ht = font_tiny.render(hints, True, TEXT_DIM)
        surface.blit(ht, (WIDTH - ht.get_width() - 10, sb_y + (28 - ht.get_height())//2))


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    sandbox = Sandbox()
    time_val = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            sandbox.handle_event(event)

        sandbox.apply_physics()
        time_val += 0.016
        sandbox.draw(screen, time_val)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()