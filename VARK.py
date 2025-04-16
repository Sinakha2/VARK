import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import os

def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        st.markdown(
            """
            <script>
                setTimeout(() => { window.location.reload(); }, 100);
            </script>
            """,
            unsafe_allow_html=True
        )

# تعریف مقدار پیش‌فرض (dummy) برای st.radio
dummy_option = "لطفا گزینه‌ای را انتخاب کنید"

# Callback: به محض تغییر انتخاب در ویجت (st.radio)، اگر جواب معتبر است، پاسخ ذخیره شده و به سؤال بعدی منتقل می‌شود
def on_option_change():
    current_index = st.session_state.current_index
    answer = st.session_state.get(f"q{current_index}")
    # اگر هنوز گزینه پیش‌فرض انتخاب شده است، اقدامی انجام نده
    if answer == dummy_option:
        return

    # ذخیره پاسخ معتبر
    st.session_state.answers[questions[current_index][0]] = answer
    if current_index < len(questions) - 1:
        st.session_state.current_index = current_index + 1
    else:
        # پایان پرسشنامه: ذخیره نتایج در فایل اکسل
        combined = st.session_state.user_info.copy()
        combined.update({q: st.session_state.answers.get(q, "") for q, _ in questions})
        df_row = pd.DataFrame([combined])
        file_name = "vark_results.xlsx"
        if os.path.exists(file_name):
            try:
                existing_df = pd.read_excel(file_name, engine="openpyxl")
                df_row = pd.concat([existing_df, df_row], ignore_index=True)
            except Exception:
                pass
        df_row.to_excel(file_name, index=False)
        st.session_state.finished = True
    safe_rerun()

# تنظیمات صفحه
st.set_page_config(layout="wide", page_title="VARK Questionnaire")
st.title("📋 پرسشنامه سبک‌های یادگیری VARK")

# تنظیم فونت (در صورت وجود فایل Vazir.ttf)
font_path = "fonts/Vazir.ttf"
if os.path.exists(font_path):
    mpl.font_manager.fontManager.addfont(font_path)
    mpl.rcParams["font.family"] = "Vazir"
    mpl.rcParams["axes.unicode_minus"] = False

# تعریف سوالات و گزینه‌ها
questions = [
    ("سوال 1: شما قصد دارید به شخصی که می‌خواهد به فرودگاه، ایستگاه راه‌آهن یا مرکز شهر برود کمک کنید. شما:",
     ["با او می‌روید", "آدرس را به او می‌گویید", "آدرس را برای او می‌نویسید", "برای او نقشه می‌کشید یا به او نقشه می‌دهید"]),
    ("سوال 2: شما مطمئن نیستید که یک کلمه چگونه نوشته می‌شود. شما:",
     ["کلمه را در ذهن تصویر می‌کنید", "تلفظ را بررسی می‌کنید", "آن را در فرهنگ لغت پیدا می‌کنید", "روی کاغذ نوشته و مقایسه می‌کنید"]),
    ("سوال 3: شما در حال برنامه‌ریزی تعطیلات برای گروهی هستید. شما:",
     ["برخی از موارد را نام می‌برید", "از نقشه یا وب‌سایت استفاده می‌کنید", "یک کپی از سفرنامه به آن‌ها می‌دهید", "از طریق ایمیل یا تلفن خبر می‌دهید"]),
    ("سوال 4: وقتی می‌خواهید یاد بگیرید که چگونه یک نرم‌افزار جدید را استفاده کنید، شما:",
     ["ویدئو آموزشی را تماشا می‌کنید", "به توضیحات صوتی گوش می‌دهید", "راهنمای استفاده را مطالعه می‌کنید", "با امتحان کردن نرم‌افزار، آن را کشف می‌کنید"]),
    ("سوال 5: برای یادگیری مهارت جدید، شما ترجیح می‌دهید:",
     ["تصاویر یا نمودارها را ببینید", "به توضیحات شفاهی گوش دهید", "یادداشت بردارید و دستورالعمل‌ها را بخوانید", "فعالیت فیزیکی انجام دهید و تمرین کنید"]),
    ("سوال 6: وقتی می‌خواهید مسیر رفتن به مقصدی را یاد بگیرید، شما:",
     ["نقشه نگاه می‌کنید", "درباره مسیر صحبت می‌کنید و توضیح می‌خواهید", "یادداشت برمی‌دارید", "خودتان امتحان می‌کنید و با تجربه یاد می‌گیرید"]),
    ("سوال 7: وقتی می‌خواهید شخص جدیدی را به یاد بیاورید، شما ابتدا:",
     ["چهره او را تصور می‌کنید", "نام او را در ذهن تکرار می‌کنید", "نام او را می‌نویسید", "به یاد می‌آورید که چه تجربه‌ای با او داشته‌اید"]),
    ("سوال 8: وقتی می‌خواهید بهترین خرید ممکن را انجام دهید، شما:",
     ["مقایسه قیمت‌ها و مشخصات را انجام می‌دهید", "با افراد باتجربه مشورت می‌کنید", "نظرات و بررسی‌های آنلاین را می‌خوانید", "کالاها را امتحان می‌کنید و تجربه می‌کنید"]),
    ("سوال 9: وقتی یک مهارت ورزشی جدید را یاد می‌گیرید، شما:",
     ["حرکات مربی را تماشا می‌کنید", "به توضیحات او گوش می‌دهید", "دستورالعمل‌ها را می‌خوانید", "خودتان تمرین می‌کنید و تجربه می‌کنید"]),
    ("سوال 10: وقتی دوست دارید یک فیلم را بیشتر درک کنید، شما:",
     ["به صحنه‌های بصری و جلوه‌های ویژه دقت می‌کنید", "به مکالمات و موسیقی متن گوش می‌دهید", "نقدها و خلاصه داستان را مطالعه می‌کنید", "احساسات و حرکات بازیگران را درک می‌کنید"]),
    ("سوال 11: وقتی در حال مطالعه هستید، برای درک بهتر موضوع:",
     ["از نمودارها و تصاویر استفاده می‌کنید", "با صدای بلند می‌خوانید", "یادداشت‌برداری می‌کنید", "حرکت و تمرین انجام می‌دهید"]),
    ("سوال 12: وقتی در حال یادگیری یک مهارت عملی هستید، شما ترجیح می‌دهید:",
     ["ابتدا نگاه کنید و ببینید چگونه انجام می‌شود", "به توضیحات مربی گوش دهید", "دستورالعمل‌ها را بخوانید و مطالعه کنید", "آن را انجام دهید و تمرین کنید"]),
    ("سوال 13: وقتی در حال گوش دادن به موسیقی هستید، شما بیشتر به:",
     ["کاور و طراحی آلبوم نگاه می‌کنید", "کلمات و ملودی توجه می‌کنید", "متن آهنگ را مطالعه می‌کنید", "با موسیقی هماهنگ می‌شوید و حرکت می‌کنید"]),
    ("سوال 14: وقتی می‌خواهید یک مهارت جدید را یاد بگیرید، شما ابتدا:",
     ["به نمونه‌های تصویری نگاه می‌کنید", "توضیحات صوتی می‌شنوید", "راهنما و دستورالعمل می‌خوانید", "تمرین و تکرار می‌کنید"]),
    ("سوال 15: وقتی در حال انجام یک پروژه‌ی گروهی هستید، شما ترجیح می‌دهید:",
     ["ابتدا نمودارها و دیاگرام‌ها را بررسی کنید", "با اعضای تیم بحث کنید", "دستورالعمل‌های مکتوب را مرور کنید", "مستقیماً پروژه را انجام دهید"]),
    ("سوال 16: وقتی در حال آموزش دادن به کسی هستید، شما:",
     ["از تصاویر و نمودارها استفاده می‌کنید", "با او درباره موضوع صحبت می‌کنید", "مطالب را به صورت مکتوب ارائه می‌دهید", "او را تشویق به تمرین عملی می‌کنید"])
]

# انتخاب نقش کاربر از طریق Sidebar
user_role = st.sidebar.radio("👤 نقش شما:", ["شرکت‌کننده", "سوپروایزر"])

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "mypassword123"

# ------------------------------
# بخش سوپروایزر (مدیریت)
if user_role == "سوپروایزر":
    st.subheader("🔐 ورود به داشبورد مدیریت")
    username = st.text_input("نام کاربری:")
    password = st.text_input("رمز عبور:", type="password")
    if st.button("✅ ورود"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("🚀 ورود موفقیت‌آمیز!")
            safe_rerun()
        else:
            st.error("❌ نام کاربری یا رمز عبور اشتباه است!")
    
    if "admin_logged_in" in st.session_state:
        st.subheader("📊 داشبورد مدیریت نتایج کاربران")
        file_name = "vark_results.xlsx"
        if os.path.exists(file_name):
            try:
                df = pd.read_excel(file_name, engine="openpyxl")
            except Exception as e:
                st.error("خطا در خواندن فایل اکسل: " + str(e))
                df = pd.DataFrame()
            if not df.empty:
                df = df.drop_duplicates(subset=["شماره دانشجویی"])
            st.write("### لیست کاربران و پاسخ‌ها")
            search_query = st.text_input("🔍 جستجو براساس نام یا شماره دانشجویی:")
            if search_query:
                filtered_df = df[
                    df["نام"].str.contains(search_query, case=False, na=False) |
                    df["شماره دانشجویی"].astype(str).str.contains(search_query, case=False, na=False)
                ]
                st.dataframe(filtered_df)
            else:
                st.dataframe(df)
            
            # تحلیل: محاسبه امتیازات و تعیین سبک یادگیری غالب
            cat_counts = {"Visual": 0, "Auditory": 0, "Read/Write": 0, "Kinesthetic": 0}
            for index, row in df.iterrows():
                for (q_text, opts) in questions:
                    if q_text in row:
                        answer = row[q_text]
                        try:
                            option_index = opts.index(answer)
                        except ValueError:
                            option_index = None
                        if option_index is not None:
                            if option_index == 0:
                                cat_counts["Visual"] += 1
                            elif option_index == 1:
                                cat_counts["Auditory"] += 1
                            elif option_index == 2:
                                cat_counts["Read/Write"] += 1
                            elif option_index == 3:
                                cat_counts["Kinesthetic"] += 1
            dominant_style = max(cat_counts, key=cat_counts.get)
            # نگاشت سبک‌های یادگیری به فارسی
            learning_style_map = {
                "Visual": "دیداری",
                "Auditory": "شنیداری",
                "Read/Write": "خواندنی/نوشتاری",
                "Kinesthetic": "عملی"
            }
            persian_style = learning_style_map.get(dominant_style, dominant_style)
            st.success(f"مدل یادگیری شما: {persian_style}")
            
            # نمایش نمودارها
            st.write("### نمودارها")
            color_map = {"Visual": "#3498db", "Auditory": "#e74c3c", "Read/Write": "#2ecc71", "Kinesthetic": "#f39c12"}
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(list(cat_counts.keys()), list(cat_counts.values()),
                   color=[color_map[s] for s in cat_counts.keys()], edgecolor="black")
            ax.set_xlabel("Learning Style", fontsize=12)
            ax.set_ylabel("Count", fontsize=12)
            ax.set_title("Vertical Bar Chart", fontsize=14)
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            for i, v in enumerate(list(cat_counts.values())):
                ax.text(i, v + 0.2, str(v), ha='center', fontweight='bold', fontsize=12)
            st.pyplot(fig)
            
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            ax2.barh(list(cat_counts.keys()), list(cat_counts.values()),
                     color=[color_map[s] for s in cat_counts.keys()], edgecolor="black")
            ax2.set_ylabel("Learning Style", fontsize=12)
            ax2.set_xlabel("Count", fontsize=12)
            ax2.set_title("Horizontal Bar Chart", fontsize=14)
            ax2.grid(axis="x", linestyle="--", alpha=0.7)
            for i, v in enumerate(list(cat_counts.values())):
                ax2.text(v + 0.2, i, str(v), va='center', fontweight='bold', fontsize=12)
            st.pyplot(fig2)
            
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            ax3.pie(list(cat_counts.values()), labels=list(cat_counts.keys()),
                    autopct='%1.1f%%', startangle=90,
                    colors=[color_map[s] for s in cat_counts.keys()],
                    wedgeprops={'edgecolor': 'black'})
            ax3.axis("equal")
            ax3.set_title("Pie Chart", fontsize=14)
            st.pyplot(fig3)
            
            st.write("### مدیریت داده‌ها")
            col1, col2 = st.columns(2)
            with col1:
                delete_id = st.text_input("شماره دانشجویی جهت حذف رکورد:")
                if st.button("🗑 حذف رکورد"):
                    if delete_id:
                        df_new = df[df["شماره دانشجویی"].astype(str) != delete_id]
                        df_new.to_excel(file_name, index=False)
                        st.success(f"✅ رکورد مربوط به شماره دانشجویی {delete_id} حذف شد!")
                        safe_rerun()
                    else:
                        st.error("❌ لطفاً شماره دانشجویی را وارد کنید.")
            with col2:
                if st.button("🗑 حذف همه دیتا"):
                    blank_df = pd.DataFrame()
                    blank_df.to_excel(file_name, index=False)
                    st.success("✅ تمامی داده‌ها حذف شدند!")
                    safe_rerun()
            
            if st.button("📥 دانلود اکسل"):
                st.success("✅ فایل اکسل vark_results.xlsx آماده دانلود است!")
        else:
            st.warning("🚨 هنوز هیچ کاربری آزمون را انجام نداده است!")

# ------------------------------
# بخش شرکت‌کننده (پرسشنامه)
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
            safe_rerun()
    else:
        if st.session_state.get("finished", False):
            # محاسبه سبک یادگیری بدون نمایش امتیازهای جزئی
            cat_counts = {"Visual": 0, "Auditory": 0, "Read/Write": 0, "Kinesthetic": 0}
            for q_text, opts in questions:
                answer = st.session_state.answers.get(q_text)
                if answer is not None:
                    try:
                        option_index = opts.index(answer)
                    except ValueError:
                        option_index = None
                    if option_index is not None:
                        if option_index == 0:
                            cat_counts["Visual"] += 1
                        elif option_index == 1:
                            cat_counts["Auditory"] += 1
                        elif option_index == 2:
                            cat_counts["Read/Write"] += 1
                        elif option_index == 3:
                            cat_counts["Kinesthetic"] += 1
            dominant_style = max(cat_counts, key=cat_counts.get)
            learning_style_map = {
                "Visual": "دیداری",
                "Auditory": "شنیداری",
                "Read/Write": "خواندنی/نوشتاری",
                "Kinesthetic": "عملی"
            }
            persian_style = learning_style_map.get(dominant_style, dominant_style)
            st.success(f"مدل یادگیری شما: {persian_style}")
        else:
            current_index = st.session_state.current_index
            q_text, opts = questions[current_index]
            st.subheader(f"❓ {q_text}")
            # استفاده از گزینه‌های کامل شامل یک گزینه پیش‌فرض برای انتخاب
            full_options = [dummy_option] + opts
            st.radio("انتخاب پاسخ", full_options, key=f"q{current_index}", on_change=on_option_change)
