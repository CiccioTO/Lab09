from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione


        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_regioni()
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        lista_relazioni = TourDAO.get_tour_attrazioni()

        for row in lista_relazioni:
            t_id= row["id_tour"]
            a_id= row["id_attrazione"]

            if t_id in self.tour_map and a_id in self.attrazioni_map:
                tour_ogg=self.tour_map[t_id]
                attraz_ogg=self.attrazioni_map[a_id]

                tour_ogg.attrazioni.add(attraz_ogg)
                tour_ogg.valore_culturale_totale+=attraz_ogg.valore_culturale


        # TODO

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1
        self.tour_correnti=[]


        # TODO
        if max_giorni is not None and max_budget is not None:

            for tour in self.tour_map:
                tours=self.tour_map[tour]

                if tours.id_regione == id_regione and tours.durata_giorni <= max_giorni and tours.costo <= max_budget:
                    self.tour_correnti.append(tours)

        else:
            for tour in self.tour_map:
                tours=self.tour_map[tour]

                if tours.id_regione == id_regione:
                    self.tour_correnti.append(tours)


        self._ricorsione(start_index=0,pacchetto_parziale=[],durata_corrente=0,costo_corrente=0,valore_corrente=0,attrazioni_usate=set(), tour_adatti=self.tour_correnti,max_giorni=max_giorni,max_budget=max_budget)


        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set, tour_adatti: list,max_giorni: int , max_budget: float):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno


        if valore_corrente > self._valore_ottimo :

            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()

        for i in range(start_index, len(tour_adatti)):
            tour=tour_adatti[i]

            if max_giorni is not None and (durata_corrente+ tour.durata_giorni) > max_giorni:
                continue
            if max_budget is not None and (costo_corrente + tour.costo) > max_budget:
                continue

            id_attrazioni_nuove = {a.id for a in tour.attrazioni}
            if not attrazioni_usate.isdisjoint(id_attrazioni_nuove):
                continue



            pacchetto_parziale.append(tour)
            durata = durata_corrente + tour.durata_giorni
            costo = costo_corrente + tour.costo
            valore = valore_corrente + tour.valore_culturale_totale
            attrazioni = attrazioni_usate.union(id_attrazioni_nuove)
            self._ricorsione(i+1, pacchetto_parziale, durata,
                            costo, valore, attrazioni,
                            tour_adatti, max_giorni, max_budget)


            pacchetto_parziale.pop()





        return pacchetto_parziale

