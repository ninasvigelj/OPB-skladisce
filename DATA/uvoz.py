# https://pxweb.stat.si/SiStatData/pxweb/sl/Data/-/1906903S.px/table/tableViewLayout2/
# https://pxweb.stat.si/SiStatData/pxweb/sl/Data/-/1418807S.px/table/tableViewLayout2/
# https://pxweb.stat.si/SiStatData/pxweb/sl/Data/-/0309250S.px/table/tableViewLayout2/
# https://pxweb.stat.si/SiStatData/pxweb/sl/Data/-/0723405S.px/table/tableViewLayout2/

#uvoz podatkov z API-ji

import psycopg2
import pandas  as pd
from re import sub
# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import auth_public as config


database = config.database
host = config.host
port = config.port
user = config.user
password = config.password

# Ustvarimo povezavo
conn = psycopg2.connect(database=database, host=host, port=port, user=user, password=password)


# Iz povezave naredimo cursor, ki omogoča
# zaganjanje ukazov na bazi

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def ustvari_tabelo_stranke(ime_tabele : str) -> None:   # da poveš pythonu kakšni tipi so vhodi in kakšen tip naj funkcija vrne
    """
    Funkcija pobriše in na novo ustvari tabelo o podatkih strank.
    """
    cur.execute(f"""
        DROP table if exists {ime_tabele};
        CREATE table if not exists  {ime_tabele}(            
            customer_id text primary key,
            first_name text,
            last_name text,
            company text,
            city text,
            country text,
            phone_1 text,
            phone_2 text,
            email text,
            subscription_date date,
            website text
        );
    """)
    conn.commit()

# drop mamo samo zato, da lahko še enkrat poženemo

def preberi_csv(ime_datoteke : str) -> pd.DataFrame:
    df = pd.read_csv(ime_datoteke, 
                     sep=",", 
                     index_col=0)

    return df

def preimenuj_stolpce_stranke(df: pd.DataFrame) -> pd.DataFrame:
    """
    Funkcija preimenuje stolpce v DataFrame-u, da ustrezajo camelCase konvenciji.
    """
    df = df.rename(columns={
            "Customer Id": "customer_id",
            "First Name": "first_name",
            "Last Name": "last_name",
            "Company": "company",
            "City": "city",
            "Country": "country",
            "Phone 1": "phone_1",
            "Phone 2": "phone_2",
            "Email": "email",
            "Subscription Date": "subscription_date",
            "Website": "website"
        }   # tukej mamo nek slovar v kaj se pretvorijo stolpci
    ) 
    return df

def transformiraj_stranke(df: pd.DataFrame) -> pd.DataFrame:

    # Pretvorba stolpca subscription_date v datum:
    df['subscription_date'] = pd.to_datetime(df['subscription_date'], errors='coerce')

    # Če je vrednost neveljaven datum, se pretvori v None; sicer pretvorimo v Python date objekt
    #df['subscription_date'] = df['subscription_date'].apply(lambda x: x.date() if pd.notnull(x) else None)
    
    # Definiramo vrstni red stolpcev, kot so definirani v tabeli
    columns = [
        "customer_id", "first_name", "last_name", "company",
        "city", "country", "phone_1", "phone_2", "email",
        "subscription_date", "website"
    ]
    
    # Poskrbimo, da DataFrame vsebuje točno te stolpce v pravem vrstnem redu
    df = df.reindex(columns=columns)
    return df


def zapisi_df(df: pd.DataFrame) -> None:

    ime_tabele = "customers"

    # Poskrbimo, da tabela obstaja
    ustvari_tabelo_stranke(ime_tabele)
    
    # Če DataFrame nima stolpca 'Index', ga dodamo iz indeksa
    #df = df.reset_index()

    # Prvi korak: Stolpci v csvju so drugače poimenovani,
    # kot bi si jih želeli imeti v bazi.
    df = preimenuj_stolpce_stranke(df)
    
    # Transformiramo podatke v DataFrame-u
    df = transformiraj_stranke(df)
    
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
    # Preberi CSV datoteko, pri čemer privzamemo, da je datoteka
    # "customers-100.csv" v isti mapi kot tvoj skript ali podaj absolutno pot.
    df = preberi_csv("VajeKodaPrimer\customers-100.csv")
    
    # Zapiši podatke iz DataFrame-a v tabelo "customers"
    zapisi_df(df)
    
    print("CSV datoteka je bila uspešno zabeležena v bazi.")