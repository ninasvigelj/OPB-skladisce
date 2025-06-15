import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import DATA.auth_public as auth
import datetime
import os
import pandas as pd

DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


class Repo:
    def __init__(self):
        self.conn = psycopg2.connect(
            database=auth.db,
            host=auth.host,
            user=auth.user,
            password=auth.password,
            port=DB_PORT
        )
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def bdp_po_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke BDP po regijah
        """
        query = """
            SELECT f.leto, r.regija, f.BDP
            FROM fact_bdp_regije f
            JOIN dim_regije r ON f.regija_id = r.regija_id
        """
        df = pd.read_sql(query, self.conn)
        #self.conn.close()
        return df
    
    def stanovanja_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o stanovanjih po občinah s pridruženimi regijami
        """
        query = """
            SELECT f.leto, o.obcina, o.regija, f.sobe, f.povrsina_m2, f.stevilo
            FROM fact_stanovanja_obcine f
            JOIN dim_obcine o ON f.obcina_id = o.obcina_id
        """ # vrne dataframe s stolpci: leto, obcina, regija, sobe, povrsina_m2, stevilo
        df = pd.read_sql(query, self.conn)
        self.conn.close()
        return df
    
    def vse_po_regijah(self) -> pd.DataFrame:
        """
        Vrne združene podatke o BDPju, št. podjetij in delovno aktivnih po regijah.
        """
        query = """
            WITH bdp AS (
                SELECT f.leto, r.regija, f.BDP
                FROM fact_bdp_regije f
                JOIN dim_regije r ON f.regija_id = r.regija_id
            ),
            podjetja AS (
                SELECT f.leto, o.regija, SUM(f.stevilo) AS stevilo_podjetij
                FROM fact_st_podjetij f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.regija
            ),
            delovno AS (
                SELECT f.leto, o.regija, SUM(f.stevilo) AS delovno_aktivno
                FROM fact_delovno_aktivno f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.regija
            ),
            stanovanja AS (
                SELECT f.leto, o.regija, SUM(f.stevilo) AS stevilo_stanovanj
                FROM fact_stanovanja_obcine f
                JOIN dim_obcine o ON f.obcina_id = o.obcina_id
                GROUP BY f.leto, o.regija
            )
            SELECT bdp.leto, bdp.regija, bdp.BDP, podjetja.stevilo_podjetij, delovno.delovno_aktivno, stanovanja.stevilo_stanovanj
            FROM bdp
            LEFT JOIN podjetja ON bdp.leto = podjetja.leto AND bdp.regija = podjetja.regija
            LEFT JOIN delovno ON bdp.leto = delovno.leto AND bdp.regija = delovno.regija
            LEFT JOIN stanovanja ON bdp.leto = stanovanja.leto AND bdp.regija = stanovanja.regija
        """
        df = pd.read_sql(query, self.conn)
        #self.conn.close()
        return df

# repo = Repo()
# bdp = repo.vse_po_regijah()
# print(bdp.head())