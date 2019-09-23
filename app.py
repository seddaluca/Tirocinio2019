import firebase as firebase
from flask import Flask, request, make_response, jsonify
from datetime import date

import random
import pandas as pd
import numpy as np

from firebase import firebase
from setUp import SetUp

# initialize the flask app
app = Flask(__name__)

#region FoodList
firebaseList = {
    "first dishes": [{
        0: {"id": 0, "take": 3, "calories": 200, "name": "Vegetagle Soup"}
    }, {
        1: {"id": 1, "take": 3, "calories": 250, "name": "Vegetable couscous"}
    }, {
        2: {"id": 2, "take": 3, "calories": 350, "name": "Pasta with artichokes"}
    }, {
        3: {"id": 3, "take": 3, "calories": 230, "name": "Mushroom and Potato Soup"}
    }, {
        4: {"id": 4, "take": 3, "calories": 210, "name": "Cream of Pumpkin"}
    }, {
        5: {"id": 5, "take": 3, "calories": 360, "name": "Ricotta Pasta"}
    }, {
        6: {"id": 6, "take": 3, "calories": 360, "name": "Tagliatelle with Mushrooms"}
    }, {
        7: {"id": 7, "take": 3, "calories": 375, "name": "Spaghetti with Garlic and Oil"}
    }, {
        8: {"id": 8, "take": 3, "calories": 385, "name": "Gnocchi with Tomato Sauce"}
    }],

    "fruit" : [{
        0: {"id": 0, "take": 11, "calories": 89, "name": "banana"}
    }, {
        1: {"id": 1, "take": 2, "calories": 52, "name": "apple"}
    }, {
        2: {"id": 2, "take": 5, "calories": 57, "name": "pear"}
    }],

    "second dishes" : [{
        0: {"id": 0, "take": 3, "calories": 290, "name": "Grilled Lamb Chops"}
    }, {
        1: {"id": 1, "take": 3, "calories": 185, "name": "Hard Boiled Eggs"}
    }, {
        2: {"id": 2, "take": 3, "calories": 200, "name": "Grilled Pork Chops"}
    }, {
        3: {"id": 3, "take": 3, "calories": 220, "name": "Paprika Chicken Legs"}
    }, {
        4: {"id": 4, "take": 3, "calories": 250, "name": "Sea Bass in Salt Crust"}
    }, {
        5: {"id": 5, "take": 3, "calories": 270, "name": "Pan-Fried Chicken"}
    }],

    "side dishes": [{
        0: {"id": 0, "take": 10, "calories": 77, "name": "potato"}
    }, {
        1: {"id": 1, "take": 11, "calories": 18, "name": "tomato"}
    }]
}
#endregion

responseList = ['I suggest you ',
                    'I recommend you ']

list = {'meal': 'meal',
            'single dish': ['first',
                            'second',
                            'side dish',
                            'fruit']
            } # lista di supporto per suddividere le tipologie di pasti

# default route
@app.route('/')
def index():
    return 'Hello World!'

# function for responses
def results():
    # build a request object
    req = request.get_json(force=True)

    action = req.get('queryResult') # recupero l'insieme di valori contenuti all'interno del

    queryText = req.get('queryText')

    if (action.get('action') != None): # controllo se l'azione è diversa da None
        if (action.get('action') == 'input.unknown'): # se il valore è uguale a input.unkown (default)
            return {'fulfillmentText': queryText}

    if (action.get('action') == 'input.meal'): # se il valore è uguale a input.meal (default)
        return {'fulfillmentText': response(action)}

    if (action.get('action') == 'input.change'):
        return {'fulfillmentText': changeFood(action)}

# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return make_response(jsonify(results())) # return response

def cleanLast():
    side = ['First.txt',
            'Second.txt',
            'Side.txt',
            'Fruit.txt']

    for j in range(0,4):
        try: # file esiste
            try: # file esiste e contiene minimo una riga
                dataset = pd.read_csv(str(date.isocalendar(date.today())[1])+side[j], sep=",", error_bad_lines=False)  # Leggo tutto il file

                for i in range(0, len(dataset.index)):
                    dataset.iloc[i]["Last"] = 0

                dataset.to_csv(index=False, path_or_buf=str(date.isocalendar(date.today())[1])+side[j])

            except pd.errors.EmptyDataError: # eccezione nel caso il file sia vuoto
                print()
        except FileNotFoundError: # eccezione nel caso non venga trovato il file
            print()

# catResponse(response, str(date.isocalendar(date.today())[1])+'First.txt', listFirstDishes, elementFirstDishes)
def catResponse(new, response, file, list, element):
    if new:
        value = manage(file, list, element)

        if value == (None, True):
            return (element.get("name") + ' (' + str(element.get("calories")) + ' kcal)', True)

        elif value == (None, False):
            print("error")

            return (None, False)
        else:
            element = list.__getitem__(value[0]).get(value[0]) # prendo il primo valore della coppia -> value[0]
            return (element.get("name") + ' (' + str(element.get("calories")) + ' kcal)', True)

    else:
        value = checkChange(file, list)

        if value == (None, False):
            return (None, False)
        else:
            print("Value: " + str(value[0]))

            element = list.__getitem__(value[0]).get(value[0]) # prendo il primo valore della coppia -> value[0]

            print("Element:" + str(element))

            return (element.get("name") + ' (' + str(element.get("calories")) + ' kcal)', True)

def checkChange(file, list):
    dataset = pd.read_csv(file, sep=",", error_bad_lines=False)  # Leggo tutto il file

    old = dataset.loc[dataset["Last"].idxmax()]

    obj = 0  # da modificare

    print(str(list))

    print(str(old))

    if old.loc["Last"] == 1:
        if len(list) > len(dataset.index):
            lenList = len(list) - 1

            while True:  # do-while: restituisco un prodotto diverso dal precedente e non ancora proposto
                value = random.randint(0, lenList)

                if value not in dataset["ID"].to_list():
                    break

            for i in range(0, len(list)):  # prelevo l'elemento dalla lista
                if value == list[i].__getitem__(i).get('id'):
                    obj = list[i].__getitem__(i)

            dataset.loc[dataset["Last"].idxmax()]["Take"] += 1
            dataset.loc[dataset["Last"].idxmax()]["Last"] = 0

            dataset = dataset.append(pd.DataFrame({"ID": [obj.get("id")],
                                                   "Take": [(obj.get("take")-1)],
                                                   "Last": [1]}), ignore_index=True)

            dataset.to_csv(index=False, path_or_buf=file)

            print("Sic: " + str(obj.get("id")))

            return (obj.get("id"), False)

        elif len(list) == len(dataset):
            index = 0

            for i in range(0, len(dataset.index)):
                if old.loc["ID"] == dataset.iloc[i]["ID"]:
                    index = i

            flag = False

            for i in range(0, len(dataset.index)):
                if dataset.iloc[i]["ID"] != old.loc["ID"] and dataset.iloc[i]["Take"] > 0:
                    dataset.iloc[i]["Take"] -= 1
                    dataset.iloc[i]["Last"] = 1

                    obj = dataset.iloc[i]["ID"]

                    flag = True

                    break

            print("Popo")

            if flag:
                dataset.iloc[index]["Take"] += 1
                dataset.iloc[index]["Last"] = 0

                dataset.to_csv(index=False, path_or_buf=file)

                return (obj, True)
            else:
                dataset.to_csv(index=False, path_or_buf=file)

                return (index, False)

    return (None, False)

# function for manage dataset
def manage(file, list, obj):
    try: # file esiste
        try: # file esiste e contiene minimo una riga
            dataset = pd.read_csv(file, sep=",", error_bad_lines=False)  # Leggo tutto il file

            '''
            for i in range(0, len(dataset.index)):
                dataset.iloc[i]["Last"] = 0
            '''

            if obj.get("id") not in dataset["ID"].to_list(): # alimento non ancora mangiato nella settimana x
                dataset = dataset.append(pd.DataFrame({"ID": [obj.get("id")],
                                                       "Take": [obj.get("take")-1],
                                                       "Last": [1]}), ignore_index=True)

                dataset.to_csv(index=False, path_or_buf=file)
            else: # è stato mangiato
                for i in range(0, len(dataset.index)):
                    # se posso assumere ancora l'alimento
                    if (obj.get("id") == dataset.iloc[i]["ID"] and int(dataset.iloc[i]["Take"]) > 0):
                        print("Decremento la colonna Take per l'elemento " + str(dataset.iloc[i]["ID"]))

                        dataset.iloc[i]["Take"] -= 1
                        dataset.iloc[i]["Last"] = 1

                        dataset.to_csv(index=False, path_or_buf=file)

                    elif (obj.get("id") == dataset.iloc[i]["ID"] and int(dataset.iloc[i]["Take"]) == 0):
                        # se non posso assumere l'alimento, cerco l'alimento che posso ancora assumere (max Take)
                        print("Cercare un nuovo alimento, possibile rimpiazzo: "
                              + str(dataset.loc[dataset["Take"].idxmax()]))

                        if len(list) == len(dataset.index): # proposti almeno una volta tutti i prodotti
                            value = dataset.loc[dataset["Take"].idxmax()]

                            for j in range(0, len(dataset.index)): # recupero la riga e decremento Take
                                if value.loc["ID"] == dataset.iloc[j]["ID"]:
                                    if dataset.iloc[j]["Take"] > 0:
                                        dataset.iloc[j]["Take"] -= 1
                                        dataset.iloc[j]["Last"] = 1
                                        break

                                    elif dataset.iloc[j]["Take"] == 0:
                                        return (None, False) # coppia che indica un errore

                            dataset.to_csv(index=False, path_or_buf=file)

                            return (value.loc["ID"], False)

                        elif len(list) > len(dataset.index): # non sonoo stati prodotti tutti i prodotti
                            lenList = len(list) - 1

                            while True: # do-while: restituisco un prodotto diverso dal precedente e non ancora proposto
                                value = random.randint(0, lenList)

                                if value != obj.get("id") and value not in dataset["ID"].to_list():
                                    break

                            for i in range(0, len(list)): # prelevo l'elemento dalla lista
                                if value == list[i].__getitem__(i).get('id'):
                                    obj = list[i].__getitem__(i)

                            dataset = dataset.append(pd.DataFrame({"ID": [obj.get("id")],
                                                                   "Take": [obj.get("take")-1],
                                                                   "Last": [1]}), ignore_index=True)

                            dataset.to_csv(index=False, path_or_buf=file)

                            return (obj.get("id"), False)

        except pd.errors.EmptyDataError: # eccezione nel caso il file sia vuoto
            dataset = pd.DataFrame(pd.DataFrame({"ID": [obj.get("id")], "Take": [obj.get("take")-1], "Last": [1]}))

            dataset.to_csv(index=False, path_or_buf=file)
    except FileNotFoundError: # eccezione nel caso non venga trovato il file
            dataset = pd.DataFrame(pd.DataFrame({"ID": [obj.get("id")], "Take": [obj.get("take")-1], "Last": [1]}))

            dataset.to_csv(index=False, path_or_buf=file)

    return (None, True)

def response(action):
    responseListFood  = []

    typeOfMeal = action.get('parameters').get('TypeOfMeal')

    response = responseList[random.randint(0, 1)]  # imposto la risposta di default

    listFirstDishes = firebaseList.get('first dishes')
    listSecondDishes = firebaseList.get('second dishes')
    listSideDishes = firebaseList.get('side dishes')
    listFruit = firebaseList.get('fruit')

    lenListFirstDishes = len(listFirstDishes) - 1
    lenListSecondDishes = len(listSecondDishes) - 1
    lenListSideDishes = len(listSideDishes) - 1
    lenListFruit = len(listFruit) - 1

    firstDishes = random.randint(0, lenListFirstDishes)
    secondDishes = random.randint(0, lenListSecondDishes)
    sideDishes = random.randint(0, lenListSideDishes)
    fruit = random.randint(0, lenListFruit)

    elementFirstDishes = listFirstDishes.__getitem__(firstDishes).get(firstDishes)
    elementSecondDishes = listSecondDishes.__getitem__(secondDishes).get(secondDishes)
    elementSideDishes = listSideDishes.__getitem__(sideDishes).get(sideDishes)
    elementFruit = listFruit.__getitem__(fruit).get(fruit)

    cleanLast()

    if len(typeOfMeal) == 1:
        if list.get('meal') in typeOfMeal:
            value = catResponse(True,
                                response,
                                str(date.isocalendar(date.today())[1]) + 'First.txt',
                                listFirstDishes,
                                elementFirstDishes)

            print(str(value))

            if value[1] == True:
                responseListFood.append(value[0])

            value = catResponse(True,
                                response,
                                str(date.isocalendar(date.today())[1]) + 'Second.txt',
                                listSecondDishes,
                                elementSecondDishes)

            if value[1] == True:
                responseListFood.append(value[0])

            value = catResponse(True,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Side.txt',
                                   listSideDishes,
                                   elementSideDishes)

            if value[1] == True:
                responseListFood.append(value[0])

            value = catResponse(True,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Fruit.txt',
                                   listFruit,
                                   elementFruit)

            if value[1] == True:
                responseListFood.append(value[0])

        if list.get('single dish')[0] in typeOfMeal:
            value = catResponse(True,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'First.txt',
                                   listFirstDishes,
                                   elementFirstDishes)

            if value[1] == True:
                return response + value[0]
            else:
                return "My work is done, you've already eatten."

        if list.get('single dish')[1] in typeOfMeal:
            value = catResponse(True,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Second.txt',
                                   listSecondDishes,
                                   elementSecondDishes)

            if value[1] == True:
                return response + value[0]
            else:
                return "My work is done, you've already eatten."

        if list.get('single dish')[2] in typeOfMeal:
            value = catResponse(True,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Side.txt',
                                   listSideDishes,
                                   elementSideDishes)

            if value[1] == True:
                return response + value[0]
            else:
                return "My work is done, you've already eatten."

        if list.get('single dish')[3] in typeOfMeal:
            value = catResponse(True,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Fruit.txt',
                                   listFruit,
                                   elementFruit)

            if value[1] == True:
                return response + value[0]
            else:
                return "My work is done, you've already eatten."

    if len(typeOfMeal) > 1:
        for i in range(0, len(typeOfMeal)):
            if list.get('single dish')[0] in typeOfMeal[i]:
                value = catResponse(True,
                                       response,
                                       str(date.isocalendar(date.today())[1]) + 'First.txt',
                                       listFirstDishes,
                                       elementFirstDishes)

                if value[1] == True:
                    responseListFood.append(value[0])

            if list.get('single dish')[1] in typeOfMeal[i]:
                value = catResponse(True,
                                       response,
                                       str(date.isocalendar(date.today())[1]) + 'Second.txt',
                                       listSecondDishes,
                                       elementSecondDishes)

                if value[1] == True:
                    responseListFood.append(value[0])

            if list.get('single dish')[2] in typeOfMeal[i]:
                value = catResponse(True,
                                       response,
                                       str(date.isocalendar(date.today())[1]) + 'Side.txt',
                                       listSideDishes,
                                       elementSideDishes)

                if value[1] == True:
                    responseListFood.append(value[0])

            if list.get('single dish')[3] in typeOfMeal[i]:
                value = catResponse(True,
                                       response,
                                       str(date.isocalendar(date.today())[1]) + 'Fruit.txt',
                                       listFruit,
                                       elementFruit)

                if value[1] == True:
                    responseListFood.append(value[0])

    if len(responseListFood) > 0:
        for i in range (0, len(responseListFood)):
            if i == 0:
                response += responseListFood[i]
            elif i == len(responseListFood) - 1:
                response += ' and ' + responseListFood[i]
            else:
                response += ', ' + responseListFood[i]

        return response

    return "My work is done, you've already eatten."

def changeFood(action):
    print(action)

    responseListFood = []

    typeOfMeal = action.get('parameters').get('TypeOfMeal')

    response = responseList[random.randint(0, 1)]  # imposto la risposta di default

    listFirstDishes = firebaseList.get('first dishes')
    listSecondDishes = firebaseList.get('second dishes')
    listSideDishes = firebaseList.get('side dishes')
    listFruit = firebaseList.get('fruit')

    if len(typeOfMeal) == 1:
        if list.get('meal') in typeOfMeal:
            value = catResponse(False,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'First.txt',
                                   listFirstDishes,
                                   None)

            if value[1] == True:
                responseListFood.append(value[0])

            value = catResponse(False,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Second.txt',
                                   listSecondDishes,
                                   None)

            if value[1] == True:
                responseListFood.append(value[0])

            value = catResponse(False,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Side.txt',
                                   listSideDishes,
                                   None)

            if value[1] == True:
                responseListFood.append(value[0])

            value = catResponse(False,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Fruit.txt',
                                   listFruit,
                                   None)

            if value[1] == True:
                responseListFood.append(value[0])

        if list.get('single dish')[0] in typeOfMeal:
            value = catResponse(False,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'First.txt',
                                   listFirstDishes,
                                   None)

            if value[1] == True:
                return response + value[0]
            else:
                return "My work is done, you've already eatten."

        if list.get('single dish')[1] in typeOfMeal:
            value = catResponse(False,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Second.txt',
                                   listSecondDishes,
                                   None)

            if value[1] == True:
                return response + value[0]
            else:
                return "My work is done, you've already eatten."

        if list.get('single dish')[2] in typeOfMeal:
            value = catResponse(False,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Side.txt',
                                   listSideDishes,
                                   None)

            if value[1] == True:
                return response + value[0]
            else:
                return "My work is done, you've already eatten."

        if list.get('single dish')[3] in typeOfMeal:
            value = catResponse(False,
                                   response,
                                   str(date.isocalendar(date.today())[1]) + 'Fruit.txt',
                                   listFruit,
                                   None)

            if value[1] == True:
                return response + value[0]
            else:
                return "My work is done, you've already eatten."

    if len(typeOfMeal) > 1:
        for i in range(0, len(typeOfMeal)):
            if list.get('single dish')[0] in typeOfMeal[i]:
                value = catResponse(False,
                                       response,
                                       str(date.isocalendar(date.today())[1]) + 'First.txt',
                                       listFirstDishes,
                                       None)

                if value[1] == True:
                    responseListFood.append(value[0])

            if list.get('single dish')[1] in typeOfMeal[i]:
                value = catResponse(False,
                                       response,
                                       str(date.isocalendar(date.today())[1]) + 'Second.txt',
                                       listSecondDishes,
                                       None)

                if value[1] == True:
                    responseListFood.append(value[0])

            if list.get('single dish')[2] in typeOfMeal[i]:
                value = catResponse(False,
                                       response,
                                       str(date.isocalendar(date.today())[1]) + 'Side.txt',
                                       listSideDishes,
                                       None)

                if value[1] == True:
                    responseListFood.append(value[0])

            if list.get('single dish')[3] in typeOfMeal[i]:
                value = catResponse(False,
                                       response,
                                       str(date.isocalendar(date.today())[1]) + 'Fruit.txt',
                                       listFruit,
                                       None)

                if value[1] == True:
                    responseListFood.append(value[0])

    if len(responseListFood) > 0:
        for i in range(0, len(responseListFood)):
            if i == 0:
                response += responseListFood[i]
            elif i == len(responseListFood) - 1:
                response += ' and ' + responseListFood[i]
            else:
                response += ', ' + responseListFood[i]

        return response

    return "My work is done, you've already eatten."

# run the app
if __name__ == '__main__':
   app.run()