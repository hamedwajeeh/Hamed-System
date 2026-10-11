import os
import re
import pandas as pd
import streamlit as st

CUSTOMERS_FILE = "hamed_customers.csv"
REQUESTS_FILE = "hamed_requests.csv"
DELETED_IDS_FILE = "hamed_deleted_ids.txt"

if not os.path.exists(CUSTOMERS_FILE):
    pd.DataFrame(columns=["ID", "Name", "Age", "Email"]).to_csv(CUSTOMERS_FILE, index=False)

if not os.path.exists(REQUESTS_FILE):
    pd.DataFrame(columns=["Name", "Age", "Email"]).to_csv(REQUESTS_FILE, index=False)

if not os.path.exists(DELETED_IDS_FILE):
    with open(DELETED_IDS_FILE, "w") as f:
        pass


def load_customers():
    return pd.read_csv(CUSTOMERS_FILE)


def save_customers(df):
    df.to_csv(CUSTOMERS_FILE, index=False)


def load_requests():
    return pd.read_csv(REQUESTS_FILE)


def save_requests(df):
    df.to_csv(REQUESTS_FILE, index=False)


def load_deleted_ids():
    if not os.path.exists(DELETED_IDS_FILE):
        return []
    with open(DELETED_IDS_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return []
        return content.split(",")


def save_deleted_ids(ids_list):
    with open(DELETED_IDS_FILE, "w") as f:
        f.write(",".join(ids_list))


def is_valid_email(email_str):
    if email_str.lower() == "none":
        return True
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email_str))


def get_next_available_id():
    deleted_ids = load_deleted_ids()
    if deleted_ids:
        next_id = deleted_ids.pop(0)
        save_deleted_ids(deleted_ids)
        return next_id

    df_cust = load_customers()
    existing_ids = [str(x).strip() for x in df_cust["ID"].tolist() if pd.notna(x)]
    if not existing_ids: return "A1"

    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']
    last_id = existing_ids[-1]
    try:
        last_char, last_num = last_id.upper(), int(last_id[1:])
        if last_num < 150: return f"{last_char}{last_num + 1}"
        return f"{alphabet[alphabet.index(last_char) + 1]}1"
    except:
        return "A1"


st.set_page_config(page_title="Hamed System", page_icon="👑", layout="centered")

st.markdown("""
    <style>
    @keyframes fadeInAndMoveUp {
        0% { font-size: 36px; margin-top: 150px; opacity: 0; filter: blur(5px); }
        40% { font-size: 36px; margin-top: 150px; opacity: 1; filter: blur(0px); }
        100% { font-size: 24px; margin-top: 5px; opacity: 1; filter: blur(0px); }
    }
    .animated-title {
        text-align: center;
        color: #B71C1C;
        font-weight: bold;
        animation: fadeInAndMoveUp 2.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
        margin-bottom: 25px;
    }
    .fixed-crown-container { position: fixed; bottom: 25px; left: 25px; z-index: 9999; }
    div.fixed-crown-container > button { background-color: transparent !important; font-size: 26px !important; border: none !important; cursor: pointer; }
    div.stButton > button:first-child { background-color: #D32F2F !important; color: white !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="animated-title">Hamed Customer Service System - Beta</div>', unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "guest_view"

if st.session_state.page == "guest_view":
    st.subheader("📝 طلب إضافة مستخدم")
    with st.form("g_form", clear_on_submit=True):
        name = st.text_input("الاسم").strip()
        age = st.number_input("العمر", min_value=1, max_value=120, value=25)
        email = st.text_input("البريد الإلكتروني").strip()

        if st.form_submit_button("إرسال الطلب"):
            if name and email:
                if is_valid_email(email):
                    df_req = load_requests()
                    new_r = pd.DataFrame([{"Name": name, "Age": int(age), "Email": email}])
                    df_req = pd.concat([df_req, new_r], ignore_index=True)
                    save_requests(df_req)
                    st.success("🎉 تم إرسال الطلب بنجاح في قائمة الانتظار الحية!")
                else:
                    st.error("❌ صيغة البريد غير صحيحة! أدخل إيميل يحتوي على @ وجيميل، أو اكتب none لتعمل بنجاح.")
            else:
                st.error("❌ الرجاء ملء الحقول أولاً!")

    st.markdown('<div class="fixed-crown-container">', unsafe_allow_html=True)
    if st.button("👑", key="crown_btn"):
        st.session_state.page = "host_login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "host_login":
    if st.button("⬅️ العودة للقائمة الرئيسية"):
        st.session_state.page = "guest_view"
        st.rerun()

    st.subheader("🔑 رمز التحقق للرئيس")
    code = st.text_input("أدخل الرمز السري للوحة التحكم للتحقق:", type="password").strip()

    if code == "110251":
        st.session_state.page = "host_panel"
        st.rerun()
    elif code != "":
        st.error("❌ الرمز السري المكتوب خاطئ!")

elif st.session_state.page == "host_panel":
    if st.button("⬅️ خروج"):
        st.session_state.page = "guest_view"
        st.rerun()

    st.success("🔓 مرحبا بك أيها الرئيس")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📥 الطلبات المعلقة", "📊 العملاء الحاليين", "➕ إضافة عميل مباشرة", "📱 رابط الموقع"])

    with tab1:
        st.write("### الطلبات التي في انتظار قبولك الفوري:")
        df_req = load_requests()
        if not df_req.empty:
            for index, row in df_req.iterrows():
                col_t, col_b = st.columns(2)
                col_t.write(f"👤 **الاسم:** {row['Name']} | 🎂 **العمر:** {row['Age']} | ✉️ **الإيميل:** {row['Email']}")
                if col_b.button("قبول الحساب والتفعيل", key=f"ac_{index}"):
                    nid = get_next_available_id()
                    df_cust = load_customers()
                    new_cust = pd.DataFrame(
                        [{"ID": nid, "Name": row['Name'], "Age": int(row['Age']), "Email": row['Email']}])
                    df_cust = pd.concat([df_cust, new_cust], ignore_index=True)
                    save_customers(df_cust)

                    df_req = df_req.drop(index).reset_index(drop=True)
                    save_requests(df_req)

                    st.success(f"تم تفعيل الحساب الصادر بـ ID: {nid}")
                    st.rerun()
        else:
            st.info("لا توجد طلبات معلقة حالياً.")

    with tab2:
        st.write("### قائمة جميع العملاء المسجلين:")
        df_cust = load_customers()
        if not df_cust.empty:
            st.dataframe(df_cust, use_container_width=True)
            search_id = st.text_input("🔍 بحث سريع بالـ ID:").strip().upper()
            if search_id:
                res = df_cust[df_cust["ID"].astype(str).str.upper() == search_id]
                if not res.empty:
                    st.json(res.iloc[0].to_dict())
                else:
                    st.error("لم يتم العثور على المعرف.")

            for index, row in df_cust.iterrows():
                with st.expander(f"🆔 {row['ID']} - {row['Name']}"):
                    en = st.text_input("الاسم", value=row['Name'], key=f"en_{index}")
                    ea = st.number_input("العمر", value=int(row['Age']), key=f"ea_{index}")
                    ee = st.text_input("الإيميل", value=row['Email'], key=f"ee_{index}")
                    col_save, col_del = st.columns(2)

                    if col_save.button("💾 حفظ التعديلات", key=f"sv_{index}"):
                        df_cust.at[index, "Name"] = en
                        df_cust.at[index, "Age"] = int(ea)
                        df_cust.at[index, "Email"] = ee
                        save_customers(df_cust)
                        st.success("تم تحديث بيانات العميل بنجاح!")
                        st.rerun()

                    if col_del.button("🗑️ حذف الحساب", key=f"dl_{index}"):
                        st.session_state[f"conf_{index}"] = True

                    if st.session_state.get(f"conf_{index}", False):
                        st.error("❓ هل أنت متأكد تماماً من الحذف النهائي للعميل؟")
                        cy, cn = st.columns(2)
                        if cy.button("🛑 نعم، متأكد", key=f"y_{index}"):
                            deleted_ids = load_deleted_ids()
                            deleted_ids.append(row['ID'])
                            save_deleted_ids(deleted_ids)

                            df_cust = df_cust.drop(index).reset_index(drop=True)
                            save_customers(df_cust)

                            st.session_state[f"conf_{index}"] = False
                            st.success("تم الحذف بنجاح!")
                            st.rerun()
                        if cn.button("❌ إلغاء الأمر", key=f"n_{index}"):
                            st.session_state[f"conf_{index}"] = False
                            st.rerun()
        else:
            st.info("قاعدة البيانات فارغة تماماً.")

    with tab3:
        st.write("### إضافة عميل مباشرة لقاعدة البيانات بدون انتظار موافقة:")
        with st.form("d_form", clear_on_submit=True):
            dn = st.text_input("اسم العميل الجديد")
            da = st.number_input("عمر العميل الجديد", min_value=1, max_value=120, value=25)
            de = st.text_input("الإيميل الجديد")
            if st.form_submit_button("إضافة فورا"):
                if dn and is_valid_email(de):
                    nid = get_next_available_id()
                    df_cust = load_customers()
                    new_cust = pd.DataFrame([{"ID": nid, "Name": dn, "Age": int(da), "Email": de}])
                    df_cust = pd.concat([df_cust, new_cust], ignore_index=True)
                    save_customers(df_cust)
                    st.success(f"🎉 تم حفظ وإضافة العميل مباشرة بـ ID: {nid}")
                    st.rerun()
                else:
                    st.error("تأكد من كتابة الاسم وصحة صيغة الإيميل المكتوب!")

    with tab4:
        st.write("### 📱 رابط موقعك الرسمي:")
        st.info("هذا هو موقعك على الإنترنت، يعمل بكفاءة ودون فقدان للبيانات.")
