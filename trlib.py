# %%writefile trlib.py

import streamlit as st
import numpy as np

import gspread
from google.oauth2.service_account import Credentials
import datetime
from zoneinfo import ZoneInfo

import base64 
import math

def connect_to_gsheet():

    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
    client = gspread.authorize(creds)

    SHEET_NAME = "trfish-feedback"
    sheet = client.open(SHEET_NAME).sheet1

    return sheet

def save_feedback(name, feedback):
    sheet = connect_to_gsheet()
    now = datetime.datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, feedback, now])

def level_expected(current_level, goal_level, current_per, page_total):
    level_data = np.load('lvlExp.npy', allow_pickle=True)
    current_exp = level_data[current_level][2] + (level_data[current_level][1] * (current_per/100)) + page_total
    indices = np.where(level_data[:,2] <= current_exp)[0]
    expected_level = indices[-1] if len(indices) > 0 else 0

    use_goal_level = (goal_level != -1) and (goal_level > current_level)

    if use_goal_level: 
        exp_required = max(0, int(level_data[goal_level][2] - current_exp))
    else: # กรณีไม่ใช้เลเวลเป้าหมาย
        exp_required = -1 

    if expected_level >= len(level_data) - 1:
        now_per = 100.0
    else:
        now_per = (level_data[expected_level][1] - (level_data[expected_level+1][2] - current_exp)) * (100 / level_data[expected_level][1])

    if expected_level >= len(level_data) - 1:
        extra_exp = int(current_exp)
    else: 
        extra_exp = -1
    
    return expected_level ,exp_required, now_per, use_goal_level, extra_exp

def calc_bait(fish_time): return sum(fish_time) / 2

def format_time(total_seconds):
    days = int(total_seconds // (60 * 60 * 24))
    hours = int((total_seconds % (60 * 60 * 24)) // (60 * 60))
    minutes = int((total_seconds % (60 * 60)) // 60)

    parts = []
    if days > 0:
        parts.append(f"{days} วัน")
    if hours > 0:
        parts.append(f"{hours} ชั่วโมง")
    if minutes > 0:
        parts.append(f"{minutes} นาที")

    if not parts:  # กรณีเป็น 0 ทั้งหมด
        return "0 นาที"
    return " ".join(parts)

@st.dialog("วิธีใช้คำสั่งตั้งเวลาปิดคอม")
def schedule_info():
    st.markdown("""
1. กดปุ่ม `Windows` + `R` พร้อมกันบนคีย์บอร์ดเพื่อเปิดหน้าต่าง `Run`  
2. วางคำสั่งลงในช่องแล้วกดปุ่ม `Enter`  

> ℹ️ นี่เป็นเวลาโดยเฉลี่ย อาจมีความคลาดเคลื่อนจากผลการตกปลาจริงได้  
> กรุณาเลือกเบ็ดตกปลาและเพื่อนตกปลาก่อนนำคำสั่งไปใช้งาน  
""")


@st.dialog("ส่งข้อเสนอแนะ")
def feedback_dialog():
    st.markdown("หากต้องการให้เพิ่มไอเทมหรือมีข้อเสนอแนะเพิ่มเติม สามารถแจ้งได้เลยครับ 😊")
    st.markdown("ยินดีรับฟังทุกไอเดียครับ!")
    st.markdown("> ℹ️ แบบฟอร์มนี้จะไม่เก็บข้อมูลส่วนตัวใดๆ ของผู้ใช้ เช่น IP Address")
    # name = st.text_input("ชื่อเล่น (ไม่ระบุก็ได้):") # ไม่จำเป็นต้องรับข้อมูลชื่อ
    name = "ไม่ระบุนาม"
    feedback = st.text_area("กรุณาพิมพ์ข้อเสนอแนะของคุณ")

    if st.button("ส่ง"):
        # if not name.strip():
        #     # st.warning("กรุณากรอกชื่อ")
        #     name = "ไม่ระบุนาม" # หากต้องการให้รับชื่อ
        if not feedback.strip():
            st.warning("กรุณากรอกข้อเสนอแนะ")
            return
        save_feedback(name, feedback)
        st.success("ขอบคุณสำหรับข้อเสนอแนะครับ! 🎉")
        st.session_state.feedback_submitted = True

def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_price(bait, isCash):
    return bait["cash"] if isCash else bait["tr"]
    
def get_total_text(count, price, isCash):
    if price == -1:
        return "[กิจกรรมเทศกาลชูซอก] ไม่สามารถซื้อได้"
    elif price == -2:
        return "[ไม่สามารถรับได้]"
    elif price == -3:
        return "[กิจกรรมจำกัดเวลา]"
    else:
        total = count * price
        currency = "Cash" if isCash else "TR"
        return f"{total:,} {currency}"

def render_bait_cards(baits, exp_required, fish_time, isCash=False):
    cols = st.columns(2)  # สร้าง 2 คอลัมน์

    for i, bait in enumerate(baits):
        count = math.ceil(exp_required / bait["exp"])

        price = get_price(bait, isCash)

        total_print = get_total_text(count, price, isCash)
        total_seconds = count * calc_bait(fish_time)
        
        
        with cols[i % 2]:
            st.markdown(f"""
            <table style="width:100%; border-collapse: collapse; font-size:13px; line-height:1.6; margin-bottom:16px;">
                <thead>
                    <tr>
                        <th style="text-align:left; padding:8px; font-size:16px;" colspan="2">{bait['name']}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding:8px; width:50%;"><b>จำนวน:</b></td>
                        <td style="padding:8px;">{count:,} ตัว</td>
                    </tr>
                    <tr>
                        <td style="padding:8px;"><b>{'รวม Cash:' if isCash else 'รวม TR:'}</b></td>
                        <td style="padding:8px;">{total_print}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px;"><b>เวลาที่คาดว่าจะใช้:</b></td>
                        <td style="padding:8px;">{format_time(total_seconds)}</td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)


def set_mode_xp_to_worms():
    st.session_state.mode = "xp_to_worms"
    st.session_state.selectCount = False

def set_mode_worms_to_xp():
    st.session_state.mode = "worms_to_xp"
    st.session_state.selectExp = False
