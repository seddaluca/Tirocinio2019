from firebase import firebase

import random

'''
    Classe SetUp: gestisce l'accesso al DB
        - instance: attributo che contiene l'istanza del DB (inizialmente è una stringa vuota)
'''

class SetUp:
    instance = ' '

    def __init__(self): # Costruttore che inizializza l'attributo instance con l'istanza del DB
        self.instance = firebase.FirebaseApplication('https://diary-e9919.firebaseio.com', None)

    '''
        Metodo len(self, type): restituisce la dimensione della lista 
           - type: stringa che contiene la tipologia del piatto ('first dishes', ecc.)
    '''
    def len(self, type):
        return len(self.instance.get(''+type, None))

    '''
        Metodo dishes(self, type): restituisce un piatto
            - type: stringa che contiene la tipologia del piatto ('first dishes', ecc.)
    '''
    def dishes(self, type):
        return self.instance.get(''+type, random.randint(0, self.len(''+type) - 1))