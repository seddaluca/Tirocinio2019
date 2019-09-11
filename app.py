import firebase as firebase
from flask import Flask, request, make_response, jsonify
from datetime import date

import random

from firebase import firebase
from setUp import SetUp

# initialize the flask app
app = Flask(__name__)

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

    if (action.get('action') != None):
        if (action.get('action') == 'input.unknown'):
            return {'fulfillmentText': queryText}

    if (action.get('action') == 'input.meal'):
        return {'fulfillmentText': response(action)}

# create a route for webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # return response
    return make_response(jsonify(results()))

def response(action):

    responseList = ['I suggest you',
                    'I recommend you']

    response = responseList[random.randint(0, 1)] + ' - ' + str(date.today()) + ' - '# imposto la risposta di default

    typeOfMeal = action.get('parameters').get('TypeOfMeal')

    print(str(date.today().isocalendar()[1]))

    firebaseList = {
        "first dishes": [{
            0: {"take": 2, "calories": 200, "name": "Vegetagle Soup"}
        }, {
            1: {"take": 2, "calories": 250, "name": "Vegetable couscous"}
        }, {
            2: {"take": 2, "calories": 350, "name": "Pasta with artichokes"}
        }, {
            3: {"take": 2, "calories": 230, "name": "Mushroom and Potato Soup"}
        }, {
            4: {"take": 2, "calories": 210, "name": "Cream of Pumpkin"}
        }, {
            5: {"take": 2, "calories": 360, "name": "Ricotta Pasta"}
        }, {
            6: {"take": 2, "calories": 360, "name": "Tagliatelle with Mushrooms"}
        }, {
            7: {"take": 2, "calories": 375, "name": "Spaghetti with Garlic and Oil"}
        }, {
            8: {"take": 2, "calories": 385, "name": "Gnocchi with Tomato Sauce"}
        }],

        "fruit" : [{
            0: {"take": 2, "calories": 89, "name": "banana"}
        }, {
            1: {"take": 2, "calories": 52, "name": "apple"}
        }, {
            2: {"take": 2, "calories": 57, "name": "pear"}
        }],

        "second dishes" : [{
            0: {"take": 2, "calories": 290, "name": "Grilled Lamb Chops"}
        }, {
            1: {"take": 2, "calories": 185, "name": "Hard Boiled Eggs"}
        }, {
            2: {"take": 2, "calories": 200, "name": "Grilled Pork Chops"}
        }, {
            3: {"take": 2, "calories": 220, "name": "Paprika Chicken Legs"}
        }, {
            4: {"take": 2, "calories": 250, "name": "Sea Bass in Salt Crust"}
        }, {
            5: {"take": 2, "calories": 270, "name": "Pan-Fried Chicken"}
        }],

        "side dishes": [{
            0: {"take": 2, "calories": 77, "name": "potato"}
        }, {
            1: {"take": 2, "calories": 18, "name": "tomato"}
        }]
    }

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

    list = {'meal': 'meal',
            'single dish': ['first',
                            'second',
                            'side dish',
                            'fruit']
            } # lista di supporto per suddividere le tipologie di pasti

    if len(typeOfMeal) == 1:
        if list.get('meal') in typeOfMeal:
            return response + elementFirstDishes.get("name") + ' (' + str(elementFirstDishes.get("calories")) + ' kcal), ' + \
                   elementSecondDishes.get("name") + ' (' + str(elementSecondDishes.get("calories")) + ' kcal), ' + \
                   elementSideDishes.get("name") + ' (' + str(elementSideDishes.get("calories")) + ' kcal) and ' + \
                   elementFruit.get("name") + ' (' + str(elementFruit.get("calories")) + ' kcal)'


        if list.get('single dish')[0] in typeOfMeal:
            return response + elementFirstDishes.get("name") + ' (' + str(elementFirstDishes.get("calories")) + ' kcal)'

        if list.get('single dish')[1] in typeOfMeal:
            return response + elementSecondDishes.get("name") + ' (' + str(elementSecondDishes.get("calories")) + ' kcal)'

        if list.get('single dish')[2] in typeOfMeal:
            return response + elementSideDishes.get("name") + ' (' + str(elementSideDishes.get("calories")) + ' kcal)'

        if list.get('single dish')[3] in typeOfMeal:
            return response + elementFruit.get("name") + ' (' + str(elementFruit.get("calories")) + ' kcal)'

    if len(typeOfMeal) > 1:
        for i in range(0, len(typeOfMeal)):
            if list.get('single dish')[0] in typeOfMeal[i]:
                response += elementFirstDishes.get("name") + ' (' + str(elementFirstDishes.get("calories")) + ' kcal)'

            if list.get('single dish')[1] in typeOfMeal[i]:
                response += elementSecondDishes.get("name") + ' (' + str(elementSecondDishes.get("calories")) + ' kcal)'

            if list.get('single dish')[2] in typeOfMeal[i]:
                response += elementSideDishes.get("name") + ' (' + str(elementSideDishes.get("calories")) + ' kcal)'

            if list.get('single dish')[3] in typeOfMeal[i]:
                response += elementFruit.get("name") + ' (' + str(elementFruit.get("calories")) + ' kcal)'

            if i == len(typeOfMeal)-2:
                response += ' and '
            elif i < len(typeOfMeal)-1:
                response += ', '

        return response

    return 'None'

# run the app
if __name__ == '__main__':
   app.run()