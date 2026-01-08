import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Medicacio", page_icon="📈")
st.sidebar.header("Medicacio")

#--- conecció BD
conn = sqlite3.connect("./dat/MedicAid.db")
c = conn.cursor()

# --- INTERFÍCIE STREAMLIT ---
menu_med= st.selectbox("Menú", ["Veure pla de medicació","Afegir medicació", "Modificar medicació", "Borrar medicació"])

if menu_med == "Veure pla de medicació":
    
    st.subheader("Pla de Medicació")
        # --- Seleccionar usuari ---
    usuari_options = c.execute("SELECT Id_usuari, Nom_user, Cognoms_user FROM Usuaris").fetchall()
    nom_dict2 = {f"{nom} {cognoms}": codi for codi, nom, cognoms in usuari_options}

    us_nom2 = st.selectbox("Selecciona usuari", list(nom_dict2.keys()), key="usuari_select")
    if us_nom2:
        usuari_sel = nom_dict2[us_nom2]

        # --- Recuperar totes les medicacions de l’usuari ---
        medicacions = c.execute("""
            SELECT M.Id_medicacio, F.Nom_farmac, M.Preses_med, P.Horari_presa
            FROM Medicacio M
            JOIN Farmacs F ON M.Id_farmac = F.Id_farmac
            LEFT JOIN Preses_medicacio P ON M.Id_medicacio = P.Id_medicacio
            WHERE M.Id_usuari = ?
            ORDER BY M.Id_medicacio, P.Num_presa
        """, (usuari_sel,)).fetchall()

        if medicacions:
            # Convertir a DataFrame per mostrar en taula
            df = pd.DataFrame(medicacions, columns=["Id_medicacio", "Fàrmac", "Preses", "Horari"])
            st.dataframe(df, hide_index= True)
        else:
            st.info("Aquest usuari no té cap medicació registrada.")
    else:
        st.warning("Has de seleccionar un usuari")
    
if menu_med == "Afegir medicació":
    
    st.subheader("Afegir Medicacions")
        
    # Selecció d'usuari
    usuari_options = c.execute("SELECT Id_usuari, Nom_user, Cognoms_user FROM Usuaris").fetchall()
    nom_dict2 = {f"{nom} {cognoms}": codi for codi, nom, cognoms in usuari_options}
    us_nom2 = st.selectbox("Usuari", list(nom_dict2.keys()))
    
    if us_nom2:
        usuari_sel = nom_dict2[us_nom2]
    else:
        st.warning("Has de seleccionar un usuari")
        
     # Selecció de fàrmac
    farmac_options = c.execute("SELECT Id_farmac, Nom_farmac FROM Farmacs").fetchall()
    farmac_dict = {nom: codi for codi, nom in farmac_options}

    farmac_nom = st.selectbox("Fàrmac", list(farmac_dict.keys()), key="farmac_select")

    if farmac_nom:
        farmac = farmac_dict[farmac_nom]
        nom_med = c.execute("SELECT Nom_farmac FROM Farmacs WHERE Id_farmac = ?", (farmac,)).fetchone()[0]
        st.write(f"Fàrmac seleccionat: {nom_med}")
        preses_default = c.execute("SELECT Preses FROM Farmacs WHERE Id_farmac = ?", (farmac,)).fetchone()[0]
    else:
        st.warning("Has de seleccionar un fàrmac")
        preses_default = 0

    # Camps addicionals
    num_preses = st.number_input("Nº preses:", min_value=0, value=preses_default)
    horari_preses = st.text_input("Hora preses:", placeholder="HH:MM; HH:MM")

    # Inserció
    if st.button("Afegir Medicació"):

        # Inserir a Medicacio
        c.execute(
            """INSERT INTO Medicacio (Id_usuari, Id_farmac, Preses_med) 
               VALUES (?, ?, ?)""",
            (usuari_sel, farmac, num_preses))
        
        id_medicacio = c.lastrowid

        # Inserir a Preses_medicacio
        horaris = [h.strip() for h in horari_preses.split(";") if h.strip()]
        for idx, hora in enumerate(horaris, start=1):
            c.execute(
                """INSERT INTO Preses_medicacio (Id_medicacio, Num_presa, Horari_presa) 
                   VALUES (?, ?, ?)""",
                (id_medicacio, idx, hora)
            )

        conn.commit()
        st.success("Medicació i preses afegides correctament!")
            
elif menu_med == "Modificar medicació":
    
    st.subheader("Modificar Medicacions")
    
    # Selecció de medicació existent
    medicacions = c.execute("""
        SELECT m.Id_Medicacio, u.Nom_user || ' ' || u.Cognoms_user AS Usuari, f.Nom_farmac
        FROM Medicacio m
        JOIN Usuaris u ON m.Id_usuari = u.Id_usuari
        JOIN Farmacs f ON m.Id_farmac = f.Id_farmac
    """).fetchall()
        
    if medicacions:
        medic_dict = {f"{usuari} - {farmac}": mid for mid, usuari, farmac in medicacions}
        medic_nom = st.selectbox("Selecciona medicació", list(medic_dict.keys()))
        medic_id = medic_dict[medic_nom]
            
            # Obtenir dades actuals
        info = c.execute("""
            SELECT f.Nom_farmac, f.Preses, GROUP_CONCAT(p.Horari_presa, ',')
            FROM Medicacio m
            JOIN Farmacs f ON m.Id_farmac = f.Id_farmac
            LEFT JOIN Preses_medicacio p ON m.Id_Medicacio = p.Id_medicacio
            WHERE m.Id_Medicacio = ?
            GROUP BY m.Id_Medicacio""", (medic_id,)).fetchone()
            
        if info:
            nom_farmac, preses_actuals, horaris_actuals = info
            st.write(f"Fàrmac actual: {nom_farmac}")
                
                # Nombre de preses editable
            num_preses = st.number_input("Nombre de preses", min_value=1, value=preses_actuals)
                
                # Horaris actuals
            horaris_llista = horaris_actuals.split(",") if horaris_actuals else []
            horaris_nous = []
            for i in range(num_preses):
                valor = horaris_llista[i] if i < len(horaris_llista) else "08:00"
                hora = st.text_input(f"Hora presa {i+1}", value=valor)
                horaris_nous.append(hora)
                
            if st.button("Actualitzar medicació"):
                    # Esborrem horaris antics
                c.execute("DELETE FROM Preses_medicacio WHERE Id_medicacio=?", (medic_id,))
                
                # Inserim nous horaris
                for idx, h in enumerate(horaris_nous, start=1):
                    c.execute("INSERT INTO Preses_medicacio (Num_presa, Id_medicacio, Horari_presa) VALUES (?, ?, ?)", (idx, medic_id, h))
                
                # Actualitzem nombre de preses
                c.execute("UPDATE Medicacio SET Id_farmac = Id_farmac WHERE Id_Medicacio=?", (medic_id,))
                # Nota: si vols permetre canviar el fàrmac, afegeix un selectbox de fàrmacs i actualitza Id_farmac aquí
                
                conn.commit()
                st.success("Medicació actualitzada correctament!")
    else:
        st.info("No hi ha medicacions per modificar")
        
elif menu_med == "Borrar medicació":
    
    st.subheader("Borra Medicacions")
    
    # Selecció de medicació existent
    medicacions = c.execute("""
        SELECT m.Id_Medicacio, u.Nom_user || ' ' || u.Cognoms_user AS Usuari, f.Nom_farmac
        FROM Medicacio m
        JOIN Usuaris u ON m.Id_usuari = u.Id_usuari
        JOIN Farmacs f ON m.Id_farmac = f.Id_farmac
    """).fetchall()
    
    if medicacions:
        medic_dict = {f"{usuari} - {farmac}": mid for mid, usuari, farmac in medicacions}
        medic_nom = st.selectbox("Selecciona medicació a eliminar", list(medic_dict.keys()),key="borraMed_select")
        medic_id = medic_dict[medic_nom]
        
        if st.button("Eliminar medicació"):
            # Esborrem primer les preses associades
            c.execute("DELETE FROM Preses_medicacio WHERE Id_medicacio=?", (medic_id,))
            # Esborrem la medicació
            c.execute("DELETE FROM Medicacio WHERE Id_Medicacio=?", (medic_id,))
            conn.commit()
            st.success("Medicació eliminada correctament!")
    else:
        st.info("No hi ha medicacions per eliminar")

