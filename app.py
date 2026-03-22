# %%writefile app.py

import trlib as tr
import trupdate as trU
from trdata import (
    T_BAITS, 
    C_BAITS, 
    FISHING_RODS, 
    FISHING_FRIENDS, 
    ORDERED_ROD_KEYS, 
    ORDERED_FRIENDS_KEYS,
)

import streamlit as st
import numpy as np
import math



st.set_page_config(
    page_title="เครื่องมือคำนวณ Tales Runner แบบครบวงจร",
    page_icon="🎣"
)

st.sidebar.title("รวมเครื่องมือ Tales Runner")
MENU = st.sidebar.radio(
    "เลือกเมนู (จะเพิ่มในภายหลัง)",
    ["คำนวณ EXP และการตกปลา", "EXP ↔ เหยื่อตกปลา"],
    index = 0 # ค่าเริ่มต้น
)
if MENU == "คำนวณ EXP และการตกปลา":
    if st.button("[ รายละเอียดการอัปเดต (26-03-11) ]"):
        trU.update_info()
        
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown(f"<div style='font-size: 25px; font-weight: bold; margin-top: 12px;'>คำนวณ EXP เลเวล", unsafe_allow_html=True)
    with col2:
        if st.button("ฟีดแบ็ก"):
            tr.feedback_dialog()
    if st.session_state.get("feedback_submitted", False):
            st.session_state.feedback_submitted = False
    
    st.write(" ")
    level_name = np.load("lvlExp.npy", allow_pickle=True)
    level_name = level_name[:,0]
    
    # ต้องใช้ภาษาเกาหลีเพื่อให้ตรงกับฐานข้อมูลในไฟล์ lvlExp.npy
    level_color =  ["แดง ", "ส้ม ", "เหลือง ", "เขียว ", "ฟ้า ", "น้ำเงิน ", "ม่วง "]
    level_shoe = [' '.join(level_name[i].split()[1:]) for i in range(0,len(level_name), 7)]


    cols = st.columns([1,1.5,1])
    cur_color = cols[0].selectbox("เลเวลปัจจุบัน", level_color, accept_new_options=False)
    cur_shoe = cols[1].selectbox("", level_shoe, accept_new_options=False)
    cur_per_str = cols[2].text_input("ค่าประสบการณ์ ( % )", value="0.0")
    
    select_cur_level = cur_color+cur_shoe

    cur_level_index = (np.where(level_name == select_cur_level)[0][0]) 

    if cur_per_str.strip() == "":
        current_per = 0.0
    else:
        try:
            current_per = float(cur_per_str)
            if current_per >= 100:
                    st.error("กรุณากรอกตัวเลขที่น้อยกว่า 100")
                    current_per = 0.0
            elif current_per < 0:
                    st.error("กรุณากรอกตัวเลขที่มากกว่าหรือเท่ากับ 0")
                    current_per = 0.0
        except ValueError:
            st.error("กรุณากรอกตัวเลข")
            current_per = 0.0
    
    st.markdown("""
    <style>
        @media (max-width: 600px) {
            div[data-testid="stHorizontalBlock"] {
                overflow-x: auto;
                white-space: nowrap;
                -webkit-overflow-scrolling: touch;
            }
            div[data-testid="stHorizontalBlock"] > div {
                display: inline-block !important;
                vertical-align: top;
                float: none !important;
                white-space: normal;
                min-width: 150px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns([1,1.5,1])
    
    goal_color = cols[0].selectbox("เลเวลเป้าหมาย", level_color, key="goal_color", accept_new_options=False)
    goal_shoe = cols[1].selectbox("", level_shoe, key="goal_shoes", accept_new_options=False)
    select_goal_level = goal_color+goal_shoe
    cols[2].markdown("")
    goal_level_index = (np.where(level_name == select_goal_level)[0][0])
    
    
    use_fish_page = st.checkbox("คำนวณหน้าตกปลา", value=False)
    if use_fish_page:
        st.write(" ")
        st.write("คำนวณหน้าตกปลา")
        cols = st.columns([1,1])
        page1 = cols[0].number_input("กรอกหน้า 1", min_value=0, value=0, step=1)
        page2 = cols[1].number_input("กรอกหน้า 2", min_value=0, value=0, step=1)
        cols2 = st.columns([1,1])
        page3 = cols2[0].number_input("กรอกหน้า 3", min_value=0, value=0, step=1)
        page4 = cols2[1].number_input("กรอกหน้า 4", min_value=0, value=0, step=1)
        cols3 = st.columns([1,1])
        page5 = cols2[0].number_input("กรอกหน้า 5", min_value=0, value=0, step=1)
        page6 = cols2[1].number_input("กรอกหน้า 6", min_value=0, value=0, step=1)
        total_page = page1+page2+page3+page4+page5+page6
    else:
        total_page = 0
        
    expected_level ,exp_required, now_per, use_goal_level, extra_exp = tr.level_expected(cur_level_index, goal_level_index, current_per, total_page)
    
    per = now_per / 100 * 100  # 0~100%

    if extra_exp != -1:
        barText = f"({extra_exp:,} EXP)"
    elif exp_required != -1: 
        barText = f"{now_per:.2f}% (เหลืออีก {exp_required:,} EXP)"
        if (use_goal_level) and (exp_required == 0): barText = f"{now_per:.2f}%"
    else: barText = f"{now_per:.2f}%"
    
    bar_html = f"""
    <div style="width: 100%; background: linear-gradient(90deg, #ddd, #f5f5f5); border: 1px solid #ccc; border-radius: 12px; height: 32px; position: relative; margin-top: 16px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
        <div style="width: {per}%; background: linear-gradient(90deg, #4CAF50, #45a049); height: 100%;
                    border-radius: 12px 0 0 12px; transition: width 0.4s ease;"></div>
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                    display: flex; align-items: center; justify-content: center;
                    font-weight: 600; color: #222; font-size: 15px;">
            {barText}
        </div>
    </div>
    """

    # สำหรับแสดงรูปภาพ

    image_path = f"./level/{expected_level}.png"
    img_base64 = tr.get_image_base64(image_path)
    
    st.markdown(
        f"""
        <div style='font-size: 18px; font-weight: bold; margin-top: 12px; display: flex; align-items: center;'>
            เลเวลที่คาดหวัง :
            <img src='data:image/png;base64,{img_base64}' style='height: 1.1em; margin: 0 5px;'/>
            <span style='font-size: 14px; font-weight: bold;'>{level_name[expected_level]}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown(bar_html, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"<div style='font-size: 25px; font-weight: bold; margin-top: 12px;'>คำนวณเวลาตกปลา", unsafe_allow_html=True)
    
    st.write(" ")
    premium_storage = st.checkbox("ตั๋วพรีเมียม", value=False)
    ability_storage = st.checkbox("[ความสามารถ] กระชังตกปลาแบบพกพา", value=False)
    cols = st.columns(2)
    rod = cols[0].selectbox("ประเภทเบ็ดตกปลา (เรียงตามตัวอักษร)", ORDERED_ROD_KEYS, index=0)

    friend = cols[1].selectbox("เพื่อนตกปลา (เรียงตามตัวอักษร)", ORDERED_FRIENDS_KEYS, index=0)
    min_default, max_default, storage_default = FISHING_RODS[rod]
    f_min, f_max, f_storage = FISHING_FRIENDS[friend]
    
    min_default = max(0, min_default - f_min) 
    max_default = max(0, max_default - f_max) 
    storage_default += f_storage
    
    
    cols = st.columns(2)
    min_fish_time = cols[0].number_input("เวลาตกปลาขั้นต่ำ", min_value=0, value=min_default, step=1)
    max_fish_time = cols[1].number_input("เวลาตกปลาสูงสุด", min_value=0, value=max_default, step=1)
    fish_time = [min_fish_time, max_fish_time]
    if premium_storage: storage_default += 300
    else: storage_default += 150

    if ability_storage: storage_default += 5


    fish_storage = st.number_input("ความจุกระชังสูงสุด", min_value=0, value=storage_default, step=1)
    
    f_average_sec = (min_fish_time+max_fish_time)/2

    st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>ประมาณ {f_average_sec:.1f} วินาที ต่อตัว</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>ใช้เวลาประมาณ {tr.format_time(f_average_sec*fish_storage)} จนกระชังเต็ม</div>", unsafe_allow_html=True)


    if rod == '테런 낚싯대' or rod == "달토끼 낚싯대": # หากต้องการให้แปลชื่อเบ็ดในเงื่อนไขด้วย กรุณาแจ้งเพิ่มเติมได้ครับ
        st.markdown(f"""
            <div style="font-size: 15px; font-weight: bold; margin-top: 12px; margin-bottom: 8px;">
                ข้อมูลตามเวลาของ {rod}
            </div>
            <table style="width:100%; border-collapse: collapse; font-size:13px; line-height:1.6; margin-bottom:16px; border: 1px solid #ccc;">
                <thead>
                    <tr>
                        <th style="text-align:left; padding:8px;">เวลา</th>
                        <th style="text-align:left; padding:8px;">จำนวนที่คาดว่าจะได้รับ</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding:8px;">30 นาที</td>
                        <td style="padding:8px;">ประมาณ {int((30*60)//f_average_sec)} ตัว</td>
                    </tr>
                    <tr>
                        <td style="padding:8px;">1 ชั่วโมง</td>
                        <td style="padding:8px;">ประมาณ {int((60*60)//f_average_sec)} ตัว</td>
                    </tr>
                </tbody>
            </table>
        """, unsafe_allow_html=True)
        
    
    if round((f_average_sec*fish_storage)) != 0 : 
        st.markdown(f"<div style='font-size: 15px; font-weight: bold; margin-top: 12px;'>คำสั่งตั้งเวลาปิดคอมพิวเตอร์ : shutdown -s -t {round((f_average_sec)*fish_storage)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 15px; font-weight: bold; margin-top: 12px;'>คำสั่งยกเลิกการตั้งเวลา : shutdown -a</div>", unsafe_allow_html=True)
    
    st.write(" ")
    if st.button("[ดูคำแนะนำการตั้งเวลาปิดคอมพิวเตอร์]"):
        tr.schedule_info()
    
    st.markdown("---")
    
    if use_goal_level:
        st.markdown("#### ข้อมูลเหยื่อตกปลาที่ต้องใช้สำหรับเลเวลเป้าหมาย")
    
        st.markdown("##### เหยื่อธรรมดา")
        tr.render_bait_cards(T_BAITS, exp_required, fish_time, isCash=False)
    
        st.markdown("##### เหยื่อแคช")
        tr.render_bait_cards(C_BAITS, exp_required, fish_time, isCash=True)
        
elif MENU == "EXP ↔ เหยื่อตกปลา":

    
    all_baits = T_BAITS + C_BAITS
    bait_names = [bait["name"] for bait in all_baits]
    selected_name2 = st.selectbox("เลือกเหยื่อตกปลา", bait_names)
    
    selected_bait = next(b for b in all_baits if b["name"] == selected_name2)
    selected_exp = selected_bait["exp"]

    st.checkbox("EXP ที่ต้องการ → จำนวนเหยื่อที่ต้องใช้", key="selectExp", on_change=tr.set_mode_xp_to_worms)
    st.checkbox("จำนวนเหยื่อ → คำนวณ EXP ที่ได้รับ", key="selectCount", on_change=tr.set_mode_worms_to_xp)

    if not st.session_state.selectExp and not st.session_state.selectCount:    st.session_state.mode = None
    mode = st.session_state.get("mode", None)

    if mode == "xp_to_worms":
        st.subheader("กรอก EXP → คำนวณจำนวนเหยื่อที่ต้องใช้")
    
        target_xp = st.number_input("กรอก EXP เป้าหมาย", min_value=0, value=0, step=1)

        if target_xp > 0:
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>{selected_name2} : ต้องใช้ประมาณ {math.ceil(target_xp/selected_exp):,} ตัว</div>", unsafe_allow_html=True)
            

    elif mode == "worms_to_xp":
        st.subheader("จำนวนเหยื่อ → คำนวณ EXP รวมที่ได้รับ")
        
        target_count = st.number_input("กรอกจำนวนเหยื่อ", min_value=0, value=0, step=1)
        
        if target_count > 0:
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>{selected_name2} จำนวน {target_count} ตัว จะได้ประมาณ {round(selected_exp * target_count):,} EXP</div>", unsafe_allow_html=True)

    
    else:
        st.info("กรุณาเลือกวิธีการคำนวณ")
