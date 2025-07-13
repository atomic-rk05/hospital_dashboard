from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import json
import os
import requests
from datetime import datetime, timedelta
import random
from io import StringIO

app = Flask(__name__)
CORS(app)

# Global variables to store data
patients_df = None
dashboard_stats = {}

# Google Sheets CSV URL - Replace this with your Google Sheets published CSV URL
GOOGLE_SHEETS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSyFf7QSGYYAawZk80QfL30IrehHkCaYGFsj9t8digpFhnOX6DKjRDDWIyARTy2xZF53Qekhp8QuckH/pub?gid=488215142&single=true&output=csv"

def load_csv_data():
    """Load patient data from Google Sheets CSV URL"""
    global patients_df, dashboard_stats
    
    try:
        # Try to load data from Google Sheets
        print("Loading data from Google Sheets...")
        
        # Make HTTP request to get CSV data
        response = requests.get(GOOGLE_SHEETS_CSV_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse CSV data
        csv_data = StringIO(response.text)
        patients_df = pd.read_csv(csv_data)
        
        print(f"Successfully loaded {len(patients_df)} patients from Google Sheets")
        
        # Validate required columns
        required_columns = ['name', 'doctor', 'admitDate', 'disease', 'roomNo']
        missing_columns = [col for col in required_columns if col not in patients_df.columns]
        
        if missing_columns:
            print(f"Warning: Missing columns in Google Sheets: {missing_columns}")
            # Fall back to sample data if columns are missing
            patients_df = create_sample_data()
            print("Using sample data due to missing columns")
        
        # Calculate dashboard statistics
        calculate_dashboard_stats()
        
    except requests.exceptions.RequestException as e:
        print(f"Error loading from Google Sheets: {e}")
        print("Falling back to sample data...")
        patients_df = create_sample_data()
        calculate_dashboard_stats()
    except pd.errors.EmptyDataError:
        print("Google Sheets returned empty data. Using sample data.")
        patients_df = create_sample_data()
        calculate_dashboard_stats()
    except Exception as e:
        print(f"Unexpected error loading CSV: {e}")
        patients_df = create_sample_data()
        calculate_dashboard_stats()

def create_sample_data():
    """Create sample patient data"""
    sample_data = [
        {
            'name': 'Jena Brinsker',
            'doctor': 'Dr Kenny Josh',
            'admitDate': '2016-05-27',
            'disease': 'influenza',
            'roomNo': '101',
            'age': 45,
            'gender': 'Female',
            'phone': '9876543210',
            'address': 'Mumbai, Maharashtra'
        },
        {
            'name': 'Mark Hay',
            'doctor': 'Dr Mark',
            'admitDate': '2017-05-26',
            'disease': 'asthma',
            'roomNo': '105',
            'age': 32,
            'gender': 'Male',
            'phone': '9876543211',
            'address': 'Delhi, Delhi'
        },
        {
            'name': 'Anthony Davie',
            'doctor': 'Dr Cinnabar',
            'admitDate': '2018-05-21',
            'disease': 'diabetes',
            'roomNo': '106',
            'age': 58,
            'gender': 'Male',
            'phone': '9876543212',
            'address': 'Bangalore, Karnataka'
        },
        {
            'name': 'David Perry',
            'doctor': 'Dr Felix',
            'admitDate': '2016-04-20',
            'disease': 'jaundice',
            'roomNo': '105',
            'age': 28,
            'gender': 'Male',
            'phone': '9876543213',
            'address': 'Chennai, Tamil Nadu'
        },
        {
            'name': 'Anthony Davie',
            'doctor': 'Dr Beryl',
            'admitDate': '2016-05-24',
            'disease': 'malaria',
            'roomNo': '102',
            'age': 35,
            'gender': 'Male',
            'phone': '9876543214',
            'address': 'Hyderabad, Telangana'
        },
        {
            'name': 'Alan Gilchrist',
            'doctor': 'Dr Joshep',
            'admitDate': '2016-05-22',
            'disease': 'hepatitis',
            'roomNo': '103',
            'age': 42,
            'gender': 'Male',
            'phone': '9876543215',
            'address': 'Pune, Maharashtra'
        },
        {
            'name': 'Mark Hay',
            'doctor': 'Dr Jayesh',
            'admitDate': '2016-06-18',
            'disease': 'typhoid',
            'roomNo': '107',
            'age': 29,
            'gender': 'Male',
            'phone': '9876543216',
            'address': 'Kolkata, West Bengal'
        },
        {
            'name': 'Sue Woodger',
            'doctor': 'Dr Sharma',
            'admitDate': '2016-05-17',
            'disease': 'malaria',
            'roomNo': '108',
            'age': 38,
            'gender': 'Female',
            'phone': '9876543217',
            'address': 'Jaipur, Rajasthan'
        }
    ]
    
    return pd.DataFrame(sample_data)

def calculate_dashboard_stats():
    """Calculate dashboard statistics from patient data"""
    global dashboard_stats
    
    if patients_df is None or patients_df.empty:
        dashboard_stats = {
            'newPatients': 125,
            'opdPatients': 218,
            'operations': 25,
            'visitors': 2479
        }
        return
    
    # Calculate stats based on dates
    today = datetime.now()
    last_month = today - timedelta(days=30)
    last_week = today - timedelta(days=7)
    
    # Convert admitDate to datetime
    patients_df['admitDate'] = pd.to_datetime(patients_df['admitDate'])
    
    # Calculate new patients (last 30 days)
    new_patients = len(patients_df[patients_df['admitDate'] >= last_month])
    
    # Calculate OPD patients (assume 70% of total are OPD)
    total_patients = len(patients_df)
    opd_patients = int(total_patients * 0.7)
    
    # Calculate operations (assume 10% of patients had operations)
    operations = int(total_patients * 0.1)
    
    # Calculate visitors (assume 5x patients)
    visitors = total_patients * 5
    
    dashboard_stats = {
        'newPatients': new_patients if new_patients > 0 else 125,
        'opdPatients': opd_patients if opd_patients > 0 else 218,
        'operations': operations if operations > 0 else 25,
        'visitors': visitors if visitors > 0 else 2479,
        'totalPatients': total_patients
    }

def get_disease_stats():
    """Get disease statistics for charts"""
    if patients_df is None:
        return {}
    
    disease_counts = patients_df['disease'].value_counts().to_dict()
    return disease_counts

def get_monthly_stats():
    """Get monthly statistics for charts"""
    if patients_df is None:
        return {}
    
    # Group by month
    patients_df['month'] = pd.to_datetime(patients_df['admitDate']).dt.to_period('M')
    monthly_counts = patients_df.groupby('month').size().to_dict()
    
    # Convert period to string for JSON serialization
    monthly_stats = {str(k): v for k, v in monthly_counts.items()}
    
    return monthly_stats

def get_doctor_stats():
    """Get doctor statistics"""
    if patients_df is None:
        return {}
    
    doctor_counts = patients_df['doctor'].value_counts().to_dict()
    return doctor_counts

# API Routes

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return send_from_directory('.', 'templetes/index.html')

@app.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """Refresh data from Google Sheets"""
    try:
        load_csv_data()
        return jsonify({
            'message': 'Data refreshed successfully',
            'patients_count': len(patients_df) if patients_df is not None else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients data"""
    try:
        patients_list = patients_df.to_dict('records') if patients_df is not None else []
        
        # Convert datetime to string for JSON serialization
        for patient in patients_list:
            if 'admitDate' in patient:
                patient['admitDate'] = str(patient['admitDate'])[:10]  # YYYY-MM-DD format
        
        return jsonify({
            'patients': patients_list,
            'stats': dashboard_stats,
            'total': len(patients_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient"""
    try:
        if patients_df is None or patient_id >= len(patients_df):
            return jsonify({'error': 'Patient not found'}), 404
        
        patient = patients_df.iloc[patient_id].to_dict()
        if 'admitDate' in patient:
            patient['admitDate'] = str(patient['admitDate'])[:10]
        
        return jsonify(patient)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['POST'])
def add_patient():
    """Add a new patient"""
    try:
        global patients_df
        
        patient_data = request.json
        
        # Validate required fields
        required_fields = ['name', 'doctor', 'admitDate', 'disease', 'roomNo']
        for field in required_fields:
            if field not in patient_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add patient to dataframe
        new_patient = pd.DataFrame([patient_data])
        patients_df = pd.concat([patients_df, new_patient], ignore_index=True)
        
        # Recalculate stats
        calculate_dashboard_stats()
        
        return jsonify({'message': 'Patient added successfully', 'id': len(patients_df) - 1})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update a patient"""
    try:
        global patients_df
        
        if patients_df is None or patient_id >= len(patients_df):
            return jsonify({'error': 'Patient not found'}), 404
        
        patient_data = request.json
        
        # Update patient data
        for key, value in patient_data.items():
            patients_df.at[patient_id, key] = value
        
        # Recalculate stats
        calculate_dashboard_stats()
        
        return jsonify({'message': 'Patient updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient"""
    try:
        global patients_df
        
        if patients_df is None or patient_id >= len(patients_df):
            return jsonify({'error': 'Patient not found'}), 404
        
        # Remove patient
        patients_df = patients_df.drop(patients_df.index[patient_id]).reset_index(drop=True)
        
        # Recalculate stats
        calculate_dashboard_stats()
        
        return jsonify({'message': 'Patient deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            'dashboard': dashboard_stats,
            'diseases': get_disease_stats(),
            'monthly': get_monthly_stats(),
            'doctors': get_doctor_stats()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/hospital-survey', methods=['GET'])
def get_hospital_survey_data():
    """Get hospital survey chart data"""
    try:
        # Generate sample survey data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data = [random.randint(15, 60) for _ in months]
        
        return jsonify({
            'labels': months,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/new-patients', methods=['GET'])
def get_new_patients_chart():
    """Get new patients chart data"""
    try:
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
        data = [random.randint(30, 50) for _ in months]
        
        return jsonify({
            'labels': months,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/heart-surgeries', methods=['GET'])
def get_heart_surgeries_chart():
    """Get heart surgeries chart data"""
    try:
        labels = ['Jan \'19', 'Q2 Jan', 'Q3 Jan', 'Jan \'20', 'Q4 Jan', 'Q5 Jan', 'Q6 Jan']
        data = [random.randint(50, 100) for _ in labels]
        
        return jsonify({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/medical-treatment', methods=['GET'])
def get_medical_treatment_chart():
    """Get medical treatment chart data"""
    try:
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
        
        return jsonify({
            'labels': months,
            'datasets': [
                {
                    'label': 'Treatment A',
                    'data': [random.randint(20, 60) for _ in months],
                    'borderColor': '#FF9800'
                },
                {
                    'label': 'Treatment B',
                    'data': [random.randint(15, 50) for _ in months],
                    'borderColor': '#4CAF50'
                },
                {
                    'label': 'Treatment C',
                    'data': [random.randint(25, 55) for _ in months],
                    'borderColor': '#2196F3'
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Upload and process CSV file"""
    try:
        global patients_df
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.csv'):
            # Read CSV file
            patients_df = pd.read_csv(file)
            
            # Validate required columns
            required_columns = ['name', 'doctor', 'admitDate', 'disease', 'roomNo']
            missing_columns = [col for col in required_columns if col not in patients_df.columns]
            
            if missing_columns:
                return jsonify({'error': f'Missing columns: {missing_columns}'}), 400
            
            # Recalculate stats
            calculate_dashboard_stats()
            
            return jsonify({
                'message': 'CSV uploaded successfully',
                'patients_count': len(patients_df)
            })
        else:
            return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    """Export patients data to CSV"""
    try:
        if patients_df is None:
            return jsonify({'error': 'No data to export'}), 404
        
        # Convert to CSV
        csv_data = patients_df.to_csv(index=False)
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=patients_export.csv'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-sheets-url', methods=['POST'])
def update_sheets_url():
    """Update Google Sheets URL"""
    try:
        global GOOGLE_SHEETS_CSV_URL
        
        data = request.json
        new_url = data.get('url')
        
        if not new_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL format
        if not new_url.startswith('https://docs.google.com/spreadsheets/'):
            return jsonify({'error': 'Invalid Google Sheets URL'}), 400
        
        # Update URL
        GOOGLE_SHEETS_CSV_URL = new_url
        
        # Reload data from new URL
        load_csv_data()
        
        return jsonify({
            'message': 'Google Sheets URL updated successfully',
            'patients_count': len(patients_df) if patients_df is not None else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load data when starting the server
    load_csv_data()
    
    print("Hospital Dashboard Backend Started")
    print("Available endpoints:")
    print("  GET  /api/patients - Get all patients")
    print("  POST /api/patients - Add new patient")
    print("  GET  /api/patients/<id> - Get specific patient")
    print("  PUT  /api/patients/<id> - Update patient")
    print("  DELETE /api/patients/<id> - Delete patient")
    print("  GET  /api/stats - Get dashboard statistics")
    print("  POST /api/refresh-data - Refresh data from Google Sheets")
    print("  POST /api/upload-csv - Upload CSV file")
    print("  GET  /api/export-csv - Export data to CSV")
    print("  POST /api/update-sheets-url - Update Google Sheets URL")
    print(f"  Current Google Sheets URL: {GOOGLE_SHEETS_CSV_URL}")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)