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

    def bdp_delovno_stanovanja_po_regijah(self) -> pd.DataFrame:
        """
        Vrne združeno bdp z delovno aktivnim in stanovanji po regijah
        """
        return self.repo.bdp_delovno_stanovanja_po_regijah()

    def bdp_podjetja_delovno_po_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o bdp, stevilu podjetij in delovno aktivnem prebivalstvu po regijah.
        """
        return self.repo.bdp_podjetja_delovno_po_regijah()

    def stanovanja_po_obcinah_in_regijah(self) -> pd.DataFrame:
        """
        Vrne podatke o stanovanjih po občinah, sobah in letih.
        """
        return self.repo.stanovanja_po_obcinah_in_regijah()
