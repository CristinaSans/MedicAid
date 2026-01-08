import streamlit as st
import sqlite3

st.set_page_config(page_title="Calculadora Insulina", page_icon="📝")
st.sidebar.header("Calculadora Insulina")

#funció
def calcula_insulina(glucosa, norm, alt, moltAlt):
    if glucosa < 89:
        msg = "Menja carbohidrats d'absorció ràpida i espera 30 minuts per tornar a calcular"
    elif 89 <= glucosa < 150:
        msg = f"Menja normalment i posa't {norm} d'insulina"
    elif 150 <= glucosa < 200:
        msg = f"Posa't {alt} d'insulina i menja normalment"
    elif glucosa >= 200:
        msg = f"Posa't {moltAlt} d'insulina i espera a que baixi per menjar normalment"
    else:
        msg = "Valor de glucosa no reconegut"
    return msg

#--- conecció BD
conn = sqlite3.connect("./dat/MedicAid.db")
c = conn.cursor()
# --- INTERFÍCIE STREAMLIT ---
st.header("Calculadora Insulina:")

glucosa = st.number_input("Glucosa: ")

usuari_options = c.execute("SELECT Id_usuari, Nom_user, Cognoms_user FROM Usuaris").fetchall()
nom_dict = {f"{nom} {cognoms}": uid for uid, nom, cognoms in usuari_options}

us_nom = st.selectbox("Selecciona usuari", list(nom_dict.keys()), key="us_select")

if us_nom:
    usuari_sel = nom_dict[us_nom]

    # --- Buscar Id_pauta relacionat amb l'usuari ---
    pauta_data = c.execute(""" SELECT P.Id_pauta, U.Nom_user, U.Cognoms_user, P.Si_alt, P.Si_moltAlt, P.Si_estable
        FROM Usuari_pauta P
        JOIN Usuaris U ON P.Id_usuari = U.Id_usuari WHERE U.Id_usuari = ? """, (usuari_sel,)).fetchone()

    if pauta_data:
        id_pauta, nom_user, cognoms_user, si_alt, si_moltAlt, si_estable = pauta_data

        # Guardar en variables
        alt = si_alt
        moltAlt = si_moltAlt
        norm = si_estable

    else:
        st.warning("Aquest usuari no té cap pauta registrada.")
else:
    st.warning("Has de seleccionar un usuari")
    
if st.button("Calcular"):
    
   st.write(calcula_insulina(glucosa,norm,alt,moltAlt))

    
