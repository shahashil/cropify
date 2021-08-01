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
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import sqlite3
app = Flask(__name__)

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
            #print("Lat found")
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

########################### CHAIN CODE ##############################
    if (check_field_phone(rec)):
        temp=""
        print("Number alredy there")

    else:
      
        pol.message("Hey Welcome to Farm Help \n Please Enter your Land Location and soil image So we can get the weather condition of that area")
        print("response: Hey Welcome to Farm Help/ ")
        print("Please Enter your Land Location")
        insert_phone(rec)
        return str(pol)
 
    if(message_latitude):
        insert("lat",message_latitude,rec)
        insert("long",message_longitude,rec)
        print("response: Thankyou for sending the location.")
        pol.message("Thankyou for sending the location \n Now Send the Image of your Soil: ")
        return str(pol)
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
    
        API_KEY = "9PWTEYC3dF-_sx4gkKRR-iGDUv6mqnxH1XHtMxFAnnIx"
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

        payload_scoring = {"input_data": [{ "values": [ndarray]}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/e84aa939-b91d-4053-98ab-25ef9ad5eef6/predictions?version=2021-07-28', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})

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
        print(type(soil_type))
        
        pol.message("Your soil type is {} \n Now Type start_predict for prediction".format(soil_type))
        return str(pol)
    
############# / SOIL DONE #################################################
    if(msg=='start_predict'):
        if(check_field_lat(rec)):
            pass
        else:
            print("response please enter lcation")
            pol.message("please enter loc")
            return str(pol)

        if(check_field_soil(rec)):
            pass
        else:
            print("response please enter soil or send image")
            pol.message("please enter soil")
            return str(pol)

        get_lat = get_value("lat",rec)
        get_long = get_value("long",rec)
        soil = get_value("soil",rec)    
        #predict_crop(get_lat,get_long,get_soil)
        print(get_lat,get_long,soil)

    ###################### WEATHER API #################################
        api_url = 'https://api.weatherbit.io/v2.0/current?lat='+get_lat +'&lon=' + get_long + '&start_date=2021-07-25&end_date=2021-07-26&key=97af2b57bc734fd9ae8598817fd7a6bd'
        
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
   
        API_KEY = "9PWTEYC3dF-_sx4gkKRR-iGDUv6mqnxH1XHtMxFAnnIx"
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
        payload_scoring = {"input_data":[{"fields":["temperature","humidity","soil","rainfall"],"values":[[ temp, humidity,soil, rain ]]}]}
        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/77e13aac-f583-4024-bdae-b8f8c8ff1414/predictions?version=2021-07-27', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
        print("Predicted Crop According to your soil and Location is ")
        predicted_crop =response_scoring.json()
        predicted_crop= predicted_crop["predictions"][0]["values"][0][0]
        print(predicted_crop)
        insert("crop",predicted_crop,rec)
        if(predicted_crop):
            pol = MessagingResponse()
            pol.message("Predicted Crop is {}".format(predicted_crop))
            return str(pol)




################################ END CHAIN CODE ###########################
    return str(pol)
    
if __name__ == "__main__":
    app.run(debug=True)

