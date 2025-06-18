from Data.repository import Repo
import pandas as pd

class StatisticsService:
    def __init__(self):
        self.repo = Repo()
    
    def bdp_po_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o BDP po regijah in letih.
        """
        return self.repo.bdp_po_regijah()

    def vse_po_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o bdp, stevilu podjetij in delovno aktivnem prebivalstvu po regijah.
        """
        return self.repo.vse_po_regijah()

    def stanovanja_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o stanovanjih po občinah, sobah in letih.
        """
        return self.repo.stanovanja_po_obcinah_in_regijah()
    
    def vse_brez_bdp_po_obcinah(self) -> pd.DataFrame:
        """
        Vrne podatke o številu stanovanj, številu delovno aktivnih in številu podjetij po občinah in letih.
        """
        return self.repo.vse_brez_bdp_po_obcinah()

