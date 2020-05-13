
import requests
import codecs
import slackbot_settings
from slackbot.bot import respond_to
import base64
import json
from slacker import Slacker
import os
slacker = Slacker(slackbot_settings.API_TOKEN)
GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
API_KEY = '[Your API_KEY]' 
 
class DownloadFile:
    def __init__(self, file_types, save_directly):
        # 引数が省略された場合は、デフォルトのタイプを指定
        self.file_types = file_types
        self.save_directly = save_directly
 
 
    def exe_download(self, file_info):
 
        file_name = file_info['name']
        url_private = file_info['url_private_download']
 
        # 保存対象のファイルかチェックする
        if file_info['filetype'] in self.file_types:
            # ファイルをダウンロード
            self.file_download(url_private, self.save_directly + file_name)
            return self.save_directly + file_name
        else:
            # 保存対象外ファイル
            return 'file type is not applicable.'
 
    def file_download(self, download_url, save_path):
        content = requests.get(
            download_url,
            allow_redirects=True,
            headers={'Authorization': 'Bearer %s' % slackbot_settings.API_TOKEN}, stream=True
        ).content
        # 保存する
        target_file = codecs.open(save_path, 'wb')
        target_file.write(content)
        target_file.close()


# APIを呼び、認識結果をjson型で返す
def request_cloud_vison_api(image_base64):
    api_url = GOOGLE_CLOUD_VISION_API_URL + API_KEY
    req_body = json.dumps({
        'requests': [{
            'image': {
                'content': image_base64.decode('utf-8') # jsonに変換するためにstring型に変換する
            },
            'features': [{
                'type': 'TEXT_DETECTION', # ここを変更することで分析内容を変更できる
                'maxResults': 10,
            }]
        }]
    })
    res = requests.post(api_url, data=req_body)
    return res.json()

# 画像読み込み
def img_to_base64(filepath):
    with open(filepath, 'rb') as img:
        img_byte = img.read()
    return base64.b64encode(img_byte)


@respond_to('^画像認識して$')
def file_download(message):
    # ダウンロードするファイルタイプを指定する
    file_types = ['png', 'gif', 'jpg']
    # ファイルの保存ディレクトリ
    path=os.getcwd()
    #print(path)
    save_path = path+'/work/'
 
    download_file = DownloadFile(file_types, save_path)
    image = download_file.exe_download(message._body['files'][0])
    # 文字認識させたい画像をimageとする
    img_base64 = img_to_base64(image)
    result = request_cloud_vison_api(img_base64)
    text_r = result["responses"][0]["fullTextAnnotation"]["text"]
    #認識した文字のみを出力
    message.reply(text_r)

