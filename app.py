import firebase as firebase
from flask import Flask, request, make_response, jsonify
from datetime import date

import random
import pandas as pd

# initialize the flask app
app = Flask(__name__)

import csv

def reading(file):
    list = []

    try:
        with open(file, newline='') as f:
            reader = csv.reader(f)
            i = -1
            for row in reader:
                if i >= 0:
                    data = {
                        "ID": row[0],
                        "Take": row[1],
                        "Last": row[2]
                    }

                    list.append(data)
                i += 1

        return list

    except FileNotFoundError:
        print()

    return []

def writing(name, list):

    with open(name, 'w', newline='') as f:
        writer = csv.writer(f)
        # list = reading(file)
        writer.writerow(["ID", "Take", "Last"])
        for i in range(0, len(list)):
            writer.writerow([list[i].get('ID'), list[i].get('Take'), list[i].get('Last')])

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

listMeal = {'meal': 'meal',
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

def cleanList(list):
    if len(list) > 0:
        for i in range(0, len(list)):
            list[i].update({'Last': 0})

    return list

def cleanLast():
    side = ['First.csv',
            'Second.csv',
            'Side.csv',
            'Fruit.csv']

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

def catResponse2(new, listCSV, listFood, element):
    if new:
        value = manageDish(listCSV, listFood, element)

        if (value[1], value[2]) == (None, False):
            return (value[0], None, False)

        elif (value[1], value[2]) == (None, True):
            return (value[0], element.get("name") + ' (' + str(element.get("calories")) + ' kcal)', True)

        else:
            element = listFood.__getitem__(value[1]).get(value[1])  # prendo il secondo valore della coppia -> value[1]
            return (value[0], element.get("name") + ' (' + str(element.get("calories")) + ' kcal)', True)
    else:
        value = manageChangeDish(listCSV, listFood)

        print(value[0])

        if (value[1], value[2]) == (None, False):
            return (listCSV, None, False)
        else:
            element = listFood.__getitem__(value[1]).get(value[1])
            return (value[0], element.get("name") + ' (' + str(element.get("calories")) + ' kcal)', True)

def manageChangeDish(listCSV, listFood):
    listManage = []

    for i in range(0, len(listCSV)):
        listManage.append(listCSV[i].get("ID"))

    if len(listCSV) == 0:
        return (listCSV, None, False)
    elif len(listCSV) > 0:
        old = max(listCSV, key=lambda item: item['Last'])

        print("old: " + str(old))

        if int(old.get('Last')) == 1:
            if len(listFood) > len(listCSV):
                while True:  # do-while: restituisco un prodotto diverso dal precedente e non ancora proposto
                    value = random.randint(0, (len(listFood) - 1))

                    if value != int(old.get("ID")) and str(value) not in listManage:
                        break

                print("Altro " +str(value))

                for i in range(0, len(listFood)):  # prelevo l'elemento dalla lista
                    if value == listFood[i].__getitem__(i).get('id'):
                        obj = listFood[i].__getitem__(i)

                data = {'ID': int(obj.get('id')),
                        'Take': int(obj.get('take')) - 1,
                        'Last': 1}

                listCSV.append(data)

                for i in range(0, len(listCSV)):
                    if int(old.get('ID')) == int(listCSV[i].get('ID')):
                        listCSV[i].update({'Take': int(listCSV[i].get('Take')) + 1,
                                               'Last': 0})

                return (listCSV, int(obj.get("id")), False)  # --> cambiare il secondo parametro

            elif len(listFood) == len(listCSV):
                index = 0

                for i in range(0, len(listCSV)):
                    if old.get('ID') == listCSV[i].get('ID'):
                        index = i
                        break

                data = random.choice(list(filter(lambda x: int(x['Take']) > 0,
                                                 (filter(lambda x: int(x['ID']) != int(old.get('ID')), listCSV)))))

                print(str(data))

                if data != []:
                    for i in range(0, len(listCSV)):
                        if int(data.get('ID')) == int(listCSV[i].get('ID')):
                            listCSV[i].update({'Take': int(listCSV[i].get('Take')) - 1,
                                               'Last': 1})

                            listCSV[index].update({'Take': int(listCSV[index].get('Take')) + 1,
                                                   'Last': 0})

                            return (listCSV, int(listCSV[i].get('ID')), True)

                return (listCSV, index, False)

                '''
                index = 0

                for i in range(0, len(listCSV)):
                    if old.get('ID') == listCSV[i].get('ID'):
                        index = i
                        break

                for i in range(0, len(listCSV)):
                    if int(listCSV[i].get('ID')) != int(old.get('ID')) and int(listCSV[i].get('Take')) > 0:
                        listCSV[i].update({'Take': int(listCSV[i].get('Take'))-1,
                                           'Last': 1})

                        listCSV[index].update({'Take': int(listCSV[index].get('Take'))+1,
                                               'Last': 0})

                        return (listCSV, int(listCSV[i].get('ID')), True)
                
                return (listCSV, index, False)
                '''

    return (listCSV, None, False)

def checkChange(file, list):
    try:
        try:
            dataset = pd.read_csv(file, sep=",", error_bad_lines=False)  # Leggo tutto il file

            old = dataset.loc[dataset["Last"].idxmax()]

            obj = 0

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
                                                           "Take": [(obj.get("take") - 1)],
                                                           "Last": [1]}), ignore_index=True)

                    dataset.to_csv(index=False, path_or_buf=file)

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

                    if flag:
                        dataset.iloc[index]["Take"] += 1
                        dataset.iloc[index]["Last"] = 0

                        dataset.to_csv(index=False, path_or_buf=file)

                        return (obj, True)
                    else:
                        dataset.to_csv(index=False, path_or_buf=file)

                        return (index, False)
        except pd.errors.EmptyDataError: # eccezione nel caso il file sia vuoto
            return (None, False)
    except FileNotFoundError: # eccezione nel caso non venga trovato il file
        return (None, False)

    return (None, False)

'''
    Funzione che si occuperà di selezionare i pasti:
        - listCSV, lista di supporto che contiene i cibi contenuti nel file 
        - list, lista dei cibi
        - obj
'''
def manageDish(listCSV, listFood, obj):
    listManage = []

    for i in range(0, len(listCSV)):
        listManage.append(listCSV[i].get("ID"))

    if str(obj.get("id")) not in listManage:
        data = {"ID": obj.get("id"), "Take": obj.get("take") - 1, "Last": 1}

        listCSV.append(data)

    else:
        for i in range(0, len(listCSV)):
            if int(obj.get("id")) == int(listCSV[i].get("ID")) and int(listCSV[i].get("Take")) > 0:
                listCSV[i].update({"Take": int(listCSV[i].get("Take"))-1,
                                   "Last": 1})

                return (listCSV, None, True)

            elif int(obj.get("id")) == int(listCSV[i].get("ID")) and int(listCSV[i].get("Take")) == 0:
                if len(listFood) == len(listCSV):
                    data = max(list(filter(lambda x: x['ID'] != str(obj.get("id")), listCSV)),
                               key=lambda item: item['Take'])

                    if int(data['Take']) > 0: # se Take è minore di zero non posso fare nulla
                        for i in range(0, len(listCSV)):
                            if int(data['ID']) == int(listCSV[i].get('ID')):
                                listCSV[i].update({'Take': int(listCSV[i].get('Take'))-1,
                                                   'Last': 1})

                                return (listCSV, int(listCSV[i].get('ID')), False)

                    else:
                        return (listCSV, None, False)

                elif len(listFood) > len(listCSV):
                    while True:  # do-while: restituisco un prodotto diverso dal precedente e non ancora proposto
                        value = random.randint(0, (len(listFood) - 1))

                        if value != int(obj.get("id")) and str(value) not in listManage:
                            break

                    for i in range(0, len(listFood)):  # prelevo l'elemento dalla lista
                        if value == listFood[i].__getitem__(i).get('id'):
                            obj = listFood[i].__getitem__(i)

                    data = {'ID': int(obj.get('id')),
                            'Take': int(obj.get('take'))-1,
                            'Last': 1}

                    listCSV.append(data)

                    return (listCSV, obj.get("id"), False) # --> cambiare il secondo parametro

    return (listCSV, None, True)

def response(action):
    responseListFood  = []

    typeOfMeal = action.get('parameters').get('TypeOfMeal')

    response = responseList[random.randint(0, 1)]  # imposto la risposta di default

    firstCSV = reading(str(date.isocalendar(date.today())[1]) + 'First.csv')
    secondCSV = reading(str(date.isocalendar(date.today())[1]) + 'Second.csv')
    sideCSV = reading(str(date.isocalendar(date.today())[1]) + 'Side.csv')
    fruitCSV = reading(str(date.isocalendar(date.today())[1]) + 'Fruit.csv')

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

    cleanList(firstCSV)
    cleanList(secondCSV)
    cleanList(sideCSV)
    cleanList(fruitCSV)

    if len(typeOfMeal) == 1:
        if listMeal.get('meal') in typeOfMeal:
            value = catResponse2(True,
                                firstCSV,
                                listFirstDishes,
                                elementFirstDishes)

            firstCSV = value[0]

            if value[2] == True:
                responseListFood.append(value[1])

            value = catResponse2(True,
                                secondCSV,
                                listSecondDishes,
                                elementSecondDishes)

            secondCSV = value[0]

            if value[2] == True:
                responseListFood.append(value[1])

            value = catResponse2(True,
                                   sideCSV,
                                   listSideDishes,
                                   elementSideDishes)

            sideCSV = value[0]

            if value[2] == True:
                responseListFood.append(value[1])

            value = catResponse2(True,
                                   fruitCSV,
                                   listFruit,
                                   elementFruit)

            fruitCSV = value[0]

            if value[2] == True:
                responseListFood.append(value[1])

        if listMeal.get('single dish')[0] in typeOfMeal:
            value = catResponse2(True,
                                   firstCSV,
                                   listFirstDishes,
                                   elementFirstDishes)

            firstCSV = value[0]

            writing(str(date.isocalendar(date.today())[1]) + 'First.csv', firstCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Second.csv', secondCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Side.csv', sideCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Fruit.csv', fruitCSV)

            if value[2] == True:
                return response + value[1]
            else:
                return "My work is done, you've already eatten."

        if listMeal.get('single dish')[1] in typeOfMeal:
            value = catResponse2(True,
                                   secondCSV,
                                   listSecondDishes,
                                   elementSecondDishes)

            secondCSV = value[0]

            writing(str(date.isocalendar(date.today())[1]) + 'First.csv', firstCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Second.csv', secondCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Side.csv', sideCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Fruit.csv', fruitCSV)

            if value[2] == True:
                return response + value[1]
            else:
                return "My work is done, you've already eatten."

        if listMeal.get('single dish')[2] in typeOfMeal:
            value = catResponse2(True,
                                   sideCSV,
                                   listSideDishes,
                                   elementSideDishes)

            sideCSV = value[0]

            writing(str(date.isocalendar(date.today())[1]) + 'First.csv', firstCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Second.csv', secondCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Side.csv', sideCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Fruit.csv', fruitCSV)

            if value[2] == True:
                return response + value[1]
            else:
                return "My work is done, you've already eatten."

        if listMeal.get('single dish')[3] in typeOfMeal:
            value = catResponse2(True,
                                   fruitCSV,
                                   listFruit,
                                   elementFruit)

            fruitCSV = value[0]

            writing(str(date.isocalendar(date.today())[1]) + 'First.csv', firstCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Second.csv', secondCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Side.csv', sideCSV)
            writing(str(date.isocalendar(date.today())[1]) + 'Fruit.csv', fruitCSV)

            if value[2] == True:
                return response + value[1]
            else:
                return "My work is done, you've already eatten."

    if len(typeOfMeal) > 1:
        for i in range(0, len(typeOfMeal)):
            if listMeal.get('single dish')[0] in typeOfMeal[i]:
                value = catResponse2(True,
                                       firstCSV,
                                       listFirstDishes,
                                       elementFirstDishes)

                firstCSV = value[0]

                if value[2] == True:
                    responseListFood.append(value[1])

            if listMeal.get('single dish')[1] in typeOfMeal[i]:
                value = catResponse2(True,
                                       secondCSV,
                                       listSecondDishes,
                                       elementSecondDishes)

                secondCSV = value[0]

                if value[2] == True:
                    responseListFood.append(value[1])

            if listMeal.get('single dish')[2] in typeOfMeal[i]:
                value = catResponse2(True,
                                       sideCSV,
                                       listSideDishes,
                                       elementSideDishes)

                sideCSV = value[0]

                if value[2] == True:
                    responseListFood.append(value[1])

            if listMeal.get('single dish')[3] in typeOfMeal[i]:
                value = catResponse2(True,
                                       fruitCSV,
                                       listFruit,
                                       elementFruit)

                fruitCSV = value[0]

                if value[2] == True:
                    responseListFood.append(value[1])

    writing(str(date.isocalendar(date.today())[1])+'First.csv', firstCSV)
    writing(str(date.isocalendar(date.today())[1])+'Second.csv', secondCSV)
    writing(str(date.isocalendar(date.today())[1])+'Side.csv', sideCSV)
    writing(str(date.isocalendar(date.today())[1])+'Fruit.csv', fruitCSV)

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
    responseListFood = []

    typeOfMeal = action.get('parameters').get('TypeOfMeal')

    response = responseList[random.randint(0, 1)]  # imposto la risposta di default

    firstCSV = reading(str(date.isocalendar(date.today())[1]) + 'First.csv')
    secondCSV = reading(str(date.isocalendar(date.today())[1]) + 'Second.csv')
    sideCSV = reading(str(date.isocalendar(date.today())[1]) + 'Side.csv')
    fruitCSV = reading(str(date.isocalendar(date.today())[1]) + 'Fruit.csv')

    listFirstDishes = firebaseList.get('first dishes')
    listSecondDishes = firebaseList.get('second dishes')
    listSideDishes = firebaseList.get('side dishes')
    listFruit = firebaseList.get('fruit')

    if len(typeOfMeal) == 1:
        if listMeal.get('meal') in typeOfMeal:
            value = catResponse2(False,
                                 firstCSV,
                                 listFirstDishes,
                                 None)

            firstCSV = value[0]

            if value[2] == True:
                responseListFood.append(value[1])

            value = catResponse2(False,
                                   secondCSV,
                                   listSecondDishes,
                                   None)

            secondCSV = value[0]

            if value[2] == True:
                responseListFood.append(value[1])

            value = catResponse2(False,
                                   sideCSV,
                                   listSideDishes,
                                   None)

            sideCSV = value[0]

            if value[2] == True:
                responseListFood.append(value[1])

            value = catResponse2(False,
                                   fruitCSV,
                                   listFruit,
                                   None)

            firstCSV = value[0]

            if value[2] == True:
                responseListFood.append(value[1])

        if listMeal.get('single dish')[0] in typeOfMeal:
            value = catResponse2(False,
                                   firstCSV,
                                   listFirstDishes,
                                   None)

            firstCSV = value[0]

            writing(str(date.isocalendar(date.today())[1]) + 'First.csv', firstCSV)

            if value[2] == True:
                return response + value[1]
            else:
                return "My work is done, you've already eatten."

        if listMeal.get('single dish')[1] in typeOfMeal:
            value = catResponse2(False,
                                   secondCSV,
                                   listSecondDishes,
                                   None)

            secondCSV = value[0]

            writing(str(date.isocalendar(date.today())[1]) + 'Second.csv', secondCSV)

            if value[2] == True:
                return response + value[1]
            else:
                return "My work is done, you've already eatten."

        if listMeal.get('single dish')[2] in typeOfMeal:
            value = catResponse2(False,
                                   sideCSV,
                                   listSideDishes,
                                   None)

            sideCSV = value[0]

            writing(str(date.isocalendar(date.today())[1]) + 'Side.csv', sideCSV)

            if value[2] == True:
                return response + value[1]
            else:
                return "My work is done, you've already eatten."

        if listMeal.get('single dish')[3] in typeOfMeal:
            value = catResponse2(False,
                                 fruitCSV,
                                 listFruit,
                                 None)

            fruitCSV = value[0]

            writing(str(date.isocalendar(date.today())[1]) + 'Fruit.csv', fruitCSV)

            if value[2] == True:
                return response + value[1]
            else:
                return "My work is done, you've already eatten."

    if len(typeOfMeal) > 1:
        for i in range(0, len(typeOfMeal)):
            if listMeal.get('single dish')[0] in typeOfMeal[i]:
                value = catResponse2(False,
                                       firstCSV,
                                       listFirstDishes,
                                       None)

                firstCSV = value[0]

                if value[2] == True:
                    responseListFood.append(value[1])

            if listMeal.get('single dish')[1] in typeOfMeal[i]:
                value = catResponse2(False,
                                       secondCSV,
                                       listSecondDishes,
                                       None)

                secondCSV = value[0]

                if value[2] == True:
                    responseListFood.append(value[1])

            if listMeal.get('single dish')[2] in typeOfMeal[i]:
                value = catResponse2(False,
                                     sideCSV,
                                     listSideDishes,
                                     None)

                sideCSV = value[0]

                if value[2] == True:
                    responseListFood.append(value[1])

            if listMeal.get('single dish')[3] in typeOfMeal[i]:
                value = catResponse2(False,
                                     fruitCSV,
                                     listFruit,
                                     None)

                fruitCSV = value[0]

                if value[2] == True:
                    responseListFood.append(value[1])

    writing(str(date.isocalendar(date.today())[1]) + 'First.csv', firstCSV)
    writing(str(date.isocalendar(date.today())[1]) + 'Second.csv', secondCSV)
    writing(str(date.isocalendar(date.today())[1]) + 'Side.csv', sideCSV)
    writing(str(date.isocalendar(date.today())[1]) + 'Fruit.csv', fruitCSV)

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