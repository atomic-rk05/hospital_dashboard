




from flask import Flask, jsonify, request, send_from_directory, Response
from flask_cors import CORS
import pandas as pd
import json
import os
import requests
from datetime import datetime, timedelta
import random
from io import StringIO
import traceback

app = Flask(__name__)
CORS(app)

# Global variables to store data
patients_df = None
dashboard_stats = None
growth_metrics = None

# Google Sheets CSV URL - Replace this with your Google Sheets published CSV URL
GOOGLE_SHEETS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSyFf7QSGYYAawZk80QfL30IrehHkCaYGFsj9t8digpFhnOX6DKjRDDWIyARTy2xZF53Qekhp8QuckH/pub?gid=488215142&single=true&output=csv"

def load_dashboard_stats():
    """Load dashboard statistics data"""
    global dashboard_stats
    
    try:
        dashboard_stats = pd.DataFrame({
            'csvmetric': ['newPatients', 'opdPatients', 'operations', 'visitors'],
            'value': ['234', '89%', '45', '25000'],
            'progress': [75, 89, 60, 85],
            'color': ['#2e9e5b', '#e74c3c', '#2e9e5b', '#f39c12']
        })
        
        print("Dashboard stats loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading dashboard stats: {e}")
        return False

def load_growth_metrics():
    """Load growth metrics data"""
    global growth_metrics
    
    try:
        growth_metrics = pd.DataFrame({
            'csvmetric': ['newPatient', 'heartSurgeries', 'medicalTreatment'],
            'growth_text': ['+12%', '-5%', '+8%'],
            'growth_type': ['positive', 'negative', 'positive'],
            'overall': ['75%', '78%', '92%'],
            'monthly': ['52%', '8%', '15%'],
            'day': ['12%', '1%', '3%']
        })
        
        print("Growth metrics loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading growth metrics: {e}")
        return False

class ChartDataProvider:
    """Class to provide all chart data configurations"""
    
    @staticmethod
    def get_new_patients_chart():
        return {
            "type": "doughnut",
            "data": {
                "datasets": [{
                    "data": [85, 15],
                    "backgroundColor": ["#36a2eb", "#6c5ce7"],
                    "borderWidth": 0
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "cutout": "70%",
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {"enabled": False}
                }
            }
        }
    
    @staticmethod
    def get_opd_patients_chart():
        return {
            "type": "bar",
            "data": {
                "labels": [""] * 12,
                "datasets": [{
                    "data": [50, 40, 45, 50, 55, 40, 35, 30, 45, 50, 55, 40],
                    "backgroundColor": "#36a2eb",
                    "barThickness": 4,
                    "borderRadius": 2
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {"enabled": False}
                },
                "scales": {
                    "x": {"display": False},
                    "y": {"display": False}
                }
            }
        }
    
    @staticmethod
    def get_hospital_survey_chart():
        return {
            "type": "line",
            "data": {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                "datasets": [{
                    "data": [50, 40, 30, 40, 50, 45, 35, 55, 25, 30, 22, 17],
                    "borderColor": "#6c5ce7",
                    "tension": 0.4,
                    "pointRadius": 0,
                    "borderWidth": 3
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False}
                },
                "scales": {
                    "x": {
                        "grid": {"display": False}
                    },
                    "y": {
                        "beginAtZero": True,
                        "max": 60,
                        "ticks": {"stepSize": 10}
                    }
                }
            }
        }
    
    @staticmethod
    def get_operations_chart():
        return {
            "type": "line",
            "data": {
                "labels": [""] * 7,
                "datasets": [{
                    "data": [50, 25, 20, 30, 25, 35, 30],
                    "borderColor": "#8e44ad",
                    "tension": 0,
                    "pointRadius": 0,
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {"enabled": False}
                },
                "scales": {
                    "x": {"display": False},
                    "y": {"display": False}
                }
            }
        }
    
    @staticmethod
    def get_visitors_chart():
        return {
            "type": "line",
            "data": {
                "labels": [""] * 12,
                "datasets": [{
                    "data": [60, 25, 30, 35, 40, 50, 40, 30, 25, 35, 50, 40],
                    "borderColor": "#6c5ce7",
                    "backgroundColor": "rgba(108, 92, 231, 0.2)",
                    "tension": 0.4,
                    "pointRadius": 0,
                    "borderWidth": 2,
                    "fill": True
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {"enabled": False}
                },
                "scales": {
                    "x": {"display": False},
                    "y": {"display": False}
                }
            }
        }
    
    @staticmethod
    def get_new_patient_chart():
        return {
            "type": "line",
            "data": {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
                "datasets": [
                    {
                        "label": "Current",
                        "data": [60, 25, 40, 30, 45, 35, 45],
                        "borderColor": "#4bc0c0",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "tension": 0.4,
                        "pointRadius": 0,
                        "borderWidth": 2,
                        "fill": True
                    },
                    {
                        "label": "Previous",
                        "data": [30, 35, 25, 45, 30, 40, 35],
                        "borderColor": "#aaa",
                        "backgroundColor": "rgba(170, 170, 170, 0.2)",
                        "tension": 0.4,
                        "pointRadius": 0,
                        "borderWidth": 2,
                        "fill": True
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False}
                },
                "scales": {
                    "x": {
                        "grid": {"display": False}
                    },
                    "y": {
                        "beginAtZero": True,
                        "max": 100,
                        "ticks": {"stepSize": 20}
                    }
                }
            }
        }
    
    @staticmethod
    def get_heart_surgeries_chart():
        return {
            "type": "bar",
            "data": {
                "labels": ["Jan '19", "Q2 Jan", "Q3 Jan", "Q4 Jan", "Q5 Jan", "Q6 Jan"],
                "datasets": [
                    {
                        "label": "Dataset 1",
                        "data": [45, 55, 41, 67, 22, 43],
                        "backgroundColor": "#36a2eb"
                    },
                    {
                        "label": "Dataset 2",
                        "data": [71, 23, 20, 8, 13, 27],
                        "backgroundColor": "#4bc0c0"
                    },
                    {
                        "label": "Dataset 3",
                        "data": [11, 17, 15, 15, 21, 14],
                        "backgroundColor": "#ff9f40"
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False}
                },
                "scales": {
                    "x": {
                        "stacked": True,
                        "grid": {"display": False}
                    },
                    "y": {
                        "stacked": True,
                        "beginAtZero": True,
                        "max": 100,
                        "ticks": {"stepSize": 20}
                    }
                }
            }
        }
    
    @staticmethod
    def get_medical_treatment_chart():
        return {
            "type": "line",
            "data": {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
                "datasets": [
                    {
                        "label": "Treatment A",
                        "data": [60, 40, 35, 50, 90, 40, 50, 40],
                        "borderColor": "#f59e0b",
                        "backgroundColor": "transparent",
                        "borderWidth": 2,
                        "tension": 0.4,
                        "borderDash": [5, 5]
                    },
                    {
                        "label": "Treatment B",
                        "data": [55, 35, 40, 20, 25, 30, 35, 40],
                        "borderColor": "#3b82f6",
                        "backgroundColor": "transparent",
                        "borderWidth": 2,
                        "tension": 0.4
                    },
                    {
                        "label": "Treatment C",
                        "data": [35, 45, 30, 25, 15, 40, 20, 30],
                        "borderColor": "#10b981",
                        "backgroundColor": "transparent",
                        "borderWidth": 2,
                        "tension": 0.4,
                        "borderDash": [3, 3]
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False}
                },
                "scales": {
                    "x": {
                        "grid": {"display": False}
                    },
                    "y": {
                        "min": 0,
                        "max": 100
                    }
                }
            }
        }

def load_csv_data():
    """Load patient data from Google Sheets CSV URL with timeout and fallback"""
    global patients_df
    
    try:
        print("Loading data from Google Sheets...")
        
        # Make HTTP request with shorter timeout
        response = requests.get(GOOGLE_SHEETS_CSV_URL, timeout=5)
        response.raise_for_status()
        
        # Parse CSV data
        csv_data = StringIO(response.text)
        patients_df = pd.read_csv(csv_data)
        
        # Validate data
        if patients_df.empty:
            print("Google Sheets returned empty data. Using sample data.")
            patients_df = create_sample_data()
        else:
            print(f"Successfully loaded {len(patients_df)} patients from Google Sheets")
            
            # Validate required columns
            required_columns = ['name', 'doctor', 'admitDate', 'disease', 'roomNo']
            missing_columns = [col for col in required_columns if col not in patients_df.columns]
            
            if missing_columns:
                print(f"Warning: Missing columns in Google Sheets: {missing_columns}")
                patients_df = create_sample_data()
                print("Using sample data due to missing columns")
        
    except requests.exceptions.Timeout:
        print("Google Sheets request timed out. Using sample data.")
        patients_df = create_sample_data()
    except requests.exceptions.RequestException as e:
        print(f"Error loading from Google Sheets: {e}")
        print("Falling back to sample data...")
        patients_df = create_sample_data()
    except pd.errors.EmptyDataError:
        print("Google Sheets returned empty data. Using sample data.")
        patients_df = create_sample_data()
    except Exception as e:
        print(f"Unexpected error loading CSV: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        patients_df = create_sample_data()

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
    
    print(f"Created sample data with {len(sample_data)} patients")
    return pd.DataFrame(sample_data)

def get_disease_stats():
    """Get disease statistics for charts"""
    if patients_df is None:
        return {}
    
    try:
        disease_counts = patients_df['disease'].value_counts().to_dict()
        return disease_counts
    except Exception as e:
        print(f"Error getting disease stats: {e}")
        return {}

def get_monthly_stats():
    """Get monthly statistics for charts"""
    if patients_df is None:
        return {}
    
    try:
        # Group by month
        patients_df['month'] = pd.to_datetime(patients_df['admitDate']).dt.to_period('M')
        monthly_counts = patients_df.groupby('month').size().to_dict()
        
        # Convert period to string for JSON serialization
        monthly_stats = {str(k): v for k, v in monthly_counts.items()}
        
        return monthly_stats
    except Exception as e:
        print(f"Error getting monthly stats: {e}")
        return {}

def get_doctor_stats():
    """Get doctor statistics"""
    if patients_df is None:
        return {}
    
    try:
        doctor_counts = patients_df['doctor'].value_counts().to_dict()
        return doctor_counts
    except Exception as e:
        print(f"Error getting doctor stats: {e}")
        return {}

# Initialize data function
def initialize_data():
    """Initialize all data with error handling"""
    try:
        print("Initializing hospital dashboard data...")
        
        # Load all data
        load_csv_data()
        load_dashboard_stats()
        load_growth_metrics()
        
        print("Data initialization completed successfully")
        return True
    except Exception as e:
        print(f"Error during data initialization: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

# API Routes

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'patients_loaded': patients_df is not None,
        'dashboard_stats_loaded': dashboard_stats is not None,
        'growth_metrics_loaded': growth_metrics is not None,
        'patient_count': len(patients_df) if patients_df is not None else 0
    })

@app.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """Refresh data from Google Sheets"""
    try:
        initialize_data()
        return jsonify({
            'message': 'Data refreshed successfully',
            'patients_count': len(patients_df) if patients_df is not None else 0
        })
    except Exception as e:
        print(f"Error refreshing data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Initialize data if not loaded
        if dashboard_stats is None:
            load_dashboard_stats()
        
        if dashboard_stats is None:
            return jsonify({'error': 'Dashboard stats not loaded'}), 500
        
        # Convert to dictionary with metric name as key
        stats_dict = {}
        for _, row in dashboard_stats.iterrows():
            stats_dict[row['csvmetric']] = {
                'value': row['value'],
                'progress': row['progress'],
                'color': row['color']
            }
        
        return jsonify(stats_dict)
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/growth-metrics', methods=['GET'])
def get_growth_metrics():
    """Get growth metrics"""
    try:
        # Initialize data if not loaded
        if growth_metrics is None:
            load_growth_metrics()
        
        if growth_metrics is None:
            return jsonify({'error': 'Growth metrics not loaded'}), 500
        
        # Convert to dictionary with metric name as key
        metrics_dict = {}
        for _, row in growth_metrics.iterrows():
            metrics_dict[row['csvmetric']] = {
                'growth_text': row['growth_text'],
                'growth_type': row['growth_type'],
                'overall': row['overall'],
                'monthly': row['monthly'],
                'day': row['day']
            }
        
        return jsonify(metrics_dict)
    except Exception as e:
        print(f"Error getting growth metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get combined dashboard data (stats + growth metrics)"""
    try:
        # Initialize data if not loaded
        if dashboard_stats is None:
            load_dashboard_stats()
        if growth_metrics is None:
            load_growth_metrics()
            
        # Get dashboard stats
        stats_dict = {}
        if dashboard_stats is not None:
            for _, row in dashboard_stats.iterrows():
                stats_dict[row['csvmetric']] = {
                    'value': row['value'],
                    'progress': row['progress'],
                    'color': row['color']
                }
        
        # Get growth metrics
        metrics_dict = {}
        if growth_metrics is not None:
            for _, row in growth_metrics.iterrows():
                metrics_dict[row['csvmetric']] = {
                    'growth_text': row['growth_text'],
                    'growth_type': row['growth_type'],
                    'overall': row['overall'],
                    'monthly': row['monthly'],
                    'day': row['day']
                }
        
        return jsonify({
            'dashboard_stats': stats_dict,
            'growth_metrics': metrics_dict
        })
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients data"""
    try:
        # Initialize data if not loaded
        if patients_df is None:
            load_csv_data()
            
        patients_list = patients_df.to_dict('records') if patients_df is not None else []
        
        # Convert datetime to string for JSON serialization
        for patient in patients_list:
            if 'admitDate' in patient:
                patient['admitDate'] = str(patient['admitDate'])[:10]  # YYYY-MM-DD format
        
        return jsonify({
            'patients': patients_list,
            'total': len(patients_list)
        })
    except Exception as e:
        print(f"Error getting patients: {e}")
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
        print(f"Error getting patient: {e}")
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
        
        return jsonify({'message': 'Patient added successfully', 'id': len(patients_df) - 1})
    except Exception as e:
        print(f"Error adding patient: {e}")
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
        
        return jsonify({'message': 'Patient updated successfully'})
    except Exception as e:
        print(f"Error updating patient: {e}")
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
        
        return jsonify({'message': 'Patient deleted successfully'})
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics for data analysis"""
    try:
        stats = {
            'diseases': get_disease_stats(),
            'monthly': get_monthly_stats(),
            'doctors': get_doctor_stats()
        }
        return jsonify(stats)
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

# Chart API Routes
@app.route('/api/charts/new-patients', methods=['GET'])
def get_new_patients_chart():
    """Get new patients chart data"""
    try:
        return jsonify(ChartDataProvider.get_new_patients_chart())
    except Exception as e:
        print(f"Error getting new patients chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/opd-patients', methods=['GET'])
def get_opd_patients_chart():
    """Get OPD patients chart data"""
    try:
        return jsonify(ChartDataProvider.get_opd_patients_chart())
    except Exception as e:
        print(f"Error getting OPD patients chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/hospital-survey', methods=['GET'])
def get_hospital_survey_chart():
    """Get hospital survey chart data"""
    try:
        return jsonify(ChartDataProvider.get_hospital_survey_chart())
    except Exception as e:
        print(f"Error getting hospital survey chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/operations', methods=['GET'])
def get_operations_chart():
    """Get operations chart data"""
    try:
        return jsonify(ChartDataProvider.get_operations_chart())
    except Exception as e:
        print(f"Error getting operations chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/visitors', methods=['GET'])
def get_visitors_chart():
    """Get visitors chart data"""
    try:
        return jsonify(ChartDataProvider.get_visitors_chart())
    except Exception as e:
        print(f"Error getting visitors chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/new-patient', methods=['GET'])
def get_new_patient_chart():
    """Get new patient chart data"""
    try:
        return jsonify(ChartDataProvider.get_new_patient_chart())
    except Exception as e:
        print(f"Error getting new patient chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/heart-surgeries', methods=['GET'])
def get_heart_surgeries_chart():
    """Get heart surgeries chart data"""
    try:
        return jsonify(ChartDataProvider.get_heart_surgeries_chart())
    except Exception as e:
        print(f"Error getting heart surgeries chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/medical-treatment', methods=['GET'])
def get_medical_treatment_chart():
    """Get medical treatment chart data"""
    try:
        return jsonify(ChartDataProvider.get_medical_treatment_chart())
    except Exception as e:
        print(f"Error getting medical treatment chart: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/all', methods=['GET'])
def get_all_charts():
    """Get all chart data in a single request"""
    try:
        return jsonify({
            'newPatients': ChartDataProvider.get_new_patients_chart(),
            'opdPatients': ChartDataProvider.get_opd_patients_chart(),
            'hospitalSurvey': ChartDataProvider.get_hospital_survey_chart(),
            'operations': ChartDataProvider.get_operations_chart(),
            'visitors': ChartDataProvider.get_visitors_chart(),
            'newPatient': ChartDataProvider.get_new_patient_chart(),
            'heartSurgeries': ChartDataProvider.get_heart_surgeries_chart(),
            'medicalTreatment': ChartDataProvider.get_medical_treatment_chart()
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
    print("  GET  /api/stats - Get statistics for data analysis")
    print("  POST /api/refresh-data - Refresh data from Google Sheets")
    print("  POST /api/upload-csv - Upload CSV file")
    print("  GET  /api/export-csv - Export data to CSV")
    print("  POST /api/update-sheets-url - Update Google Sheets URL")
    print("\nChart endpoints:")
    print("  GET  /api/charts/new-patients - New patients chart")
    print("  GET  /api/charts/opd-patients - OPD patients chart")
    print("  GET  /api/charts/hospital-survey - Hospital survey chart")
    print("  GET  /api/charts/operations - Operations chart")
    print("  GET  /api/charts/visitors - Visitors chart")
    print("  GET  /api/charts/new-patient - New patient trend chart")
    print("  GET  /api/charts/heart-surgeries - Heart surgeries chart")
    print("  GET  /api/charts/medical-treatment - Medical treatment chart")
    print("  GET  /api/dashboard-stats - Dashboard stats")
    print("  GET  /api/growth-metrics - Growth metrics")
    print("  GET  /api/charts/all - All charts data")
    
    app.run(debug=True)
