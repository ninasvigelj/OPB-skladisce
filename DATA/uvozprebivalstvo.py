import psycopg2
import pandas as pd
from re import findall
import psycopg2.extras
import io

import auth_public

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

# Povezava do baze
conn = psycopg2.connect(
    database=auth_public.db,
    host=auth_public.host,
    port=auth_public.port,
    user=auth_public.user,
    password=auth_public.password
)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def ustvari_tabelo_delovnoaktivno(ime_tabele: str) -> None:
    """
    Ustvari tabelo za podatke o delovno aktivnem prebivalstvu po občinah prebivališča.
    """
    cur.execute(f"""
        DROP TABLE IF EXISTS {ime_tabele};
        CREATE TABLE IF NOT EXISTS {ime_tabele} (
            prebivalisce TEXT,
            leto INTEGER,
            stevilo INTEGER,
            regija TEXT,
            PRIMARY KEY (prebivalisce, leto)
        );
    """)

    conn.commit()


def preberi_in_transformiraj_csv(ime_datoteke: str) -> pd.DataFrame:
    """
    Prebere CSV z odvečnimi narekovaji in ga preoblikuje v dolgo (long) obliko.
    """
    # Preberi surove vrstice
    with open(ime_datoteke, "r", encoding="cp1250") as f:
        lines = f.readlines()

    # Odstrani odvečne dvojne narekovaje in popravi vrstico
    cleaned_lines = [line.replace('""', '"').replace('"', '') for line in lines]

    # Združi v en CSV string
    csv_content = "\n".join(cleaned_lines)

    # Preberi CSV iz popravljene vsebine
    df = pd.read_csv(io.StringIO(csv_content), sep=";")

    # Poimenuj prva dva stolpca
    df = df.rename(columns={df.columns[0]: "prebivalisce", df.columns[1]: "spol"})

    # Pretvori "-" v NaN
    df = df.replace("-", pd.NA)

    # V dolgo obliko
    df_long = df.melt(id_vars=["prebivalisce", "spol"], var_name="leto_raw", value_name="stevilo")

    # Izlušči leto
    df_long["leto"] = df_long["leto_raw"].apply(lambda x: int(findall(r"\d{4}", x)[0]) if findall(r"\d{4}", x) else None)

    # Pretvori v številke
    df_long["stevilo"] = pd.to_numeric(df_long["stevilo"], errors="coerce")

    # Počisti neveljavne vrstice
    df_long = df_long.dropna(subset=["leto", "stevilo"])

    # Popravi kodiranje znakov v 'prebivalisce'
    df_long["prebivalisce"] = df_long["prebivalisce"].str.replace(r" \(prebivališče\)", "", regex=True)
    df_long = df_long.rename(columns={"naselje": "prebivalisce"})

    # Pretvori tipe
    df_long["leto"] = df_long["leto"].astype(int)
    df_long["stevilo"] = df_long["stevilo"].astype(int)
    

    return df_long[["prebivalisce", "leto", "stevilo"]]

def dodaj_regije(df: pd.DataFrame) -> pd.DataFrame:
    """
    Če obstaja tabela obcine_po_regijah, doda stolpec 'regija' glede na 'prebivalisce'.
    Pri tem upošteva tudi dvojezična imena občin (npr. 'Izola/Isola').
    """
    # Preveri obstoj tabele
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'obcine_po_regijah'
        );
    """)
    obstaja = cur.fetchone()[0]

    if not obstaja:
        print("Tabela 'obcine_po_regijah' ne obstaja. Dodajam stolpec 'regija' z vrednostjo '-'.")
        df["regija"] = "-"
        return df

    # Preberi občine in regije v slovar
    cur.execute("SELECT obcina, regija FROM obcine_po_regijah;")
    rezultati = cur.fetchall()
    obcine_dict = {r["obcina"]: r["regija"] for r in rezultati}

    # Funkcija za iskanje regije, tudi za dvojezična imena
    def najdi_regijo(prebivalisce: str) -> str:
        kandidati = [ime.strip() for ime in prebivalisce.split("/")]
        for kandidat in kandidati:
            if kandidat in obcine_dict:
                return obcine_dict[kandidat]
        return "-"

    # Uporabi funkcijo na stolpec
    df["regija"] = df["prebivalisce"].apply(najdi_regijo)

    return df



def zapisi_df_v_bazo(df: pd.DataFrame, ime_tabele: str) -> None:
    """
    Zapiše podatke v bazo.
    """
    ustvari_tabelo_delovnoaktivno(ime_tabele)

    records = df.values.tolist()
    columns = df.columns.tolist()
    sql = f"INSERT INTO {ime_tabele} ({', '.join(columns)}) VALUES %s"

    try:
        psycopg2.extras.execute_values(cur, sql, records)
        conn.commit()
        print("Vstavljanje zaključeno.")
    except Exception as e:
        print("Napaka pri vstavljanju v bazo:", e)
        conn.rollback()


if __name__ == "__main__":
    df = preberi_in_transformiraj_csv("projekt\DATA\csv_datoteke\delovnoaktivno.csv")
    
    # dodamo regije
    df = dodaj_regije(df)
    zapisi_df_v_bazo(df, "delovno_aktivno")
    print("CSV datoteka je bila uspešno zabeležena v bazi.")