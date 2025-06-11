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
conn = psycopg2.connect(database=database, host=host, port=port, user=user, password=password)


# Iz povezave naredimo cursor, ki omogoča
# zaganjanje ukazov na bazi

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def ustvari_tabelo(ime_tabele : str) -> None:   # da poveš pythonu kakšni tipi so vhodi in kakšen tip naj funkcija vrne
    """
    Funkcija pobriše in na novo ustvari tabelo regij z id.
    """
    cur.execute(f"""
        DROP table if exists {ime_tabele};
        CREATE table if not exists  {ime_tabele}(     
            regija_id serial primary key,       
            regija text
        );
    """)
    conn.commit()

# drop mamo samo zato, da lahko še enkrat poženemo

def pridobi_regije() -> pd.DataFrame:
    regije = [
        "Pomurska", "Podravska", "Koroška", "Savinjska",
        "Zasavska", "Posavska", "Jugovzhodna Slovenija",
        "Osrednjeslovenska", "Gorenjska", "Primorsko-notranjska",
        "Goriška", "Obalno-kraška"
    ]
    return pd.DataFrame({"regija": regije})


def transformiraj(df: pd.DataFrame) -> pd.DataFrame:

    # Če je vrednost neveljaven datum, se pretvori v None; sicer pretvorimo v Python date objekt
    #df['subscription_date'] = df['subscription_date'].apply(lambda x: x.date() if pd.notnull(x) else None)
    
    # Definiramo vrstni red stolpcev, kot so definirani v tabeli
    columns = [
            "regija"
    ]
    # Poskrbimo, da DataFrame vsebuje točno te stolpce v pravem vrstnem redu
    df = df.reindex(columns=columns)
    return df


def zapisi_df(df: pd.DataFrame) -> None:

    ime_tabele = "dim_regije"

    # Poskrbimo, da tabela obstaja
    ustvari_tabelo(ime_tabele)
    
    # Če DataFrame nima stolpca 'Index', ga dodamo iz indeksa
    #df = df.reset_index()
    
    # Transformiramo podatke v DataFrame-u
    df = transformiraj(df)
    
    # shranimo stolpce v seznam
    columns = df.columns.tolist()

    # Pretvorimo podatke v seznam tuple-ov
    records = df.values.tolist()    
    
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
    df = pridobi_regije()
    zapisi_df(df)
    print("CSV datoteka je bila uspešno zabeležena v bazi.")