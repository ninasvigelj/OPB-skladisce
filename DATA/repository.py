import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import auth_public as auth
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
        self.conn.close()
        return df

    def st_podjetij_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o številu podjetij po občinah in regijah
        """
        query = """
            SELECT f.leto, o.obcina, o.regija, f.stevilo
            FROM fact_st_podjetij f
            JOIN dim_obcine o ON f.obcina_id = o.obcina_id
        """
        df = pd.read_sql(query, self.conn)
        self.conn.close()
        return df

    def delovno_aktivno_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o delovno aktivnem prebivalstvu po občinah in pripadajočih regijah.
        """
        
        query = """
            SELECT f.leto, o.obcina, o.regija, f.stevilo
            FROM fact_delovno_aktivno f
            JOIN dim_obcine o ON f.obcina_id = o.obcina_id
        """
        df = pd.read_sql(query, self.conn)
        self.conn.close()
        return df

    def stanovanja_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o stanovanjih po občinah s pridruženimi regijami
        """
        query = """
            SELECT f.leto, o.obcina, o.regija, f.sobe, f.povrsina_m2, f.stevilo
            FROM fact_stanovanja_obcine f
            JOIN dim_obcine o ON f.obcina_id = o.obcina_id
        """
        df = pd.read_sql(query, self.conn)
        self.conn.close()
        return df