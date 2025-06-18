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
            obcina_id integer,
            leto integer,
            stevilo integer,
            PRIMARY KEY (obcina_id, leto)
        );
    """)
    conn.commit()

# drop mamo samo zato, da lahko še enkrat poženemo

def preberi_csv(ime_datoteke : str) -> pd.DataFrame:
    df = pd.read_csv(ime_datoteke, 
                    sep=";",
                    encoding='windows-1250')
    return df


import pandas as pd

def preimenuj_stolpce(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preimenuje originalne stolpce v standardizirano obliko za nadaljnjo obdelavo.
    """
    stolpci = {
        "OBČINA PREBIVALIŠČA": "obcina",
        "SPOL": "spol",
        "2008": "leto_2008",
        "2009": "leto_2009",
        "2010": "leto_2010",
        "2011": "leto_2011",
        "2012": "leto_2012",
        "2013": "leto_2013",
        "2014": "leto_2014",
        "2015": "leto_2015",
        "2016": "leto_2016",
        "2017": "leto_2017",
        "2018": "leto_2018",
        "2019": "leto_2019",
        "2020": "leto_2020",
        "2021": "leto_2021",
        "2022": "leto_2022",
        "2023": "leto_2023"
    }
    return df.rename(columns=stolpci)

def transformiraj(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pretvori široko tabelo v dolgo obliko z ustreznimi stolpci:
    obcina | leto | stevilo
    """
    # Omejimo se na ustrezne stolpce
    stolpci = ["obcina"] + [f'leto_{leto}' for leto in range(2008, 2024)]
    df = df[stolpci]

    df.loc[:, "obcina"] = df["obcina"].str.replace(r"\s*\(prebivališče\)", "", regex=True)

    # Spremenimo Kanal v Kanal ob Soči
    df.loc[:, "obcina"] = df["obcina"].str.replace("Kanal", "Kanal ob Soči", regex=True)

    # Pretvorimo v dolgo obliko
    df_long = df.melt(id_vars="obcina", var_name="leto", value_name="stevilo")

    # odstranimo Slovenijo, ker ni zares občina
    df_long = df_long[df_long["obcina"] != "SLOVENIJA"]

    # odstranimo neznano občino prebivališča
    df_long = df_long[df_long["obcina"] != "Neznana občina prebivališča"]

    # Odstranimo vrstice s simbolom '-' ali manjkajočimi vrednostmi
    df_long = df_long[df_long["stevilo"] != "-"]
    df_long = df_long.dropna(subset=["stevilo"])

    # Pretvorimo 'leto' iz npr. 'leto_2008' v število 2008
    df_long["leto"] = df_long["leto"].str.extract(r'(\d{4})').astype(int)

    # Pretvorimo stolpec 'stevilo' v integer, če je možno
    df_long["stevilo"] = df_long["stevilo"].astype(int)

    return df_long


def zapisi_df(df: pd.DataFrame) -> None:

    ime_tabele = "fact_delovno_aktivno"

    # Poskrbimo, da tabela obstaja
    ustvari_tabelo(ime_tabele)
    
    # Če DataFrame nima stolpca 'Index', ga dodamo iz indeksa
    #df = df.reset_index()
    df = preimenuj_stolpce(df)

    # Transformiramo podatke v DataFrame-u
    df = transformiraj(df)

    # Dodamo pripadajoče regije
    df = dodaj_obcina_id(df)

    if "obcina" in df.columns:
        df = df.drop(columns=["obcina"])
    
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

def dodaj_obcina_id(df: pd.DataFrame) -> pd.DataFrame:
    # Preveri obstoj tabele
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'dim_obcine'
        );
    """)
    obstaja = cur.fetchone()[0]

    if not obstaja:
        print("Tabela 'dim_obcine' ne obstaja.")
        df["obcina_id"] = None
        return df

    # Preberi občine in regije v slovar
    cur.execute("SELECT obcina, obcina_id FROM dim_obcine;")
    rezultati = cur.fetchall()
    obcine_dict = {r["obcina"]: r["obcina_id"] for r in rezultati}

    # Funkcija za iskanje regije, tudi za dvojezična imena
    def najdi_id(prebivalisce: str) -> int | None:
        kandidati = [ime.strip() for ime in prebivalisce.split("/")]
        for kandidat in kandidati:
            if kandidat in obcine_dict:
                return obcine_dict[kandidat]
            else:
                print(kandidat)

    # Uporabi funkcijo na stolpec
    df["obcina_id"] = df["obcina"].apply(najdi_id)

    return df


if __name__ == "__main__":
    df = preberi_csv("projekt\DATA\csv_datoteke\delovnoaktivno.csv")

    zapisi_df(df)
    
    print("CSV datoteka je bila uspešno zabeležena v bazi.")
