import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- ページ設定 ---
st.set_page_config(page_title="引越し見積もり比較", page_icon="🚚", layout="wide")

# --- タイトルと概要 ---
st.title("🚚 引越し料金 徹底比較アプリ")
st.markdown("山口県 ➡ 大阪府（3月末 繁忙期）")

# --- データベース接続 (Google Sheets) ---
# キャッシュを無効化して常に最新データを取得
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # データを取得
    df = conn.read(worksheet="シート1", ttl=0)
    # 空の行を削除
    df = df.dropna(how="all")
except Exception as e:
    st.error(f"データベースへの接続に失敗しました: {e}")
    st.stop()

# --- サイドバー：新規データの入力 ---
st.sidebar.header("📝 新規見積もりの登録")

with st.sidebar.form("entry_form"):
    vendor = st.text_input("業者名（例: アート、ハート）")
    price = st.number_input("合計金額 (円)", min_value=0, step=1000)
    
    col1, col2 = st.columns(2)
    with col1:
        date_start = st.date_input("積込日")
    with col2:
        date_end = st.date_input("搬入日")
        
    plan = st.selectbox("プラン", ["基本コース", "梱包お任せ", "開梱お任せ", "全お任せ", "フリー便", "時間指定"])
    
    # PDFにある詳細項目
    box_num = st.text_input("ダンボール数（例: S10, M20）")
    options = st.text_input("オプション（例: エアコン脱着, 洗濯機）")
    memo = st.text_area("備考（特典、注意事項など）")
    
    submitted = st.form_submit_button("登録する")

    if submitted:
        if not vendor or price == 0:
            st.warning("業者名と金額は必須です！")
        else:
            # 新しいデータを作成
            new_data = pd.DataFrame([{
                "業者名": vendor,
                "合計金額": price,
                "引越し日(積込)": date_start.strftime('%Y/%m/%d'),
                "引越し日(搬入)": date_end.strftime('%Y/%m/%d'),
                "プラン": plan,
                "ダンボール": box_num,
                "オプション(洗濯機等)": options,
                "備考": memo
            }])
            
            # 既存データと結合して更新
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            # Googleシートに書き込み
            conn.update(worksheet="シート1", data=updated_df)
            
            st.success("登録完了！データがクラウドに保存されました。")
            st.rerun()

# --- メイン画面：データの表示と分析 ---

# データが存在する場合のみ表示
if not df.empty:
    # 1. 最安値の強調表示
    min_price = df["合計金額"].min()
    best_vendor = df[df["合計金額"] == min_price].iloc[0]["業者名"]
    
    st.info(f"🏆 現在の最安値: **{min_price:,.0f}円** ({best_vendor})")

    # 2. グラフで比較 (スマホで見やすいようにタブ分け)
    tab1, tab2 = st.tabs(["📊 グラフで比較", "📋 詳細リスト"])
    
    with tab1:
        st.bar_chart(df, x="業者名", y="合計金額", color="業者名")
        
        # 3月の繁忙期アラート（PDFの日付に基づく）
        st.warning("⚠️ **3月22日〜28日は超繁忙期です**\n\nPDFの見積もりによると、この期間は料金が通常より高騰します。また、トラックの確保が困難になるため、**即決**を求められるケースが多いです。")

    with tab2:
        # データフレームを表示（スマホでもスクロールで見れる設定）
        st.dataframe(df, use_container_width=True)

else:
    st.info("👈 左側のサイドバーから、最初の見積もりを登録してください。")