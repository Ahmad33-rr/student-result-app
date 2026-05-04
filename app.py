import streamlit as st
import pandas as pd
import time

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام النتائج الاحترافية", layout="centered")

# 2. تصميم CSS متطور (تعديل الحجم ليتناسب مع ما تحته)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .main { background: #0f172a; }
    
    /* تنسيق الحاوية الأساسية */
    .basic-info-card { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; border: 1px solid #3b82f6; margin-top: 20px; }
    .subject-card { background: #111827; border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; margin-bottom: 10px; }
    .mark-value { color: white; font-size: 40px; font-weight: bold; margin: 0; }
    .fail-mark { color: #ef4444 !important; }
    
    /* إخفاء نصوص الليبل المزعجة */
    .stTextInput label, div[data-testid="stSegmentedControl"] label { display: none; }
    
    /* جعل أزرار "رقم الاكتتاب / الاسم" تأخذ كامل العرض لتتساوى مع المستطيلات تحتها */
    div[data-testid="stSegmentedControl"] { width: 100%; }
    div[data-testid="stSegmentedControl"] > div { width: 100%; display: flex; }
    div[data-testid="stSegmentedControl"] button { flex-grow: 1; }
    
    /* زر الطباعة الصغير في الأسفل */
    .print-container { text-align: center; margin-top: 30px; }
    .small-print-btn {
        background-color: #334155;
        color: #94a3b8;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 5px 15px;
        font-size: 12px;
        cursor: pointer;
        transition: 0.3s;
    }
    .small-print-btn:hover { background-color: #1e293b; color: white; }

    @media print {
        .no-print { display: none !important; }
        .main { background: white !important; }
        .subject-card { border: 1px solid #ccc !important; page-break-inside: avoid; }
        .mark-value, b { color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة الحالة (لتمكين البحث المتكرر)
if 'data_ready' not in st.session_state:
    st.session_state.data_ready = False
if 'current_student' not in st.session_state:
    st.session_state.current_student = None

# دالة لتصفير البحث عند تغيير المدخلات
def reset_search():
    st.session_state.data_ready = False
    st.session_state.current_student = None

# --- الواجهة الرئيسية ---
st.markdown("<h1 class='no-print' style='text-align: center; color: #3b82f6;'> وزارة التربية والتعليم</h1>", unsafe_allow_html=True)

try:
    df = pd.read_excel('grades.xlsx')
    df.columns = df.columns.str.strip()

    # خيار التحديد في المنتصف
    st.markdown("<div class='no-print' style='text-align: center; margin-bottom:10px; color:#94a3b8;'>حدد طريقة البحث:</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([0.5, 3, 0.5]) # تعديل طفيف في نسب الأعمدة للتوسيع
    with c2:
        search_option = st.segmented_control(
            "طريقة البحث", 
            ["رقم الاكتتاب", "الاسم الكامل"], 
            selection_mode="single", 
            default="رقم الاكتتاب",
            on_change=reset_search 
        )

        search_query = ""
        if search_option == "رقم الاكتتاب":
            search_query = st.text_input("رقم الاكتتاب", placeholder="🔍 أدخل رقم الاكتتاب...", on_change=reset_search)
        else:
            search_query = st.text_input("اسم الطالب", placeholder="👤 أدخل الاسم الثلاثي...", on_change=reset_search)

        search_btn = st.button("إظهار النتيجة ✨", use_container_width=True)

    if search_btn:
        if search_query:
            with st.spinner('جاري التحقق من سجلات الامتحانات...'):
                time.sleep(3)
            
            if search_option == "رقم الاكتتاب":
                res = df[df['رقم الاكتتاب'].astype(str) == str(search_query)]
            else:
                res = df[df['اسم الطالب'].str.contains(str(search_query), na=False)]
            
            if not res.empty:
                st.session_state.current_student = res.iloc[0]
                st.session_state.data_ready = True
            else:
                reset_search()
                st.error("⚠️ لم يتم العثور على نتيجة لهذه البيانات.")
        else:
            st.warning("⚠️ يرجى إدخال بيانات البحث.")

    # عرض النتائج
    if st.session_state.data_ready and st.session_state.current_student is not None:
        s = st.session_state.current_student
        subjects = ['اللغة العربية', 'اللغة الانكليزية', 'التربية الدينية', 'اللغة الفرنسية', 'الفيزياء', 'الكيمياء', 'علم الاحياء', 'الرياضيات']
        marks = [s[sub] for sub in subjects]
        avg = sum(marks) / len(subjects)
        failed_count = len([m for m in marks if m < 60])
        status = "ناجح" if (failed_count == 0 or (failed_count <= 2 and all(m >= 25 for m in marks if m < 60))) and avg >= 60 else "راسب"

        st.markdown(f"""
            <div class="basic-info-card">
                <p>الاسم: <b>{s['اسم الطالب']}</b></p>
                <p>رقم الاكتتاب: <b>{s['رقم الاكتتاب']}</b></p>
                <p>المعدل: <b>{avg:.2f}%</b></p>
                <p>الحالة: <b style="color:{'#10b981' if status=='ناجح' else '#ef4444'}">{status}</b></p>
            </div>
        """, unsafe_allow_html=True)

        if st.checkbox("📊 عرض تفاصيل المواد كاملة"):
            if status == "ناجح":
                st.success("🎉 مبارك النجاح! تستحق كل خير.")
                st.balloons()
            else:
                st.error("😔 لا تيأس، هذه البداية فقط وليست النهاية.")

            for sub in subjects:
                val = s[sub]
                cls = "fail-mark" if val < 60 else ""
                st.markdown(f"""
                    <div class="subject-card">
                        <p style='color:#94a3b8; margin:0; font-size:14px;'>{sub}</p>
                        <h2 class="mark-value {cls}">{val}</h2>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("""
                <div class="no-print print-container">
                    <button class="small-print-btn" onclick="window.print()">🖨️ طباعة كشف العلامات</button>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"تأكد من ملف الإكسل. الخطأ: {e}")