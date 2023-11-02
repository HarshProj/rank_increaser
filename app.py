from flask import Flask, render_template, request
import pickle
import json

app = Flask(__name__)

model = pickle.load(open('model.pkl' , 'rb'))

with open('jsons/tlr.json', 'r') as json_file:
    tlr_data = json.load(json_file)

with open('jsons/go.json', 'r') as json_file:
    go_data = json.load(json_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_rank = int(request.form.get('rank'))
        predicted_values = model.predict([[input_rank]])

        predicted_tlr = predicted_values[0, 0]
        predicted_go = int(predicted_values[0, 2])

        # Convert predicted_tlr to an integer
        predicted_tlr = int(predicted_tlr)

        predicted_number = tlr_data.get(str(str(predicted_tlr)))
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

        return render_template('suggest.html', predicted_number=predicted_number , predicted_values=predicted_values , placement_percentage=placement_percentage, median_package=median_package)
    
    except Exception as e:
        return f"Prediction Error: {str(e)}"

if __name__ == '__main__':
    app.run()
