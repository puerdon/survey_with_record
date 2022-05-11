from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import base64

app = Flask(__name__)
CORS(app)

@app.route("/save_data", methods=['POST'])
def save_data():

    if request.json is not None:
        print('@@@@')
        random_number_id = request.json['random_number_id']


        # 如果是得到 survey 的
        if request.json["trial_type"] == "survey": 
            print(request.json)
            subject_name = request.json['response']['name']
            os.mkdir(f'data/{random_number_id}')
            return jsonify({"status": "success"})

        # 如果是得到 html-audio-response 的
        elif request.json["trial_type"] == "html-audio-response": 
                audio_base64_string = request.json['response']
                print(audio_base64_string)
                audiofile = base64.b64decode(bytes(audio_base64_string, 'utf-8'))

                print('cccccc')
                print(audiofile)

                with open(f'./data/{random_number_id}/x.wav', 'wb') as f:
                    f.write(audiofile)
                return jsonify({"status": "success"})

                pass
    return None


@app.route("/survey", methods=['GET'])
def survey():
    return render_template('survey.html')