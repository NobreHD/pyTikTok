import gevent.monkey
gevent.monkey.patch_all()
from flask import Flask, render_template, request, send_from_directory
import random, threading, webbrowser, urllib.request, shutil, os, ast, glob
from urllib.parse import unquote
from TikTokApi import TikTokApi

api = TikTokApi.get_instance(use_test_endpoints=True, custom_verifyFp="verify_ky1ijcxv_2CyNGLL0_IC37_4B8i_B060_QWztoQA5m8cI")
app = Flask(__name__)

@app.route('/page/<int:page>')
@app.route("/")
def index(page=1):
    page = 1 if page < 1 else page
    videos = api.by_hashtag("minecraft", count=24, offset=int((page-1)*24) , custom_verifyFp="verify_ky1ijcxv_2CyNGLL0_IC37_4B8i_B060_QWztoQA5m8cI")
    return render_template("index.html", videos=videos, page=page)

@app.route("/assets/<path:path>")
def send_assets(path):
    return send_from_directory("assets", path)

@app.route("/download/<int:id>")
def download(id):
    try:
        video = api.get_tiktok_by_id(id)["itemInfo"]["itemStruct"]
        urllib.request.urlretrieve(video["video"]["downloadAddr"], f"download/tiktok-{id}.mp4")
        return send_from_directory(os.path.join(os.getcwd(), "download"), f"tiktok-{id}.mp4", as_attachment=True)
    except:
        return '<meta http-equiv="refresh" content="0; url=/">'
    
@app.route("/downloadAll")
def downloadAll():
    if not os.path.exists("download"):
        os.mkdir("download")
    if os.path.exists("download.zip"):
        os.remove("download.zip")
    
    files = glob.glob("download/*")
    if(len(files) > 0):
        for f in files:
            os.remove(f)
    
    videoList = ast.literal_eval(unquote(request.cookies.get('selected')))
    print(videoList)
    for video in videoList:
        videoObject = api.get_tiktok_by_id(video)["itemInfo"]["itemStruct"]
        urllib.request.urlretrieve(videoObject["video"]["downloadAddr"], f"download/tiktok-{videoObject['id']}.mp4")
    shutil.make_archive("download", 'zip', "download")
    return send_from_directory(os.getcwd(), "download.zip", as_attachment=True)

@app.errorhandler(500)
def server_error(e):
    return '<meta http-equiv="refresh" content="1">'

@app.errorhandler(404)
def server_error(e):
    return '<meta http-equiv="refresh" content="0, url=/">'

if __name__ == "__main__":
    port = 5000# + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    app.run(port=port, debug=False)