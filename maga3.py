import streamlit as st

st.set_page_config(page_title="Prosty magazyn", layout="centered")

st.title("📦 Prosty magazyn (bez zapisu do plików)")

# Inicjalizacja magazynu w pamięci sesji
if "magazyn" not in st.session_state:
    st.session_state.magazyn = []

# --- Dodawanie towaru ---
st.header("➕ Dodaj towar")

with st.form("dodaj_towar"):
    nazwa = st.text_input("Nazwa towaru")
    ilosc = st.number_input("Ilość", min_value=1, step=1)
    cena = st.number_input("Cena za sztukę", min_value=0.0, step=0.01)

    submitted = st.form_submit_button("Dodaj")

    if submitted:
        if nazwa.strip() == "":
            st.warning("Podaj nazwę towaru.")
        else:
            st.session_state.magazyn.append({
                "nazwa": nazwa,
                "ilosc": ilosc,
                "cena": cena
            })
            st.success(f"Dodano towar: {nazwa}")

# --- Wyświetlanie magazynu ---
st.header("📋 Stan magazynu")

if not st.session_state.magazyn:
    st.info("Magazyn jest pusty.")
else:
    for i, towar in enumerate(st.session_state.magazyn):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

        col1.write(f"**{towar['nazwa']}**")
        col2.write(f"Ilość: {towar['ilosc']}")
        col3.write(f"Cena: {towar['cena']} zł")

        if col4.button("❌", key=f"usun_{i}"):
            st.session_state.magazyn.pop(i)
            st.experimental_rerun()

# --- Wartość magazynu ---
st.header("💰 Wartość magazynu")

wartosc = sum(t["ilosc"] * t["cena"] for t in st.session_state.magazyn)
st.write(f"**Łączna wartość magazynu:** {wartosc:.2f} zł")
