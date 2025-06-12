import streamlit as st
from collections import deque, Counter
import pandas as pd
import altair as alt

ALL_SYMBOLS = ["🥕", "🍅", "🌽", "🥬", "🌭", "🥩", "🍢"]
SPIRAL_SYMBOLS = {"🌭", "🥩", "🍢"}
history = st.session_state.get("history", deque(maxlen=20))

data = pd.DataFrame([
    ("🥕", False, "Salad Ringan"),
    ("🌭", True, "Spiral Trigger"),
    ("🥩", True, "Spiral Aktif"),
    ("🍢", True, "Spiral Lanjut"),
    ("🍅", True, "Spiral Melambat"),
    ("🥬", False, "Reset / Salad Berat"),
    ("🌽", False, "Salad Netral"),
], columns=["Simbol", "Spiral", "Loop"])

st.set_page_config(page_title="Greedy Spiral Predictor", layout="centered")
st.title("🔮 Prediksi Spiral Greedy")
st.markdown("Klik simbol sesuai hasil terakhir dari permainan:")
cols = st.columns(len(ALL_SYMBOLS))
clicked = None
for i, s in enumerate(ALL_SYMBOLS):
    if cols[i].button(s):
        clicked = s
        history.append(s)
        st.session_state["history"] = history

def predict_next(hist):
    if len(hist) < 2:
        return None, 0.0, "(Belum cukup data)"
    last2 = list(hist)[-2:]
    pairs = zip(data["Simbol"].shift(1), data["Simbol"])
    nexts = [curr for prev, curr in pairs if list(last2)[-2] == prev and list(last2)[-1] == curr]
    if not nexts:
        return None, 0.0, "(Belum ada pola)"
    pred, count = Counter(nexts).most_common(1)[0]
    conf = round(count / len(nexts) * 100, 2)
    loop_info = data[data["Simbol"] == pred].iloc[-1]["Loop"]
    return pred, conf, loop_info

if history:
    st.subheader("📊 Histori Simbol")
    st.write(" ".join(history))
    pred, conf, loop = predict_next(history)
    if pred:
        st.subheader("🔮 Prediksi Berikutnya")
        st.success(f"{pred}  |  Akurasi: {conf}%  |  Status: {loop}")

if history:
    st.subheader("📈 Grafik Simbol")
    df_hist = pd.DataFrame(Counter(history).items(), columns=["Simbol", "Frekuensi"])
    chart = alt.Chart(df_hist).mark_bar().encode(
        x="Simbol", y="Frekuensi", color=alt.Color("Simbol", legend=None)
    )
    st.altair_chart(chart, use_container_width=True)

st.caption("🧠 Sistem by Baraka + GPT — versi awal spiral reader")
