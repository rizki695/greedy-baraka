import streamlit as st
from collections import deque, Counter
import pandas as pd
import altair as alt
import os

ALL_SYMBOLS = ["🥕", "🍅", "🌽", "🥬", "🌭", "🥩", "🍢"]
SPIRAL_SYMBOLS = {"🌭", "🥩", "🍢"}
history = st.session_state.get("history", deque(maxlen=50))
log_path = "riwayat_aktual.csv"

@st.cache_data
def load_dataset():
    if os.path.exists("dataset_spiral.csv"):
        return pd.read_csv("dataset_spiral.csv")
    else:
        return pd.DataFrame(columns=["prev_symbol", "next_symbol"])

@st.cache_data
def load_log():
    if os.path.exists(log_path):
        return pd.read_csv(log_path)
    else:
        return pd.DataFrame(columns=["prev_symbol", "next_symbol"])

def save_to_log(prev, next_):
    log_df = load_log()
    new_row = pd.DataFrame([[prev, next_]], columns=["prev_symbol", "next_symbol"])
    log_df = pd.concat([log_df, new_row], ignore_index=True)
    log_df.drop_duplicates(inplace=True)
    log_df.to_csv(log_path, index=False)

data = load_dataset()
log_data = load_log()

st.set_page_config(page_title="Prediksi Spiral Greedy", layout="centered")
st.title("🔮 Prediksi Spiral Greedy + Auto Learning")

st.markdown("Klik simbol sesuai hasil terakhir dari permainan:")
cols = st.columns(len(ALL_SYMBOLS))
clicked = None
for i, s in enumerate(ALL_SYMBOLS):
    if cols[i].button(s):
        clicked = s
        if len(history) >= 1:
            save_to_log(history[-1], s)
        history.append(s)
        st.session_state["history"] = history

def predict_top_two(hist):
    combined = pd.concat([data, log_data], ignore_index=True)
    freq = Counter()
    if len(hist) >= 2:
        last2 = tuple(hist)[-2:]
        freq.update(combined[combined["prev_symbol"] == last2[1]]["next_symbol"])
    elif len(hist) >= 1:
        last = hist[-1]
        freq.update(combined[combined["prev_symbol"] == last]["next_symbol"])

    if len(freq) < 2:
        global_freq = Counter(combined["next_symbol"])
        for symb, count in global_freq.items():
            if symb not in freq:
                freq[symb] = count
            if len(freq) >= 2:
                break

    top2 = freq.most_common(2)
    results = []
    total = sum(freq.values())
    for symb, count in top2:
        conf = round(count / total * 100, 2) if total > 0 else 0.0
        results.append((symb, conf))
    return results

def detect_spiral(hist):
    spiral_count = sum(1 for s in hist if s in SPIRAL_SYMBOLS)
    if spiral_count >= 4:
        return "🟢 Spiral Aktif"
    elif spiral_count >= 2:
        return "🟡 Spiral Melemah"
    return "🔴 Spiral Off"

if history:
    st.subheader("📊 Histori Simbol")
    st.write(" → ".join(history))

    spiral_status = detect_spiral(history)
    results = predict_top_two(history)

    st.subheader("🔮 2 Prediksi Terbaik Berdasarkan Dataset + Log")
    for i, (symb, conf) in enumerate(results, 1):
        st.success(f"{i}️⃣ {symb} | Confidence: {conf}%")

    if len(results) < 2:
        st.warning("Hanya 1 simbol yang tersedia dari kombinasi dataset + log.")

    st.info(f"📡 Spiral Status: {spiral_status}")

    st.subheader("📈 Grafik Simbol")
    df_hist = pd.DataFrame(Counter(history).items(), columns=["Simbol", "Frekuensi"])
    chart = alt.Chart(df_hist).mark_bar().encode(
        x="Simbol", y="Frekuensi", color=alt.Color("Simbol", legend=None)
    )
    st.altair_chart(chart, use_container_width=True)

st.caption("🧠 Sistem by Baraka + GPT — auto belajar & selalu tampilkan 2 prediksi")
