import os
import threading
import time
from pyrogram import Client
from pyrogram import filters
import pyrogram


# setup
bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "") 
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)
os.system("chmod 777 ./ffmpeg/ffmpeg")


# start command
@app.on_message(filters.command(['start']))
def echo(client, message : pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id,f"**Welcome** {message.from_user.mention}\n__just to send me a Video file__")


# upload status
def upstatus(statusfile,message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile,"r") as upread:
            txt = upread.read()
        try:
            app.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)


# download status
def downstatus(statusfile,message):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile,"r") as upread:
            txt = upread.read()
        try:
            app.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)


# progress writter
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt',"w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


# compress
def compress(message,msg):

    dowsta = threading.Thread(target=lambda:downstatus(f'{message.id}downstatus.txt',msg),daemon=True)
    dowsta.start()
    vfile = app.download_media(message, progress=progress, progress_args=[message,"down"])
    if os.path.exists(f'{message.id}downstatus.txt'):
        os.remove(f'{message.id}downstatus.txt')

    name = vfile.split("/")[-1]
    cmd = f'./ffmpeg/ffmpeg -i {vfile} -c:v libx265 -vtag hvc1 output-{message.id}.mkv'
    app.edit_message_text(message.chat.id, msg.id, "__Compressing__") 
    try:
        os.system(cmd)
    except:
        app.edit_message_text(message.chat.id, msg.id, "**Error**")
        return

    file_exists = os.path.exists(f'output-{message.id}.mkv')
    if file_exists:
        os.remove(vfile)
    else:
        app.edit_message_text(message.chat.id, msg.id, "**Error**")
        return

    os.rename(f'output-{message.id}.mkv',name)
    app.edit_message_text(message.chat.id, msg.id, "__Uploading__")
    upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',msg),daemon=True)
    upsta.start()
    app.send_document(message.chat.id,document=name, force_document=True, progress=progress, progress_args=[message,"up"], reply_to_message_id=message.id)

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    app.delete_messages(message.chat.id,[msg.id])      
    os.remove(name)


# document
@app.on_message(filters.document)
def documnet(client, message):
    try:
        mimetype = message.document.mime_type
        if "video" in mimetype:
            msg = app.send_message(message.chat.id,"__Downloading__", reply_to_message_id=message.id) 
            comp = threading.Thread(target=lambda:compress(message,msg),daemon=True)
            comp.start() 
    except:
        app.send_message(message.chat.id,"**Send only Videos**")    


# video
@app.on_message(filters.video)
def video(client, message):
    msg = app.send_message(message.chat.id,"__Downloading__", reply_to_message_id=message.id)   
    comp = threading.Thread(target=lambda:compress(message,msg),daemon=True)
    comp.start()


# infinty polling
app.run()
