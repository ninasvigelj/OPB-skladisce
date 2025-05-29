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
            obcina text primary key,
            leto_2008 text,
            leto_2009 text,
            leto_2010 text,
            leto_2011 text,
            leto_2012 text,
            leto_2013 text,
            leto_2014 text,
            leto_2015 text,
            leto_2016 text,
            leto_2017 text,
            leto_2018 text,
            leto_2019 text,
            leto_2020 text,
            leto_2021 text,
            leto_2022 text,
            leto_2023 text
        );
    """)
    conn.commit()

# drop mamo samo zato, da lahko še enkrat poženemo

def preberi_csv(ime_datoteke : str) -> pd.DataFrame:
    df = pd.read_csv(ime_datoteke, 
                    sep=";",
                    encoding='windows-1250')
    return df


def transformiraj(df: pd.DataFrame) -> pd.DataFrame:

    # Če je vrednost neveljaven datum, se pretvori v None; sicer pretvorimo v Python date objekt
    #df['subscription_date'] = df['subscription_date'].apply(lambda x: x.date() if pd.notnull(x) else None)
    
    # Definiramo vrstni red stolpcev, kot so definirani v tabeli
    columns = ["obcina"] + [f'leto_{leto}' for leto in range(2008, 2023)]
    
    # Poskrbimo, da DataFrame vsebuje točno te stolpce v pravem vrstnem redu
    df = df.reindex(columns=columns)
    return df

def preimenuj_stolpce(df: pd.DataFrame) -> pd.DataFrame:
    """
    Funkcija preimenuje stolpce v DataFrame-u, da ustrezajo camelCase konvenciji.
    """
    df = df.rename(columns={
            "OBČINE":"obcina",
            "2008 Število podjetij":"leto_2008",
            "2009 Število podjetij":"leto_2009",
            "2010 Število podjetij":"leto_2010",
            "2011 Število podjetij":"leto_2011",
            "2012 Število podjetij":"leto_2012",
            "2013 Število podjetij":"leto_2013",
            "2014 Število podjetij":"leto_2014",
            "2015 Število podjetij":"leto_2015",
            "2016 Število podjetij":"leto_2016",
            "2017 Število podjetij":"leto_2017",
            "2018 Število podjetij":"leto_2018",
            "2019 Število podjetij":"leto_2019",
            "2020 Število podjetij":"leto_2020",
            "2021 Število podjetij":"leto_2021",
            "2022 Število podjetij":"leto_2022",
            "2023 Število podjetij":"leto_2023"
        }  
    ) 
    return df

def zapisi_df(df: pd.DataFrame) -> None:

    ime_tabele = "st_podjetij"

    # Poskrbimo, da tabela obstaja
    ustvari_tabelo(ime_tabele)
    
    # Če DataFrame nima stolpca 'Index', ga dodamo iz indeksa
    #df = df.reset_index()
    df = preimenuj_stolpce(df)

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
    df = preberi_csv("projekt\DATA\csv_datoteke\stpodjetij.csv")
    zapisi_df(df)
    
    print("CSV datoteka je bila uspešno zabeležena v bazi.")