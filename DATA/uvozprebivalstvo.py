import psycopg2
import pandas as pd
from re import findall
import psycopg2.extras

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


def ustvari_tabelo_delovnoprebiv(ime_tabele: str) -> None:
    """
    Ustvari tabelo za podatke o delovno aktivnem prebivalstvu po občinah prebivališča.
    """
    cur.execute(f"""
        DROP TABLE IF EXISTS {ime_tabele};
        CREATE TABLE IF NOT EXISTS {ime_tabele} (
            naselje TEXT,
            leto INTEGER,
            stevilo INTEGER,
            PRIMARY KEY (naselje, leto)
        );
    """)
    conn.commit()


def preberi_in_transformiraj_csv(ime_datoteke: str) -> pd.DataFrame:
    """
    Prebere CSV in ga preoblikuje v dolgo (long) obliko.
    """
    df = pd.read_csv(ime_datoteke, sep=";", encoding="cp1250")

    # Počistimo imena stolpcev
    df.columns = [col.replace('"', '').strip() for col in df.columns]
    df = df.rename(columns={df.columns[0]: "naselje", df.columns[1]: "spol"})

    # Pretvori "-" v NaN
    df = df.replace("-", pd.NA)

    # Pretvori v dolgo obliko
    df_long = df.melt(id_vars=["naselje", "spol"], var_name="leto_raw", value_name="stevilo")

    # Iz 'leto_raw' izlušči leto kot število
    df_long["leto"] = df_long["leto_raw"].apply(lambda x: int(findall(r"\d{4}", x)[0]) if findall(r"\d{4}", x) else None)

    # Pretvori 'stevilo' v številko
    df_long["stevilo"] = pd.to_numeric(df_long["stevilo"], errors="coerce")

    # Odstrani vrstice brez letnice ali števila
    df_long = df_long.dropna(subset=["leto", "stevilo"])

    # Pretvori tipe
    df_long["leto"] = df_long["leto"].astype(int)
    df_long["stevilo"] = df_long["stevilo"].astype(int)

    # Odstrani stolpec 'spol'
    df_long = df_long.drop(columns=["spol", "leto_raw"])

    return df_long


def zapisi_df_v_bazo(df: pd.DataFrame, ime_tabele: str) -> None:
    """
    Zapiše podatke v bazo.
    """
    ustvari_tabelo_delovnoprebiv(ime_tabele)

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
    df = preberi_in_transformiraj_csv("projekt/DATA/exceli/delovnoprebiv.csv")
    zapisi_df_v_bazo(df, "delovno_aktivno")
    print("CSV datoteka je bila uspešno zabeležena v bazi.")
