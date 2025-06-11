from DATA.repository import Repo
import pandas as pd

class StatisticsService:
    def __init__(self):
        self.repo = Repo()
    
    def bdp_po_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o BDP po regijah in letih.
        """
        return self.repo.bdp_po_regijah()

    def st_podjetij_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne število podjetij po občinah in letih.
        """
        return self.repo.st_podjetij_po_obcinah_in_regijah()

    def delovno_aktivno_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o delovno aktivnem prebivalstvu po občinah in letih.
        """
        return self.repo.delovno_aktivno_po_obcinah_in_regijah()

    def stanovanja_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o stanovanjih po občinah, sobah in letih.
        """
        return self.repo.stanovanja_po_obcinah_in_regijah()
