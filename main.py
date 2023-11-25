import streamlit as st

st.title("Pozdrav od Adel")

jmeno = st.text_input("Zadejte své jméno")
st.write(f"Ahoj {jmeno}, tady Adél")