# import flask dependencies
from flask import Flask, request, make_response, jsonify, send_from_directory
from DialogflowAgent import get_reply
import os
from twilio.twiml.messaging_response import MessagingResponse

# import userClass

from generateResponse import formatResponse, generateResponse

phone=''

# initialize the flask app
app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='images/favicon.ico')

# default route
@app.route('/')
def index():
    return 'Rentaly Bot'





# function for responses
def results(phone):
    # build a request object
    req = request.get_json(force=True)

    # define variables
    newPrice=''
    roomNum=''
    propertyCode=''
    status=''
    decision=''
    

    # fetch intent from json
    result = req.get('queryResult')

    intent = str(result.get('intent').get('displayName'))
    # print(intent, '\n\n', result)
    
    if intent == 'Update Rent' or intent == 'Update Vacancy': 
        try:
            status = str(result.get('parameters').get('roomStatus'))  
            propertyCode = str(result.get('parameters').get('propertyCode'))  
            roomNum = int(result.get('parameters').get('roomNumber'))   
            roomNum = str(roomNum)
            newPrice = str(result.get('parameters').get('roomCost').get('amount'))              
        except Exception:
            pass 
        
       
    if intent == 'Update Rent - getRoomNumber' or intent == 'Update Vacancy - getRoomNumber':     
        roomNum = int(result.get('parameters').get('roomNumber'))   
        roomNum = str(roomNum)

    if intent == 'Update Rent - getRoomCost':  
        newPrice = str(result.get('parameters').get('roomCost').get('amount'))    
        roomNum  = int(result.get('outputContexts')[1].get('parameters').get('roomNumber'))
        roomNum = str(roomNum)
        propertyCode= str(result.get('outputContexts')[1].get('parameters').get('propertyCode'))
    
    if intent == 'Update Vacancy - getRoomStatus':  
        status = str(result.get('parameters').get('roomStatus'))    
        roomNum  = int(result.get('outputContexts')[1].get('parameters').get('roomNumber'))
        roomNum = str(roomNum)
        propertyCode= str(result.get('outputContexts')[1].get('parameters').get('propertyCode'))
   

    if intent == 'Update Rent - Confirmation':
        newPrice = str(result.get('outputContexts')[1].get('parameters').get('roomCost').get('amount'))
        roomNum  = int(result.get('outputContexts')[1].get('parameters').get('roomNumber'))
        roomNum = str(roomNum)        
        propertyCode= str(result.get('outputContexts')[1].get('parameters').get('propertyCode'))
        decision = str(result.get('parameters').get('confirmation'))  

    if intent == 'Update Rent - Steps Confirmation':
        newPrice = str(result.get('outputContexts')[0].get('parameters').get('roomCost').get('amount'))
        roomNum  = int(result.get('outputContexts')[0].get('parameters').get('roomNumber'))
        roomNum = str(roomNum)        
        propertyCode= str(result.get('outputContexts')[0].get('parameters').get('propertyCode'))
        decision = str(result.get('parameters').get('confirmation'))  

    if intent == 'Update Vacancy - Confirmation':
        propertyCode = str(result.get('outputContexts')[1].get('parameters').get('propertyCode'))  
        roomNum = int(result.get('outputContexts')[1].get('parameters').get('roomNumber'))   
        roomNum = str(roomNum)         
        status = str(result.get('outputContexts')[1].get('parameters').get('roomStatus')) 
        decision = str(result.get('parameters').get('confirmation'))

    if intent == 'Update Vacancy - Steps Confirmation':
        propertyCode = str(result.get('outputContexts')[1].get('parameters').get('propertyCode'))  
        roomNum = int(result.get('outputContexts')[1].get('parameters').get('roomNumber'))   
        roomNum = str(roomNum)         
        status = str(result.get('outputContexts')[1].get('parameters').get('roomStatus')) 
        decision = str(result.get('parameters').get('confirmation'))
     
    # generate appropriate response
    botMessage = generateResponse(intent, newPrice, propertyCode, roomNum, phone, status, decision)

    # return a fulfillment response
    return formatResponse(botMessage)

# create a route for dialogflow fufilment webhook
@app.route('/dialogflow', methods=['GET', 'POST'])
def webhook():    
    
    # open and read the file after the appending:    
    f = open("current.txt", "r")    
    phone =f.read()
    f.close()
    
    # return response
    return make_response(jsonify(results(phone)))

# create a route for twilio webhook
@app.route("/chat", methods=['GET','POST'])
def bot_reply():   
    # Fetch the message from user
    phone = request.form.get('From').strip('whatsapp:+')    
    msg = request.form.get('Body')
    
    # writing current user's phone number to file
    f = open("current.txt", "w")
    f.write(phone)
    f.close()



    
    # Create reply to user
    resp = MessagingResponse()
    reply = get_reply(msg, phone)
    print('Reply: '+reply)
    resp.message(reply)


    return str(resp)


# run the app
if __name__ == '__main__':
#    app.secret_key = 'super secret key'
#    app.config['SESSION_TYPE'] = 'filesystem'

  
   app.run()