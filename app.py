import streamlit as st
import pandas as pd
from openai import OpenAI
import datetime

# --- [ตั้งค่าหน้าตาแอป] ---
st.set_page_config(page_title="My Wallet AI", page_icon="💰", layout="centered")

# Custom CSS ให้เหมือน Apple Wallet
st.markdown("""
    <style>
    .main { background-color: #f5f5f7; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #007aff; color: white; border: none; }
    .debt-card {
        background: linear-gradient(135deg, #1c1c1e 0%, #3a3a3c 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .total-banner {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #007aff;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- [ส่วนจัดการข้อมูล - จำลองการเชื่อมต่อ] ---
if 'debt_data' not in st.session_state:
    st.session_state.debt_data = []
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# --- [UI: ส่วนหัวแอป] ---
st.title("💰 My Wallet AI")
st.write(f"วันที่: {datetime.date.today().strftime('%d/%m/%Y')}")

tab1, tab2, tab3 = st.tabs(["หนี้สิน", "รายรับ-จ่าย", "วิเคราะห์ AI"])

with tab1:
    st.subheader("💳 รายการหนี้สิน")
    
    # ฟอร์มเพิ่มหนี้
    with st.expander("➕ เพิ่มรายการหนี้"):
        d_name = st.text_input("ชื่อหนี้ (เช่น บัตรเครดิต, ผ่อนรถ)")
        d_amount = st.number_input("ยอดหนี้คงเหลือ", min_value=0.0)
        d_interest = st.number_input("ดอกเบี้ยต่อปี (%)", min_value=0.0)
        d_term = st.number_input("ระยะเวลาที่เหลือ (เดือน)", min_value=1)
        
        if st.button("บันทึกหนี้สิน"):
            st.session_state.debt_data.append({
                "name": d_name, "amount": d_amount, 
                "interest": d_interest, "term": d_term
            })
            st.success("บันทึกเรียบร้อย")

    # แสดงผล Card หนี้
    total_debt = 0
    total_monthly_pay = 0
    
    for item in st.session_state.debt_data:
        # คำนวณยอดจ่ายต่อเดือนแบบคร่าวๆ (เงินต้น/ระยะเวลา + ดอกเบี้ย)
        monthly_interest = (item['amount'] * (item['interest']/100)) / 12
        monthly_installment = (item['amount'] / item['term']) + monthly_interest
        
        st.markdown(f"""
        <div class="debt-card">
            <small>{item['name']}</small>
            <h2>฿{item['amount']:,.2f}</h2>
            <p>ต้องจ่ายเดือนละ: ฿{monthly_installment:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        total_debt += item['amount']
        total_monthly_pay += monthly_installment

    # บรรทัดสรุปยอดหนี้รวม
    st.markdown(f"""
    <div class="total-banner">
        <small>ยอดหนี้รวมทั้งหมด</small>
        <h2 style='color:#ff3b30;'>฿{total_debt:,.2f}</h2>
        <p>ยอดที่ต้องเตรียมจ่ายต่อเดือน: <b>฿{total_monthly_pay:,.2f}</b></p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.subheader("📝 บันทึกรายรับ-รายจ่าย")
    t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
    t_detail = st.text_input("รายละเอียด")
    t_amount = st.number_input("จำนวนเงิน", min_value=0.0)
    
    # อัปโหลดสลิป
    uploaded_file = st.file_uploader("📸 อัปโหลดสลิปโอนเงิน", type=['png', 'jpg', 'jpeg'])
    
    if st.button("บันทึกรายการ"):
        st.session_state.transactions.append({
            "type": t_type, "detail": t_detail, "amount": t_amount
        })
        st.toast("บันทึกสำเร็จ!")

with tab3:
    st.subheader("🤖 AI วิเคราะห์การเงิน")
    if st.button("เริ่มวิเคราะห์ด้วย AI"):
        if not st.session_state.debt_data:
            st.warning("กรุณากรอกข้อมูลหนี้สินก่อนวิเคราะห์")
        else:
            with st.spinner("AI กำลังประมวลผล..."):
                # ตัวอย่างการเรียกใช้ OpenAI (ต้องใส่ API Key ใน Secrets)
                # client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                # สรุปข้อมูลส่งให้ AI
                summary = f"ยอดหนี้รวม {total_debt} บาท จ่ายรายเดือนรวม {total_monthly_pay} บาท"
                
                # จำลองคำตอบ AI
                st.info(f"💡 คำแนะนำจาก AI:\nจากยอดหนี้ของคุณ แนะนำให้ปิดหนี้ที่ดอกเบี้ยสูงที่สุดก่อน (Snowball Method) และพยายามคุมรายจ่ายไม่ให้เกิน 50% ของรายได้เพื่อความคล่องตัวครับ")
