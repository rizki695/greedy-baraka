import streamlit as st
from collections import deque, Counter
import pandas as pd
import altair as alt

# Konstanta
ALL_SYMBOLS = ["🥕", "🍅", "🌽", "🥬", "🌭", "🥩", "🍢"]
SPIRAL_SYMBOLS = {"🌭", "🥩", "🍢"}
history = st.session_state.get("history", deque(maxlen=50))

# Load dataset spiral dari file CSV
@st.cache_data
def load_dataset():
    df = pd.read_csv("dataset_spiral.csv")
    return df

data = load_dataset()

st.set_page_config(page_title="Prediksi Spiral Greedy", layout="centered")
st.title("🔮 Prediksi Spiral Greedy (Dari Dataset Riil)")

st.markdown("Klik simbol sesuai hasil terakhir dari permainan:")
cols = st.columns(len(ALL_SYMBOLS))
for i, s in enumerate(ALL_SYMBOLS):
    if cols[i].button(s):
        history.append(s)
        st.session_state["history"] = history

def predict_top_two(hist):
    if len(hist) >= 2:
        last2 = tuple(hist)[-2:]
        match = data[(data["prev_symbol"] == last2[0]) & (data["next_symbol"] == last2[1])]
        count_next = data[data["prev_symbol"] == last2[1]]["next_symbol"]
        freq = Counter(count_next)
        top2 = freq.most_common(2)
    elif len(hist) >= 1:
        last = hist[-1]
        count_next = data[data["prev_symbol"] == last]["next_symbol"]
        freq = Counter(count_next)
        top2 = freq.most_common(2)
    else:
        freq = Counter(data["next_symbol"])
        top2 = freq.most_common(2)

    results = []
    for symb, count in top2:
        total = sum(freq.values())
        conf = round(count / total * 100, 2)
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

    st.subheader("🔮 2 Prediksi Terbaik Berdasarkan Dataset")
    for i, (symb, conf) in enumerate(results, 1):
        st.success(f"{i}️⃣ {symb} | Confidence: {conf}%")

    st.info(f"📡 Spiral Status: {spiral_status}")

    st.subheader("📈 Grafik Simbol")
    df_hist = pd.DataFrame(Counter(history).items(), columns=["Simbol", "Frekuensi"])
    chart = alt.Chart(df_hist).mark_bar().encode(
        x="Simbol", y="Frekuensi", color=alt.Color("Simbol", legend=None)
    )
    st.altair_chart(chart, use_container_width=True)

st.caption("🧠 Sistem by Baraka + GPT — baca spiral dari CSV historis pribadi")
