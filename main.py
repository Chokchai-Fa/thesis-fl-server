import pickle
import os
from datetime import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import helper
import shutil
import sys

load_dotenv()

class FLServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.round_for_fl = int(os.environ.get('ROUND_FOR_FL'))
        self.number_of_client = int(os.environ.get('NUMBER_OF_CLIENT'))
        self.git_repo_url = os.environ.get('GIT_FL_REPO')
        self.repo_path = './fl'
        self.count_fl_round = 1
        self.client_list = []
        self.count_client = 0

        self.setup_routes()

    def setup_routes(self):
        self.app.route('/actknowlege', methods=['GET'])(self.trained_actknowledge)

    def weigth_aggregate(self):
        file_list = os.listdir("./")
        weight_files = [file for file in file_list if 'weight-client' in file]

        all_weights = []

        for weight_file in weight_files:
            file_path = os.path.join('./', weight_file)
            with open(file_path, 'rb') as file:
                weights = pickle.load(file)
                all_weights.append(weights)

        aggregated_weights = {'intercept': 0.0, 'slope': 0.0}

        for weights in all_weights:
            aggregated_weights['intercept'] += weights['intercept']
            aggregated_weights['slope'] += weights['slope']

        num_elements = len(all_weights)
        aggregated_weights['intercept'] /= num_elements
        aggregated_weights['slope'] /= num_elements

        print(f"Aggregated Model round {self.count_fl_round} successfully")
        print("Aggregated Model Coefficients:", aggregated_weights)

        current_datetime = datetime.now()
        timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        global_model_file = f"{timestamp}-global_weight.pkl"

        directory_path = f"{self.repo_path}/round{self.count_fl_round}"
        os.makedirs(directory_path, exist_ok=True)

        with open(os.path.join(directory_path, global_model_file), 'wb') as file:
            pickle.dump(aggregated_weights, file)

        return f'round{self.count_fl_round}/{global_model_file}'
    
    def trained_actknowledge(self):
        client = request.args.get('client')

        if client not in self.client_list:
            self.client_list.append(client)
            self.count_client +=1

        if self.count_client == self.number_of_client and self.count_fl_round <= self.round_for_fl:
            repo = helper.git_clone(self.git_repo_url, self.repo_path)
            global_model_file = self.weigth_aggregate()
            helper.git_push('main',global_model_file, repo,'commit from fl server')
            shutil.rmtree(self.repo_path, ignore_errors=True)
            self.count_client = 0
            self.count_fl_round += 1

        if self.count_fl_round == self.round_for_fl:
            sys.exit()

        data = {'message': 'success'}
        return jsonify(data), 200

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    fl_app = FLServer()
    fl_app.run()