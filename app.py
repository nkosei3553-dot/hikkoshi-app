import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import pandas as pd

# ページ設定
st.title("引越し見積もり比較アプリ 🚛")

# -------------------------------------------
# 1. スプレッドシートへの接続設定
# -------------------------------------------
# Secretsから鍵情報を読み込む
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
key_dict = json.loads(st.secrets["service_account_info"])
creds = Credentials.from_service_account_info(key_dict, scopes=scope)
client = gspread.authorize(creds)

# スプレッドシートを開く（名前注意！）
spreadsheet_name = "moving_app_db"  # 昨日作ったシートの名前
try:
    sheet = client.open(spreadsheet_name).sheet1
except Exception as e:
    st.error(f"エラー：スプレッドシート '{spreadsheet_name}' が見つかりません。名前が合っているか、共有設定ができているか確認してください。")
    st.stop()

# -------------------------------------------
# 2. 入力フォーム（データの追加）
# -------------------------------------------
st.subheader("📝 新しい見積もりを登録")

with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("業者名（例：サカイ、アート）")
        price = st.number_input("見積もり金額（円）", min_value=0, step=1000)
    with col2:
        date = st.date_input("訪問見積もりの日")
        memo = st.text_area("メモ（特典や値引き条件など）")
    
    submitted = st.form_submit_button("登録する")

    if submitted:
        if company and price:
            # スプレッドシートに行を追加
            new_row = [str(date), company, price, memo]
            sheet.append_row(new_row)
            st.success(f"{company} の見積もりを登録しました！")
        else:
            st.warning("業者名と金額は必ず入力してください。")

# -------------------------------------------
# 3. データの表示（登録済みリスト）
# -------------------------------------------
st.markdown("---")
st.subheader("📊 見積もり一覧リスト")

# データを取得して表示
data = sheet.get_all_records()

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)

    # 簡単な分析（最安値の表示）
    min_price = df["見積もり金額（円）"].min() if "見積もり金額（円）" in df.columns else 0
    st.info(f"💰 現在の最安値： **{min_price:,} 円**")
else:
    st.write("まだデータがありません。")
