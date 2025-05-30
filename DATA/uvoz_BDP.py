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
            leto integer,
            BDP integer,
            regija text,
            PRIMARY KEY (regija, leto)
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
    """Naredi tabelo s stolci leto, regija, bdp.
    """
    # Omejimo se na ustrezne stolpce
    df = df.drop(columns=['MERITVE'])
    col = ["STATISTIČNA REGIJA"] + [f"{leto}" for leto in range(2008, 2024)]
    
    print("Obstoječi stolpci v df:", df.columns.tolist())
    df = df[col]
    df = df.rename(columns={'STATISTIČNA REGIJA': 'regija'})

    # Pretvorimo 
    df_trans = df.melt(id_vars="regija", var_name="leto", value_name="bdp")

    return df_trans

def zapisi_df(df: pd.DataFrame) -> None:

    ime_tabele = "BDP_regije"

    # Poskrbimo, da tabela obstaja
    ustvari_tabelo(ime_tabele)
    
    # Če DataFrame nima stolpca 'Index', ga dodamo iz indeksa
    #df = df.reset_index()

    # Transformiramo podatke v DataFrame-u
    df = transformiraj(df)
    
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
    df = preberi_csv(r"C:\Users\laraj\OneDrive - Univerza v Ljubljani\semester 6\OPB\projektna naloga\OPB-skladisce\DATA\csv_datoteke\bdp.csv")

    zapisi_df(df)
    
    print("CSV datoteka je bila uspešno zabeležena v bazi.")
