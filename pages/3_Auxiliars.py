import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Auxiliars", page_icon="📝")
st.sidebar.header("Auxiliars")

#--- conecció BD
conn = sqlite3.connect("./dat/MedicAid.db")
c = conn.cursor()

# --- INTERFÍCIE STREAMLIT ---
tab1, tab2,tab3,tab4 = st.tabs(["Fàrmacs","Tipus medicació", "Malalties","Pautes"])

with tab1:
    menu_farmacs= st.selectbox("Menú", ["Veure fàrmacs","Afegir fàrmac", "Modificar fàrmac", "Borrar fàrmac"])
    
    if menu_farmacs == "Veure fàrmacs":
                 
        st.subheader("Llista Fàrmacs")
            
        rows = c.execute("SELECT * FROM Farmacs").fetchall()
        if rows:
            headers = ("Id","Nom","Tipus","Dosis","Preses")
            data = [list(row) for row in rows]
            df = pd.DataFrame(data, columns=headers)
            st.dataframe(df,hide_index= True)
            st.write(f"Nombre de fàrmacs: {len(rows)}")
        else:
            st.info("No hi ha fàrmacs")
                
    if menu_farmacs == "Afegir fàrmac":
        
        st.subheader("Afegir Fàrmacs")
             
        nom_farm = st.text_input("Nom fàrmac: ")
        tipus_options = c.execute("SELECT Id_tipus, Nom_tipus FROM Tipus_medicacio").fetchall()
        tipus_dict = {nom: codi for codi, nom in tipus_options}
        tipus_nom = st.selectbox("Tipus de medicació", list(tipus_dict.keys()),key="Tipus_select")
        codi_tipus = tipus_dict[tipus_nom]
        dosi = st.text_input("Dosi fàrmac:")
        num_preses= st.number_input("Nº preses: ")

        if st.button("Afegir fàrmac"):
            c.execute("""INSERT INTO Farmacs(Nom_farmac, Tipus_farmac, Dosi_farmac, Preses ) 
                        VALUES (?, ?, ?, ?)""",(nom_farm,codi_tipus, dosi,num_preses))
            conn.commit()
                
            st.success("Fàrmac afegit correctament!")
                     
    elif menu_farmacs == "Modificar fàrmac":
        
        st.subheader("Modificar Fàrmacs")
                # --- Seleccionar el fàrmac a modificar ---
        farmacs_options = c.execute("SELECT Id_farmac, Nom_farmac, Tipus_farmac, Dosi_farmac, Preses FROM Farmacs").fetchall()
        farmacs_dict = {nom: fid for fid, nom, tipus, dosi, preses in farmacs_options}

        farmac_nom_sel = st.selectbox("Selecciona el fàrmac a modificar", list(farmacs_dict.keys()), key="farmac_mod_select")
        farmac_id = farmacs_dict[farmac_nom_sel]

        # Obtenir dades actuals del fàrmac seleccionat
        farmac_data = c.execute(
            "SELECT Nom_farmac, Tipus_farmac, Dosi_farmac, Preses FROM Farmacs WHERE Id_farmac = ?",
            (farmac_id,)
        ).fetchone()

        nom_actual, tipus_actual, dosi_actual, preses_actual = farmac_data

        # --- Inputs amb valors actuals ---
        nom_farm = st.text_input("Nou nom fàrmac:", value=nom_actual)

        tipus_options = c.execute("SELECT Id_tipus, Nom_tipus FROM Tipus_medicacio").fetchall()
        tipus_dict = {nom: codi for codi, nom in tipus_options}

        # Trobar el nom del tipus actual
        tipus_nom_actual = c.execute("SELECT Nom_tipus FROM Tipus_medicacio WHERE Id_tipus = ?", (tipus_actual,)).fetchone()[0]

        tipus_nom = st.selectbox("Nou tipus de medicació", list(tipus_dict.keys()), index=list(tipus_dict.keys()).index(tipus_nom_actual), key="Tipus_mod_select")
        codi_tipus = tipus_dict[tipus_nom]

        dosi = st.text_input("Nova dosi fàrmac:", value=dosi_actual)
        num_preses = st.number_input("Nou nº preses:", min_value=0, value=preses_actual)

        # --- Botó per modificar ---
        if st.button("Modificar fàrmac", key="modificar_farmac"):
            c.execute(
                """UPDATE Farmacs 
                   SET Nom_farmac = ?, Tipus_farmac = ?, Dosi_farmac = ?, Preses = ?
                   WHERE Id_farmac = ?""",
                (nom_farm, codi_tipus, dosi, num_preses, farmac_id)
            )
            conn.commit()
            st.success("Fàrmac modificat correctament!")
            
    elif menu_farmacs == "Borrar fàrmac":
        
        st.subheader("Borrar Fàrmacs")
        
        farmacs_options = c.execute("SELECT Id_farmac, Nom_farmac FROM Farmacs").fetchall()
        farmacs_dict = {nom: fid for fid, nom in farmacs_options}

        farmac_nom_sel = st.selectbox("Selecciona el fàrmac a eliminar", list(farmacs_dict.keys()), key="farmac_del_select")
        farmac_id = farmacs_dict[farmac_nom_sel]

        # --- Botó per eliminar ---
        if st.button("Eliminar fàrmac", key="eliminar_farmac"):
            c.execute("DELETE FROM Farmacs WHERE Id_farmac = ?", (farmac_id,))
            conn.commit()
            st.success(f"Fàrmac '{farmac_nom_sel}' eliminat correctament!")

with  tab2:
        
    menu_tipus= st.selectbox("Menú", ["Veure tipus de medicació","Afegir tipus", "Borrar tipus"])
            
    if menu_tipus == "Veure tipus de medicació":
            
        st.subheader("Llista Tipus")
            
        rows = c.execute("SELECT * FROM Tipus_medicacio").fetchall()
        if rows:
            headers = ("Id tipus","Nom")
            data = [list(row) for row in rows]
            df = pd.DataFrame(data, columns=headers)
            st.dataframe(df,hide_index= True)
            st.write(f"Nombre de tipus: {len(rows)}")
        else:
            st.info("No hi ha tipus guardats")
                
    elif menu_tipus =="Afegir tipus":

        st.subheader("Afegir Tipus")

        nom_tipus = st.text_input("Nom tipus: ")

        if st.button("Afegir Tipus"):
            c.execute("""INSERT INTO Tipus_medicacio(Nom_tipus) VALUES (?)""", (nom_tipus,))
            conn.commit()
            
            st.success("Tipus afegit correctament!")

    elif menu_tipus == "Borrar tipus":

        st.subheader("Borrar Tipus")

        tipus_options = c.execute("SELECT Id_tipus, Nom_tipus FROM Tipus_medicacio").fetchall()
        tipus_dict = {nom: codi for codi, nom in tipus_options}
        tipus_nom = st.selectbox("Tipus de medicació", list(tipus_dict.keys()),key="Borra_tipus")
        codi_tipus = tipus_dict[tipus_nom]
        
        if st.button('Borrar tipus'):
            c.execute("""DELETE  CREATE TABLE IF NOT EXISTS Usuari_pauta(
            Id_pauta INTEGER AUTOINCREMENT PRIMARY KEY,
            Id_usuari INTEGER,
            Si_moltAlt INTEGER,
            Si_alt INTEGER,
            Si_estable INTEGER
            );
            FROM Tipus_medicacio WHERE Id_tipus= ?""", (codi_tipus,))
            conn.commit()
            st.success("Tipus eliminat")
                    
with tab3:
        
    menu_malalties= st.selectbox("Menú", ["Veure malalties","Afegir malaltia", "Borrar malaltia"])
    
    if menu_malalties == "Veure malalties":
        
        st.subheader("Llista Malalties")
        
        rows = c.execute("SELECT * FROM Malalties").fetchall()
        if rows:
            headers = ("Id","Nom")
            data = [list(row) for row in rows]
            df = pd.DataFrame(data, columns=headers)
            st.dataframe(df,hide_index= True)
            st.write(f"Nombre de malalties: {len(rows)}")
        else:
            st.info("No hi ha dades")
            
    elif menu_malalties == "Afegir malaltia":
        
        st.subheader("Afegir Malalties")
        
        codi_mal= st.text_input("Identificador: ")
        nom_mal= st.text_input("Nom tipus: ")
            
        if st.button("Afegir malaltia"):
            try:
                c.execute("""INSERT INTO Malalties (Id_malaltia,Nom_malaltia) VALUES (?,?)""", (codi_mal,nom_mal,))
                conn.commit()
                    
                st.success("Malaltia afegida correctament!")
            except:
                st.warning("Id malaltia ya existeix")
    elif menu_malalties == "Borrar malaltia":
        
        st.subheader("Borrar Malalties")
            
        mal_options = c.execute("SELECT Id_malaltia, Nom_malaltia FROM Malalties").fetchall()
        mal_dict = {nom: codi for codi, nom in mal_options}
        mal_nom = st.selectbox("Malalties", list(mal_dict.keys()))
        if mal_nom:
            codi_mal = mal_dict[mal_nom]
        else:
            st.warning("Has de seleccionar malaltia")
                
        if st.button('Borrar Malaltia'):
            c.execute("""DELETE FROM Malalties WHERE Id_malaltia= ?""", (codi_mal,))
            conn.commit()
            st.success("Malaltia eliminada")
            
with tab4:
    
    menu_pauta = st.selectbox("Menú Pautes", ["Veure pautes","Afegir pauta", "Modificar pauta", "Borrar pauta"])

    if menu_pauta == "Veure pautes":
        
        st.subheader("Llista Pautes")
        
        rows = c.execute("SELECT * FROM Usuari_pauta").fetchall()
        
        if rows:
            headers = ("Id_pauta","Id_usuari","Si_moltAlt","Si_alt","Si_estable")
            data = [list(row) for row in rows]
            df = pd.DataFrame(data, columns=headers)
            st.dataframe(df, hide_index= True)
            st.write(f"Nombre de pautes: {len(rows)}")
        else:
            st.info("No hi ha pautes")
            
    elif menu_pauta == "Afegir pauta":
        
        st.subheader("Afegir Pautes")
        # --- Seleccionar usuari existent ---
        usuaris_options = c.execute("SELECT Id_usuari, Nom_user FROM Usuaris").fetchall()
        usuaris_dict = {nom: uid for uid, nom in usuaris_options}

        usuari_nom = st.selectbox("Selecciona usuari", list(usuaris_dict.keys()), key="usuari_add_select")
        id_usuari = usuaris_dict[usuari_nom]

        si_moltAlt = st.number_input("Si molt alt:", min_value=0)
        si_alt = st.number_input("Si alt:", min_value=0)
        si_estable = st.number_input("Si estable:", min_value=0)

        if st.button("Afegir pauta"):
            c.execute("""INSERT INTO Usuari_pauta(Id_usuari, Si_moltAlt, Si_alt, Si_estable) 
                         VALUES (?, ?, ?, ?)""",(id_usuari, si_moltAlt, si_alt, si_estable))
            conn.commit()
            st.success("Pauta afegida correctament!")

    elif menu_pauta == "Modificar pauta":
        
        st.subheader("Modifica Pautes")
        
        pautes_options = c.execute("""
            SELECT p.Id_pauta, u.Nom_user 
            FROM Usuari_pauta p
            JOIN Usuaris u ON p.Id_usuari = u.Id_usuari""").fetchall()

        pautes_dict = {f"{nom} - Pauta {pid}": pid for pid, nom in pautes_options}

        pauta_sel = st.selectbox("Selecciona la pauta a modificar", list(pautes_dict.keys()), key="pauta_mod_select")
        pauta_id = pautes_dict[pauta_sel]

        pauta_data = c.execute(
            "SELECT Id_usuari, Si_moltAlt, Si_alt, Si_estable FROM Usuari_pauta WHERE Id_pauta = ?",
            (pauta_id,)
        ).fetchone()

        id_actual, moltAlt_actual, alt_actual, estable_actual = pauta_data

        # Mostrem l’usuari però no es pot modificar
        usuari_nom = c.execute("SELECT Nom_user FROM Usuaris WHERE Id_usuari = ?", (id_actual,)).fetchone()[0]
        st.info(f"Usuari assignat: {usuari_nom} (Id: {id_actual})")

        # Inputs només per les variables modificables
        si_moltAlt = st.number_input("Nou Si molt alt:", min_value=0, value=moltAlt_actual)
        si_alt = st.number_input("Nou Si alt:", min_value=0, value=alt_actual)
        si_estable = st.number_input("Nou Si estable:", min_value=0, value=estable_actual)

        if st.button("Modificar pauta", key="modificar_pauta"):
            c.execute(
                """UPDATE Usuari_pauta 
                   SET Si_moltAlt = ?, Si_alt = ?, Si_estable = ?
                   WHERE Id_pauta = ?""",
                (si_moltAlt, si_alt, si_estable, pauta_id)
            )
            conn.commit()
            st.success("Pauta modificada correctament!")


    elif menu_pauta == "Borrar pauta":
        
        st.subheader("Borra Pautes")
        
        # --- Obtenir pautes amb usuari associat ---
        pautes_options = c.execute("""
            SELECT p.Id_pauta, u.Nom_user 
            FROM Usuari_pauta p
            JOIN Usuaris u ON p.Id_usuari = u.Id_usuari
        """).fetchall()

        # Diccionari amb format "Usuari Nom - Pauta Id"
        pautes_dict = {f"{nom} - Pauta {pid}": pid for pid, nom in pautes_options}

        pauta_sel = st.selectbox("Selecciona la pauta a eliminar", list(pautes_dict.keys()), key="pauta_del_select")
        pauta_id = pautes_dict[pauta_sel]

        if st.button("Eliminar pauta", key="eliminar_pauta"):
            c.execute("DELETE FROM Usuari_pauta WHERE Id_pauta = ?", (pauta_id,))
            conn.commit()
            st.success(f"Pauta '{pauta_sel}' eliminada correctament!")




