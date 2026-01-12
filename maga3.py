import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Magazyn Neon PRO", layout="wide")

# --- CUSTOM CSS (Stylizacja Neonowa) ---
st.markdown("""
    <style>
    /* Tło i główne kolory */
    .stApp {
        background-color: #0E1117;
        color: #00f2ff;
    }
    /* Nagłówki */
    h1, h2, h3 {
        color: #39FF14 !important;
        text-shadow: 0 0 10px #39FF14;
    }
    /* Karty i kontenery */
    [data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #00f2ff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 0 5px #00f2ff;
    }
    /* Przyciski */
    .stButton>button {
        background-color: #0E1117;
        color: #39FF14;
        border: 2px solid #39FF14;
        border-radius: 5px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #39FF14;
        color: #0E1117;
        box-shadow: 0 0 15px #39FF14;
    }
    /* Inputy */
    input {
        background-color: #161b22 !important;
        color: #00f2ff !important;
        border: 1px solid #00f2ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICJALIZACJA SESJI ---
if "magazyn" not in st.session_state:
    st.session_state.magazyn = []

# --- TABS ---
tab_mag, tab_dodaj, tab_finanse = st.tabs(["📋 MAGAZYN", "➕ DOSTAWA", "💰 RACHUNKOWOŚĆ"])

# --- TAB: MAGAZYN ---
with tab_mag:
    st.header("⚡ Stan Systemu")
    
    if not st.session_state.magazyn:
        st.info("System pusty. Oczekiwanie na dane...")
    else:
        search = st.text_input("Szukaj w bazie (Neon Search)...")
        
        for i, t in enumerate(st.session_state.magazyn):
            if search.lower() in t['nazwa'].lower():
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    c1.markdown(f"### {t['nazwa']}")
                    c1.caption(f"Kategoria: {t['kategoria']}")
                    c2.metric("Ilość", t['ilosc'])
                    c3.metric("Wartość Netto", f"{t['ilosc']*t['cena']:.2f} zł")
                    if c4.button("USUŃ", key=f"del_{i}"):
                        st.session_state.magazyn.pop(i)
                        st.rerun()

# --- TAB: DODAWANIE ---
with tab_dodaj:
    st.header("📥 Wprowadź Nowy Zasób")
    with st.form("nowy_towar"):
        col1, col2 = st.columns(2)
        nazwa = col1.text_input("Nazwa")
        kat = col2.selectbox("Kategoria", ["Hardware", "Software", "Energia", "Inne"])
        
        col3, col4, col5 = st.columns(3)
        ilosc = col3.number_input("Ilość", min_value=1)
        cena = col4.number_input("Cena zakupu Netto", min_value=0.0)
        vat = col5.selectbox("Stawka VAT", [23, 8, 5, 0])
        
        marza = st.slider("Marża sprzedaży (%)", 0, 200, 30)
        
        if st.form_submit_button("ZAINICJUJ TRANSFER"):
            st.session_state.magazyn.append({
                "nazwa": nazwa,
                "ilosc": ilosc,
                "cena": cena,
                "kategoria": kat,
                "vat": vat,
                "marza": marza
            })
            st.success("Dane przesłane pomyślnie.")
            st.rerun()

# --- TAB: RACHUNKOWOŚĆ I PODATKI ---
with tab_finanse:
    st.header("📊 Finanse i Opodatkowanie")
    
    if not st.session_state.magazyn:
        st.warning("Brak danych do analizy finansowej.")
    else:
        # Obliczenia
        wartosc_netto = sum(t['ilosc'] * t['cena'] for t in st.session_state.magazyn)
        
        # Wyliczanie podatku VAT (dla każdego produktu osobno)
        laczny_vat = sum((t['ilosc'] * t['cena']) * (t['vat']/100) for t in st.session_state.magazyn)
        
        # Estymacja przychodu przy zadanej marży
        wartosc_sprzedazy_netto = sum((t['ilosc'] * t['cena']) * (1 + t['marza']/100) for t in st.session_state.magazyn)
        potencjalny_zysk = wartosc_sprzedazy_netto - wartosc_netto

        # Wyświetlanie statystyk
        m1, m2, m3 = st.columns(3)
        m1.metric("Wartość Zakupu (Netto)", f"{wartosc_netto:.2f} zł")
        m2.metric("Podatek VAT (do zapłaty)", f"{laczny_vat:.2f} zł", delta_color="inverse")
        m3.metric("Wartość Brutto", f"{wartosc_netto + laczny_vat:.2f} zł")
        
        st.divider()
        
        st.subheader("📈 Analiza Zysku")
        c1, c2 = st.columns(2)
        c1.metric("Przewidywany Przychód (Netto)", f"{wartosc_sprzedazy_netto:.2f} zł")
        c2.metric("Szacowany Zysk (na czysto)", f"{potencjalny_zysk:.2f} zł", delta=f"{marza}% marży")

        # Tabela podatkowa
        st.subheader("📝 Szczegółowe zestawienie")
        df = pd.DataFrame(st.session_state.magazyn)
        df['Wartość Netto'] = df['ilosc'] * df['cena']
        df['Kwota VAT'] = df['Wartość Netto'] * (df['vat']/100)
        df['Sugerowana Cena Sprzedaży (Szt)'] = df['cena'] * (1 + df['marza']/100)
        
        st.dataframe(df[['nazwa', 'ilosc', 'cena', 'vat', 'Kwota VAT', 'Sugerowana Cena Sprzedaży (Szt)']], use_container_width=True)
