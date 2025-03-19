import csv
import json
from datetime import datetime

def export_to_csv(data, filename):
    if not filename.endswith('.csv'):
        filename += '.csv'
        
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def export_to_json(data, filename):
    if not filename.endswith('.json'):
        filename += '.json'
        
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile, default=str, indent=4)

def format_data_for_export(session, model):
    records = session.query(model).all()
    return [record.__dict__ for record in records]