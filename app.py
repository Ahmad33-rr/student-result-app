import streamlit as st
import pandas as pd
import time

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="بوابة نتائج الثالث الثانوي", layout="centered")

# 2. تصميم CSS المتكامل (الهوية البصرية والحركات)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* الإعدادات العامة والخطوط */
    html, body, [class*="st-"] { 
        font-family: 'Cairo', sans-serif; 
        direction: rtl; 
        text-align: right; 
    }
    
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* العناوين */
    .main-header { text-align: center; color: #D4AF37; margin-bottom: 5px; }
    .sub-header { 
        text-align: center; color: #ffffff; font-size: 24px; 
        margin-bottom: 30px; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; 
    }

    /* حاوية البحث */
    .search-box {
        background: rgba(255, 255, 255, 0.03);
        padding: 30px;
        border-radius: 15px;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }

    /* إخفاء جملة Press Enter to apply المزعجة */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* بطاقة النتيجة (الكرت الذهبي) */
    .result-card {
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 25px;
        background: linear-gradient(145deg, #0a0a0a, #1a1a1a);
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.1);
        margin-bottom: 20px;
    }
    
    .info-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(212, 175, 55, 0.1); }
    .info-label { color: #D4AF37; font-weight: bold; }
    .info-value { color: #ffffff; }

    /* تنسيق الجدول وتوسيط العناوين */
    .results-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
        border: 1px solid #D4AF37;
    }
    .results-table th { 
        background-color: #D4AF37; color: #000; padding: 12px; 
        text-align: center !important; 
    }
    .results-table td { 
        border: 1px solid rgba(212, 175, 55, 0.3); padding: 10px; 
        text-align: center; 
    }

    /* حركات أزرار ستريمليت (تأثير الضغط والتموج) */
    .stButton>button {
        background-color: #D4AF37 !important;
        color: #000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4) !important;
    }
    .stButton>button:active {
        transform: scale(0.95) !important;
        background-color: #b8962d !important;
    }

   .print-btn {
        width: 100%; 
        height: 38px; 
        padding: 0px;
        background-color: #D4AF37;
        color: #000;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .print-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4);
    }
    .print-btn:active {
        transform: scale(0.95);
    }

    /* إعدادات الطباعة */
    @media print {
        .no-print { display: none !important; }
        .stApp { background: white !important; color: black !important; }
        .result-card { border: 1px solid black !important; box-shadow: none !important; }
        .results-table th { background-color: #eee !important; color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. المنطق البرمجي (التقديرات والرسوب)
def get_rating_label(mark, is_failed_overall=False):
    """تحديد التقدير بناءً على الدرجة مع مراعاة حالة الرسوب العام"""
    if is_failed_overall: return "ضعيف "
    if mark >= 90: return "شرف "
    elif mark >= 80: return "ممتاز "
    elif mark >= 70: return "جيد جداً "
    elif mark >= 60: return "جيد "
    else: return "ضعيف "

# إدارة التنقل بين الصفحات
if 'page' not in st.session_state:
    st.session_state.page = "search"
if 'student_data' not in st.session_state:
    st.session_state.student_data = None

def go_to_search():
    st.session_state.page = "search"
    st.session_state.student_data = None

# --- واجهة البحث ---
if st.session_state.page == "search":
    st.markdown("<h1 class='main-header'>وزارة التربية والتعليم</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>نتائج الشهادة الثانوية العامة</h2>", unsafe_allow_html=True)

    try:
        df = pd.read_excel('grades.xlsx')
        df.columns = df.columns.str.strip()

        with st.container():
            st.markdown("<div class='search-box'>", unsafe_allow_html=True)
            search_type = st.segmented_control("اختر طريقة البحث", ["رقم الاكتتاب", "الاسم الكامل"], default="رقم الاكتتاب")

            if search_type == "رقم الاكتتاب":
                query = st.text_input("", placeholder="🔍 أدخل رقم الاكتتاب للبحث...")
            else:
                query = st.text_input("", placeholder="👤 أدخل الاسم الثلاثي للبحث...")

            if st.button("🔎 بـحـث", use_container_width=True):
                if query:
                    with st.spinner('جاري البحث عن النتيجة...'):
                        time.sleep(1)
                        if search_type == "رقم الاكتتاب":
                            res = df[df['رقم الاكتتاب'].astype(str) == str(query)]
                        else:
                            res = df[df['اسم الطالب'].str.contains(str(query), na=False)]
                        
                        if not res.empty:
                            st.session_state.student_data = res.iloc[0]
                            st.session_state.page = "result"
                            st.rerun()
                        else:
                            st.error("⚠️ عذراً، لم يتم العثور على أي بيانات مطابقة.")
            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"حدث خطأ في قراءة ملف البيانات: {e}")

# --- واجهة النتيجة ---
elif st.session_state.page == "result":
    s = st.session_state.student_data
    subjects = ['اللغة العربية', 'اللغة الانكليزية', 'التربية الدينية', 'اللغة الفرنسية', 'الفيزياء', 'الكيمياء', 'علم الاحياء', 'الرياضيات']
    
    marks = [float(s.get(sub, 0)) for sub in subjects]
    # تعديل 1: المعدل كعدد صحيح
    avg = int(sum(marks) / len(subjects))
    
    failed_count = sum(1 for m in marks if m < 60)
    below_quarter = sum(1 for m in marks if m < 15)
    
    if failed_count <= 2 and below_quarter == 0 and avg >= 60:
        status = "ناجح"
        overall_rating = get_rating_label(avg)
        status_color = "#10b981"
    else:
        status = "راسب"
        overall_rating = "ضعيف "
        status_color = "#ef4444"

    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>⚜️ كشف الدرجات الرسمي ⚜️</h2>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="result-card">
            <div class="info-row"><span class="info-label">الاسم الثلاثي:</span> <span class="info-value">{s.get('اسم الطالب', 'غير متوفر')}</span></div>
            <div class="info-row"><span class="info-label">اسم الأم:</span> <span class="info-value">{s.get('اسم الأم', 'غير متوفر')}</span></div>
            <div class="info-row"><span class="info-label">رقم الاكتتاب:</span> <span class="info-value">{s.get('رقم الاكتتاب', 'غير متوفر')}</span></div>
            <div class="info-row"><span class="info-label">المحافظة:</span> <span class="info-value">{s.get('المحافظة', 'غير متوفر')}</span></div>
            <div class="info-row"><span class="info-label">المعدل العام:</span> <span class="info-value" style="font-weight:bold;">{avg}%</span></div>
            <div class="info-row"><span class="info-label">النتيجة:</span> <span style="color:{status_color}; font-weight:bold;">{status}</span></div>
            <div class="info-row"><span class="info-label">التقدير العام:</span> <span style="color:#D4AF37; font-weight:bold;">{overall_rating}</span></div>
        </div>
    """, unsafe_allow_html=True)

    table_html = """
        <table class="results-table">
            <thead><tr><th>المادة</th><th>الدرجة</th><th>التقدير</th></tr></thead>
            <tbody>
    """
    for sub in subjects:
        # تعديل 2: الدرجة كعدد صحيح
        val = int(float(s.get(sub, 0)))
        val_style = f"color:#ef4444; font-weight:bold;" if val < 60 else ""
        sub_rating = get_rating_label(val)
        table_html += f"<tr><td>{sub}</td><td style='{val_style}'>{val}</td><td>{sub_rating}</td></tr>"
    
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 بحث جديد", use_container_width=True):
            go_to_search()
            st.rerun()
            
    with col2:
        st.markdown("""
            <button class='print-btn no-print' onclick='window.parent.focus(); window.parent.print();'>
                🖨️ طباعة النتيجة
            </button>
            """, unsafe_allow_html=True)
        
    if status == "ناجح" and avg >= 80:
        st.balloons()