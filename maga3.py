import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Magazyn PRO", layout="wide")

# --- Inicjalizacja danych ---
if "magazyn" not in st.session_state:
    st.session_state.magazyn = []
if "historia" not in st.session_state:
    st.session_state.historia = []

# --- Funkcje pomocnicze ---
def dodaj_log(akcja):
    now = datetime.now().strftime("%H:%M:%S")
    st.session_state.historia.insert(0, f"[{now}] {akcja}")

# --- Sidebar: Statystyki i Filtry ---
with st.sidebar:
    st.title("⚙️ Panel Sterowania")
    szukaj = st.text_input("🔍 Szukaj towaru")
    kategoria_filtr = st.multiselect("Filtr kategorii", ["Elektronika", "Spożywcze", "Biuro", "Inne"])
    
    st.divider()
    st.subheader("📊 Szybkie statystyki")
    calosc = sum(t["ilosc"] * t["cena"] for t in st.session_state.magazyn)
    st.metric("Całkowita wartość", f"{calosc:.2f} zł")
    
    # Eksport danych
    if st.session_state.magazyn:
        df = pd.DataFrame(st.session_state.magazyn)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Pobierz raport CSV", csv, "magazyn.csv", "text/csv")

# --- Główne okno: Dodawanie ---
st.title("📦 Zaawansowany Magazyn")

with st.expander("➕ Dodaj nowy towar do bazy", expanded=False):
    with st.form("dodaj_towar", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nazwa = col1.text_input("Nazwa towaru")
        kat = col2.selectbox("Kategoria", ["Elektronika", "Spożywcze", "Biuro", "Inne"])
        
        col3, col4 = st.columns(2)
        ilosc = col3.number_input("Ilość początkowa", min_value=1, step=1)
        cena = col4.number_input("Cena zakupu (szt.)", min_value=0.0, step=0.01)

        submitted = st.form_submit_button("Dodaj produkt")
        if submitted:
            if nazwa.strip():
                st.session_state.magazyn.append({
                    "nazwa": nazwa, "ilosc": ilosc, "cena": cena, "kategoria": kat
                })
                dodaj_log(f"Dodano: {nazwa} ({ilosc} szt.)")
                st.success(f"Dodano produkt: {nazwa}")
                st.rerun()
            else:
                st.error("Nazwa nie może być pusta!")

# --- Widok Magazynu ---
st.header("📋 Aktualne stany")

if not st.session_state.magazyn:
    st.info("Twój magazyn jest obecnie pusty. Dodaj pierwszy produkt w panelu powyżej.")
else:
    # Nagłówki tabeli
    h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 1])
    h1.write("**Nazwa / Kategoria**")
    h2.write("**Cena jedn.**")
    h3.write("**Ilość**")
    h4.write("**Wartość**")
    h5.write("**Opcje**")
    st.divider()

    for i, towar in enumerate(st.session_state.magazyn):
        # Logika filtrowania
        if szukaj.lower() not in towar['nazwa'].lower(): continue
        if kategoria_filtr and towar['kategoria'] not in kategoria_filtr: continue

        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            
            # Nazwa i kategoria
            c1.markdown(f"**{towar['nazwa']}** \n<small>{towar['kategoria']}</small>", unsafe_allow_html=True)
            c2.write(f"{towar['cena']:.2f} zł")
            
            # Edycja ilości (+ / -)
            col_plus, col_val, col_minus = c3.columns([1, 2, 1])
            if col_plus.button("➕", key=f"p_{i}"):
                st.session_state.magazyn[i]['ilosc'] += 1
                dodaj_log(f"Zwiększono: {towar['nazwa']} (+1)")
                st.rerun()
            
            col_val.write(f"{towar['ilosc']}")
            
            if col_minus.button("➖", key=f"m_{i}"):
                if st.session_state.magazyn[i]['ilosc'] > 0:
                    st.session_state.magazyn[i]['ilosc'] -= 1
                    dodaj_log(f"Zmniejszono: {towar['nazwa']} (-1)")
                    st.rerun()

            # Wartość
            c4.write(f"**{towar['ilosc'] * towar['cena']:.2f} zł**")

            # Usuwanie
            if c5.button("🗑️", key=f"del_{i}"):
                p_nazwa = st.session_state.magazyn.pop(i)
                dodaj_log(f"Usunięto z bazy: {p_nazwa['nazwa']}")
                st.rerun()
            st.divider()

# --- Dziennik Zdarzeń ---
with st.expander("📜 Historia operacji"):
    for wpis in st.session_state.historia[:10]: # Pokazuje 10 ostatnich
        st.text(wpis)
