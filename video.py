from os.path import exists
import os
import threading
from pyrogram import Client
from pyrogram import filters

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "") 

app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)
os.system("chmod 777 ./ffmpeg/ffmpeg")

@app.on_message(filters.command(['start']))
def echo(client, message):
    app.send_message(message.chat.id,"Welcome\nFirst you have to send me a video File")

def progress(current, total):
    #app.edit_message_text(chat_id=mess.chat.id,message_id=mess.id+1,text=f"{current * 100 / total:.1f}%")
    #await app.send_message(mess.chat.id,f"{current * 100 / total:.1f}%")
    print(f"{current * 100 / total:.1f}%")

def compress(message):
    #cmd = "./ffmpeg/ffmpeg -loglevel verbose -i k.mkv -c:v libx265 -vtag hvc1 output.mp4"
    vfile = app.download_media(message, progress=progress)
    name = vfile.split("/")[-1]
    print(name)
    cmd = f'./ffmpeg/ffmpeg -i {vfile} -c:v libx265 -vtag hvc1 output-{message.id}.mkv'
    app.send_message(message.chat.id,"Compressing") 
    try:
        os.system(cmd)
    except:
        app.send_message(message.chat.id,"Error")
        return

    file_exists = os.path.exists(f'output-{message.id}.mkv')
    if file_exists:
        os.remove(vfile)
    else:
        app.send_message(message.chat.id,"Error")
        return
    os.rename(f'output-{message.id}.mkv',name)
    app.send_message(message.chat.id,"Uploading")
    app.send_document(message.chat.id,document=name, progress=progress)
    os.remove(name)

@app.on_message(filters.document)
def documnet(client, message):
    try:
        mimetype = message.document.mime_type
        if "video" in mimetype:
            app.send_message(message.chat.id,"Downloading") 
            comp = threading.Thread(target=lambda:compress(message),daemon=True)
            comp.start() 
    except:
        app.send_message(message.chat.id,"Send Video")    

@app.on_message(filters.video)
def video(client, message):
    app.send_message(message.chat.id,"Downloading")       
    comp = threading.Thread(target=lambda:compress(message),daemon=True)
    comp.start()

app.run()
