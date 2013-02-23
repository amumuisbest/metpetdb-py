from webservices.db import _DbObject, _DbGetQuery

# http://127.0.0.1:8000/api/chemicalanalysis/12287/
class ChemicalAnalysisObject(_DbObject):
    def __init__(self, id = None):
        self.getQuery = _ChemicalAnalysisGetQuery();
        
        if id:
            self._get({"chemical_analysis_id": id})
            
    def get(self, id):
        return self._get({"chemical_analysis_id": id})
            
    def exists(self):
        return "id" in self.attributes
        
class _ChemicalAnalysisGetQuery(_DbGetQuery):
    def __init__(self):
        self.oneQuery = (
            "SELECT "
                "ca.chemical_analysis_id AS id, "
                "ca.public_data, "
                "ca.analyst, "
                "ca.analysis_method, "
                "ca.analysis_date, "
                "ca.description, "
                "ca.where_done as analysis_location, "
                "minerals.name as analysis_material, "
                "ca.stage_x, "
                "ca.stage_y, "
                "ca.total, "
                "ca.spot_id as pointnumber, "
                "users.name as owner_name "
            "FROM "
                "users, "
                "subsamples, "
                "chemical_analyses as ca, "
                "minerals "
            "WHERE "
                "ca.subsample_id = subsamples.subsample_id AND "
                "minerals.mineral_id = ca.mineral_id AND "
                "users.user_id = subsamples.user_id AND "
                "ca.chemical_analysis_id = %(chemical_analysis_id)s"
            )
               
        self.manyQueries = {
            "elements": (
                "SELECT "
                    "elements.name as name, "
                    "cae.amount as wt_percentage "
                "FROM "
                    "chemical_analysis_elements as cae, "
                    "elements "
                "WHERE "
                    "cae.element_id = elements.element_id AND "
                    "cae.chemical_analysis_id = %(chemical_analysis_id)s"
                ),
            "oxides": (
                "SELECT "
                    "oxides.species as name, "
                    "cao.amount as wt_percentage "
                "FROM "
                    "chemical_analysis_oxides as cao, "
                    "oxides "
                "WHERE "
                    "cao.oxide_id = oxides.oxide_id AND "
                    "cao.chemical_analysis_id = %(chemical_analysis_id)s"
                )
            }
            
# This is displayed on bottom of subsamples page view          
class ChemicalAnalysisTableObject(_DbObject):
    def __init__(self, subsample_id = None):
        self.getQuery = _ChemicalAnalysisTableGetQuery();
        
        if id:
            self._get({"subsample_id": subsample_id})
            
    def get(self, id):
        return self._get({"subsample_id": subsample_id})

    def exists(self):
        return "*" in self.attributes and len(self.attributes["*"]) > 0
        
class _ChemicalAnalysisTableGetQuery(_DbGetQuery):
    def __init__(self):
        self.manyQueries = {
            "*": (
                "SELECT "
                    "ca.chemical_analysis_id AS id, "
                    "ca.spot_id as pointnumber, "
                    "ca.public_data, "
                    "ca.analysis_method, "
                    "ca.analysis_date, "
                    "ca.analyst, "
                    "ca.total, "
                    "ca.description, "
                    "ca.where_done as analysis_location, "
                    "ca.reference_x, "
                    "ca.reference_y, "
                    "minerals.name as analysis_material "
                "FROM "
                    "subsamples, "
                    "chemical_analyses as ca, "
                    "minerals "
                "WHERE "
                    "ca.subsample_id = subsamples.subsample_id AND "
                    "minerals.mineral_id = ca.mineral_id AND "
                    "subsamples.subsample_id = %(subsample_id)s"
                )
            }
