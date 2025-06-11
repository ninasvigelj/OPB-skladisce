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
    Funkcija pobriše in na novo ustvari tabelo o dokončani stanovanjih v občinah po letih.
    """
    cur.execute(f"""
        DROP table if exists {ime_tabele};
        CREATE table if not exists  {ime_tabele}(            
            obcina_id integer,
            leto integer,
            sobe integer,
            povrsina_m2 integer,
            stevilo integer,
            PRIMARY KEY (obcina_id, leto, sobe)
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
    """Naredi tabelo s stolci občina, leto, št. sob,št. stanovanj, površina    """
      # Omejimo se na ustrezne stolpce
    cols_to_drop = [col for col in df.columns if "Stanovanja - SKUPAJ" in col]
    df = df.drop(columns=cols_to_drop)
  
    df = df.rename(columns={"OBČINE": "obcina"})

    df.loc[:, "obcina"] = df["obcina"].str.replace("Kanal", "Kanal ob Soči", regex=True)
    df.loc[:, "obcina"] = df["obcina"].str.replace(r"Sveta Trojica v Slov\. goricah\*", "Sveta Trojica v Slov. goricah", regex=True)
    

    df_long = df.melt(id_vars=["obcina", "MERITVE"], var_name="leto_sobe", value_name="vrednost")
       
    df_long[["leto", "sobe"]] = df_long["leto_sobe"].str.extract(r"(\d{4})\s+(.*)")
    
    df_pivot = df_long.pivot(index=["obcina", "leto", "sobe"], columns="MERITVE", values="vrednost").reset_index()
    df_pivot = df_pivot.rename(columns={"Površina [m2]": "povrsina_m2", "Število": "stevilo"})
    
   
    df_pivot["povrsina_m2"] = pd.to_numeric(df_pivot["povrsina_m2"], errors='coerce')
    df_pivot["stevilo"] = pd.to_numeric(df_pivot["stevilo"], errors='coerce')

    pretvori_sobe = {
    "Enosobna": 1,
    "Dvosobna": 2,
    "Trisobna": 3,
    "Štirisobna": 4,
    "Pet- in večsobna": 5
    }
    df_pivot["sobe"] = df_pivot["sobe"].map(pretvori_sobe)

    #odstranimo Slovenijo, ker ni zares občina
    df_pivot = df_pivot[df_pivot["obcina"] != "SLOVENIJA"]

    df_pivot = df_pivot.dropna(subset=["povrsina_m2", "stevilo"], how="all")

    df_pivot["povrsina_m2"] = df_pivot["povrsina_m2"].round().astype('Int64')
    df_pivot["stevilo"] = df_pivot["stevilo"].round().astype('Int64')
    df_pivot["leto"] = df_pivot["leto"].astype(int)
    df_pivot["sobe"] = df_pivot["sobe"].astype('Int64')

   
    
    print("Max povrsina_m2:", df_pivot["povrsina_m2"].max())
    print("Max stevilo:", df_pivot["stevilo"].max())
    df_pivot = df_pivot.where(pd.notnull(df_pivot), None)

    print(df_pivot[df_pivot['obcina'] == 'Ankaran/Ancarano'])

    return df_pivot
    
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

    # Uporabi funkcijo na stolpec
    df["obcina_id"] = df["obcina"].apply(najdi_id)

    return df
 
def zapisi_df(df: pd.DataFrame) -> None:

    ime_tabele = "fact_stanovanja_občine"

    # Poskrbimo, da tabela obstaja
    ustvari_tabelo(ime_tabele)
    
    # Če DataFrame nima stolpca 'Index', ga dodamo iz indeksa
    #df = df.reset_index()

    # Transformiramo podatke v DataFrame-u
    df = transformiraj(df)

    df = dodaj_obcina_id(df)

    
    
    if "obcina" in df.columns:
        df = df.drop(columns=["obcina"])
 

    df = df.where(pd.notnull(df), None)
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col].dtype):
            df[col] = df[col].astype('float')
    
    # shranimo stolpce v seznam
    columns = df.columns.tolist()

    # Pretvorimo podatke v seznam tuple-ov
    records = df.values.tolist()    #records je uvistvu seznam seznamov
    
    # Pripravimo SQL ukaz za vstavljanje podatkov
    sql = f"INSERT INTO {ime_tabele} ({', '.join(columns)}) VALUES %s"

    # Uporabimo pd.notnull, da pretvorimo NaN v None
    records = df.where(pd.notnull(df), None).to_records(index=False)

    records = [(None if pd.isna(x) else x.item() if hasattr(x, 'item') else x for x in row) for row in records]
    records = [tuple(row) for row in records]
    
    # Uporabimo execute_values za množični vnos
    # Izvede po en insert ukaz na vrstico oziroma record iz seznama records
    # V odzadju zadeva deluje precej bolj optimlano kot en insert na ukaz!
    # Za množičen vnos je potrebno uporabiti psycopg2.extras.execute_values
    psycopg2.extras.execute_values(cur, sql, records)
    
    # Potrdimo spremembe v bazi
    conn.commit()


if __name__ == "__main__":
    df = preberi_csv(r"C:\Users\laraj\OneDrive - Univerza v Ljubljani\semester 6\OPB\projektna naloga\OPB-skladisce\DATA\csv_datoteke\stanovanja.csv")
    #print("Stolpci v CSV:", df.columns.tolist())
    zapisi_df(df)
    
    print("CSV datoteka je bila uspešno zabeležena v bazi.")
