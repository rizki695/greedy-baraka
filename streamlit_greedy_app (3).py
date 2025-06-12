import streamlit as st
from collections import deque, Counter
import pandas as pd
import altair as alt

ALL_SYMBOLS = ["🥕", "🍅", "🌽", "🥬", "🌭", "🥩", "🍢"]
SPIRAL_SYMBOLS = {"🌭", "🥩", "🍢"}
history = st.session_state.get("history", deque(maxlen=30))

# Dataset pelatihan pola spiral + loop dari histori Bang Aji
data = pd.DataFrame([
    ("🥕", False, "Salad Ringan"),
    ("🌭", True, "Spiral Trigger"),
    ("🥩", True, "Spiral Aktif"),
    ("🍢", True, "Spiral Lanjut"),
    ("🍅", True, "Spiral Melambat"),
    ("🥬", False, "Reset / Salad Berat"),
    ("🌽", False, "Salad Netral"),
    ("🍢", True, "Spiral Campur"),
    ("🌭", True, "Spiral Ulang"),
    ("🍅", True, "Spiral Delay"),
    ("🥬", False, "Loop Salad Berat"),
    ("🥕", False, "Loop Salad Ringan"),
], columns=["Simbol", "Spiral", "Loop"])

st.set_page_config(page_title="Greedy Spiral Predictor", layout="centered")
st.title("🔮 Prediksi Spiral Greedy (Final Versi)")

st.markdown("Klik simbol sesuai hasil terakhir dari permainan:")
cols = st.columns(len(ALL_SYMBOLS))
for i, s in enumerate(ALL_SYMBOLS):
    if cols[i].button(s):
        history.append(s)
        st.session_state["history"] = history

def predict_next(hist):
    if len(hist) < 2:
        return fallback_prediction(hist)

    last2 = tuple(list(hist)[-2:])
    pairs = list(zip(data["Simbol"].shift(1), data["Simbol"]))
    match = [curr for prev, curr in pairs if prev == last2[0] and curr == last2[1]]

    if match:
        pred, count = Counter(match).most_common(1)[0]
        conf = round(count / len(match) * 100, 2)
        loop = data[data["Simbol"] == pred].iloc[-1]["Loop"]
        return pred, conf, loop

    # Fallback jika 2 simbol terakhir tidak ditemukan
    return fallback_prediction(hist)

def fallback_prediction(hist):
    if not hist:
        return None, 0.0, "(Belum ada data)"
    last = hist[-1]
    candidates = data[data["Simbol"] != last]["Simbol"].value_counts()
    if not candidates.empty:
        pred = candidates.index[0]
        conf = round((candidates.iloc[0] / candidates.sum()) * 100, 2)
        loop = data[data["Simbol"] == pred].iloc[-1]["Loop"]
        return pred, conf, loop
    return None, 0.0, "(Tidak ditemukan)"

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

    pred, conf, loop = predict_next(history)
    spiral_status = detect_spiral(history)

    st.subheader("🔮 Prediksi Berikutnya")
    if pred:
        st.success(f"Prediksi: {pred} | Akurasi: {conf}% | Status Loop: {loop}")
        st.info(f"📡 Status Spiral: {spiral_status}")
    else:
        st.warning("Belum ada data cukup untuk prediksi.")

if history:
    st.subheader("📈 Grafik Simbol")
    df_hist = pd.DataFrame(Counter(history).items(), columns=["Simbol", "Frekuensi"])
    chart = alt.Chart(df_hist).mark_bar().encode(
        x="Simbol", y="Frekuensi", color=alt.Color("Simbol", legend=None)
    )
    st.altair_chart(chart, use_container_width=True)

st.caption("🧠 Sistem by Baraka + GPT — versi final spiral+loop auto prediction")
