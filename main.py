from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from PIL import Image
import requests 
import shutil 
from ibm_watson_machine_learning import APIClient
import ibm_boto3
from ibm_botocore.client import Config
import json
import numpy as np
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import sqlite3
from datetime import date
import datetime
from twilio.rest import Client

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/sms", methods=['POST'])

def sms_reply():
    #############ALL DATABASE FUNCTIONS #########################################
    def check_field_phone(value):
        conn =sqlite3.connect("./db-browser/crops_user.db")
        cur = conn.cursor()
        cur = conn.execute("SELECT phone from users where phone= '{}' ".format(value))
        rows = cur.fetchall()
        conn.close()
        if(len(rows)>0):
            return True
        else:
            return False
    def insert_phone(phone):
        conn =sqlite3.connect("./db-browser/crops_user.db")
        conn.execute("INSERT INTO  users (phone) values ('{}')".format(phone))
        conn.commit()
        conn.close()
        return True

    def insert(field,value,phone):
        conn =sqlite3.connect("./db-browser/crops_user.db")
        conn.execute("update users set {} = '{}' where phone='{}'".format(field,value,phone))
        conn.commit()
        conn.close()
        return True

    def check_field_lat(value):
        conn =sqlite3.connect("./db-browser/crops_user.db")
        cur = conn.cursor()
        cur = conn.execute("SELECT lat from users where phone= '{}' ".format(value))
        rows = cur.fetchall()
        conn.close()
        if rows[0][0]:
            return True
        else:
            return False

    def check_field_soil(value):
        conn =sqlite3.connect("./db-browser/crops_user.db")
        cur = conn.cursor()
        cur = conn.execute("SELECT soil from users where phone= '{}' ".format(value))
        rows = cur.fetchall()
        conn.close()
        if rows[0][0]:
            return True
        else:
            return False

    def get_value(field,number):
        conn =sqlite3.connect("./db-browser/crops_user.db")
        cur = conn.cursor()
        rows = cur.fetchall()
        cur = conn.execute("SELECT {} from users where phone ='{}'".format(field,number))
        for rows in cur:
            return rows[0]


 ###################################### END OF FUNC ##########################       
    """Respond to incoming calls with a simple text message."""
    # Fetch the message 
    msg = request.form.get('Body')
    media_msg = request.form.get('NumMedia') #return 1 if media
    pic_url = request.form.get('MediaUrl0') 
    rec=request.form.get('From')
    rec=rec[9:]
    message_latitude = request.values.get('Latitude') 
    message_longitude = request.values.get('Longitude') 
    loc = request.values.get('Location')
    print(type(message_latitude))
    pol = MessagingResponse()
    # pol.message("You said: {}".format(rec))
    data = request.data

    print("My data is :",data)
########################### CHAIN CODE ##############################
    if(msg=='Help'):
        pol.message("This are our Steps \n 1). First is you provide you location \n 2). Second is you provide your soil image or type soil_type typeofyoursoil \n 3). Type start_predict for prediction \n 4).To get next week's weather, type next_week_weather \n 5).To get daily updates on weather, type send_alerts and to stop the updates type dont_send_alerts")
    if (check_field_phone(rec)):
        temp=""
        print("Number alredy there")

    else:
      
        pol.message("Hey Welcome to Cropify \nPlease Enter your Land Location\nType Help for Details")
        print("response: Hey Welcome to Cropify/ ")
        print("Please Enter your Land Location")
        insert_phone(rec)
      
 
    if(message_latitude):
        insert("lat",message_latitude,rec)
        insert("long",message_longitude,rec)
        print("response: Thankyou for sending the location.")
        pol.message("Thankyou for sending the location \n Now Send the Image of your Soil Or Give it by the code soil_type typeofyoursoil: ")
    if(msg[0:9] =="soil_type"):
        #image_code
        input_soil_type= msg[10:]
        insert("soil", input_soil_type,rec)
        print("Your soil type is ",input_soil_type)
        pol.message("Thankyou we got your Soil type \nTo start prediction enter start_predict")  
    if(media_msg=='1'):
        
        #image_code
        image_url = pic_url
        global filename 
        filename= image_url.split("/")[-1]
        filename = filename+".jpg"
        r = requests.get(image_url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)  
            print('Image sucessfully Downloaded: ',filename)
        else:
            print('Image Couldnt be retreived')
          ################################################### PREPROCESS SOIL IMAGE  #########################3

        img = keras.preprocessing.image.load_img(
        filename, target_size=(150,150)
        )

        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0) # Create a batch
        ndarray=img_array.numpy()
        ndarray=ndarray.reshape(150,150,3)
        ndarray=ndarray.tolist()

        ################################################### / PREPROCESS SOIL IMAGE #########################3
    
        API_KEY = "cloud IAM api "
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

        payload_scoring = {"input_data": [{ "values": [ndarray]}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.comdeployment_url', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})

        #print(response_scoring.json())
        classes=['alluvial', 'black', 'clay', 'sandyloam']
        predicted_soil = response_scoring.json()#{'predictions': [{'id': 'dense_5', 'values': [[2.0097508430480957, -3.827359199523926, 1.7766461372375488, 2.20627760887146]]}]}
        predicted_soil = classes[np.argmax(predicted_soil["predictions"][0]["values"])]
        #print(predicted_soil)
        global soil_type
        soil_type=''
        soil_type=predicted_soil
        #soil_type=predict_soil_type(soil)
        insert("soil", soil_type,rec)
        print("Your soil type is ",soil_type)
        print("To start prediction enter start_predict")
        pol.message("Your soil type is {} \n Now Type start_predict for prediction".format(soil_type))
   
  ############# / SOIL DONE #################################################
    
    if(msg=='start_predict'):
        if(check_field_lat(rec)):
            pass
        else:
            print("response please enter location")
            pol.message("please enter loc")
          

        if(check_field_soil(rec)):
            pass
        else:
            print("response please enter soil or send image")
            pol.message("please enter soil")

        get_lat = get_value("lat",rec)
        get_long = get_value("long",rec)
        soil = get_value("soil",rec)    
        #predict_crop(get_lat,get_long,get_soil)
        print(get_lat,get_long,soil)

    ###################### WEATHER API #################################
        start_date =str(date.today()+datetime.timedelta(days=i))
        end_date = str(date.today()+datetime.timedelta(days=i+1))
        
        api_url = 'https://api.weatherbit.io/v2.0/current?lat='+get_lat +'&lon=' + get_long + '&start_date='+start_date+'&end_date='+end_date+'&key=apikey'
        
        token_response = requests.post(api_url)
        ans=token_response.json()
        #print(ans)
        rain=ans["data"][0]["pres"]
        rain = rain/10
        #print(rain)
        temp=ans["data"][0]["temp"]
        #print(ans["data"][0]["temp"])
        humidity=ans["data"][0]["rh"]
        #print(ans["data"][0]["rh"])

############################## / WEATHER API ###################################
 ##################################################   CROP PREDICTION ###########################
   
        API_KEY = "cloud IAM api "
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
        payload_scoring = {"input_data":[{"fields":["temperature","humidity","soil","rainfall"],"values":[[ temp, humidity,soil, rain ]]}]}
        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/deployment_url', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
        print("Predicted Crop According to your soil and Location is ")
        predicted_crop =response_scoring.json()
        predicted_crop= predicted_crop["predictions"][0]["values"][0][0]
        print(predicted_crop)
        insert("crop",predicted_crop,rec)
        if(predicted_crop):
            pol = MessagingResponse()
   
         pol.message("Predicted Crop is {}".format(predicted_crop))

    if msg=='next_week_weather':
        resp_message=""
        for i in range(7):
            start_date =str(date.today()+datetime.timedelta(days=i))
            end_date = str(date.today()+datetime.timedelta(days=i+1))
            get_lat= get_value("lat",rec)
            get_long = get_value("lat",rec)
            rec = rec
            api_url = 'https://api.weatherbit.io/v2.0/current?lat='+get_lat +'&lon=' + get_long + '&start_date='+start_date+'&end_date='+end_date+'&key=api_key'
            token_response = requests.post(api_url)
            ans=token_response.json()
            rain=ans["data"][0]["precip"]
            rain = rain/10
            temp=ans["data"][0]["temp"]
            pred_type=ans["data"][0]["weather"]['description']
            humidity=ans["data"][0]["rh"]
            resp_message =resp_message+ "\nFor Day "+str(i+1)+"\nRain :"+str(rain)+" mm\nTemperature(Avg.): "+str(temp)+"\nHumidity: "+str(humidity)+"\nWeather: "+pred_type
        
        pol.message(resp_message)
    if(msg=="send_alerts"):
        insert("help","yes",rec)
        pol.message("Alert Service Activated")

    if(msg=="dont_send_alerts"):
        insert("help","no",rec)
        pol.message("Alert Service Dectivated")
################################ END CHAIN CODE ###########################
    return str(pol)

@app.route("/alert", methods=['GET'])
def alert():
    ##############################FUNCTIONS###############################
    def verify_help(number):
        conn =sqlite3.connect("./db-browser/crops_user.db")
        cur = conn.cursor()
        rows = cur.fetchall()
        cur = conn.execute("SELECT help from users where phone ='{}'".format(number))
        for rows in cur:
            if rows[0]=='yes':
                return True
            else:
                return False

    def get_value(field,number):
        conn =sqlite3.connect("./db-browser/crops_user.db")
        cur = conn.cursor()
        rows = cur.fetchall()
        cur = conn.execute("SELECT {} from users where phone ='{}'".format(field,number))
        for rows in cur:
            return rows[0]
#     #max temp , low rainfall '''
    crops = [[30,80],[35,70],[35,35],[30,150],[28,50],[27,60]]
    crops_list = ["rice","wheat","Mung Bean","Tea","maize","cotton"]

    def send_reply(rec,msg):
        account_sid = 'account sid'
        auth_token = 'auth token'
        client = Client(account_sid, auth_token)
        message = client.messages \
                .create(
                body=msg,
                from_='+1616365XXXX', #twilio number
                to=rec
            )
            
    #rec=request.form.get('From')
    conn =sqlite3.connect("./db-browser/crops_user.db")
    cur = conn.cursor()
    rows = cur.fetchall()
    cur = conn.execute("SELECT phone from users ")
    for rows in cur:
        rec=rows[0]
        #rec='phone number'
        if(verify_help(rec)): #checks if service is activated
            start_date =str(datetime.date.today())
            end_date = str(date.today()+datetime.timedelta(days=1))
            get_lat= get_value("lat",rec)
            get_long = get_value("long",rec)
            print(start_date,end_date)
            print(get_lat,get_long)
            

            api_url = 'https://api.weatherbit.io/v2.0/current?lat='+get_lat +'&lon=' + get_long + '&start_date='+start_date+'&end_date='+end_date+'&key=apikey'
            token_response = requests.post(api_url)
            ans=token_response.json()
            rain=ans["data"][0]["pres"]
            rain = rain/10
            temp=ans["data"][0]["temp"]
            soil = get_value("crop",rec)
            soil_index=crops_list.index(soil)

            if crops[soil_index][0]<temp:
                msg="The Temperature Today is about to rise and would result in low yield for your crop. You shpuld try to cover your crops"
                send_reply(rec,msg)
                
            if crops[soil_index][1]>rain:
                msg="The rain might not be appropriate for youe Crop. Irrigate More for good yield"
                send_reply(rec,msg)
            else:
                send_reply(rec,"Everything Seems fine today")

    return "success"
if __name__ == "__main__":
    app.run(debug=True)
