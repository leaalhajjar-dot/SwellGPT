import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw
import pytesseract
import os

# --- 1. SYSTEM CALIBRATION ---
tess_exe = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tess_exe):
    pytesseract.pytesseract.tesseract_cmd = tess_exe

st.set_page_config(page_title="SwellGPT 🧬", layout="wide")

# --- 2. THE MEGA-DICTIONARY ---
BM = {
    # LATIN (English, French, Spanish, German, Italian, Portuguese, Swahili)
    'a':[1,0,0,0,0,0],'b':[1,1,0,0,0,0],'c':[1,0,0,1,0,0],'d':[1,0,0,1,1,0],'e':[1,0,0,0,1,0],
    'f':[1,1,0,1,0,0],'g':[1,1,0,1,1,0],'h':[1,1,0,0,1,0],'i':[0,1,0,1,0,0],'j':[0,1,0,1,1,0],
    'k':[1,0,1,0,0,0],'l':[1,1,1,0,0,0],'m':[1,0,1,1,0,0],'n':[1,0,1,1,1,0],'o':[1,0,1,0,1,0],
    'p':[1,1,1,1,0,0],'q':[1,1,1,1,1,0],'r':[1,1,1,0,1,0],'s':[0,1,1,1,0,0],'t':[0,1,1,1,1,0],
    'u':[1,0,1,0,0,1],'v':[1,1,1,0,0,1],'w':[0,1,0,1,1,1],'x':[1,0,1,1,0,1],'y':[1,0,1,1,1,1],'z':[1,0,1,0,1,1],
    
   arabic_braille = {
    'ج': [0, 1, 0, 1, 1, 0],      # Dots: 2, 4, 5
    'ث': [1, 0, 0, 1, 1, 1],      # Dots: 1, 4, 5, 6
    'ت': [0, 1, 1, 1, 1, 0],      # Dots: 2, 3, 4, 5
    'ب': [1, 1, 0, 0, 0, 0],      # Dots: 1, 2
    'أ': [0, 0, 1, 1, 0, 0],      # Dots: 3, 4
    'ر': [1, 1, 1, 0, 1, 0],      # Dots: 1, 2, 3, 5
    'ذ': [0, 1, 1, 0, 1, 1],      # Dots: 2, 3, 4, 6
    'د': [1, 0, 0, 1, 1, 0],      # Dots: 1, 4, 5
    'خ': [1, 0, 1, 1, 0, 1],      # Dots: 1, 3, 4, 6
    'ح': [1, 0, 0, 0, 1, 1],      # Dots: 1, 5, 6
    'ض': [1, 1, 0, 1, 0, 1],      # Dots: 1, 2, 4, 6
    'ص': [1, 1, 1, 1, 0, 1],      # Dots: 1, 2, 3, 4, 6
    'ش': [1, 0, 0, 1, 0, 1],      # Dots: 1, 4, 6
    'س': [0, 1, 1, 1, 0, 0],      # Dots: 2, 3, 4
    'ز': [1, 0, 1, 0, 1, 1],      # Dots: 1, 3, 5, 6
    'ف': [1, 1, 0, 1, 0, 0],      # Dots: 1, 2, 4
    'غ': [1, 1, 0, 0, 0, 1],      # Dots: 1, 2, 6
    'ع': [1, 1, 1, 0, 1, 1],      # Dots: 1, 2, 3, 5, 6
    'ظ': [1, 1, 1, 1, 1, 1],      # Dots: 1, 2, 3, 4, 5, 6
    'ط': [0, 1, 1, 1, 1, 1],      # Dots: 2, 3, 4, 5, 6
    'ن': [1, 0, 1, 1, 1, 0],      # Dots: 1, 3, 4, 5
    'م': [1, 0, 1, 1, 0, 0],      # Dots: 1, 3, 4
    'ل': [1, 1, 1, 0, 0, 0],      # Dots: 1, 2, 3
    'ك': [1, 0, 1, 0, 0, 0],      # Dots: 1, 3
    'ق': [1, 1, 1, 1, 1, 0],      # Dots: 1, 2, 3, 4, 5
    'ء': [0, 0, 1, 0, 0, 0],      # Dots: 3
    'ة': [1, 0, 0, 0, 0, 1],      # Dots: 1, 6
    'ي': [0, 1, 0, 1, 0, 0],      # Dots: 2, 4
    'و': [0, 1, 0, 1, 1, 1],      # Dots: 2, 4, 5, 6
    'ه': [1, 1, 0, 0, 1, 0],      # Dots: 1, 2, 5
    'ى': [1, 0, 1, 0, 1, 0],      # Dots: 1, 3, 5
    'ئ': [1, 0, 1, 1, 1, 1],      # Dots: 1, 3, 4, 5, 6
    'ؤ': [1, 1, 0, 0, 1, 1],      # Dots: 1, 2, 5, 6
    'إ': [0, 0, 0, 1, 0, 1],      # Dots: 4, 6
    'آ': [0, 0, 1, 1, 1, 0]       # Dots: 3, 4, 5
}

    # CHINESE BRAILLE
   # Chinese Braille Initials (声母)
chinese_braille_initials = {
    'b': [1, 1, 0, 0, 0, 0],       # Dots: 1, 2
    'p': [1, 1, 1, 1, 0, 0],       # Dots: 1, 2, 3, 4
    'm': [1, 0, 1, 1, 0, 0],       # Dots: 1, 3, 4
    'f': [1, 1, 0, 1, 0, 0],       # Dots: 1, 2, 4
    'd': [1, 0, 0, 1, 1, 0],       # Dots: 1, 4, 5
    't': [0, 1, 1, 1, 1, 0],       # Dots: 2, 3, 4, 5
    'n': [1, 0, 1, 1, 1, 0],       # Dots: 1, 3, 4, 5
    'l': [1, 1, 1, 0, 0, 0],       # Dots: 1, 2, 3
    'g': [1, 1, 0, 1, 1, 0],       # Dots: 1, 2, 4, 5 (Shares pattern with 'j')
    'k': [1, 0, 1, 0, 0, 0],       # Dots: 1, 3 (Shares pattern with 'q')
    'h': [1, 1, 0, 0, 1, 0],       # Dots: 1, 2, 5 (Shares pattern with 'x')
    'j': [1, 1, 0, 1, 1, 0],       # Dots: 1, 2, 4, 5
    'q': [1, 0, 1, 0, 0, 0],       # Dots: 1, 3
    'x': [1, 1, 0, 0, 1, 0],       # Dots: 1, 2, 5
    'zh': [0, 1, 1, 0, 0, 1],      # Dots: 2, 3, 6
    'ch': [1, 1, 1, 1, 0, 1],      # Dots: 1, 2, 3, 4, 6
    'sh': [1, 0, 0, 1, 0, 1],      # Dots: 1, 4, 6
    'r': [0, 1, 1, 1, 0, 1],       # Dots: 2, 3, 4, 6
    'z': [1, 0, 1, 0, 1, 1],       # Dots: 1, 3, 5, 6
    'c': [1, 0, 0, 1, 1, 1],       # Dots: 1, 4, 5, 6
    's': [0, 1, 1, 1, 0, 0]        # Dots: 2, 3, 4
}

# Chinese Braille Finals (韵母)
chinese_braille_finals = {
    'a': [0, 1, 0, 1, 0, 1],       # Dots: 2, 4, 6
    'o': [0, 1, 0, 0, 1, 0],       # Dots: 2, 5
    'e': [0, 1, 0, 0, 1, 0],       # Dots: 2, 5
    'ai': [0, 1, 0, 0, 1, 1],      # Dots: 2, 5, 6
    'ei': [0, 1, 0, 0, 0, 1],      # Dots: 2, 6
    'ao': [0, 1, 1, 0, 1, 0],      # Dots: 2, 3, 5
    'ou': [1, 1, 0, 0, 1, 1],      # Dots: 1, 2, 5, 6
    'an': [1, 0, 1, 0, 1, 0],      # Dots: 1, 3, 5
    'en': [0, 1, 1, 0, 0, 1],      # Dots: 2, 3, 6
    'ang': [0, 1, 0, 1, 1, 0],     # Dots: 2, 4, 5
    'eng': [0, 1, 1, 1, 1, 1],     # Dots: 2, 3, 4, 5, 6
    'i': [0, 1, 0, 0, 0, 0],       # Dots: 2
    'ia': [1, 0, 1, 1, 0, 1],      # Dots: 1, 3, 4, 6
    'ie': [1, 0, 0, 0, 1, 0],      # Dots: 1, 5
    'iao': [1, 1, 1, 1, 0, 0],     # Dots: 1, 2, 3, 4
    'iu': [0, 1, 0, 1, 0, 0],      # Dots: 2, 4
    'ian': [1, 0, 1, 1, 1, 0],     # Dots: 1, 3, 4, 5
    'in': [0, 0, 1, 0, 1, 0],      # Dots: 3, 5
    'iang': [0, 0, 1, 1, 1, 1],    # Dots: 3, 4, 5, 6
    'ing': [0, 0, 1, 1, 0, 1],     # Dots: 3, 4, 6
    'u': [1, 0, 1, 0, 0, 1],       # Dots: 1, 3, 6
    'ua': [1, 1, 0, 1, 0, 1],      # Dots: 1, 2, 4, 6
    'uo': [1, 0, 1, 1, 1, 1],      # Dots: 1, 3, 4, 5, 6
    'uai': [1, 1, 0, 1, 0, 0],     # Dots: 1, 2, 4
    'ui': [0, 1, 1, 1, 0, 0],      # Dots: 2, 3, 4
    'uan': [1, 1, 0, 0, 0, 1],     # Dots: 1, 2, 6
    'un': [1, 1, 1, 0, 1, 0],      # Dots: 1, 2, 3, 5
    'uang': [0, 1, 1, 0, 1, 1],    # Dots: 2, 3, 5, 6
    'ong': [0, 1, 1, 0, 1, 1],     # Dots: 2, 3, 5, 6
    'v': [1, 1, 0, 0, 1, 0],       # ü -> Dots: 1, 2, 5
    've': [0, 1, 1, 1, 1, 0],      # üe -> Dots: 2, 3, 4, 5
    'van': [1, 1, 1, 0, 0, 1],     # üan -> Dots: 1, 2, 3, 6
    'vn': [1, 1, 1, 1, 1, 0],      # ün -> Dots: 1, 2, 3, 4, 5
    'iong': [1, 0, 0, 1, 1, 1],    # Dots: 1, 4, 5, 6
    'er': [1, 1, 1, 1, 1, 1]       # Dots: 1, 2, 3, 4, 5, 6
}

    # HINDI (Bharati Braille)
    'अ':[1,0,0,0,0,0], 'आ':[0,0,1,1,1,0], 'इ':[0,1,0,0,0,0], 'ई':[0,1,0,0,1,1],
    'उ':[1,0,1,0,0,0], 'ऊ':[1,0,1,1,0,0], 'ए':[1,0,0,0,1,0], 'ऐ':[0,0,1,1,0,0],
    'ओ':[1,0,1,0,1,0], 'औ':[0,1,0,1,1,0], 'क':[1,0,1,0,0,0], 'ख':[1,1,0,0,0,1],
    'ग':[1,1,0,1,1,0], 'घ':[1,0,0,1,1,1], 'च':[1,0,0,1,0,0], 'छ':[0,0,1,1,1,1],
    'ज':[0,1,0,1,1,0], 'झ':[1,1,0,1,0,1], 'त':[0,1,1,1,1,0], 'थ':[1,0,1,1,0,1],
    'द':[1,1,1,0,1,1], 'ध':[0,1,1,1,0,1], 'न':[1,0,1,1,1,0], 'प':[1,1,1,1,0,0],

    # CYRILLIC (Russian)
    russian_braille = {
    'а': [1, 0, 0, 0, 0, 0],      # Dots: 1
    'б': [1, 1, 0, 0, 0, 0],      # Dots: 1, 2
    'в': [0, 1, 0, 1, 1, 1],      # Dots: 2, 4, 5, 6
    'г': [1, 1, 0, 1, 1, 0],      # Dots: 1, 2, 4, 5
    'д': [1, 0, 0, 1, 1, 0],      # Dots: 1, 4, 5
    'е': [1, 0, 0, 0, 1, 0],      # Dots: 1, 5
    'ё': [1, 0, 0, 0, 0, 1],      # Dots: 1, 6
    'ж': [0, 1, 0, 1, 1, 0],      # Dots: 2, 4, 5
    'з': [1, 0, 1, 0, 1, 1],      # Dots: 1, 3, 5, 6
    'и': [0, 1, 0, 1, 0, 0],      # Dots: 2, 4
    'й': [1, 1, 1, 1, 0, 1],      # Dots: 1, 2, 3, 4, 6
    'к': [1, 0, 1, 0, 0, 0],      # Dots: 1, 3
    'л': [1, 1, 1, 0, 0, 0],      # Dots: 1, 2, 3
    'м': [1, 0, 1, 1, 0, 0],      # Dots: 1, 3, 4
    'н': [1, 0, 1, 1, 1, 0],      # Dots: 1, 3, 4, 5
    'о': [1, 0, 1, 0, 1, 0],      # Dots: 1, 3, 5
    'п': [1, 1, 1, 1, 0, 0],      # Dots: 1, 2, 3, 4
    'р': [1, 1, 1, 0, 1, 0],      # Dots: 1, 2, 3, 5
    'с': [0, 1, 1, 1, 0, 0],      # Dots: 2, 3, 4
    'т': [0, 1, 1, 1, 1, 0],      # Dots: 2, 3, 4, 5
    'у': [1, 0, 1, 0, 0, 1],      # Dots: 1, 3, 6
    'ф': [1, 1, 0, 1, 0, 0],      # Dots: 1, 2, 4
    'х': [1, 1, 0, 0, 1, 0],      # Dots: 1, 2, 5
    'ц': [1, 0, 0, 1, 0, 0],      # Dots: 1, 4
    'ч': [1, 1, 1, 1, 1, 0],      # Dots: 1, 2, 3, 4, 5
    'ш': [1, 0, 0, 0, 1, 1],      # Dots: 1, 5, 6
    'щ': [1, 0, 1, 1, 0, 1],      # Dots: 1, 3, 4, 6
    'ъ': [1, 1, 1, 0, 1, 1],      # Dots: 1, 2, 3, 5, 6
    'ы': [0, 1, 1, 1, 0, 1],      # Dots: 2, 3, 4, 6
    'ь': [0, 1, 1, 1, 1, 1],      # Dots: 2, 3, 4, 5, 6
    'э': [0, 1, 0, 1, 0, 1],      # Dots: 2, 4, 6
    'ю': [1, 1, 0, 0, 1, 1],      # Dots: 1, 2, 5, 6
    'я': [1, 1, 0, 1, 0, 1]       # Dots: 1, 2, 4, 6
}
    # NUMBERS & SYMBOLS
    '1':[1,0,0,0,0,0],'2':[1,1,0,0,0,0],'3':[1,0,0,1,0,0],'4':[1,0,0,1,1,0],'5':[1,0,0,0,1,0],
    ' ':[0,0,0,0,0,0],'.':[0,1,0,0,1,1],'?':[0,1,1,0,0,1],'!':[0,1,1,0,1,0]
}

LANG_MAP = {
    'English': 'eng', 'Spanish': 'spa', 'French': 'fra', 'Arabic': 'ara',
    'German': 'deu', 'Russian': 'rus', 'Italian': 'ita', 'Chinese (Sim)': 'chi_sim',
    'Hindi': 'hin'
}

def draw_tactile_cell(draw, text, orig_x, orig_y, orig_w, orig_h, g_scale, ix, iy, gx, gy, i_scale, tightness):
    """Auto-centers the Braille box on the original text location to fix annoying controls"""
    scale = g_scale * i_scale
    dot_r = 2.4 * scale      
    v_spc = 6.8 * scale      
    h_spc = 6.8 * scale      
    cell_w = 26 * scale      

    # 1. Calculate new box dimensions
    box_w = (len(text) * cell_w) + (25 * tightness)
    box_h = 75 * scale * tightness
    
    # 2. AUTO-CENTER LOGIC: Calculate center of detected OCR text
    center_x = orig_x + (orig_w / 2)
    center_y = orig_y + (orig_h / 2)
    
    # 3. Position new box so its center aligns with the original center
    new_x = center_x - (box_w / 2) + ix + gx
    new_y = center_y - (box_h / 2) + iy + gy

    # THE ERASER
    draw.rectangle([new_x, new_y, new_x + box_w, new_y + box_h], fill="white")
    draw.rectangle([new_x, new_y, new_x + box_w, new_y + box_h], outline="black", width=1)
    
    # TACTILE POINTS
    for i, char in enumerate(text.lower()):
        dots = BM.get(char, [0,0,0,0,0,0])
        cx = new_x + (i * cell_w) + 12
        dot_pos = [(0,0), (0,v_spc), (0,v_spc*2), (h_spc,0), (h_spc,v_spc), (h_spc,v_spc*2)]
        for idx, (dx, dy) in enumerate(dot_pos):
            if dots[idx]:
                draw.ellipse([cx+dx, new_y+dy+12, cx+dx+dot_r*2, new_y+dy+dot_r*2+12], fill="black")

# --- 3. UI LAYOUT ---
st.sidebar.title("SwellGPT 🧬")
st.sidebar.markdown("### Made by **Neva Mission**")
... (50 lines left)
