import math

import pytest

from midge import obstacles

# Same lidar as the robot: 720 samples from -90 to +90 degrees
N = 720
ANGLE_MIN = -math.pi / 2
INCREMENT = math.pi / (N - 1)


def scan_with(obstacle_degrees=(), distance=0.5, background=math.inf):
    ranges = [background] * N
    for deg in obstacle_degrees:
        i = round((math.radians(deg) - ANGLE_MIN) / INCREMENT)
        ranges[i] = distance
    return ranges


def regions(ranges, sectors=obstacles.SECTORS_3):
    return obstacles.sector_distances(ranges, ANGLE_MIN, INCREMENT, sectors)


def test_empty_scan_is_max_range():
    assert regions(scan_with()) == {'right': 10.0, 'front': 10.0, 'left': 10.0}


def test_invalid_readings_are_ignored():
    ranges = scan_with()
    ranges[0], ranges[1], ranges[2] = float('nan'), 0.0, -1.0
    assert regions(ranges)['right'] == 10.0


@pytest.mark.parametrize('deg, sector', [(-80, 'right'), (0, 'front'), (25, 'front'), (75, 'left')])
def test_sector_of_a_reading(deg, sector):
    r = regions(scan_with([deg]))
    assert r[sector] == 0.5
    assert all(v == 10.0 for k, v in r.items() if k != sector)


def test_thin_obstacle_is_seen():
    # A single beam hitting a thin table leg must count
    assert regions(scan_with([3], distance=0.8))['front'] == 0.8


def test_five_sectors():
    r = regions(scan_with([-70, 40]), obstacles.SECTORS_5)
    assert r['right'] == 0.5 and r['front_left'] == 0.5 and r['front'] == 10.0


@pytest.mark.parametrize('degrees, state', [
    ((), obstacles.CLEAR),
    ((0,), obstacles.FRONT),
    ((-60,), obstacles.RIGHT),
    ((60,), obstacles.LEFT),
    ((0, -60), obstacles.FRONT_RIGHT),
    ((0, 60), obstacles.FRONT_LEFT),
    ((-60, 60), obstacles.CORRIDOR),
    ((-60, 0, 60), obstacles.BLOCKED),
])
def test_classify(degrees, state):
    assert obstacles.classify(regions(scan_with(degrees)), min_distance=1.0) == state


def test_distance_equal_to_threshold_is_free():
    r = {'right': 1.0, 'front': 1.0, 'left': 1.0}
    assert obstacles.classify(r, min_distance=1.0) == obstacles.CLEAR


@pytest.mark.parametrize('state, linear, angular', [
    (obstacles.CLEAR, 0.4, 0.0),
    (obstacles.CORRIDOR, 0.4, 0.0),
    (obstacles.RIGHT, 0.0, 0.8),
    (obstacles.FRONT_RIGHT, 0.0, 0.8),
    (obstacles.LEFT, 0.0, -0.8),
    (obstacles.FRONT_LEFT, 0.0, -0.8),
])
def test_avoidance_command(state, linear, angular):
    r = {'right': 5.0, 'front': 5.0, 'left': 5.0}
    assert obstacles.avoidance_command(state, r, 0.4, 0.8)[:2] == (linear, angular)


def test_front_obstacle_turns_towards_free_side_and_keeps_it():
    more_room_right = {'right': 3.0, 'front': 0.5, 'left': 1.5}
    linear, angular, sign = obstacles.avoidance_command(obstacles.FRONT, more_room_right, 0.4, 0.8)
    assert (linear, angular, sign) == (0.0, -0.8, -1)

    # Next cycle the left looks better, but the robot keeps the side it chose
    more_room_left = {'right': 1.5, 'front': 0.5, 'left': 3.0}
    _, angular, sign = obstacles.avoidance_command(obstacles.FRONT, more_room_left, 0.4, 0.8, sign)
    assert (angular, sign) == (-0.8, -1)

    # Once the front is clear the choice is forgotten
    assert obstacles.avoidance_command(obstacles.CLEAR, more_room_left, 0.4, 0.8, sign)[2] == 0
