import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime

class FraudDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.amount_col = None
        self.date_col = None
        self.entity_col = None

    def detect_fraud(self, df):
        self._detect_columns(df)
        features = self._create_features(df)
        
        self.model.fit(features)
        predictions = self.model.predict(features)
        df['anomaly_score'] = self.model.decision_function(features)
        df['anomaly'] = predictions
        
        suspicious = df[df['anomaly'] == -1]
        fraud_type = self._determine_fraud_type(suspicious)
        
        return {
            'fraud_type': fraud_type,
            'suspicious_entries': suspicious.to_dict('records')
        }

    def _detect_columns(self, df):
        amount_patterns = ['amount', 'amt', 'value']
        date_patterns = ['date', 'time', 'timestamp']
        entity_patterns = ['account', 'user', 'entity']
        
        self.amount_col = self._find_column(df, amount_patterns)
        self.date_col = self._find_column(df, date_patterns)
        self.entity_col = self._find_column(df, entity_patterns)

    def _find_column(self, df, patterns):
        for pattern in patterns:
            if pattern in df.columns:
                return pattern
        return None

    def _create_features(self, df):
        features = pd.DataFrame()
        
        if self.amount_col:
            features['log_amount'] = np.log(df[self.amount_col] + 1)
        if self.date_col:
            df[self.date_col] = pd.to_datetime(df[self.date_col])
            features['hour'] = df[self.date_col].dt.hour
            features['day_of_week'] = df[self.date_col].dt.dayofweek
        if self.entity_col:
            features['entity_freq'] = df.groupby(self.entity_col)[self.entity_col].transform('count')
        
        return features.fillna(0)

    def _determine_fraud_type(self, data):
        fraud_types = []
        if len(data) == 0:
            return ['no suspicious activity detected']
        
        avg_amount = data[self.amount_col].mean()
        time_diff = data[self.date_col].max() - data[self.date_col].min()
        
        if avg_amount > 10000:
            fraud_types.append('money_laundering')
        if time_diff.total_seconds() < 86400 and len(data) > 3:
            fraud_types.append('embezzlement')
        if len(fraud_types) == 0:
            fraud_types.append('suspicious_activity')
            
        return fraud_types

    def generate_recommendations(self, results):
        actions = {
            'immediate': [
                {
                    'title': 'Account Freeze',
                    'description': 'Temporarily freeze all suspicious accounts',
                    'deadline': '24 hours',
                    'priority': 'Critical',
                    'responsible': 'Security Team'
                }
            ],
            'investigation': [
                {
                    'title': 'Forensic Audit',
                    'description': 'Conduct detailed transaction analysis for last 90 days',
                    'deadline': '72 hours',
                    'priority': 'High',
                    'responsible': 'Audit Department'
                }
            ],
            'prevention': [
                {
                    'title': 'System Upgrade',
                    'description': 'Implement real-time monitoring system',
                    'deadline': '30 days',
                    'priority': 'Medium',
                    'responsible': 'IT Department'
                }
            ]
        }
        
        if 'money_laundering' in results['fraud_type']:
            actions['immediate'].append({
                'title': 'Regulatory Reporting',
                'description': 'File SAR (Suspicious Activity Report) with FinCEN',
                'deadline': '48 hours',
                'priority': 'Critical',
                'responsible': 'Compliance Officer'
            })
            
        if 'embezzlement' in results['fraud_type']:
            actions['investigation'].append({
                'title': 'Internal Investigation',
                'description': 'Review employee access and authorization logs',
                'deadline': '48 hours',
                'priority': 'High',
                'responsible': 'HR Department'
            })
            
        return actions

    def get_summary_stats(self, df, suspicious):
        return {
            'avg_amount': round(pd.DataFrame(suspicious)[self.amount_col].mean(), 2),
            'geo_risk': self._calculate_geo_risk(df),
            'time_score': self._calculate_time_score(df)
        }

    def _calculate_geo_risk(self, df):
        # Placeholder for actual geolocation analysis
        return np.random.randint(30, 90)

    def _calculate_time_score(self, df):
        # Placeholder for temporal pattern analysis
        return np.random.randint(40, 95)