import streamlit as st
import itertools
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="K-LOTTO", page_icon="", layout="centered")

# --- CSS: แต่งหน้าจอ ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    
    /* การ์ดผลลัพธ์ */
    .result-card {
        background-color: #262730;
        border: 2px solid #D4AF37;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px 0 rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    /* กล่องเด่นรอง */
    .den-rong-box {
        display: flex; justify-content: space-around; align-items: center;
        margin-bottom: 10px; border-bottom: 1px solid #555; padding-bottom: 10px;
    }
    .big-num { font-size: 2.2rem; font-weight: bold; color: #FF4B4B; }
    .sub-num { font-size: 2.2rem; font-weight: bold; color: #FAFAFA; }
    
    /* หัวข้อ */
    .sec-header { 
        font-size: 1rem; color: #BBB; margin-top: 10px; margin-bottom: 5px; 
        text-transform: uppercase; letter-spacing: 1px; border-top: 1px solid #444; padding-top: 5px;
    }
    
    /* Grid ตัวเลข */
    .sniper-grid { 
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; 
        font-weight: bold; font-size: 1.2rem; color: #FFD700;
    }
    .sniper-3-grid {
        display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;
        font-weight: bold; font-size: 1.1rem; color: #00CC96;
    }
    
    /* กล่องวิน */
    .vin-container {
        text-align: left;
        background: #1E1E1E;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .vin-row {
        display: flex;
        margin-bottom: 4px;
        font-size: 0.9rem;
    }
    .vin-label {
        color: #AAA;
        width: 70px;
        font-weight: bold;
    }
    .vin-val {
        color: #FFF;
        font-weight: bold;
        letter-spacing: 2px;
    }
    .no-zero { color: #888; letter-spacing: 2px; }

    .footer { font-size: 0.7rem; color: #666; margin-top: 15px; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- คำนวณ ---
def calculate_mbfs_v25(upper_3, lower_2):
    if len(upper_3) == 3: t_up, u_up = int(upper_3[1]), int(upper_3[2])
    else: t_up, u_up = int(upper_3[0]), int(upper_3[1])
    t_low, u_low = int(lower_2[0]), int(lower_2[1])

    base_a = (t_up + u_up + t_low + u_low) % 10
    base_b = (t_up + u_low) % 10
    den, rong = base_a, base_b

    flow_map = {0:[1,9,2], 1:[7,8,4], 2:[5,6,9], 3:[8,4,7], 4:[2,9,5], 
                5:[1,2,8], 6:[9,7,2], 7:[1,3,8], 8:[3,4,1], 9:[6,4,5]}
    mirror_map = {1:6, 2:7, 3:8, 4:9, 5:0, 6:1, 7:2, 8:3, 9:4, 0:5}

    priority_list = [den]
    if rong not in priority_list: priority_list.append(rong)
    
    cand_a = flow_map.get(den, [])
    cand_b = flow_map.get(rong, [])
    for i in range(max(len(cand_a), len(cand_b))):
        if i < len(cand_a) and cand_a[i] not in priority_list: priority_list.append(cand_a[i])
        if i < len(cand_b) and cand_b[i] not in priority_list: priority_list.append(cand_b[i])
            
    if den in mirror_map and mirror_map[den] not in priority_list: priority_list.append(mirror_map[den])
    if rong in mirror_map and mirror_map[rong] not in priority_list: priority_list.append(mirror_map[rong])
    
    for dist in [1, -1, 2, -2]:
        for b in [den, rong]:
            n = (b + dist) % 10
            if n not in priority_list: priority_list.append(n)

    v5 = sorted(priority_list[:5])
    v6 = sorted(priority_list[:6])
    v7 = sorted(priority_list[:7])
    v_no0 = sorted([x for x in priority_list if x != 0][:7])

    jor_sets = []
    for p in cand_a:
        pair = f"{den}{p}"
        if pair not in jor_sets and f"{p}{den}" not in jor_sets: jor_sets.append(pair)
    if den != rong:
        for p in cand_b:
            pair = f"{rong}{p}"
            if pair not in jor_sets and f"{p}{rong}" not in jor_sets: jor_sets.append(pair)
    if f"{den}{rong}" not in jor_sets and f"{rong}{den}" not in jor_sets: jor_sets.insert(0, f"{den}{rong}")
    
    if len(jor_sets) < 8:
        extras = list(itertools.combinations(v5, 2))
        for p in extras:
            pair = f"{p[0]}{p[1]}"
            if pair not in jor_sets and f"{p[1]}{p[0]}" not in jor_sets: jor_sets.append(pair)
            if len(jor_sets) >= 8: break
    jor_sets = jor_sets[:8]

    jor3 = []
    pool = []
    c1 = cand_a[0] if cand_a else (den+1)%10
    pool.append([den, rong, c1])
    c2 = cand_a[1] if len(cand_a)>1 else (den-1)%10
    pool.append([den, c1, c2])
    r1 = cand_b[0] if cand_b else (rong+1)%10
    r2 = cand_b[1] if len(cand_b)>1 else (rong-1)%10
    pool.append([rong, r1, r2])
    pool.append(priority_list[:3])
    backups = list(itertools.combinations(v7, 3))
    for b in backups[:10]: pool.append(list(b))

    seen = set()
    for s in pool:
        if len(jor3) >= 5: break
        uniq = sorted(list(set(s)))
        while len(uniq) < 3:
            for x in v7:
                if x not in uniq: uniq.append(x); break
        uniq.sort()
        sig = "".join(map(str, uniq))
        if sig not in seen:
            seen.add(sig)
            jor3.append(sig)

    return den, rong, v5, v6, v7, v_no0, jor_sets, jor3

# --- ฟังก์ชันวาดรูป (แก้เรื่องฟอนต์ไทยสี่เหลี่ยม) ---
def create_result_image(upper, lower, den, rong, jor, jor3, v5, v6, v7, v_no0):
    W, H = 600, 950 # เพิ่มความสูงเผื่อวิน
    img = Image.new('RGB', (W, H), color='#0E1117')
    d = ImageDraw.Draw(img)
    
    # *** จุดสำคัญ: โหลดฟอนต์ไทยที่อัปโหลดไว้ ***
    # ชื่อไฟล์ต้องตรงกับที่อัปโหลดใน GitHub (เช่น Kanit-Bold.ttf)
    font_name = "Kanit-Bold.ttf" 
    
    try:
        font_large = ImageFont.truetype(font_name, 60)
        font_med = ImageFont.truetype(font_name, 40)
        font_small = ImageFont.truetype(font_name, 28)
        font_xs = ImageFont.truetype(font_name, 22)
    except:
        # ถ้าหาไม่เจอจริงๆ จะใช้ Default (แต่มันจะไม่อ่านไทย)
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_xs = ImageFont.load_default()

    def draw_centered(text, y, font, fill):
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        d.text(((W-w)/2, y), text, font=font, fill=fill)

    # 1. Header
    d.rectangle([(20, 20), (W-20, H-20)], outline="#D4AF37", width=5)
    draw_centered("K-LOTTO ANALYZER", 60, font_med, "#FFFFFF")
    draw_centered(f"ผล: {upper} - {lower}", 120, font_small, "#AAAAAA")
    
    # 2. Den/Rong
    d.line([(50, 170), (W-50, 170)], fill="#555555", width=2)
    
    # วาดเด่นซ้าย รองขวา แบบจัดระยะเอง
    d.text((100, 200), f"🔥 เด่น", font=font_small, fill="#FF4B4B")
    d.text((120, 240), str(den), font=font_large, fill="#FF4B4B")
    
    d.text((380, 200), f"🚩 รอง", font=font_small, fill="#FAFAFA")
    d.text((400, 240), str(rong), font=font_large, fill="#FAFAFA")
    
    d.line([(50, 330), (W-50, 330)], fill="#555555", width=2)

    # 3. เจาะ 8 ชุด
    draw_centered("🎯 เจาะเน้น", 350, font_med, "#FFFFFF")
    y_start = 420
    for i, num in enumerate(jor):
        row = i // 4
        col = i % 4
        x = 70 + (col * 120)
        y = y_start + (row * 60)
        d.text((x, y), num, font=font_med, fill="#FFD700")

    # 4. เจาะ 3 ตัว
    draw_centered("🎲 เจาะ 3 ตัว", 560, font_med, "#FFFFFF")
    y_start = 620
    for i, num in enumerate(jor3[:3]):
        d.text((50 + (i*180), y_start), num, font=font_med, fill="#00CC96")
    if len(jor3) > 3: d.text((140, y_start+60), jor3[3], font=font_med, fill="#00CC96")
    if len(jor3) > 4: d.text((320, y_start+60), jor3[4], font=font_med, fill="#00CC96")

    # 5. วิน (แก้ไขให้ครบ 5,6,7)
    y_vin = 750
    d.line([(50, y_vin), (W-50, y_vin)], fill="#555555", width=1)
    
    # วาดทีละบรรทัด
    d.text((60, y_vin + 20), "💎 ชุดวิน", font=font_small, fill="#FFFFFF")
    
    d.text((80, y_vin + 60), "5 ตัว : ", font=font_xs, fill="#AAAAAA")
    d.text((180, y_vin + 60), ' '.join(map(str, v5)), font=font_small, fill="#FFFFFF")
    
    d.text((80, y_vin + 100), "6 ตัว : ", font=font_xs, fill="#AAAAAA")
    d.text((180, y_vin + 100), ' '.join(map(str, v6)), font=font_small, fill="#FFFFFF")
    
    d.text((80, y_vin + 140), "7 ตัว : ", font=font_xs, fill="#AAAAAA")
    d.text((180, y_vin + 140), ' '.join(map(str, v7)), font=font_small, fill="#FFFFFF")

    # by khet
    draw_centered("by khet", H-50, font_xs, "#666666")

    return img

# --- UI State Management ---
if 'page' not in st.session_state: st.session_state.page = 'input'
if 'result_data' not in st.session_state: st.session_state.result_data = None

def go_to_result(): st.session_state.page = 'result'
def go_to_input(): st.session_state.page = 'input'

# --- PAGE 1: INPUT ---
if st.session_state.page == 'input':
    st.markdown("<br><h1 style='text-align: center;'>By Khet</h1>", unsafe_allow_html=True)
    st.markdown("---")
    with st.form("calc_form"):
        c1, c2 = st.columns(2)
        upper = c1.text_input("🔹 เลขบน ", max_chars=3)
        lower = c2.text_input("🔸 เลขล่าง ", max_chars=2)
        if st.form_submit_button("🚀 คำนวณสูตร", use_container_width=True):
            if len(upper) >= 2 and len(lower) == 2 and upper.isdigit() and lower.isdigit():
                den, rong, v5, v6, v7, v_no0, jor, jor3 = calculate_mbfs_v25(upper, lower)
                st.session_state.result_data = {
                    'upper': upper, 'lower': lower, 'den': den, 'rong': rong,
                    'v5': v5, 'v6': v6, 'v7': v7, 'v_no0': v_no0,
                    'jor': jor, 'jor3': jor3
                }
                go_to_result()
                st.rerun()
            else:
                st.error("⚠️ กรุณากรอกตัวเลขให้ครบถ้วน")

# --- PAGE 2: RESULT ---
elif st.session_state.page == 'result':
    d = st.session_state.result_data
    
    # สร้างรูปภาพ (ส่ง v5, v6 ไปด้วย)
    img = create_result_image(d['upper'], d['lower'], d['den'], d['rong'], d['jor'], d['jor3'], d['v5'], d['v6'], d['v7'], d['v_no0'])
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    # เตรียม HTML ของเจาะ 8 ชุด
    jor_html = "".join([f"<div>{n}</div>" for n in d['jor']])
    
    # เตรียม HTML ของเจาะ 3 ตัว
    jor3_html = "".join([f"<div>{n}</div>" for n in d['jor3']])

    # แสดงผล Card (แก้ HTML ให้ไม่พัง)
    st.markdown(f"""
    <div class="result-card">
        <div style="font-size:0.8rem; color:#888;">ผล: {d['upper']} - {d['lower']}</div>
        <div class="den-rong-box">
            <div>🔥 เด่น<br><span class="big-num">{d['den']}</span></div>
            <div>🚩 รอง<br><span class="sub-num">{d['rong']}</span></div>
        </div>
        
        <div class="sec-header">🎯 เจาะเน้น</div>
        <div class="sniper-grid">{jor_html}</div>
        
        <div class="sec-header">🎲 เจาะ 3 ตัว</div>
        <div class="sniper-3-grid">{jor3_html}</div>
        
        <div class="sec-header">💎 ชุดวิน</div>
        <div class="vin-container">
            <div class="vin-row"><div class="vin-label">5 ตัว :</div><div class="vin-val">{' '.join(map(str, d['v5']))}</div></div>
            <div class="vin-row"><div class="vin-label">6 ตัว :</div><div class="vin-val">{' '.join(map(str, d['v6']))}</div></div>
            <div class="vin-row"><div class="vin-label">7 ตัว :</div><div class="vin-val">{' '.join(map(str, d['v7']))}</div></div>
            <div class="vin-row" style="margin-top:5px;"><div class="vin-label">No 0 :</div><div class="K">{' '.join(map(str, d['v_no0']))}</div></div>
        </div>

        <div class="footer">by khet</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.download_button("📸 โหลด", data=byte_im, file_name=f"KLOTTO-{d['upper']}.png", mime="image/png", use_container_width=True)
    if c2.button("🔄 คำนวณใหม่", use_container_width=True):
        go_to_input()
        st.rerun()
