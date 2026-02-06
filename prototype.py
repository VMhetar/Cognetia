import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import deque
import random

# Define Patient State (Simplified)
class PatientState:
    def __init__(self):
        self.symptoms = {
            'pain_level': 0.0,  # 0-10
            'fever': 0.0,       # Celsius above 37
            'heart_rate': 80.0, # BPM
            'bp_systolic': 120.0,
            'bp_diastolic': 80.0,
            'conscious': 1.0,   # 1=yes, 0=no
            'bleeding': 0.0,    # 0-10 severity
            'breathing_diff': 0.0 # 0-10
        }
        self.age = 40.0
        self.known_conditions = []  # e.g., ['diabetes', 'hypertension']
        self.time_in_er = 0  # minutes
        
    def to_vector(self):
        """Convert to numerical vector"""
        vec = list(self.symptoms.values())
        vec.append(self.age / 100.0)  # Normalized
        vec.append(len(self.known_conditions) / 5.0)  # Normalized
        vec.append(self.time_in_er / 240.0)  # Normalized to 4 hours
        return np.array(vec, dtype=np.float32)
    
    def update(self, action):
        """Simulate patient progression based on action"""
        # This is the REAL dynamics (ground truth simulation)
        # In real use, this would be actual patient response
        new_state = self.copy()
        
        # Simulate some disease progression
        if new_state.symptoms['fever'] > 0:
            new_state.symptoms['fever'] += np.random.normal(0.1, 0.05)
            
        # Action effects
        if action == 'give_antipyretic' and new_state.symptoms['fever'] > 0:
            new_state.symptoms['fever'] -= 0.5
            
        elif action == 'give_analgesic':
            new_state.symptoms['pain_level'] = max(0, new_state.symptoms['pain_level'] - 3)
            
        elif action == 'order_blood_test':
            # Test reveals information (but takes time)
            new_state.time_in_er += 30
            
        return new_state
    
    def copy(self):
        new_state = PatientState()
        new_state.symptoms = self.symptoms.copy()
        new_state.age = self.age
        new_state.known_conditions = self.known_conditions.copy()
        new_state.time_in_er = self.time_in_er
        return new_state

# Available Actions
ACTIONS = [
    'monitor_only',
    'give_analgesic',
    'give_antipyretic',
    'order_blood_test',
    'order_ecg',
    'call_cardio',
    'call_surgeon',
    'admit_icu',
    'discharge'
]