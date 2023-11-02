from flask import Flask , render_template , request , jsonify
import numpy as np
import pandas as pd
import pickle
import json

app = Flask(__name__)

model1 = pickle.load(open('model1.pkl' , 'rb'))

with open('jsons/tlr.json', 'r') as json_file:
    tlr_data = json.load(json_file)

with open('jsons/go.json', 'r') as json_file:
    go_data = json.load(json_file)

with open('jsons/oi.json', 'r') as json_file:
    oi_data = json.load(json_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_rank = int(request.form.get('rank'))
        predicted_values = model1.predict([[input_rank]])

        predicted_tlr = predicted_values[0, 0]
        predicted_go = int(predicted_values[0, 2])
        predicted_oi = int(predicted_values[0, 3])

        # Convert predicted_tlr to an integer
        predicted_tlr = int(predicted_tlr)

        predicted_number = tlr_data.get(str(predicted_tlr))
        sorted_ranks = sorted(map(int, go_data.keys()))

        # Find the nearest greater "go" value
        nearest_greater_rank = None
        for rank in sorted_ranks:
            if rank > predicted_go:
                nearest_greater_rank = rank
                break

        if nearest_greater_rank is not None:
            # Fetch the information related to the nearest greater "go" value
            go_info = go_data.get(str(nearest_greater_rank))
            placement_percentage = go_info.get("Placement_Percentage")
            median_package = go_info.get("Median_Placement_Package")
        else:
            placement_percentage = "Not found"
            median_package = "Not found"

        sorted_oi = sorted(map(int, oi_data.keys()))

        nearest_greater_oi = None
        for val in sorted_oi:
            if val >= predicted_oi:
                nearest_greater_oi = val
                break

        if nearest_greater_oi is not None:
            oi_info = oi_data.get(str(nearest_greater_oi))
            girls_percentage = oi_info.get("Percentage of Female Students")
            ews = oi_info.get("Percentage of Economically Weaker Section (EWS) Students")
        else:
            girls_percentage = "Not found"
            ews = "Not found"

        return render_template('suggest.html', predicted_number=predicted_number, predicted_values=predicted_values,
                               placement_percentage=placement_percentage, median_package=median_package,
                               girls_percentage=girls_percentage, ews=ews)

    except Exception as e:
        return f"Prediction Error: {str(e)}"
   
global cur_data
global cur_score
model = pickle.load(open('model.pkl' , 'rb'))

ranklist = {
    "nit raipur":66 
}
institute = ""


@app.route('/ScorePredictor')
def index2():
    return render_template('index2.html')

@app.route('/updated')
def update():
    try:
        c_name = cur_data
        rank = cur_score

        if c_name is not None and rank is not None:
            ranklist[c_name] = int(rank)  # Parse rank as an integer
            return jsonify({"message": "Ranking updated successfully"})
        else:
            return jsonify({"error": "Invalid data. Please provide 'institute' and 'rank' as URL parameters."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ranking2')
def get_ranking2():
    sorted_ranklist = dict(sorted(ranklist.items(), key=lambda item: item[1], reverse=True))
    enumerated_data = [(i, (institute, score)) for i, (institute, score) in enumerate(sorted_ranklist.items(), 1)]
    return render_template('ranking2.html', data=enumerated_data)


@app.route('/predict2' , methods=['POST'])
def predict2_price():
    try:
        tlr = float(request.form.get('tlr'))
        rpc = float(request.form.get('rpc'))
        go = float(request.form.get('go'))
        oi = float(request.form.get('oi'))
        perception = float(request.form.get('perception'))

        global cur_data
        cur_data = str(request.form.get('institute'))
        
        new_data = pd.DataFrame({'tlr': [tlr], 'rpc': [rpc], 'go': [go], 'oi': [oi], 'perception': [perception]})
        score = model.predict(new_data)
        global cur_score
        cur_score = score
        score = np.around(score, 2)
        return render_template('score.html', score = score[0])  # Assuming 'score' is a NumPy array, return the first element

    except Exception as e:
        return str(e)
    
if __name__ == '__main__':
    app.run()
