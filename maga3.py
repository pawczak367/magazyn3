import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA POŁĄCZENIA ---
# W wersji produkcyjnej użyj st.secrets["SUPABASE_URL"] itd.
URL = "TWOJ_SUPABASE_URL"
KEY = "TWOJ_SUPABASE_ANON_KEY"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

st.set_page_config(page_title="Magazyn PRO", layout="wide")

# --- FUNKCJE CRUD ---
def pobierz_dane():
    query = supabase.table("magazyn").select("*").execute()
    return query.data

def dodaj_towar(nazwa, ilosc, cena, kategoria):
    data = {"nazwa": nazwa, "ilosc": ilosc, "cena": cena, "kategoria": kategoria}
    supabase.table("magazyn").insert(data).execute()

def usun_towar(id_towaru):
    supabase.table("magazyn").delete().eq("id", id_towaru).execute()

# --- INTERFEJS ---
st.title("🚀 Zaawansowany System Magazynowy")

tab1, tab2, tab3 = st.tabs(["📋 Widok Magazynu", "➕ Dodaj Produkt", "📊 Statystyki"])

# --- TAB 1: LISTA PRODUKTÓW ---
with tab1:
    st.header("Aktualny stan zapasów")
    dane = pobierz_dane()
    
    if not dane:
        st.info("Brak towarów w bazie.")
    else:
        # Filtr kategorii
        kategorie = list(set([t['kategoria'] for t in dane if t['kategoria']]))
        wybrana_kat = st.multiselect("Filtruj wg kategorii", options=kategorie)
        
        for towar in dane:
            # Logika filtrowania
            if wybrana_kat and towar['kategoria'] not in wybrana_kat:
                continue
                
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
                c1.subheader(towar['nazwa'])
                c2.metric("Ilość", towar['ilosc'])
                c3.metric("Cena", f"{towar['cena']} zł")
                c4.write(f"🏷️ {towar['kategoria']}")
                
                if c5.button("🗑️", key=f"del_{towar['id']}"):
                    usun_towar(towar['id'])
                    st.rerun()

# --- TAB 2: FORMULARZ DODAWANIA ---
with tab2:
    st.header("Nowa dostawa")
    with st.form("form_dodaj", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        nazwa = col_a.text_input("Nazwa przedmiotu")
        kat = col_b.selectbox("Kategoria", ["Elektronika", "Spożywcze", "Dom", "Inne"])
        
        col_c, col_d = st.columns(2)
        ilosc = col_c.number_input("Ilość", min_value=0)
        cena = col_d.number_input("Cena netto", min_value=0.0)
        
        if st.form_submit_button("Zatwierdź i wyślij do bazy"):
            if nazwa:
                dodaj_towar(nazwa, ilosc, cena, kat)
                st.success(f"Zapisano {nazwa} w bazie danych!")
                st.rerun()
            else:
                st.error("Nazwa jest wymagana!")

# --- TAB 3: ANALITYKA ---
with tab3:
    st.header("Podsumowanie finansowe")
    if dane:
        total_value = sum(t['ilosc'] * t['cena'] for t in dane)
        total_items = sum(t['ilosc'] for t in dane)
        
        m1, m2 = st.columns(2)
        m1.metric("Łączna wartość magazynu", f"{total_value:,.2f} zł")
        m2.metric("Liczba wszystkich sztuk", total_items)
        
        # Prosty wykres
        import pandas as pd
        df = pd.DataFrame(dane)
        st.bar_chart(df.set_index('nazwa')['ilosc'])
