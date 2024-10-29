from base64 import b64encode
import os

from flask import Flask, render_template, request, send_from_directory, url_for, Response
from flask_cors import CORS, cross_origin

from models import models, ALL_MODELS
from file_handler import FileHandler
from tps.content.ops import download, find   
from tps.modules import Emphasizer
# from russian import normalize_russian
#from stressrnn import StressRNN
import logging
# from ruaccent import RUAccent

# accentizer = RUAccent()
# accentizer.load(omograph_model_size='turbo3.1', use_dictionary=True)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

# try:
#     stress_dict = find("stress.dict", raise_exception=True)
# except FileNotFoundError:
#     stress_dict = download("stress.dict")
# emphasizer = Emphasizer((stress_dict, "plane"))

#stress_rnn = StressRNN()

_valid_model_types = [key for key in models if key is not ALL_MODELS]


@app.route("/", methods=["GET"])
@cross_origin()
def index():
    return render_template("speechSynthesis.html", existing_models=models.keys())


@app.route("/inference", methods=["POST"])
@cross_origin()
def synthesize():
    request_json = request.get_json()

    text = request_json["text"]
    logging.info(f"Source text: {text}")
    # text = emphasizer.process_text(text)

    # text = normalize_russian(text)
    # logging.info(f"Normalized text: {text}")
    # text = accentizer.process_all(text)
    # #text = stress_rnn.put_stress(text, stress_symbol='+', accuracy_threshold=0.75, replace_similar_symbols=True)
    # logging.info(f"Stressed text: {text}")

    model_type = "Ruslan"

    if "voice" in request_json:
        model_type = request_json["voice"]
    

    options = {
        "rate": float(request_json.get("rate", 1.5)),
        "pitch": float(request_json.get("pitch", 1.0)),
        "volume": float(request_json.get("volume", 6))
    }

    response_code, results = FileHandler.get_synthesized_audio(text, model_type, **options)

    if response_code == 0:
        for result in results:
            filename = result.pop("filename")
            # audio_bytes = result.pop("response_audio")
            result["response_audio_url"] = url_for("media_file", filename=filename)
            # result["response_audio"] = b64encode(audio_bytes).decode("utf-8")

    # return {
        # "response_code": response_code,
        # "response": results
    # }
    output_file = os.path.join("data", "waves", os.path.basename(result["response_audio_url"]))
    # output_file = f"http://localhost:8899{result['response_audio_url']}"
    def file_iterator():
        with open(output_file, 'rb') as f:
            while chunk := f.read(2048):
                yield chunk

    return Response(file_iterator(), mimetype="audio/wav")

class InvalidVoice(Exception):
    pass

@app.route("/get_user_dict/", methods=["POST"])
@cross_origin()
def get_user_dict():
    request_json = request.get_json()
    model_type = request_json.get("voice")

    response_code = 1
    try:
        if model_type not in _valid_model_types:
            raise InvalidVoice("Parameter 'voice' must be one of the following: {}".format(_valid_model_types))

        model = models[model_type]
        result = model.get_user_dict()

        response_code = 0
    except InvalidVoice as e:
        result = str(e)
    except Exception as e:
        result = str(e)

    return {
        "response_code": response_code,
        "response": result
    }


@app.route("/update_user_dict/", methods=["POST"])
@cross_origin()
def update_user_dict():
    request_json = request.get_json()

    model_type = request_json.get("voice")
    user_dict = request_json.get("user_dict")

    response_code = 1
    try:
        if model_type not in _valid_model_types:
            raise InvalidVoice("Parameter 'voice' must be one of the following: {}".format(_valid_model_types))

        model = models[model_type]
        model.update_user_dict(user_dict)

        result = "User dictionary has been updated"
        response_code = 0
    except InvalidVoice as e:
        result = str(e)
    except Exception as e:
        result = str(e)

    return {
        "response_code": response_code,
        "response": result
    }


@app.route("/replace_user_dict/", methods=["POST"])
@cross_origin()
def replace_user_dict():
    request_json = request.get_json()

    model_type = request_json.get("voice")
    user_dict = request_json.get("user_dict")

    response_code = 1
    try:
        if model_type not in _valid_model_types:
            raise InvalidVoice("Parameter 'voice' must be one of the following: {}".format(_valid_model_types))

        model = models[model_type]
        model.replace_user_dict(user_dict)

        result = "User dictionary has been replaced"
        response_code = 0
    except InvalidVoice as e:
        result = str(e)
    except Exception as e:
        result = str(e)

    return {
        "response_code": response_code,
        "response": result
    }


@app.route("/media/<path:filename>", methods=["GET"])
@cross_origin()
def media_file(filename):
    return send_from_directory(".", filename, as_attachment=False)


if __name__ == "__main__":
    app.run()
