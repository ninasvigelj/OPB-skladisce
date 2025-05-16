import psycopg2
import pandas as pd
from re import sub

import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki


import auth_public

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
    Ustvari tabelo za podatke o delovno aktivnem prebivalstvu po mestnih naseljih.
    """
    cur.execute(f"""
        DROP TABLE IF EXISTS {ime_tabele};
        CREATE TABLE IF NOT EXISTS {ime_tabele} (
            naselje TEXT,
            leto INTEGER,
            stevilo INTEGER
        );
    """)
    conn.commit()


def preberi_in_transformiraj_csv(ime_datoteke: str) -> pd.DataFrame:
    """
    Prebere CSV, odstrani prve vrstice, preoblikuje podatke v dolgo obliko.
    """
    df = pd.read_csv(ime_datoteke, sep=";", skiprows=2, encoding='cp1250')

    # Preimenuj prvi stolpec
    df = df.rename(columns={df.columns[0]: "naselje"})

    # Odstrani morebitne odvečne narekovaje in znake
    df["naselje"] = df["naselje"].str.replace('"', '', regex=False).str.strip()

    # Pretvori v dolgo (long) obliko
    df_long = df.melt(id_vars=["naselje"], var_name="leto", value_name="stevilo")

    # Pretvori leto v integer
    df_long["leto"] = pd.to_numeric(df_long["leto"], errors="coerce")
    df_long["stevilo"] = pd.to_numeric(df_long["stevilo"], errors="coerce")

    # Odstrani vrstice z manjkajočimi vrednostmi
    df_long = df_long.dropna(subset=["leto", "stevilo"])

    # Pretvori tipe
    df_long["leto"] = df_long["leto"].astype(int)
    df_long["stevilo"] = df_long["stevilo"].astype(int)

    print(df_long)

    return df_long


def zapisi_df_v_bazo(df: pd.DataFrame, ime_tabele: str) -> None:
    """
    Zapiše podatke v bazo v tabelo z imenom `ime_tabele`.
    """
    ustvari_tabelo_delovnoaktivno(ime_tabele)

    records = df.values.tolist()
    columns = df.columns.tolist()
    sql = f"INSERT INTO {ime_tabele} ({', '.join(columns)}) VALUES %s"

    print(f"Vstavljam {len(records)} vrstic v tabelo {ime_tabele}...")
    psycopg2.extras.execute_values(cur, sql, records)
    print("Vstavljanje zaključeno.")
    conn.commit()


if __name__ == "__main__":
    df = preberi_in_transformiraj_csv("projekt\\DATA\\exceli\delovnoaktivno.csv")
    zapisi_df_v_bazo(df, "delovno_aktivno")
    print("CSV datoteka je bila uspešno zabeležena v bazi.")
