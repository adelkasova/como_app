import streamlit as st
from bucket_list.connector import Connector
import requests
from datetime import datetime
from PIL import Image

#iconka = Image.open("Ikonka/Bucket_list_iconka_60x60.png")

st.set_page_config(page_title="Bucket List by Adél", page_icon ="Ikonka/Bucket_list_iconka_60x60.png")



pocatecni_datum = datetime.strptime("01.01.1923", "%d.%m.%Y")

databaze = Connector(user="adela", password="wfzEjLk36X3aJc64!b+F",host="199.247.2.123",port="3306",database="adela_como")

prihlasovaci_udaje= databaze.ziskat_vsechny_uzivatele()


#Výběr Registrace nebo Přihlášení

if "prihlasen" not in st.session_state:
    st.session_state["prihlasen"] = False

if "jmeno" not in st.session_state:
    st.session_state["jmeno"] = None



#Nadpsi na střed
st.markdown(
    """
    <div style="text-align: center">
        <h1> BUCKET LIST 📝 </h1>
    </div>
    """,
    unsafe_allow_html=True
)

if not st.session_state["prihlasen"]:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("Registrovat se")
    with col2:
        registr_nebo_prihlasit = st.toggle("")
    with col3:
        st.markdown("""
                    <div style = "text-align:right">
                    Přihlásit se
                    """, unsafe_allow_html = True)

    #Registrační formulář
    if not registr_nebo_prihlasit:

        registracni_formular = st.form("registr", clear_on_submit=True)
        with registracni_formular:
            st.subheader(":pushpin: Registrovat se")
            jmeno = st.text_input("Zadej své přihlašovací jméno")
            heslo = st.text_input("Zadej své heslo", type="password")
            datum_narozeni =  st.date_input ("Zadej svůj datum narození", format="DD/MM/YYYY", min_value=pocatecni_datum )

            registrovat_se  = st.form_submit_button("Registrovat se")


        if registrovat_se:
            if jmeno == "" or heslo == "":
                st.warning(":warning: Vyplňte jméno a heslo!")
            elif not prihlasovaci_udaje.loc[prihlasovaci_udaje["jmeno"]==jmeno].empty:
                st.warning(":warning: Jméno je již obsazené!")
            else:
                databaze.pridat_uzivatele(jmeno=jmeno,heslo=heslo, datum_narozeni=datum_narozeni)


    #Přihlašovací formulář
    if registr_nebo_prihlasit:

        prihlasovaci_formular = st.form("form", clear_on_submit=True)
        with prihlasovaci_formular:
            st.subheader(":pushpin: Přihlásit se")
            jmeno = st.text_input("Zadej své přihlašovací jméno")
            heslo = st.text_input("Zadej své heslo", type="password")

            prihlasit = st.form_submit_button("Přihlásit se",)
        

        if prihlasit:
            if jmeno == "" or heslo == "":
                st.warning(":warning: Vyplňte jméno a heslo!")
            udaje_uzivatele = prihlasovaci_udaje.loc[prihlasovaci_udaje["jmeno"]== jmeno]
            if not udaje_uzivatele.empty: 
                heslo_uzivatele = udaje_uzivatele.loc[udaje_uzivatele["heslo"]== heslo]
                if not heslo_uzivatele.empty:
                    st.session_state["jmeno"] = jmeno
                    st.session_state["prihlasen"] = True
                    st.rerun()
                else: 
                    st.error(":x: Špatné heslo!")
            else:
                st.error(":x: Jméno nenalezeno!")

#Kategorie

if st.session_state["prihlasen"]:

        
    st.header(f"Vítej {st.session_state['jmeno']}, zde máš možnost sestavit si svůj Bucket List.") 
    st.subheader ("A co je to vlastně ten Bucket list?")     
    st.caption("To je seznam věcí, co si můžeš splnit než zaplepeš bačkorami. :zombie:")


    st.header("Inspirace pro tvůj Bucket List! :pencil:")
    st.caption("Tady najdeš různé kategorie a tipy na úkoly, co by tvůj Bucket list mohl obsahovat, ale fantazii se meze nekladou!")

    moje_ukoly, pridani_ukolu = st.tabs(["Moje úkoly", "Přidat vlastní úkol"])

    with moje_ukoly:
            
        kategorie = databaze.ziskat_kategorie_ukolu()
        kategorie_ukolu = st.selectbox("", options=kategorie, index=None, placeholder="Vyber si svou kategorii")


    #Úkoly
        pridane_ukoly_uzivatele = databaze.ziskat_splnene_ukoly()                    
        pridane_ukoly_uzivatele = pridane_ukoly_uzivatele.loc[pridane_ukoly_uzivatele["jmeno"] == st.session_state['jmeno']]
        vybrane_ukoly_uzivatele = pridane_ukoly_uzivatele.loc[:,"ukol"].to_list()


        if kategorie_ukolu:
            ukol = databaze.ziskat_nazvy_ukolu_podle_kategorie(kategorie=kategorie_ukolu)
            for vybrany_ukol in vybrane_ukoly_uzivatele:
                try:
                    ukol.remove(vybrany_ukol)
                except:
                    pass

            muj_ukol = st.selectbox("", options=ukol, index=None, placeholder="Vyber si svůj úkol")

    #nový úkol - svůj vlastní
            

            pridat_ukol = st.button("Přidat úkol", use_container_width = True)
        

        #Vybrané úkoly

            if pridat_ukol:
                aktualni_datum = datetime.now().date()
                databaze.pridat_splneny_ukol(jmeno=st.session_state["jmeno"], kategorie=kategorie_ukolu, ukol=muj_ukol, splneno=False, datum=aktualni_datum)
                st.success(":shamrock: Úkol byl přidán na tvůj Bucket List!")
                st.rerun()

        #Bucket list
        


        tabulka_bl = st.data_editor(pridane_ukoly_uzivatele, hide_index = True, disabled = ["jmeno", "kategorie", "ukol"],
                    column_config = {
                        "jmeno": None,
                        "kategorie": st.column_config.TextColumn("Kategorie"),
                        "ukol": st.column_config.TextColumn("Úkol"),
                        "splneno": st.column_config.CheckboxColumn("Splněno"),
                        "datum": st.column_config.DateColumn("Datum splnění"),
                        "poznamka": st.column_config.TextColumn("Poznámka")
                    }, use_container_width = True)


        
        ulozit_tabulku = st.button("Uložit", use_container_width = True)
        
        if ulozit_tabulku:
            databaze.upravit_tabulku_splnene_ukoly(tabulka_bl)
            st.success(":shamrock: Bucket List byl uložen!")

    with pridani_ukolu:
        kategorie = databaze.ziskat_kategorie_ukolu()
        kategorie_ukolu = st.selectbox("", options=kategorie, index=None, placeholder="Vyber si svou kategorii", key="new")

        vlastni_ukol = st.text_input("Zadej svůj úkol")

        pridat_vlastni_ukol = st.button("Přidat vlastni úkol", use_container_width = True)

        if pridat_vlastni_ukol:
            databaze.pridat_ukol(kategorie=kategorie_ukolu, ukol=vlastni_ukol, cas=None)
            st.success(":shamrock: Vlastní úkol byl uložen!")       
            
        

