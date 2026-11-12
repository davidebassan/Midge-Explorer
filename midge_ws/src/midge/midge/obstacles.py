"""Obstacle detection and reactive avoidance, independent of ROS so it can be unit tested.

The lidar looks forward (-90 to +90 degrees). The scan is split in angular sectors
(right ... left) and each sector keeps its closest reading.
"""
import math

# Sector limits in degrees, from right (negative angles) to left
SECTORS_3 = {
    'right': (-90.0, -30.0),
    'front': (-30.0, 30.0),
    'left': (30.0, 90.0),
}
SECTORS_5 = {
    'right': (-90.0, -54.0),
    'front_right': (-54.0, -18.0),
    'front': (-18.0, 18.0),
    'front_left': (18.0, 54.0),
    'left': (54.0, 90.0),
}

# Avoidance states
CLEAR = 'No obstacle found'
FRONT = 'Found obstacle in front'
RIGHT = 'Found obstacle in front_right'
LEFT = 'Found obstacle in front_left'
FRONT_RIGHT = 'Found obstacle in front and front_right'
FRONT_LEFT = 'Found obstacle in front and front_left'
CORRIDOR = 'Found obstacle in front_left and front_right'
BLOCKED = 'Found obstacle in front and front_left and front_right'


def sector_distances(ranges, angle_min, angle_increment, sectors=SECTORS_3, max_range=10.0):
    """Closest valid reading in each sector, capped at max_range.

    Readings that are NaN, infinite (no hit) or not positive count as max_range.
    """
    result = {name: max_range for name in sectors}
    for i, distance in enumerate(ranges):
        if not math.isfinite(distance) or distance <= 0.0:
            continue
        angle = math.degrees(angle_min + i * angle_increment)
        for name, (low, high) in sectors.items():
            if low <= angle <= high and distance < result[name]:
                result[name] = distance
    return result


def classify(regions, min_distance):
    """Which of the eight obstacle situations the three regions (right/front/left) describe."""
    front = regions['front'] < min_distance
    left = regions['left'] < min_distance
    right = regions['right'] < min_distance

    if front and left and right:
        return BLOCKED
    if front and right:
        return FRONT_RIGHT
    if front and left:
        return FRONT_LEFT
    if front:
        return FRONT
    if left and right:
        return CORRIDOR
    if right:
        return RIGHT
    if left:
        return LEFT
    return CLEAR


def avoidance_command(state, regions, linear_speed, angular_speed, turn_sign=0):
    """Velocity for one avoidance state.

    Returns (linear, angular, turn_sign). Positive angular turns left (counter-clockwise).
    turn_sign remembers the side chosen for an obstacle straight ahead, so the robot
    keeps turning the same way until the front is clear instead of hesitating.
    BLOCKED is handled by the caller (turn around); here it only rotates in place.
    """
    if state == CLEAR:
        return linear_speed, 0.0, 0
    if state == CORRIDOR:
        return linear_speed, 0.0, 0
    if state in (RIGHT, FRONT_RIGHT):
        return 0.0, angular_speed, 0
    if state in (LEFT, FRONT_LEFT):
        return 0.0, -angular_speed, 0
    # FRONT or BLOCKED: turn towards the side with more room, and stick to it
    if turn_sign == 0:
        turn_sign = 1 if regions['left'] >= regions['right'] else -1
    return 0.0, turn_sign * angular_speed, turn_sign
