#https://blog.techbridge.cc/2020/01/12/%E7%B0%A1%E6%98%8E-python-line-bot-&-liff-js-sdk%E5%85%A5%E9%96%80%E6%95%99%E5%AD%B8/
import pymongo
import pandas as pd
threshold_count = 5 #每五分鐘顯示一筆
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["solarsafety"]

from datetime import datetime,timedelta


from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ButtonsTemplate,
)

from linebot.models import TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
from linebot.exceptions import LineBotApiError
import pyimgur
CLIENT_ID = "xxxxxxxx"






channel_secret = "dc152d1bb53d2d27c763d770fc12974f"
channel_access_token = "wfGhN6VZ+rBoK2QRhIo9nnL+toOzUS6G/fMg6vUpZDmIbvtUoymNLp6SWqvZ06LjvZol2k6nb3DkdWgpAYyl/voxZC2/+yQBkT0E/TNzjL8uJrRqyqO9tWlPtBwjFB2Qr5iWtcpIDtDR+U8Aulo5yQdB04t89/1O/w1cDnyilFU="


app = Flask(__name__)

    
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


def insert_notification(title,target,time,content,email):
    col = db["notification"]
    data = {
        "EventID":email+time,
        "Title":title,
        "System":target,
        "Time":time,
        "Content":content,  
        "Email":email      
    }
    try:
        col.insert_one(data)  
        return True
    except Exception as e:
        print("Error message: ", e)    
        return False         
def update_user_LineID(Line_token,LineID):
    col = db["user"]

    res = query_user_by_Line_token(Line_token)
    #print(res)
    if res == False:
        return "No this user"
    else:

        update_data = {"$set":{"LineID":LineID}}
        query = {
            "LineToken":Line_token,
        }   
        try:
            col.update_one(query,update_data)
            print("res['Email']",res['Email'])
            return res['Email']
        except Exception as e:
            print("Error message: ", e)    
            return False 
        
def query_temp_LineID(LineID):
    time = (datetime.today()-timedelta(hours=1)).strftime("%Y/%m/%d %H:%M:%S")
    time = (datetime.today()-timedelta(minutes=5)).strftime("%Y/%m/%d %H:%M:%S")

    field_show = {"_id":0,"LineID":1,"Time":1}    
    query = {
        "LineID":LineID,
    }
    collection = db["LineID"]
    result = list(collection.find(query,field_show))
    if result == []:
        return False
    else:
        if result[0]['Time'] <  time:
            collection.delete_one(query)
            return "Time out"
        else:
            return True


def insert_Line_ID_list(Line_ID,time):
    col = db["LineID"]
    data = {
        "LineID":Line_ID,
        "Time":time,
    }    

    try:
        x = col.insert_one(data)
        print("Temp LineID Insert Success",x)
        return True        
    except Exception as e:
        print("Temp LineID Insert failure")
        return False

def query_user_by_Line_token(Line_token):
    field_show = {"_id":0,"LineID":1,"Email":1}    
    query = {
        "LineToken":Line_token,
    }
    collection = db["user"]
    result = list(collection.find(query,field_show))
    if result == []:
        print("No this user")
        return False
    else:
        return result[0] 

def query_user_by_LineID(LineID):
    field_show = {"_id":0,"Email":1,"Password":1,"CollectionNameList":1,"LineID":1}    
    query = {
        "LineID":LineID,
    }
    collection = db["user"]
    result = list(collection.find(query,field_show))
    if result == []:
        print("No this user")
        return False
    else:
        return result[0]  
    
def query_device_year_data(device_ID,year):
    field_show = {"_id":0,"Data":1}    
    query = {
        "DeviceID":device_ID,
        "Year":year,
    }
    collection = db["DevID_Year_Data"]
    result = list(collection.find(query,field_show))
    return result

def query_device_month_data(device_ID,year,month):
    #print(device_ID,year,month)
    field_show = {"_id":0,"Data":1}    
    query = {
        "DeviceID":device_ID,
        "Year":year,
        "Month":month,
    }
    collection = db["DevID_Month_Data"]
    result = list(collection.find(query,field_show))
    return result


def query_all_device():
    field_show = {"_id":0,"DeviceID":1,"CollectionName":1}
    collection = db["device"]
    result = collection.find({},field_show)
    df = pd.DataFrame(list(result))
    return list(df['DeviceID']),list(df['CollectionName'])


def query_all_system_by_collection(system):
    field_show = {"_id":0,"系統名稱":1,"GatewayID":1,"系統類型":1,"系統位置":1,"系統容量":1,"系統開始時間":1,"總累積電量":1,"Device數量":1}  
    query = {
        "CollectionName":system,
    }    
    collection = db["system"]
    result = collection.find(query,field_show)  

    return list(result)
def query_single_system_by_collection_name(system):
    field_show = {"_id":0,"系統名稱":1}   
    query = {
        "CollectionName":system,
    }        
    collection = db["system"]
    result = list(collection.find(query,field_show))
    print("result",result)
    res = result[0]['系統名稱']    
    return res

def query_single_system(system):
    field_show = {"_id":0,"DevicesID":1,"AUOCollectionName":1}   
    query = {
        "CollectionName":system,
    }        
    collection = db["system"]
    result = list(collection.find(query,field_show))

    return result


def query_single_device(device_ID):
    field_show = {"_id":0,"系統名稱":1,"GatewayID":1,"DeviceID":1,"Device類型":1,"Device位置":1,"Device容量":1,"Device開始時間":1,"總累積電量":1}    
    collection = db["device"]
    result = collection.find({"DeviceID":device_ID},field_show) 

    field_show = {"_id":0,"CollectionName":1,"AUOCollectionName":1}    
    collection = db["device"]
    collection_name = list(collection.find({"DeviceID":device_ID},field_show))[0]['CollectionName']
    collection_name_AUO = list(collection.find({"DeviceID":device_ID},field_show))[0]['AUOCollectionName']    
    
    return list(result),collection_name,collection_name_AUO



def query_last_data(collection_name,device_ID):
    field_show = {"_id":0,"DevID":1,"DevHumidity":1,"DevTemperature":1,"DevPower":1,"DevCurrent":1,"DevVoltage":1,"DateTime":1}   
    collection = db[collection_name]
    result = list(collection.find({"DevID":device_ID},field_show).sort([('DateTime', -1)]).limit(-1))
    if result != []:
        return result[0]
    else:
        return False

def query_last_data_AUO(collection_name):
    field_show = {"_id":0,"DateTime":1,"IrradiationAvg":1,"HumidityAvg":1,"TemperatureAvg":1,"Direction":1,"Gust":1,"Speed":1}   
    collection = db[collection_name]
    result = list(collection.find({},field_show).sort([('DateTime', -1)]).limit(-1))
    #print(result,CollectionName)
    if result == []:
        return []
    return result[0]


def query_data_all(collection_name,device_ID,start_day,end_day):

    field_show = {"DevID":1,"DevHumidity":1,"DevTemperature":1,"DevPower":1,"DevCurrent":1,"DevVoltage":1,"DateTime":1}    
    query = {
        "DevID":device_ID,
        "$and":
        [
        {"DateTime":{"$gte":start_day}}
        ,{"DateTime":{"$lte":end_day}}

        ]}
    collection = db[collection_name]
    result = list(collection.find(query,field_show))    
    
    
    if 'phoebot' in collection_name:
        threshold_count = 5
        
        data = {"DevPower":[],"DevCurrent":[],"DevVoltage":[],"DevHumidity":[],"DevTemperature":[],"DateTime":[]}
        count = 0
        for r in result:
            if count % threshold_count == 0:
                if r["DevPower"] == 0:
                    data["DevPower"].append(r["DevPower"])
                else:
                    data["DevPower"].append(r["DevPower"]/100)

                if r["DevCurrent"] == 0:
                    data["DevCurrent"].append(r["DevCurrent"])
                else:
                    data["DevCurrent"].append(r["DevCurrent"]/10000)

                if r["DevVoltage"] == 0:
                    data["DevVoltage"].append(r["DevVoltage"])
                else:
                    data["DevVoltage"].append(r["DevVoltage"]/1000)    

                data["DevHumidity"].append(r["DevHumidity"])
                data["DevTemperature"].append(r["DevTemperature"])
                data["DateTime"].append(r["DateTime"][5:16])
            count+=1        
        
        
        
    else:
        threshold_count = 1
 
        data = {"DevPower":[],"DevCurrent":[],"DevVoltage":[],"DevHumidity":[],"DevTemperature":[],"DateTime":[]}
        count = 0
        for r in result:
            if count % threshold_count == 0:
                data["DevPower"].append(r["DevPower"])

                data["DevCurrent"].append(r["DevCurrent"])
 

                data["DevVoltage"].append(r["DevVoltage"])
 

                data["DevHumidity"].append(r["DevHumidity"])
                data["DevTemperature"].append(r["DevTemperature"])
                data["DateTime"].append(r["DateTime"][5:16])
            count+=1
    return data






def send_image(target,to):
    if target == 'power':
        PATH = "figure/"+target+".png" #A Filepath to an image on your computer"
        title = "power"
        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title=title)
        print(uploaded_image.link)

        
    image_url = uploaded_image.link
    
    try:
        line_bot_api.push_message(to, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
    except LineBotApiError as e:
        # error handle
        raise e        


# 此為 Webhook callback endpoint
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body（負責）
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# decorator 負責判斷 event 為 MessageEvent 實例，event.message 為 TextMessage 實例。所以此為處理 TextMessage 的 handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    today = datetime.today().strftime("%Y/%m/%d")
    tomorrow = (datetime.today()+timedelta(days=1)).strftime("%Y/%m/%d")
    now_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")

    input_text = event.message.text
    Line_ID =  event.source.user_id
        
    print("event.source.userId",event.source.user_id)
    
    user_data = query_user_by_LineID(Line_ID)
    print(user_data)

        
    if user_data == False:
        flag2 = query_temp_LineID(Line_ID)
        if flag2 == True: #已經有輸入過"使用者認證"
            flag3 = update_user_LineID(input_text,Line_ID)
            #print("flag3",flag3)
            if '@' in flag3 :
                result = "認證成功"
                now_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
                insert_notification("Line 認證成功","PowerWatcher LINE帳號",now_time,"您已經認證Line帳號，現在開始可以使用PowerWatcher LINE官方帳號做系統操作",flag3)
            elif flag3 == False:
                result = "認證失敗請洽系統管理員"
            else:
                result = "您輸入錯誤的Line Token，請重新輸入"
        elif flag2 == "Time out":
            result = "認證超時，請重新認證\n\n 請輸入：使用者認證"
        else:
            if input_text in ['使用者認證']:  
                flag = insert_Line_ID_list(Line_ID,now_time)
                if flag == True:
                    result = "請輸入您PowerWatcher的Line Token帳號" + "\n\n\n請您前往使用者資訊查詢您的Line Token (位置：使用者->使用者資訊)\n\n\n請在五分鐘內完成認證"
                else:
                    result = "系統有問題，請聯絡系統管理員，謝謝"

            else:    
                result = "請先透過PowerWatcher網站Line Token認證使用者。" + '\n\n\n' + '1.請在Line Chat Bot上輸入 "使用者認證"' + '\n' 


        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result))   
    else:
        print("input_text",user_data['Email'],input_text)
        if input_text in ['使用者認證']:   
            result = "您已經認證過此Line帳號了"   
            
        elif input_text == '本日數據':
            result = ''
            system_list = user_data['CollectionNameList']

            system_name_list = []
            result = ""
            for i,system in enumerate(system_list):
                
                data = []
                data_AUO = []                
                tmp = query_single_system(system)
                device_list = tmp[0]['DevicesID']
                AOU_collection_name = tmp[0]['AUOCollectionName']    
                #print(AOU_collection_name)
                if AOU_collection_name == '46B_AUO':
                    AOU_collection_name = 'shalun_AUO'                
                
                
                data_AUO.append(query_last_data_AUO(AOU_collection_name))
                
                if device_list != []:
                    device_list = device_list.split(',')
                for device in device_list:
                    system_name_list.append(query_single_system_by_collection_name(system))   
                    data = query_data_all(system,device,today,tomorrow)

                    total_power = round(sum(data['DevPower'])/1000/12,2) 
                    #print(total_power)
                    r = '監控系統：' + str(system_name_list[i] )+ '\nDeviceID: '+ str(device)+"\n發/耗電量 : " + str(total_power) + '度(kWh) \n\n'
                    result += r
        elif input_text == '你是誰':
        # 決定要回傳什麼 Component 到 Channel
            result = "PowerWatcher"

        elif input_text not in ['即時數據','本日數據']:
            system_list = user_data['CollectionNameList']
            if input_text == "Dashboard":
                result = "http://140.113.73.56:8000/#/dashboard"
            elif input_text == "監控系統":
                result = "http://140.113.73.56:8000/#/system"        
            elif input_text == "數據報表":
                result = "http://140.113.73.56:8000/#/data/data"
            elif input_text == "使用者管理":
                result = "http://140.113.73.56:8000/#/user/management"                
            else:
                result = "請點選圖文選單上的按鈕或輸入以下關鍵字：\n 1. Dashboard\n 2.監控系統\n 3.數據報表\n 4.使用者管理\n 5.即時數據\n 6.本日數據"



        elif input_text == '即時數據':
            result = ''
            system_list = user_data['CollectionNameList'][:-2]

            system_name_list = []
            for i,system in enumerate(system_list):
                system_name_list.append(query_single_system_by_collection_name(system))
                result = result + str(i+1) + '. '+ '監控系統：' +  str(system_name_list[i] )+'\n\n'
                data = []
                data_AUO = []                
                tmp = query_single_system(system)
                device_list = tmp[0]['DevicesID']
                AOU_collection_name = tmp[0]['AUOCollectionName']    
                #print(AOU_collection_name)
               
                
                data_AUO = query_last_data_AUO(AOU_collection_name)
                #data_AUO.append(query_last_data_AUO(AOU_collection_name))
                """
                if data_AUO != []:
                    r = '感測樹資料\n\n'+'回傳時間：' + str(data_AUO['DateTime'] )+ '\n' +'環境平均日照((W/M²))：' + str(data_AUO['IrradiationAvg'] )+ '\n' + '環境平均濕度(%)：' + str(data_AUO['HumidityAvg']) + '\n'  + '環境平均溫度(℃)：' + str(data_AUO['TemperatureAvg']) + '\n' 
                    result = result  +r   
                """    
                if device_list != []:
                    device_list = device_list.split(',')
                    result = result + '\n監控系統資料\n\n'
                for device in device_list:
                    deviceID = device
                    #print(system,device)
                    if '-' in device:
                        deviceID = device.split('-')[2]
                    d = query_last_data(system,deviceID)
                    if d != False:
                        if 'AboCom' in system_name_list[i]:
                            r = '回傳時間：' + str(d['DateTime'] )+ '\n' +  'DeviceID：' + str(d['DevID']) + '\n'  + '現在功率(W)：' + str(d['DevPower']/100) + '\n' + '現在電壓(V)：' + str(d['DevVoltage']/1000) + '\n' + '現在電流(A)：' + str(d['DevCurrent']/10000) + '\n' + '現在溫度(℃)：' + str(d['DevTemperature']) + '\n' + '現在濕度(%)：' + str(d['DevHumidity']) + '\n\n'
                        else:
                            r = '回傳時間：' + str(d['DateTime'] )+ '\n' +  'DeviceID：' + str(d['DevID']) + '\n'  + '現在功率(W)：' + str(d['DevPower']) + '\n' + '現在電壓(V)：' + str(d['DevVoltage']) + '\n' + '現在電流(A)：' + str(d['DevCurrent']) + '\n' + '現在溫度(℃)：' + str(d['DevTemperature']) + '\n' + '現在濕度(%)：' + str(d['DevHumidity']) + '\n\n'
                        result = result  + r                         
                        #data.append(data_tmp)
                result = result + '\n\n'     
            if result == '':
                result = '此用戶沒有管理任何監控系統'
                

        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str(result))) 
        


@app.route("/")
def home():
    return "Rhhoot Page"    

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True
    app.run(debug=True,host="0.0.0.0",port="7123")

