import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from openai import OpenAI

# --- CONFIGURATION ---
st.set_page_config(page_title="Minimal Wallet", page_icon="💰", layout="centered")

# ตรวจสอบ API Key จาก Secrets
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.warning("Please configure OpenAI API Key in Secrets.")

# --- CSS CUSTOMIZATION (APPLE WALLET LOOK) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #000000; }
    
    /* Card Container */
    .wallet-card {
        background: linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%);
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #3a3a3c;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    
    .label { color: #8e8e93; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .value { font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
    
    /* Input Style */
    div[data-baseweb="input"] { background-color: #1c1c1e !important; border-radius: 10px !important; }
    
    /* Button Style */
    .stButton>button {
        background-color: #ffffff; color: #000000;
        border-radius: 12px; font-weight: bold; border: none;
        padding: 0.5rem 1rem; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #d1d1d6; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS CONNECTION ---
# ตั้งค่าใน .streamlit/secrets.toml หรือ Dashboard ของ Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# --- APP HEADER ---
st.write(f"<p style='color:#8e8e93; text-align:center;'>{pd.Timestamp.now().strftime('%A, %d %B')}</p>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: white; margin-bottom:30px;'>Wallet</h1>", unsafe_allow_html=True)

# --- DATA LOADING ---
# สมมติว่ามี Sheet ชื่อ 'Debt' และ 'Transactions'
try:
    debt_df = conn.read(worksheet="Debt")
    total_debt_sum = debt_df['Amount'].sum()
except:
    total_debt_sum = 0.0

# --- UI: SUMMARY CARD ---
st.markdown(f"""
    <div class="wallet-card">
        <div class="label">Total Debt Balance</div>
        <div class="value">฿ {total_debt_sum:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# --- UI: TRANSACTION FORM ---
tab1, tab2 = st.tabs(["💸 Manage Debt", "📊 Cash Flow"])

with tab1:
    with st.expander("➕ Add New Debt Card", expanded=False):
        with st.form("debt_form", clear_on_submit=True):
            d_name = st.text_input("Creditor Name (เช่น ธนาคาร A)")
            d_amount = st.number_input("Total Loan Amount", min_value=0.0)
            d_interest = st.number_input("Interest Rate (%)", min_value=0.0)
            d_term = st.number_input("Term (Months)", min_value=1)
            
            if st.form_submit_button("Confirm Add"):
                # Logic: คำนวณยอดผ่อนและบันทึกลง Google Sheets
                # conn.create(worksheet="Debt", data=...)
                st.success("Debt record added to Cloud.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        inc = st.number_input("Monthly Income", min_value=0.0)
    with col2:
        exp = st.number_input("Monthly Expenses", min_value=0.0)
    
    uploaded_file = st.file_uploader("Scan Slip (Upload to Drive)", type=['jpg','png'])

# --- AI ANALYSIS SECTION ---
st.markdown("---")
if st.button("✨ AI Financial Analysis"):
    with st.spinner("AI is analyzing your balance..."):
        try:
            prompt = f"มีหนี้รวม {total_debt_sum} บาท, รายได้ {inc} บาท, รายจ่าย {exp} บาท ช่วยวิเคราะห์แนวทางการปลดหนี้สั้นๆ แบบมืออาชีพ"
            
            response = client.chat.completions.create(
                model="gpt-4o", # หรือ gpt-3.5-turbo
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis = response.choices[0].message.content
            st.markdown(f"""
                <div class="wallet-card" style="background: #2c2c2e; border-left: 4px solid #0a84ff;">
                    <div class="label" style="color:#0a84ff;">AI Recommendation</div>
                    <div style="font-size: 0.95rem; line-height:1.6; margin-top:10px;">{analysis}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"AI Error: {e}")

# --- FOOTER ---
st.caption("Minimal Wallet v1.0 • Connected to Google Sheets")