import picamera
import requests
import json
import shlex
import subprocess
import os

from time import sleep

id = "1"
ip = "210.125.31.25"
port = 3000

url_get_interval = "http://" + ip + ":" + str(port) + "/video/get_interval"
url_upload = "http://" + ip + ":" + str(port) + "/video/upload"

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 24

    while True:
        try:
            #GET REFRESH INTERVAL
            headers = {"id": "1"}
            res = requests.get(url_get_interval, headers = headers, timeout = 3)
            result = res.content
        except:
            print "[ID:"+id+"] Can not retrive an interval from server"
            sleep(3)
            continue

        data = json.loads(result)
        try:
            print("[ID:"+str(id)+"] interval="+str(data['data']))
        except Exception as e:
            print(e.message)
            print("[ID:"+id+'] Unregistered cam')
            sleep(3)
            continue

        if(data["data"]):
           interval = int(data["data"])
           filename = "rec_" + id + ".h264" 

           try:
               os.remove(filename)
           except:
               pass

           try:
               os.remove("rec_"+id+".mp4")
           except:
               pass

           print('recording...')
           camera.start_recording(filename, format='h264')
           camera.wait_recording(interval)
           camera.stop_recording()

           command = shlex.split("MP4Box -add {f}.h264 {f}.mp4".format(f="rec_"+id))
           try:
               output = subprocess.check_output(command, stderr=subprocess.STDOUT)
           except subprocess.CalledProcessError as e:
               print('converting error')
               continue

           files = open("rec_"+id+".mp4")
           upload = {'file': files}
           try:
               res = requests.post(url_upload, files = upload, headers = headers)
           except:
               print("Server out of service")
               continue
               
