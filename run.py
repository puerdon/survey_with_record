from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import base64
import json

app = Flask(__name__, static_folder='data/')
CORS(app)

# 檢查有沒有data資料夾
if not os.path.isdir('./data'):
    os.mkdir('./data')

@app.route("/save_data", methods=['POST'])
def save_data():

    if request.json is not None:

        random_number_id = request.json['random_number_id']

        # 如果是得到 survey 的
        if request.json["trial_type"] == "survey": 
            print(request.json)
            name = request.json['response']['name']
            age = request.json['response']['age']
            data = {
                "name": name,
                "age": age
            }
            
            os.mkdir(f'./data/{random_number_id}')

            with open(f'./data/{random_number_id}/data.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False)

            return jsonify({"status": "success"})

        # 如果是得到 html-audio-response 的
        elif request.json["trial_type"] == "html-audio-response": 
                audio_base64_string = request.json['response']
                audiofile = base64.b64decode(bytes(audio_base64_string, 'utf-8'))

                with open(f'./data/{random_number_id}/x.wav', 'wb') as f:
                    f.write(audiofile)
                return jsonify({"status": "success"})

                pass
    return None


@app.route("/survey", methods=['GET'])
def survey():
    return render_template('survey.html')

@app.route("/result", methods=['GET'])
def result():
    user_id = request.args.get('id')

    data = None
    # read json
    with open(f'./data/{user_id}/data.json', 'r') as f:
        data = json.load(f)

    name = data['name']
    age = data['age']

    audio_link = f"{user_id}/x.wav"

    return render_template('result.html', name=name, age=age, audio_link=audio_link)