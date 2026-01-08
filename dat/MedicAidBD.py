import streamlit as st
import sqlite3
import os

def crear_taules():
    global conexion
    cursor = conexion.cursor()

    txt = """
    CREATE TABLE IF NOT EXISTS Usuaris(
    Id_usuari INTEGER  PRIMARY KEY AUTOINCREMENT ,
    Nom_user VARCHAR(25),
    Cognoms_user VARCHAR(30),
    Edat_user INTEGER,
    );
    
    CREATE TABLE IF NOT EXISTS Medicacio (
    Id_Medicacio INTEGER  PRIMARY KEY AUTOINCREMENT,
    Id_usuari INTEGER,
    Id_farmac INTEGER,
    FOREIGN KEY (Id_usuari) REFERENCES Usuaris(Id_usuari),
    FOREIGN KEY (Id_farmac) REFERENCES Farmacs(Id_farmac)
    FOREIGN KEY (Tipus_med) REFERENCES Tipus_medicacio(Id_tipus)
    );
    
    CREATE TABLE IF NOT EXISTS Preses_medicacio(
    Num_presa INTEGER AUTOINCREMENT,
    Id_medicacio INTEGER,
    Horari_presa VARCHAR (100)
    PRIMARY KEY (Num_presa,Id_medicacio ),
    FOREIGN KEY (Id_medicacio) REFERENCES Medicacio(Id_medicacio)
    );
    
    CREATE TABLE IF NOT EXISTS Preses_medicacio (
    Num_presa    INTEGER,
    Id_medicacio INTEGER,
    Horari_presa VARCHAR (100),
    PRIMARY KEY (
        Num_presa,
        Id_medicacio
    ),
    FOREIGN KEY (
        Id_medicacio
    )
    REFERENCES Medicacio (Id_medicacio)
    
);

    CREATE TABLE IF NOT EXISTS Malalties (
    Id_malaltia CHAR(2) PRIMARY KEY,
    Nom_malaltia VARCHAR(30)
    );
    CREATE TABLE IF NOT EXISTS Farmacs(
    Id_farmac INTEGER AUTOINCREMENT PRIMARY KEY,
    Nom_farmac VARCHAR(50),
    Dosi_farmac INTEGER,
    Preses INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS Malalties_usuari(
    Id_user INTEGER,
    Id_malatia INTEGER,
    PRIMARY KEY (
        Id_user,
        Id_malaltia
    ),
    FOREIGN KEY (Id_user)REFERENCES Usuaris(Id_usuari),
    FOREIGN KEY (Id_malatia)REFERENCES Malalties (Id_malaltia)
    );
    
    CREATE TABLE IF NOT EXISTS Usuari_pauta(
    Id_pauta INTEGER AUTOINCREMENT PRIMARY KEY,
    Id_usuari INTEGER,
    Si_moltAlt INTEGER,
    Si_alt INTEGER,
    Si_estable INTEGER
    );

    """
    cursor.executescript(txt)
    conexion.commit()


def obrir_bd():
    global conexion
    try:
        file_name = "./dat/MedicAid.bd"
        if os.path.isfile(file_name):
            print("existeix")
            conexion = sqlite3.connect(file_name)
        else:
            print("File does not exist.")
            conexion = sqlite3.connect(file_name)
            crear_taules()
    except Exception as e:
        print("No puc crear la base de dades", e)
        

if __name__ == "__main__":
    print("This script is running directly.")
    obrir_bd()
    
