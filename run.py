from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import base64
import json

app = Flask(__name__, static_folder='static/')
CORS(app)

SURVEY_LIMIT = 20

# 檢查有沒有data資料夾
if not os.path.isdir('./data'):
    os.mkdir('./data')

@app.route("/save_data", methods=['POST'])
def save_data():
    # print(request.json)
    if request.json is not None:

        unique_id = request.json['unique_id']
        survey_id = request.json['survey_id']


        # 如果是一開始的基本資料
        if request.json["trial_type"] == 'survey':
            if 'age' in request.json['response']:
            # print(request.json)
            # name = request.json['response']['name']
                age = request.json['response']['age']
                gender = request.json['response']['gender']
                primary_lang = request.json['response']['primary_lang']
                parent_lang = request.json['response']['parent_lang']
                dialect = request.json['response']['dialect']
                group_name = request.json['response']['group_name']
                place = request.json['response']['place']
                village_time = request.json['response']['village_time']
                most_freq_lang = request.json['response']['most_freq_lang']
                freq = request.json['response']['freq']
                with_whom = request.json['response']['with_whom']
                other = request.json['response']['other']

                data = {
                    # "name": name,
                    "subject_info": {
                        "age": age,
                        "gender": gender,
                        "primary_lang": primary_lang,
                        "parent_lang": parent_lang,
                        "dialect": dialect,
                        "group_name": group_name,
                        "place": place,
                        "village_time": village_time,
                        "most_freq_lang": most_freq_lang,
                        "freq": freq,
                        "with_whom": with_whom,
                        "other": other
                    },
                    "results": [],
                    "bank_info": ""
                }

                os.makedirs(f'./data/{survey_id}/{unique_id}', exist_ok=True)

                with open(f'./data/{survey_id}/{unique_id}/data.json', 'w') as f:
                    json.dump(data, f, ensure_ascii=False)

                return jsonify({"status": "success"})

            elif 'bank_name' in request.json['response']:

                bank_data = {
                    'bank_real_name': request.json['response']['bank_real_name'],
                    'id_card': request.json['response']['id_card'],
                    'address': request.json['response']['address'],
                    'bank_name': request.json['response']['bank_name'],
                    'bank_branch': request.json['response']['bank_branch'],
                    'bank_id': request.json['response']['bank_id']
                }
                
                with open(f'./data/{survey_id}/{unique_id}/data.json', 'r') as f:
                    d = json.load(f)
                    d['bank_info'] = bank_data

                with open(f'./data/{survey_id}/{unique_id}/data.json', 'w') as f:
                    json.dump(d, f, ensure_ascii=False)

                return jsonify({"status": "success"})

        # 如果是得到 html-audio-response 的
        elif request.json["trial_type"] == "html-audio-response":

            # print(request.json)
            # step 1: 寫入音檔
            audio_base64_string = request.json['response']
            audiofile = base64.b64decode(bytes(audio_base64_string, 'utf-8'))
            image_name = request.json['image_name'].rstrip(".png").split('/')[-1].rstrip('.')

            with open(f'./data/{survey_id}/{unique_id}/{image_name}.wav', 'wb') as f:
                f.write(audiofile)

            # step 2: 寫入文字檔
            with open(f'./data/{survey_id}/{unique_id}/data.json', 'r') as f:
                data = json.load(f)
                data['results'].append({
                    "image_name": image_name,
                    "text": request.json['textarea']
                })

            with open(f'./data/{survey_id}/{unique_id}/data.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False)

            return jsonify({"status": "success"})

        # 如果是得到 html-audio-response 的
        elif request.json["trial_type"] == "browser-check":

            # step 2: 寫入文字檔
            with open(f'./data/{survey_id}/{unique_id}/data.json', 'r') as f:
                data = json.load(f)
                data['browser_check'] = {}
                for k in request.json:
                    data['browser_check'][k] = request.json[k]

            with open(f'./data/{survey_id}/{unique_id}/data.json', 'w') as f:
                json.dump(data, f, ensure_ascii=False)

            return jsonify({"status": "success"})

        # 只有選擇 不要報酬 才會進來這裡
        elif request.json["trial_type"] == "html-button-response":

            if request.json["response"] == 1:
                with open(f'./data/{survey_id}/{unique_id}/data.json', 'r') as f:
                    d = json.load(f)
                    d['bank_info'] = 'no need'

                with open(f'./data/{survey_id}/{unique_id}/data.json', 'w') as f:
                    json.dump(d, f, ensure_ascii=False)

                return jsonify({"status": "success"})

    return None


@app.route("/survey/<survey_id>", methods=['GET'])
def survey(survey_id):

    dirs = os.listdir(f'./data/{survey_id}')
    number = len(list(filter(lambda x: x.startswith('2'), dirs)))

    if number < SURVEY_LIMIT:
        return render_template(f'survey_{survey_id}.html')
    else:
        return render_template('full.html')

@app.route("/results", methods=['GET'])
def results():
    results = []
    dirs = os.listdir('./data')
    for dir_ in dirs:
        if dir_.startswith('.'):
            continue
        with open(f'./data/{dir_}/data.json', 'r') as f:
            data = json.load(f)
            results.append({
                'age': data['age'],
                'gender': data['gender'],
                'id': dir_
            })
    return render_template('results.html', results=results)


@app.route("/result/", methods=['GET'])
def result_list_survey_id():

    survey_ids = []
    
    for dir_ in os.listdir(f'./data'):
        print(dir_)
        if not dir_.startswith('2') and not dir_.startswith('.'):
            survey_ids.append(dir_)
    print(survey_ids)
    return render_template('result_list_survey_id.html', data=survey_ids)

@app.route("/result/<survey_id>/", methods=['GET'])
def result_of_a_survey(survey_id):

    data = []
    dirs = []
    for dir_ in os.listdir(f'./data/{survey_id}'):
        if dir_.startswith('.'):
            continue
        dirs.append(dir_)
    dirs.sort()

    for dir_ in dirs:
        with open(f'./data/{survey_id}/{dir_}/data.json', 'r') as f:
            d = json.load(f)
            d['user_id'] = dir_
            data.append(d)

    print(data)
    return render_template('result_of_a_survey.html', data=data, survey_id=survey_id)

@app.route("/result/<survey_id>/<subject_id>", methods=['GET'])
def result_of_a_subject(survey_id, subject_id):

    data = None
    audio_files = []
    has_bank_info = False

    try:
        with open(f'./data/{survey_id}/{subject_id}/data.json', 'r') as f:
            d = json.load(f)
            data = d
            data['user_id'] = subject_id
            data['survey_id'] = survey_id
            if isinstance(data['bank_info'], str) and data['bank_info'] == 'no need':
                has_bank_info = False
            else:
                has_bank_info = True
        for dir_ in os.listdir(f'./data/{survey_id}/{subject_id}'):
            if dir_.endswith('.wav'):
                audio_files.append(dir_)
        # print(data)
        audio_files = sorted(audio_files)
        return render_template('result_of_a_subject.html', data=data, audio_files=audio_files, has_bank_info=has_bank_info)    


    except Exception as e:
        print(e)
        return render_template('error.html')

@app.route("/data/<survey_id>/<subject_id>/<filename>", methods=['GET'])
def send_data(survey_id,subject_id,filename):
    return send_file(f'./data/{survey_id}/{subject_id}/{filename}')

