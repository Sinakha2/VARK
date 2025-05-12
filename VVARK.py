import streamlit as st
import pandas as pd
import os
import sqlite3
import json
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder  # در صورت نیاز؛ در غیر این صورت می‌توانید حذف شود.

# ---------------------------
# تابع جایگزین برای رفرش کردن صفحه
# ---------------------------
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.markdown("<script>window.location.reload();</script>", unsafe_allow_html=True)

# ---------------------------
# تابع درخواست رفرش (یکبار در انتهای اجرای کد)
# ---------------------------
def request_rerun():
    st.session_state["request_rerun"] = True

# ---------------------------
# تنظیمات پایگاه داده SQLite برای سوالات
# ---------------------------
def init_db():
    conn = sqlite3.connect('questions.db', timeout=10)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            position INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            q_type TEXT NOT NULL DEFAULT 'single'
        )
    ''')
    conn.commit()
    c.execute("SELECT COUNT(*) FROM questions")
    if c.fetchone()[0] == 0:
        # سوالات پیش‌فرض
        default_questions = [
            ("چگونه به شخصی که قصد دارد به فرودگاه، ایستگاه راه‌آهن یا مرکز شهر برود کمک می‌کنید؟",
             ["با او می‌روید", "آدرس را به او می‌گویید", "آدرس را برای او می‌نویسید", "برای او نقشه می‌دهید"]),
            ("نحوه‌ی نوشتن صحیح یک کلمه را چگونه یاد می‌گیرید؟",
             ["کلمه را در ذهن تصویر می‌کنید", "تلفظ را بررسی می‌کنید", "آن را در فرهنگ لغت پیدا می‌کنید", "روی کاغذ نوشته و مقایسه می‌کنید"]),
            ("در برنامه‌ریزی تعطیلات برای یک گروه، چه روشی را ترجیح می‌دهید؟",
             ["برخی موارد را نام می‌برید", "از نقشه یا وب‌سایت استفاده می‌کنید", "یک کپی از سفرنامه به آن‌ها می‌دهید", "از طریق ایمیل یا تلفن خبر می‌دهید"]),
            ("زمانی که می‌خواهید نحوه‌ی استفاده از یک نرم‌افزار جدید را یاد بگیرید، چگونه عمل می‌کنید؟",
             ["ویدئو آموزشی تماشا می‌کنید", "به توضیحات صوتی گوش می‌دهید", "راهنمای استفاده را مطالعه می‌کنید", "با امتحان کردن نرم‌افزار آن را کشف می‌کنید"]),
            ("برای یادگیری مهارت جدید، کدام شیوه (مانند مشاهده تصاویر/نمودارها، گوش دادن یا خواندن/نوشتن) را ترجیح می‌دهید؟",
             ["تصاویر یا نمودارها", "گوش دادن", "خواندن/نوشتن", "فعالیت عملی"]),
            ("در یادگیری مسیر رفتن به مقصد، چه روشی به شما کمک می‌کند؟",
             ["مشاهده نقشه", "گفتگو و توضیح", "یادداشت‌برداری", "انجام عملی"]),
            ("برای به خاطر سپردن افراد جدید، چه تکنیکی را به کار می‌برید؟",
             ["تصویر چهره", "تکرار نام", "نوشتن نام", "یادآوری تجربه مشترک"]),
            ("در هنگام خرید، کدام روش (مثل مقایسه مشخصات یا گرفتن مشورت) را به کار می‌برید؟",
             ["مقایسه قیمت و مشخصات", "مشورت با افراد باتجربه", "مطالعه نظرات آنلاین", "آزمایش کالا"]),
            ("در یادگیری یک مهارت ورزشی جدید، چگونه پیش می‌روید؟",
             ["تماشا حرکات مربی", "گوش دادن به توضیحات", "مطالعه دستورالعمل‌ها", "تمرین مستقیم"]),
            ("برای درک بهتر یک فیلم، به چه جنبه‌هایی (مانند صحنه‌های بصری یا گفتار) توجه می‌کنید؟",
             ["صحنه‌های بصری", "مکالمات", "متن داستان", "احساسات و حرکات"]),
            ("در مطالعه، برای فهم بهتر موضوع از چه ابزارهایی (مانند نمودار یا تصویر) استفاده می‌کنید؟",
             ["استفاده از نمودار/تصویر", "خواندن بلند", "یادداشت‌برداری", "تمرین عملی"]),
            ("هنگام یادگیری یک مهارت عملی، کدام رویکرد (مشاهده، شنیدن یا انجام عملی) برایتان مؤثر است؟",
             ["مشاهده", "شنیدن", "خواندن", "انجام عملی"]),
            ("زمانی که به موسیقی گوش می‌دهید، به کدام جنبه (مثلاً کاور آلبوم یا متن آهنگ) بیشتر توجه می‌کنید؟",
             ["کاور آلبوم", "موسیقی و ملودی", "متن آهنگ", "احساسات و حرکات"]),
            ("در فراگیری یک مهارت جدید، ابتدا به چه چیزی نگاه می‌کنید؟",
             ["نمونه‌های تصویری", "توضیحات صوتی", "راهنما و دستورالعمل", "تمرین عملی"]),
            ("در انجام پروژه‌ی گروهی، چه روشی برای یادگیری و همکاری مؤثرتر است؟",
             ["بررسی نمودار/دیاگرام", "گفتگوی تیمی", "مرور دستورالعمل مکتوب", "انجام عملی"]),
            ("هنگام آموزش دادن به دیگران، کدام روش (تصویری، گفتاری، کتبی یا عملی) را به کار می‌برید؟",
             ["تصویری", "گفتاری", "کتبی", "عملی"])
        ]
        for pos, (q_text, opts) in enumerate(default_questions, start=1):
            c.execute("INSERT INTO questions (position, question, options, q_type) VALUES (?, ?, ?, ?)",
                      (pos, q_text, json.dumps(opts, ensure_ascii=False), "single"))
        conn.commit()
    conn.close()

# تابع load_questions: دریافت سوالات از پایگاه داده بر اساس ترتیب (position)
def load_questions():
    conn = sqlite3.connect('questions.db', timeout=10)
    c = conn.cursor()
    c.execute("SELECT position, question, options, q_type FROM questions ORDER BY position ASC")
    rows = c.fetchall()
    conn.close()
    questions = []
    for row in rows:
        pos = row[0]
        question_text = row[1]
        options = json.loads(row[2])
        q_type = row[3]
        questions.append((pos, question_text, options, q_type))
    return questions

# ---------------------------
# توابع مدیریت سوالات: افزودن، حذف، بازنشانی
# ---------------------------
def add_question(q_text, opts, position, q_type):
    """
    با استفاده از این تابع، سوال جدید در موقعیت مشخص درج شده و سایر سوالات شیفت پیدا می‌کنند.
    ابتدا شماره سوالات از موقعیت درج به اندازه 1000 افزایش می‌یابد تا از تداخل جلوگیری شود،
    سپس 999 واحد کم شده تا شماره صحیح در نهایت اختصاص یابد.
    """
    conn = sqlite3.connect('questions.db', timeout=10)
    c = conn.cursor()
    try:
        c.execute("BEGIN IMMEDIATE TRANSACTION")
        # شیفت سوالاتی که موقعیت آن‌ها >= position است:
        c.execute("UPDATE questions SET position = position + 1000 WHERE position >= ?", (position,))
        c.execute("UPDATE questions SET position = position - 999 WHERE position >= ?", (position + 1000,))
        # درج سوال جدید در موقعیت دلخواه:
        c.execute("INSERT INTO questions (position, question, options, q_type) VALUES (?, ?, ?, ?)",
                  (position, q_text, json.dumps(opts, ensure_ascii=False), q_type))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def remove_question(position):
    # حذف سوال و شیفت سوالات بعدی به صورت خودکار (کاهش شماره)
    conn = sqlite3.connect('questions.db', timeout=10)
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE position = ?", (position,))
    c.execute("UPDATE questions SET position = position - 1 WHERE position > ?", (position,))
    conn.commit()
    conn.close()

def reset_questions():
    # حذف کامل جدول سوالات و سپس مقداردهی اولیه مجدد
    conn = sqlite3.connect('questions.db', timeout=10)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS questions")
    conn.commit()
    conn.close()
    init_db()

# ---------------------------
# تنظیمات اولیه
# ---------------------------
init_db()
dummy_option = "لطفا گزینه‌ای را انتخاب کنید"

# تابع ثبت پاسخ‌ها (ثبت پاسخ کاربر در پرسشنامه)
def submit_answer(answer):
    current_index = st.session_state.current_index
    questions = load_questions()  # دریافت به‌روز از پایگاه داده
    pos, question_text, options, q_type = questions[current_index]
    st.session_state.answers[question_text] = answer
    if current_index < len(questions) - 1:
        st.session_state.current_index += 1
    else:
        base_columns = ["نام", "نام خانوادگی", "شماره دانشجویی", "رشته تحصیلی", "مقطع تحصیلی"]
        combined = st.session_state.user_info.copy()
        ordered = {col: combined.get(col, "") for col in base_columns}
        for pos, q_text, _, _ in questions:
            ordered[f"سوال {pos}"] = st.session_state.answers.get(q_text, "")
        df_row = pd.DataFrame([ordered])
        file_name = "vark_results.xlsx"
        if os.path.exists(file_name):
            try:
                existing_df = pd.read_excel(file_name, engine="openpyxl")
                df_row = pd.concat([existing_df, df_row], ignore_index=True)
            except Exception:
                pass
        df_row.to_excel(file_name, index=False)
        st.session_state.finished = True
    request_rerun()

# ---------------------------
# تنظیمات صفحه و فونت
# ---------------------------
st.set_page_config(layout="wide", page_title="VARK Questionnaire")
st.title("📋 پرسشنامه سبک‌های یادگیری VARK")
font_path = "fonts/Vazir.ttf"
if os.path.exists(font_path):
    mpl.font_manager.fontManager.addfont(font_path)
    mpl.rcParams["font.family"] = "Vazir"
    mpl.rcParams["axes.unicode_minus"] = False

user_role = st.sidebar.radio("👤 نقش شما:", ["شرکت‌کننده", "سوپروایزر"])
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Dr.DehqaniSBU"

# ---------------------------
# بخش مدیریت (سوپروایزر)
# ---------------------------
if user_role == "سوپروایزر":
    st.subheader("🔐 ورود به داشبورد مدیریت")
    username = st.text_input("نام کاربری:")
    password = st.text_input("رمز عبور:", type="password")
    if st.button("✅ ورود"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("🚀 ورود موفقیت‌آمیز!")
            request_rerun()
        else:
            st.error("❌ نام کاربری یا رمز عبور اشتباه است!")
    
    if st.session_state.get("admin_logged_in", False):
        # دکمه بازنشانی سوالات به حالت اولیه
        st.subheader("🔄 بازنشانی سوالات به حالت اولیه")
        if st.button("بازنشانی سوالات"):
            reset_questions()
            st.success("سوالات به حالت اولیه بازیابی شدند!")
            request_rerun()
        
        # دکمه پاک کردن تمام داده‌های ثبت‌شده
        file_name = "vark_results.xlsx"
        if st.button("پاک کردن تمام داده‌ها"):
            if os.path.exists(file_name):
                os.remove(file_name)
                st.success("تمام داده‌های ثبت‌شده پاک شدند!")
                request_rerun()
            else:
                st.info("داده‌ای جهت پاک کردن وجود ندارد!")
            
        # نمایش نتایج کاربران و نمودارهای توزیع سبک‌های یادگیری
        if os.path.exists(file_name):
            try:
                df = pd.read_excel(file_name, engine="openpyxl")
            except Exception as e:
                st.error("خطا در خواندن فایل اکسل: " + str(e))
                df = pd.DataFrame()
            if not df.empty:
                base_columns = ["نام", "نام خانوادگی", "شماره دانشجویی", "رشته تحصیلی", "مقطع تحصیلی"]
                questions_sorted = load_questions()
                ques_columns = [f"سوال {q[0]}" for q in questions_sorted]
                final_columns = base_columns + ques_columns
                df = df.reindex(columns=final_columns)
                df.index = df.index + 1
                st.subheader("نتایج کاربران:")
                st.dataframe(df)
                
                st.subheader("Learning Style Distribution:")
                counts = {"Visual": 0, "Auditory": 0, "Read/Write": 0, "Kinesthetic": 0}
                for pos, q_text, opts, q_type in load_questions():
                    if q_type in ["single", "multiple"]:
                        for ans in df[f"سوال {pos}"]:
                            if pd.notna(ans) and ans != "":
                                try:
                                    idx = opts.index(ans)
                                    if idx == 0:
                                        counts["Visual"] += 1
                                    elif idx == 1:
                                        counts["Auditory"] += 1
                                    elif idx == 2:
                                        counts["Read/Write"] += 1
                                    elif idx == 3:
                                        counts["Kinesthetic"] += 1
                                except ValueError:
                                    continue
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(list(counts.keys()), list(counts.values()),
                       color=["#3498db", "#e74c3c", "#2ecc71", "#f39c12"])
                ax.set_title("Learning Style Distribution")
                ax.set_xlabel("Learning Style")
                ax.set_ylabel("Count")
                st.pyplot(fig)
                total = sum(counts.values())
                if total > 0:
                    fig2, ax2 = plt.subplots(figsize=(6, 4))
                    ax2.pie(list(counts.values()), labels=list(counts.keys()),
                            autopct="%1.1f%%", startangle=90,
                            colors=["#3498db", "#e74c3c", "#2ecc71", "#f39c12"])
                    ax2.axis("equal")
                    st.pyplot(fig2)
                else:
                    st.info("هیچ داده‌ای برای رسم نمودار دایره‌ای وجود ندارد.")
            else:
                st.info("🚨 هنوز هیچ کاربری آزمون را انجام نداده است!")
        else:
            st.info("🚨 فایل نتایج (vark_results.xlsx) یافت نشد!")
        
        st.markdown("---")
        st.header("🔧 مدیریت سوالات پرسشنامه")
        q_type_selected = st.selectbox("انتخاب نوع سوال:", ["توضیحی", "4 گزینه‌ای", "چند گزینه‌ای"])
        # برای سوالات چند گزینه‌ای، تعداد گزینه‌ها به صورت دینامیک خارج از فرم تنظیم می‌شود.
        if q_type_selected == "چند گزینه‌ای":
            num_options = st.number_input("تعداد گزینه‌ها برای سوال چند گزینه‌ای:", 
                                          min_value=2, max_value=10, 
                                          value=st.session_state.get("num_options_multiple", 2),
                                          step=1, key="num_options_multiple")
        with st.expander("افزودن سوال جدید"):
            with st.form("add_question_form"):
                q_text = st.text_area("متن سوال:")
                new_options = []
                if q_type_selected == "توضیحی":
                    st.info("برای سوال توضیحی نیازی به وارد کردن گزینه نیست.")
                elif q_type_selected == "4 گزینه‌ای":
                    st.write("لطفاً گزینه‌های موردنظر را وارد کنید (تعداد گزینه‌ها به صورت ثابت است):")
                    option1 = st.text_input("گزینه ۱:", key="option1")
                    option2 = st.text_input("گزینه ۲:", key="option2")
                    option3 = st.text_input("گزینه ۳:", key="option3")
                    option4 = st.text_input("گزینه ۴:", key="option4")
                    new_options = [option1, option2, option3, option4]
                    new_options = [opt for opt in new_options if opt.strip() != ""]
                elif q_type_selected == "چند گزینه‌ای":
                    st.write("لطفاً گزینه‌های موردنظر را وارد کنید:")
                    number = st.session_state.get("num_options_multiple", 2)
                    for i in range(int(number)):
                        opt = st.text_input(f"گزینه {i+1}:", key=f"m_option_{i}")
                        new_options.append(opt)
                    new_options = [opt for opt in new_options if opt.strip() != ""]
                insertion_index = st.number_input(
                    "درج سوال در موقعیت (شماره):",
                    min_value=1,
                    max_value=len(load_questions()) + 1,
                    value=1,
                    step=1,
                    key="insertion_index"
                )
                submitted = st.form_submit_button("افزودن سوال")
                if submitted:
                    if not q_text:
                        st.error("لطفاً متن سوال را وارد کنید.")
                    elif q_type_selected != "توضیحی" and len(new_options) == 0:
                        st.error("لطفاً حداقل یک گزینه وارد کنید.")
                    else:
                        if q_type_selected == "توضیحی":
                            final_type = "توضیحی"
                        elif q_type_selected == "4 گزینه‌ای":
                            final_type = "single"
                        else:
                            final_type = "multiple"
                        add_question(q_text, new_options, insertion_index, final_type)
                        st.success("سوال جدید افزوده شد!")
                        request_rerun()
        with st.expander("حذف سوال"):
            questions = load_questions()
            if questions:
                question_choices = {f"سوال {q[0]}: {q[1][:50]}..." : q[0] for q in questions}
                selected = st.selectbox("انتخاب سوال برای حذف", list(question_choices.keys()))
                if st.button("حذف سوال"):
                    pos = question_choices[selected]
                    remove_question(pos)
                    st.success("سوال انتخاب‌شده حذف شد!")
                    request_rerun()

# ---------------------------
# بخش شرکت‌کننده
# ---------------------------
if user_role == "شرکت‌کننده":
    if "user_info_submitted" not in st.session_state:
        st.subheader("📝 ورود اطلاعات شرکت‌کننده")
        name = st.text_input("نام:")
        lastname = st.text_input("نام خانوادگی:")
        student_id = st.text_input("شماره دانشجویی:")
        major = st.text_input("رشته تحصیلی:")
        level = st.selectbox("مقطع تحصیلی:", ["کارشناسی", "کارشناسی ارشد", "دکتری"])
        if st.button("✅ شروع آزمون"):
            st.session_state.user_info = {
                "نام": name,
                "نام خانوادگی": lastname,
                "شماره دانشجویی": student_id,
                "رشته تحصیلی": major,
                "مقطع تحصیلی": level
            }
            st.session_state.user_info_submitted = True
            st.session_state.current_index = 0
            st.session_state.answers = {}
            request_rerun()
    else:
        if st.session_state.get("finished", False):
            counts = {"Visual": 0, "Auditory": 0, "Read/Write": 0, "Kinesthetic": 0}
            questions = load_questions()
            for pos, q_text, opts, q_type in questions:
                ans = st.session_state.answers.get(q_text)
                if ans:
                    if q_type == "توضیحی":
                        continue
                    if q_type in ["single", "multiple"]:
                        for selected in ans if isinstance(ans, list) else [ans]:
                            try:
                                idx = opts.index(selected)
                                if idx == 0:
                                    counts["Visual"] += 1
                                elif idx == 1:
                                    counts["Auditory"] += 1
                                elif idx == 2:
                                    counts["Read/Write"] += 1
                                elif idx == 3:
                                    counts["Kinesthetic"] += 1
                            except ValueError:
                                continue
            dominant = max(counts, key=counts.get)
            style_map = {"Visual": "Visual", "Auditory": "Auditory", "Read/Write": "Read/Write", "Kinesthetic": "Kinesthetic"}
            participant_style = style_map.get(dominant, dominant)
            st.success(f"Your Learning Style: {participant_style}")
        else:
            questions = load_questions()
            if st.session_state.current_index < len(questions):
                cur_question = questions[st.session_state.current_index]
                pos, question_text, options, q_type = cur_question
                display_text = f"سوال {pos}: {question_text}"
                st.subheader(f"❓ {display_text}")
                
                if q_type == "توضیحی":
                    answer = st.text_area("پاسخ شما:", key=f"q{st.session_state.current_index}")
                    if st.button("ثبت پاسخ"):
                        submit_answer(answer)
                
                elif q_type == "single":
                    default_text = "گزینه مورد نظر را انتخاب کنید"
                    single_options = [default_text] + options
                    
                    def on_single_change():
                        answer_selected = st.session_state.get(f"q{st.session_state.current_index}")
                        if answer_selected != default_text:
                            submit_answer(answer_selected)
                    
                    answer = st.radio(
                        "انتخاب پاسخ:",
                        single_options,
                        index=0,
                        key=f"q{st.session_state.current_index}",
                        on_change=on_single_change
                    )
                    st.write("توجه: فقط یک‌بار پاسخ خود را انتخاب کنید.")
                
                elif q_type == "multiple":
                    answer = st.multiselect("انتخاب پاسخ (می‌توانید چند گزینه را انتخاب کنید)", options,
                                            key=f"q{st.session_state.current_index}")
                    if st.button("ثبت پاسخ"):
                        submit_answer(answer)
                
                else:
                    answer = st.multiselect("انتخاب پاسخ", options, key=f"q{st.session_state.current_index}")
                    if st.button("ثبت پاسخ"):
                        submit_answer(answer)
            else:
                st.error("همه سوالات پاسخ داده شده‌اند یا مشکلی در شماره‌بندی وجود دارد.")

# ---------------------------
# بررسی درخواست رفرش (rerun) در انتهای کد
# ---------------------------
if st.session_state.get("request_rerun", False):
    st.session_state["request_rerun"] = False
    safe_rerun()
