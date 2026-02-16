import streamlit as st
import itertools
from PIL import Image, ImageDraw, ImageFont
import io

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="K-LOTTO", page_icon="", layout="centered")

# --- CSS: แต่งหน้าจอให้สวยและซ่อน Element ที่ไม่จำเป็น ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* การ์ดผลลัพธ์ */
    .result-card {
        background-color: #262730;
        border: 2px solid #D4AF37; /* สีทอง */
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 15px 0 rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .den-rong-box {
        display: flex; justify-content: space-around; align-items: center;
        margin-bottom: 10px; border-bottom: 1px solid #555; padding-bottom: 10px;
    }
    .big-num { font-size: 2rem; font-weight: bold; color: #FF4B4B; }
    .sec-header { font-size: 0.9rem; color: #BBB; margin-top: 8px; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Grid ตัวเลข */
    .sniper-grid { 
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; 
        font-weight: bold; font-size: 1.2rem; color: #FFD700;
    }
    .sniper-3-grid {
        display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;
        font-weight: bold; font-size: 1.1rem; color: #00CC96;
    }
    
    .vin-box { font-size: 0.85rem; text-align: left; margin-top: 8px; color: #EEE; background: #333; padding: 5px; border-radius: 5px;}
    .footer { font-size: 0.7rem; color: #666; margin-top: 15px; }
    
    /* ซ่อน UI ของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 1. Logic คำนวณ (เหมือนเดิม) ---
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

# --- 2. ฟังก์ชันวาดรูป (Image Generator) ---
def create_result_image(upper, lower, den, rong, jor, jor3, v7, v_no0):
    W, H = 600, 850
    img = Image.new('RGB', (W, H), color='#0E1117')
    d = ImageDraw.Draw(img)
    try:
        font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
        font_med = ImageFont.truetype("DejaVuSans-Bold.ttf", 35)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 25)
    except:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    def draw_centered(text, y, font, fill):
        bbox = d.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        d.text(((W-w)/2, y), text, font=font, fill=fill)

    d.rectangle([(20, 20), (W-20, H-20)], outline="#D4AF37", width=5)
    draw_centered("K-LOTTO ANALYZER", 50, font_med, "#FFFFFF")
    draw_centered(f"ผล: {upper} - {lower}", 100, font_small, "#AAAAAA")
    
    d.line([(50, 150), (W-50, 150)], fill="#555555", width=2)
    d.text((100, 180), f"🔥 เด่น: {den}", font=font_large, fill="#FF4B4B")
    d.text((350, 180), f"🚩 รอง: {rong}", font=font_large, fill="#FAFAFA")
    d.line([(50, 260), (W-50, 260)], fill="#555555", width=2)

    draw_centered("🎯 เจาะเน้น", 280, font_med, "#FFFFFF")
    y_start = 350
    for i, num in enumerate(jor):
        row = i // 4
        col = i % 4
        x = 70 + (col * 120)
        y = y_start + (row * 60)
        d.text((x, y), num, font=font_med, fill="#FFD700")

    draw_centered("🎲 เจาะ 3 ตัว", 500, font_med, "#FFFFFF")
    y_start = 560
    for i, num in enumerate(jor3[:3]):
        d.text((50 + (i*180), y_start), num, font=font_med, fill="#00CC96")
    d.text((140, y_start+60), jor3[3], font=font_med, fill="#00CC96")
    d.text((320, y_start+60), jor3[4], font=font_med, fill="#00CC96")

    y_vin = 680
    d.text((50, y_vin), f"💎 : {' '.join(map(str, v7))}", font=font_small, fill="#EEEEEE")
    d.text((50, y_vin+40), f"🛡️ : {' '.join(map(str, v_no0))}", font=font_small, fill="#AAAAAA")
    draw_centered("by khet", 780, font_small, "#666666")
    return img

# --- 3. UI State Management (ระบบสลับหน้า) ---

# สร้างตัวแปรเก็บสถานะหน้า (Session State)
if 'page' not in st.session_state:
    st.session_state.page = 'input' # เริ่มต้นที่หน้า Input
if 'result_data' not in st.session_state:
    st.session_state.result_data = None

# ฟังค์ชั่นสำหรับเปลี่ยนหน้า
def go_to_result():
    st.session_state.page = 'result'
def go_to_input():
    st.session_state.page = 'input'

# --- หน้าจอที่ 1: กรอกข้อมูล (Input Page) ---
if st.session_state.page == 'input':
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>By Khet", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#888;'>ระบบคำนวณ</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.form("calc_form"):
        c1, c2 = st.columns(2)
        upper = c1.text_input("🔹 เลขบน", max_chars=3)
        lower = c2.text_input("🔸 เลขล่าง", max_chars=2)
        
        submitted = st.form_submit_button("🚀 คำนวณสูตร", use_container_width=True)
        
        if submitted:
            if len(upper) >= 2 and len(lower) == 2 and upper.isdigit() and lower.isdigit():
                # คำนวณและบันทึกผลลง Session
                res = calculate_mbfs_v25(upper, lower)
                st.session_state.result_data = {
                    'upper': upper, 'lower': lower,
                    'den': res[0], 'rong': res[1],
                    'v5': res[2], 'v6': res[3], 'v7': res[4], 'v_no0': res[5],
                    'jor': res[6], 'jor3': res[7]
                }
                go_to_result() # สั่งเปลี่ยนหน้า
                st.rerun() # รีเฟรชหน้าจอทันที
            else:
                st.error("⚠️ กรุณากรอกตัวเลขให้ครบถ้วน")

# --- หน้าจอที่ 2: แสดงผลลัพธ์ (Result Page) ---
elif st.session_state.page == 'result':
    data = st.session_state.result_data
    
    # สร้างรูปภาพเตรียมไว้
    img = create_result_image(
        data['upper'], data['lower'], data['den'], data['rong'],
        data['jor'], data['jor3'], data['v7'], data['v_no0']
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    # แสดงการ์ดผลลัพธ์ (HTML)
    st.markdown(f"""
    <div class="result-card">
        <div style="font-size:0.8rem; color:#888;">ผล: {data['upper']} - {data['lower']}</div>
        <div class="den-rong-box">
            <div>🔥 เด่น<br><span class="big-num">{data['den']}</span></div>
            <div>🚩 รอง<br><span style="font-size:1.8rem; font-weight:bold;">{data['rong']}</span></div>
        </div>
        
        <div class="sec-header">🎯 เจาะเน้น</div>
        <div class="sniper-grid">
            {''.join([f'<div>{n}</div>' for n in data['jor']])}
        </div>
        
        <div class="sec-header" style="margin-top:10px;">🎲 เจาะ 3 ตัว</div>
        <div class="sniper-3-grid">
            {''.join([f'<div>{n}</div>' for n in data['jor3']])}
        </div>
        
        <div style="margin-top:10px; border-top:1px solid #444; padding-top:5px;">
            <div class="vin-box">💎 : <span style="color:#FFF;">{' '.join(map(str, data['v7']))}</span></div>
            <div class="vin-box">🛡️ : <span style="color:#AAA;">{' '.join(map(str, data['v_no0']))}</span></div>
        </div>
        <div class="footer">by khet</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ปุ่มควบคุม (Download & Back)
    col_dl, col_reset = st.columns([1, 1])
    
    with col_dl:
        st.download_button(
            label="📸 โหลด",
            data=byte_im,
            file_name=f"KLOTTO_{data['upper']}-{data['lower']}.png",
            mime="image/png",
            use_container_width=True
        )
        
    with col_reset:
        if st.button("🔄 คำนวณใหม่", use_container_width=True):
            go_to_input()
            st.rerun()
