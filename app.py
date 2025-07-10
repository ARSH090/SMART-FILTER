from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

# Make folders if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_term = request.form['search_term'].strip()
        file = request.files['file']

        if not file:
            return "No file uploaded"

        # Save uploaded file
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Read file (auto detect extension)
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Filter: any cell contains search_term
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)
        filtered_df = df[mask]

        if filtered_df.empty:
            return "No matching rows found."

        # Save filtered file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"filtered_{timestamp}.xlsx"
        output_path = os.path.join(RESULT_FOLDER, output_filename)
        filtered_df.to_excel(output_path, index=False)

        return f"Filtered file ready: <a href='/download/{output_filename}'>Download Here</a>"

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(RESULT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
