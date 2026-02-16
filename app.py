import streamlit as st
import itertools

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="K-L",
    page_icon="🎰",
    layout="centered"
)

# --- ใส่ CSS ให้ดูสวยแบบ Dark Mode ---
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .result-box {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #4F4F4F;
        margin-bottom: 20px;
    }
    .highlight {
        color: #FF4B4B;
        font-weight: bold;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: white;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #4F4F4F;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. ส่วนคำนวณ (Logic v25) ---
def calculate_mbfs_v25(upper_3, lower_2):
    if len(upper_3) == 3:
        t_up = int(upper_3[1])
        u_up = int(upper_3[2])
    else:
        t_up = int(upper_3[0])
        u_up = int(upper_3[1])
        
    t_low = int(lower_2[0])
    u_low = int(lower_2[1])

    base_a = (t_up + u_up + t_low + u_low) % 10
    base_b = (t_up + u_low) % 10

    den = base_a
    rong = base_b

    flow_map = {
        1: [7, 8, 4], 2: [5, 6, 9], 3: [8, 4, 7],
        4: [2, 9, 5], 5: [1, 2, 8], 6: [9, 7, 2],
        7: [1, 3, 8], 8: [3, 4, 1], 9: [6, 4, 5],
        0: [1, 9, 2]
    }
    mirror_map = {1:6, 2:7, 3:8, 4:9, 5:0, 6:1, 7:2, 8:3, 9:4, 0:5}

    priority_list = []
    priority_list.append(den)
    if rong not in priority_list: priority_list.append(rong)
    
    candidates_a = flow_map.get(den, [])
    candidates_b = flow_map.get(rong, [])
    
    max_len = max(len(candidates_a), len(candidates_b))
    for i in range(max_len):
        if i < len(candidates_a):
            n = candidates_a[i]
            if n not in priority_list: priority_list.append(n)
        if i < len(candidates_b):
            n = candidates_b[i]
            if n not in priority_list: priority_list.append(n)
            
    if den in mirror_map:
        n = mirror_map[den]
        if n not in priority_list: priority_list.append(n)
    if rong in mirror_map:
        n = mirror_map[rong]
        if n not in priority_list: priority_list.append(n)
        
    for dist in [1, -1, 2, -2, 3, -3]:
        for b in [den, rong]:
            n = (b + dist) % 10
            if n not in priority_list: priority_list.append(n)

    vin_main_5 = sorted(priority_list[:5])
    vin_main_6 = sorted(priority_list[:6])
    vin_main_7 = sorted(priority_list[:7]) 
    no_zero_list = [x for x in priority_list if x != 0]
    vin_no_zero_7 = sorted(no_zero_list[:7])

    jor_sets = []
    for partner in candidates_a:
        pair = f"{den}{partner}"
        if pair not in jor_sets and f"{partner}{den}" not in jor_sets:
            jor_sets.append(pair)
            
    if den != rong:
        for partner in candidates_b:
            pair = f"{rong}{partner}"
            if pair not in jor_sets and f"{partner}{rong}" not in jor_sets:
                jor_sets.append(pair)
                
    pair_dr = f"{den}{rong}"
    if pair_dr not in jor_sets and f"{rong}{den}" not in jor_sets:
        jor_sets.insert(0, pair_dr)

    if len(jor_sets) < 8:
        extras = list(itertools.combinations(vin_main_5, 2))
        for p in extras:
            pair_str = f"{p[0]}{p[1]}"
            if pair_str not in jor_sets and f"{p[1]}{p[0]}" not in jor_sets:
                jor_sets.append(pair_str)
            if len(jor_sets) >= 8: break
    jor_sets = jor_sets[:8]

    jor_3_sets = []
    seen_3_sets = set()
    pool_candidates = []

    c1 = candidates_a[0] if candidates_a else (den+1)%10
    pool_candidates.append([den, rong, c1])
    
    c2 = candidates_a[1] if len(candidates_a)>1 else (den-1)%10
    pool_candidates.append([den, c1, c2])
    
    r1 = candidates_b[0] if candidates_b else (rong+1)%10
    r2 = candidates_b[1] if len(candidates_b)>1 else (rong-1)%10
    pool_candidates.append([rong, r1, r2])
    
    pool_candidates.append(priority_list[:3])
    
    sorted_vin = sorted(vin_main_7)
    seq_set = []
    for i in range(len(sorted_vin)-2):
        if sorted_vin[i+1] == sorted_vin[i]+1 and sorted_vin[i+2] == sorted_vin[i]+2:
            seq_set = [sorted_vin[i], sorted_vin[i+1], sorted_vin[i+2]]
            break
    if seq_set: pool_candidates.append(seq_set)
    else: pool_candidates.append([priority_list[0], priority_list[3], priority_list[4]])

    backup_combs = list(itertools.combinations(vin_main_7, 3))
    for combo in backup_combs[:10]: pool_candidates.append(list(combo))

    for s in pool_candidates:
        if len(jor_3_sets) >= 5: break
        unique_s = list(set(s))
        fill_idx = 0
        while len(unique_s) < 3:
            if fill_idx < len(vin_main_7):
                if vin_main_7[fill_idx] not in unique_s:
                    unique_s.append(vin_main_7[fill_idx])
            fill_idx += 1
        unique_s.sort()
        sig = f"{unique_s[0]}{unique_s[1]}{unique_s[2]}"
        if sig not in seen_3_sets:
            seen_3_sets.add(sig)
            jor_3_sets.append(sig)

    return den, rong, vin_main_5, vin_main_6, vin_main_7, vin_no_zero_7, jor_sets, jor_3_sets

# --- 2. ส่วนหน้าเว็บ (UI) ---
st.title("KHET")
st.caption("ระบบคำนวณ")

col1, col2 = st.columns(2)
with col1:
    upper = st.text_input("🔹 บน (3 ตัว)", max_chars=3, placeholder="เช่น 032")
with col2:
    lower = st.text_input("🔸 ล่าง (2 ตัว)", max_chars=2, placeholder="เช่น 12")

if st.button("🚀 คำนวณสูตร", use_container_width=True):
    if len(upper) >= 2 and len(lower) == 2 and upper.isdigit() and lower.isdigit():
        den, rong, v5, v6, v7, v_no0, jor, jor3 = calculate_mbfs_v25(upper, lower)
        
        st.markdown("---")
        st.subheader("✨ แนวทาง            ")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='result-box' style='text-align:center;'>🔥 เด่น<br><span class='big-font highlight'>{den}</span></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='result-box' style='text-align:center;'>🚩 รอง<br><span class='big-font'>{rong}</span></div>", unsafe_allow_html=True)
            
        st.markdown("##### 🎯 เจาะเน้น")
        jor_html = ""
        for i, num in enumerate(jor):
            jor_html += f"<span style='font-size:20px; font-weight:bold; margin-right:15px; color:#FFD700;'>{num}</span>"
            if i == 3: jor_html += "<br>"
        st.markdown(f"<div class='result-box' style='text-align:center;'>{jor_html}</div>", unsafe_allow_html=True)

        st.markdown("##### 🎲 เจาะ 3 ตัว")
        jor3_html = ""
        for i, num in enumerate(jor3):
            jor3_html += f"<span style='font-size:20px; font-weight:bold; margin-right:15px; color:#00CC96;'>{num}</span>"
            if i == 2: jor3_html += "<br>"
        st.markdown(f"<div class='result-box' style='text-align:center;'>{jor3_html}</div>", unsafe_allow_html=True)

        st.markdown("##### 💎 ชุดวิน")
        st.markdown(f"""
        <div class='result-box'>
            <b>วิน 5 ตัว :</b> <span class='highlight'>{' '.join(map(str, v5))}</span><br>
            <b>วิน 6 ตัว :</b> {' '.join(map(str, v6))}<br>
            <b>วิน 7 ตัว :</b> {' '.join(map(str, v7))}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### 🛡️")
        st.success(f"{' '.join(map(str, v_no0))}")
        
    else:
        st.error("⚠️ กรุณากรอกตัวเลขให้ครบถ้วน")

st.markdown("<div class='footer'>by khet</div>", unsafe_allow_html=True)
