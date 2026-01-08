import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Usuaris", page_icon="👥")
st.sidebar.header("Usuaris")
#--- conecció BD
conn = sqlite3.connect("./dat/MedicAid.db")
c = conn.cursor()

# --- INTERFÍCIE STREAMLIT ---
menu_us= st.selectbox("Menú", ["Veure usuaris","Crear nou usuari", "Modificar usuari", "Borrar usuari"])
   
if menu_us == "Veure usuaris":
    
    st.subheader("Llista d'Usuaris")
    
    query = """
        SELECT u.Id_usuari,
               u.Nom_user,
               u.Cognoms_user,
               u.Edat_user,
        GROUP_CONCAT(m.Nom_malaltia, CHAR(10)) AS Malalties
        FROM Usuaris u
        LEFT JOIN Malalties_usuari mu ON u.Id_usuari = mu.Id_user
        LEFT JOIN Malalties m ON mu.Id_malaltia = m.Id_malaltia
        GROUP BY u.Id_usuari
    """
    rows = c.execute(query).fetchall()
        
    if rows:
        headers = ("Id","Nom","Cognoms","Edat","Malalties")
        df = pd.DataFrame(rows, columns=headers)
            
        # Mostrem amb salts de línia
        st.dataframe(df.style.set_properties(**{'white-space': 'pre-wrap'}),hide_index= True)
            
        st.write(f"Nombre d'usuaris: {len(rows)}")
    else:
        st.info("No hi ha usuaris")
            
elif menu_us == "Crear nou usuari":
        
        st.subheader("Crea un Nou Usuari")

        nom = st.text_input("Nom")
        cognoms = st.text_input("Cognoms")
        edat = st.number_input("Edat", min_value=0, max_value=120)
       
        # Selecció de malalties disponibles
        malalties_options = c.execute("SELECT Id_malaltia, Nom_malaltia FROM Malalties").fetchall()
        malalties_dict = {nom: mid for mid, nom in malalties_options}
        malalties_seleccionades = st.multiselect("Malalties", list(malalties_dict.keys()))
            
       
        if st.button("Crear usuari complet", key="crear_us_complet"):
            # Inserir usuari
            c.execute(
                "INSERT INTO Usuaris (Nom_user, Cognoms_user, Edat_user) VALUES (?, ?, ?)",
                (nom, cognoms, edat)
            )
            usuari_id = c.lastrowid

            # Inserir malalties associades
            for mal in malalties_seleccionades:
                mal_id = malalties_dict[mal]
                c.execute(
                    "INSERT INTO Malalties_usuari (Id_user, Id_malaltia) VALUES (?, ?)",
                    (usuari_id, mal_id)
                )
                
            conn.commit()
            st.success("Usuari creat correctament!")
                
elif menu_us == "Modificar usuari":

        st.subheader("Modifica Usuari Existent")
            
        # Selecció usuari
        usuaris = c.execute("SELECT Id_usuari, Nom_user || ' ' || Cognoms_user FROM Usuaris").fetchall()
        if usuaris:
            usuari_dict = {nom: uid for uid, nom in usuaris}
            usuari_nom = st.selectbox("Selecciona usuari", list(usuari_dict.keys()),key="usuari_select")
            usuari_id = usuari_dict[usuari_nom]
                
        # Carregar dades actuals
            query = c.execute("SELECT Nom_user, Cognoms_user, Edat_user FROM Usuaris WHERE Id_usuari=?", (usuari_id,)).fetchone()
            nom_actual, cognoms_actual, edat_actual = query
                
            nom = st.text_input("Nom", value=nom_actual)
            cognoms = st.text_input("Cognoms", value=cognoms_actual)
            edat = st.number_input("Edat", min_value=0, max_value=120, value=edat_actual)
                
        # Carregar malalties disponibles
            malalties_options = c.execute("SELECT Id_malaltia, Nom_malaltia FROM Malalties").fetchall()
            malalties_dict = {nom: mid for mid, nom in malalties_options}
                
        # Carregar malalties actuals de l’usuari
            malalties_user = c.execute("SELECT Id_malaltia FROM Malalties_usuari WHERE Id_user=?", (usuari_id,)).fetchall()
            malalties_user_ids = [mid for (mid,) in malalties_user]
            malalties_user_noms = [nom for nom, mid in malalties_dict.items() if mid in malalties_user_ids]
                
        # Multiselect amb les malalties
            malalties_seleccionades = st.multiselect("Malalties", list(malalties_dict.keys()), default=malalties_user_noms)
                
            if st.button("Actualitzar usuari"):
        # Actualitzar dades bàsiques
                 c.execute("UPDATE Usuaris SET Nom_user=?, Cognoms_user=?, Edat_user=? WHERE Id_usuari=?", (nom, cognoms, edat, usuari_id))
                    
        # Actualitzar malalties: esborrem totes i tornem a inserir les seleccionades
                 c.execute("DELETE FROM Malalties_usuari WHERE Id_user=?", (usuari_id,))
                 for mal in malalties_seleccionades:
                    mal_id = malalties_dict[mal]
                    c.execute("INSERT INTO Malalties_usuari (Id_user, Id_malatia) VALUES (?, ?)", (usuari_id, mal_id))
                    
                 conn.commit()
                 st.success("Usuari actualitzat correctament amb les noves malalties!")
        else:
            st.info("No hi ha usuaris per modificar")

elif menu_us == "Borrar usuari":
    
    st.subheader("Borra Usuari")
        
 # Selecció usuari
    usuaris = c.execute("SELECT Id_usuari, Nom_user || ' ' || Cognoms_user FROM Usuaris").fetchall()
    if usuaris:
        usuari_dict = {nom: uid for uid, nom in usuaris}
        usuari_nom = st.selectbox("Selecciona usuari a eliminar", list(usuari_dict.keys()),key="borraUser_select")
        usuari_id = usuari_dict[usuari_nom]
            
        if st.button("Eliminar usuari"):
    # Esborrem primer les malalties associades
            c.execute("DELETE FROM Malalties_usuari WHERE Id_user=?", (usuari_id,))
                
    # Esborrem medicació associada (si vols que també s’elimini)
            medicacions = c.execute("SELECT Id_Medicacio FROM Medicacio WHERE Id_usuari=?", (usuari_id,)).fetchall()
            for (mid,) in medicacions:
                c.execute("DELETE FROM Preses_medicacio WHERE Id_medicacio=?", (mid,))
                c.execute("DELETE FROM Medicacio WHERE Id_Medicacio=?", (mid,))
                
    # Finalment esborrem l’usuari
            c.execute("DELETE FROM Usuaris WHERE Id_usuari=?", (usuari_id,))
                
            conn.commit()
            st.success("Usuari i dades associades eliminats correctament!")
    else:

        st.info("No hi ha usuaris per eliminar")


