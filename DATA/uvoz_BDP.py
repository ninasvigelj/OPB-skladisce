import psycopg2
import pandas  as pd
from re import sub
# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) 

import auth_public

database = auth_public.db
host = auth_public.host
port = auth_public.port
user = auth_public.user
password = auth_public.password

# Ustvarimo povezavo
conn = psycopg2.connect(database=database, host=host, 
                        port=port, user=user, password=password)

# Iz povezave naredimo cursor, ki omogoča
# zaganjanje ukazov na bazi

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def ustvari_tabelo(ime_tabele : str) -> None:   # da poveš pythonu kakšni tipi so vhodi in kakšen tip naj funkcija vrne
    """
    Funkcija pobriše in na novo ustvari tabelo o podatkih strank.
    """
    cur.execute(f"""
        DROP table if exists {ime_tabele};
        CREATE table if not exists  {ime_tabele}(            
            regija_id integer,
            leto integer,
            BDP integer,
            PRIMARY KEY (regija_id, leto)
        );
    """)
    conn.commit()

# drop mamo samo zato, da lahko še enkrat poženemo

def preberi_csv(ime_datoteke : str) -> pd.DataFrame:
    df = pd.read_csv(ime_datoteke, 
                    sep=';',             # ali ',' – preveri ročno v datoteki!
                    encoding='windows-1250',    # če to ne dela, poskusi 'latin1' ali 'windows-1250'
                    skiprows=1  )
    return df

def transformiraj(df: pd.DataFrame) -> pd.DataFrame:
    """Naredi tabelo s stolpci leto, regija, bdp.
    """
    # Omejimo se na ustrezne stolpce
    df = df.drop(columns=['MERITVE'])
    print(df)
    col = ["STATISTIČNA REGIJA"] + [f"{leto}" for leto in range(2008, 2024)]
    
    df = df[col]
    df = df.rename(columns={'STATISTIČNA REGIJA': 'regija'})

    # Pretvorimo 
    df_trans = df.melt(id_vars="regija", var_name="leto", value_name="bdp")

    df_trans = df_trans[df_trans["regija"] != "SLOVENIJA"]
    return df_trans

def zapisi_df(df: pd.DataFrame) -> None:

    ime_tabele = "fact_BDP_regije"

    # Poskrbimo, da tabela obstaja
    ustvari_tabelo(ime_tabele)
    
    # Če DataFrame nima stolpca 'Index', ga dodamo iz indeksa
    #df = df.reset_index()

    # Transformiramo podatke v DataFrame-u
    df = transformiraj(df)

    # Naloži dim_regije za mapping regija -> regija_id
    cur.execute("SELECT regija_id, regija FROM dim_regije;")
    regije = cur.fetchall()
    df_regije = pd.DataFrame(regije, columns=["regija_id", "regija"])
    
    # Združi da dobiš regija_id
    df = df.merge(df_regije, on="regija", how="left")
    
    # Preveri, če manjka kak regija
    if df["regija_id"].isnull().any():
        missing = df[df["regija_id"].isnull()]["regija"].unique()
        raise ValueError(f"Nekatere regije niso bile najdene v dim_regije: {missing}")

    # Odstrani ime regije, saj v bazi shranjujemo samo id
    df = df.drop(columns=["regija"])

      # Pravilno zaporedje stolpcev za vnos v bazo
    df = df[["regija_id", "leto", "bdp"]]
    
    # shranimo stolpce v seznam
    columns = df.columns.tolist()

    # Pretvorimo podatke v seznam tuple-ov
    records = df.values.tolist()    #records je uvistvu seznam seznamov
    
    # Pripravimo SQL ukaz za vstavljanje podatkov
    sql = f"INSERT INTO {ime_tabele} ({', '.join(columns)}) VALUES %s"
    
    # Uporabimo execute_values za množični vnos
    # Izvede po en insert ukaz na vrstico oziroma record iz seznama records
    # V odzadju zadeva deluje precej bolj optimlano kot en insert na ukaz!
    # Za množičen vnos je potrebno uporabiti psycopg2.extras.execute_values
    psycopg2.extras.execute_values(cur, sql, records)
    
    # Potrdimo spremembe v bazi
    conn.commit()


if __name__ == "__main__":
    df = preberi_csv(r"C:\Users\laraj\OneDrive - Univerza v Ljubljani\semester 6\OPB\projektna naloga\OPB-skladisce\DATA\csv_datoteke\bdp_cel.csv")

    zapisi_df(df)
    
    print("CSV datoteka je bila uspešno zabeležena v bazi.")
