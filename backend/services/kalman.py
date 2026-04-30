import numpy as np

class KalmanTracker:
    def __init__(self):
        self.x = None  # [lat, lng, v_lat, v_lng]
        self.P = np.eye(4) * 500

        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])

        self.R = np.eye(2) * 0.0001
        self.Q = np.eye(4) * 0.00001

    def initialize(self, lat, lng):
        self.x = np.array([[lat], [lng], [0], [0]])

    def predict(self, dt):
        F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        self.x = F @ self.x
        self.P = F @ self.P @ F.T + self.Q

    def update(self, lat, lng):
        z = np.array([[lat], [lng]])

        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

    def get_position(self):
        return float(self.x[0]), float(self.x[1])