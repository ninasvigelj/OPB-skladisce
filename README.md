# OPB-skladisce

V najinem projektu sva naredili podatkovno skladišče podatkov. Za fact tabele sva vzeli tabele `fact_bdp_regije`, `fact_delovno_aktivno`, `fact_st_podjetij` in `fact_stanovanja_obcine`, ter jim dodali tabeli dimenzij `dim_regije` oz. `dim_obcine`. Podatke sva pridobili s spletne strani [SiStat](https://pxweb.stat.si/SiStat/sl). 

Repozitorij je sestavljen iz treh glavnih map: [Data](./Data), [Presentation](./Presentation) in [Services](./Services). V Data sva pobrali podatke, v Services sva jih uvozili kot dataframe in nato v mapi Presentation oblikovali grafe in postavitev strani. 

Za sam zagon aplikacije je potrebno naložiti vse zgoraj naštete mape ter datoteko [app.py](./app.py). Za prikaz vizualizacije podatkov je nato potrebno zagnati datoteko `app.py` in slediti povezavi, ki se izpiše v terminalu.

*Lara Jeraj in Nina Švigelj*
