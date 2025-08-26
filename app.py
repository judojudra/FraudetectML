from flask import Flask, render_template, request, redirect, url_for
import os
from fraud_detection import FraudDetector
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(file_path):
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format")
        return df
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            try:
                file.save(filename)
                df = process_file(filename)
                
                detector = FraudDetector()
                analysis_results = detector.detect_fraud(df)
                recommendations = detector.generate_recommendations(analysis_results)
                summary_stats = detector.get_summary_stats(df, analysis_results['suspicious_entries'])
                
                return render_template('results.html',
                    fraud_type=analysis_results['fraud_type'],
                    suspicious_entries=analysis_results['suspicious_entries'],
                    recommendations=recommendations,
                    summary=summary_stats,
                    current_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
            except Exception as e:
                if os.path.exists(filename):
                    os.remove(filename)
                return render_template('error.html',
                    error_message=str(e),
                    supported_columns="Required columns: Transaction amount, date, and at least one entity identifier"
                )
    
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)