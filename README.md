# Cropify
Call for Code Submission Repository
## What is Cropify?
Cropify is a WhatsApp chatbot made with Twilio using IBM's Watson's machine learning which helps farmers to get predict their crops for better yield .
In Cropify farmers can get weekly analysis of weather condition which would be much helpful for their crops. Also we understand that at farms you may not get an Internet connection every time so we can send them daily alerts on SMS by which they can take appropriate action for their crops. They can activate or deactivate the alerts anytime . We created a Notebook Job in IBM Cloud Pak which will create daily SMS alerts for the weather analysis
Cropify uses IBM Watson's powerful computation to predict the soil type by deploying image recognition model on IBM space and crops are predicted by getting the locations temperature humidity and temperature which are get by using weather Bit company Api, and the crops are predicted by scoring those parameters on Machine Learning Model made with AutoAI. We have taken refrence from many sources for the needed parameters value or range for best yield and have trained our model according.
## The Problem.
Maximum crops are produced from small scale or marginal farmers of those many lack much needed Knowledge or they dont have any proper access to proper information on the suitable requirements to grow crops through which they get best yield. Also due to unpredictable weather conditions many crops are affected or destroyed sometimes due to extreme weather conditions. Also not many farmers get access to a 3G/4G internet through which they can get proper information on weekly or daily  weather. 
## How Cropify Helps Them.
Cropify hepls them from identifying the type of soil they have on their land, getting the locations Avg. rainfall, temperature and humidity .
Cropify then takes this parameters and predict the type of crop they should  grow  for best yield.
Cropify also provides them for weeks weather so that they can plan accordingly.
Keeping the Internet connectivity problem in mind faemers can receive alerts on weather for their crops on SMS, so even if they are not connected they still can get SMS for weather conditions.
Farmers can initialize this product when the connection is available and once the soil, crops are predicted and the alert service is activated they can receive weather updates on SMS, so no connectivity problem.

## Solution Flow
<img src="https://github.com/shahashil/cropify/blob/main/cropify_flow.PNG">
The  message sent from farmer through WhatsApp is sent to twilio which then forwards our request to the Flask app. If the requested service is to predict the type of soil
then image is then  forwarded to the deployed Image Recognition Model in IBM Watson and after getting the prediction back its information is saved in our databse SQLite3.
After that User needs to send their location of land, in WhatsApp by which we will retrive their coordinates and store it in our database. Once the user request to get prediction on the type of crop to grow we take the coordinates stored in database and get humidity, rain and temperature for that location with WeatherBit API and forward it as a parameter along with the type of soil already predicted to the Machine Learning Model Created with AutoAI Expreriment in IBM Watson. Along with that you can also get Weekly weather updates on your WhatsApp. A Notebook Job is setup in IBM Watson which will set out a HTTP request to our flask app which will then send out daily SMS alert according to our crop predicted.


<!--- NEXT GOAL  --->
<!---
## Road Map
<img src="https://github.com/shahashil/cropify/blob/main/Cropify%20roadmap.png">

### Next Goals
The current changes or addition we're working on is getting better data on the crop requirement for better yield also getting more insights on that. After that we're trying to better our Image recognition algorithms for better classificaiton of images based on the texture and adding additional feature on predicting it by the availability of types of soil in that area or region. After that we're trying to get better sources for weather APIs to get better prediction. To get better on our alert systems along with adding solutions for extreme weathers which could help them to save crops.

### Next Goals
Create a Forum type architecture where Farmers can send their questions or can ask for help or can send crop images for health checkup to the regisgtered experts from their WhatsApp only which would be handy for them in case of emergencies. Next we will try to Make a better flow of conversation and to make it feel more humanly we will integrate Watson Assist which would make conversations better.

### Next Goals
Create better authentification system for new users to join. creating New Feature where uesers can opt to receive 'Ask for Help' from other farmers on WhatsApp.

### Around Mid 2022
Look out for farmers which would benefit from this project and start pilot project. After that analysing the results and improving our system or algorithms before starting the service for other people.
--->
<!--- Coomments --->

## Getting Started
**Prerequisite**
+ Register for [IBM Cloud Account](https://cloud.ibm.com/registration)
+ Get weatherBit API key or any other Weather API key 
+ Setup [Twilio Account](https://www.twilio.com/try-twilio)

Create a Machine Learning and IBM Watson Service in IBM Cloud.
From there in IBM cloud Pak for Data create a AutoAI expreriment and choose to train csv file of data for parameters(Temperature, Humidity, Rainfall and soil) for which the predicted crop gives high yield. Save the pipleline with the highest accuracy and save that as mdoel and promote it to deployemnt sapce and deploy it. Get the Python code generated for accessing the Model for prediction. It will require you to enter IAM api key which can be generated from [IBM Cloud IAM Key](https://cloud.ibm.com/iam).

To Make an image recognition Model you can train its model in Notebook in IBM cloub pak, but to train the dataset for Images you first need to uplaod it to any Object bucket, before that you need to create an storage service. To get access of objects in bucket create service credentials and copy its credentials. The code to download it is provided in the (uploaded)notebook itself. Then after training you need to create and publish its model to deployment space and then deploy it. Again copy the Python code generated for accessing the Model for prediction through REST API.

To send Http Request in Flask app create a Notebook job and in that write code to send out a post or get http request to your Flask url and append '/alert' for alerts route. Set the job scheduling to Daily if you want to send Alerts daily.

In the Twilio account you need to give Webhook link of the flask app   and append '/sms' for our App route, in WhatsApp settings in programmable Message tab.

The main driver code file is uploaded as 'main.py'

## Output Images



![alt-text-1](https://raw.githubusercontent.com/shahashil/cropify/main/Images/crop1.PNG "") ![alt-text-1](https://raw.githubusercontent.com/shahashil/cropify/main/Images/crop2.PNG "") ![alt-text-1](https://raw.githubusercontent.com/shahashil/cropify/main/Images/crop4.PNG "") ![alt-text-1](https://raw.githubusercontent.com/shahashil/cropify/main/Images/crop3.PNG "")
