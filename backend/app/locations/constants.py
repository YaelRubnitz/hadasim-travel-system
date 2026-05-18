"""Centralized domain constants and thresholds for the location system."""

# Movement Analytics Thresholds
DEFAULT_STOP_RADIUS_KM = 0.04  # 40 meters
DEFAULT_MIN_STOP_DURATION_S = 300.0  # 5 minutes
DEFAULT_JUMP_SPEED_KPH = 25.0
DEFAULT_MIN_JUMP_DURATION_S = 30.0

# Proximity & Group Analytics Thresholds
DEFAULT_FAR_FROM_TEACHER_KM = 3.0  # Students > 3km are considered FAR
DEFAULT_ISOLATED_PEER_DISTANCE_M = 150.0  # Student with no peer within 150m is ISOLATED
