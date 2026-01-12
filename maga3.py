import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- KONFIGURACJA POŁĄCZENIA ---
# Pobierz te dane z ustawień Supabase (Settings -> API)
SUPABASE_URL = https://bhvyvyowqofvngpjitzq.supabase.co
SUPABASE_KEY = sb_publishable_4YjSj8q8TiQg_9O1hFSbZg_cDoTNJhf

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Inicjalizacja klienta
supabase = init_connection()

# --- USTAWIENIA STRONY ---
st.set_page_config(page_title="CyberMagazyn 2026", layout="centered")

# --- NEONOWY CSS (Zielony + Błękitny + Białe Nazwy) ---
st.markdown("""
    <style>
    /* Główny kolor tła i błękitne teksty */
    .stApp { background-color: #0E1117; color: #00f2ff; }
    
    /* Neonowe zielone nagłówki */
    h1, h2, h3 { 
        color: #39FF14 !important; 
        text-shadow: 0 0 12px #39FF14; 
        font-family: 'Courier New', monospace;
    }
    
    /* BIAŁE, JASNE NAZWY PRODUKTÓW */
    .product-title {
        color: #FFFFFF !important; 
        font-size: 1.5rem;
        font-weight: bold;
        text-shadow: 0 0 5px #ffffff;
        margin-bottom: 0px;
    }

    /* Stylizacja kart produktów */
    .product-box {
        border-left: 4px solid #39FF14;
        padding-left: 15px;
        margin-bottom: 25px;
        background-color: #161b22;
        padding-top: 10px;
        padding-bottom: 10px;
        border-radius: 0 10px 10px 0;
    }

    /* Przycisk usuwania (Czerwony Neon) */
    .stButton>button {
        background-color: transparent;
        color: #ff3131;
        border: 2px solid #ff3131;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff3131;
        color: white;
        box-shadow: 0 0 20px #ff3131;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ CYBER-WAREHOUSE PRO")

# --- ZAKŁADKI ---
tab_mag, tab_fin = st.tabs(["📋 MAGAZYN", "💰 RACHUNKOWOŚĆ"])

# --- TAB 1: MAGAZYN ---
with tab_mag:
    st.header("➕ Dodaj Towar")
    with st.form("new_item", clear_on_submit=True):
        name = st.text_input("Nazwa towaru")
        c1, c2, c3 = st.columns(3)
        q = c1.number_input("Ilość", min_value=1, step=1)
        p = c2.number_input("Cena Netto (zł)", min_value=0.0, step=0.01)
        v = c3.selectbox("VAT %", [23, 8, 5, 0])
        
        if st.form_submit_button("DODAJ DO BAZY"):
            if name:
                supabase.table("magazyn").insert({"nazwa": name, "ilosc": q, "cena": p, "vat": v}).execute()
                st.success(f"Pomyślnie dodano: {name}")
                st.rerun()

    st.header("📋 Stan Zasobów")
    
    # Pobieranie produktów z Supabase
    response = supabase.table("magazyn").select("*").order("id", desc=True).execute()
    produkty = response.data

    if not produkty:
        st.info("Magazyn jest obecnie pusty.")
    else:
        for item in produkty:
            # Kontener stylizowany na kartę
            st.markdown(f"""
                <div class="product-box">
                    <div class="product-title">{item['nazwa']}</div>
                    <span style="color: #00f2ff;">Ilość: {item['ilosc']} | Cena: {item['cena']:.2f} zł | VAT: {item['vat']}%</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Przycisk usuwania pod kartą
            if st.button(f"USUŃ: {item['nazwa']}", key=f"del_{item['id']}"):
                supabase.table("magazyn").delete().eq("id", item['id']).execute()
                st.rerun()

# --- TAB 2: RACHUNKOWOŚĆ ---
with tab_fin:
    st.header("📊 Rozliczenia i Podatki")
    
    if produkty:
        df = pd.DataFrame(produkty)
        
        # Obliczenia finansowe
        df['Suma Netto'] = df['ilosc'] * df['cena']
        df['Kwota VAT'] = df['Suma Netto'] * (df['vat'] / 100)
        df['Suma Brutto'] = df['Suma Netto'] + df['Kwota VAT']
        
        # Metryki
        m1, m2, m3 = st.columns(3)
        m1.metric("Łącznie NETTO", f"{df['Suma Netto'].sum():,.2f} zł")
        m2.metric("Łącznie VAT", f"{df['Kwota VAT'].sum():,.2f} zł")
        m3.metric("Łącznie BRUTTO", f"{df['Suma Brutto'].sum():,.2f} zł")
        
        st.divider()
        st.subheader("📝 Pełny arkusz podatkowy")
        # Wyświetlamy tabelę (Pandas stylizuje ją automatycznie w Streamlit)
        st.dataframe(df[['nazwa', 'ilosc', 'cena', 'vat', 'Suma Netto', 'Kwota VAT', 'Suma Brutto']], 
                     use_container_width=True)
    else:
        st.warning("Brak danych do wygenerowania raportu.")
