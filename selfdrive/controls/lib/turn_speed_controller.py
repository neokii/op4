import numpy as np
import time
from common.params import Params
from cereal import log
from common.realtime import sec_since_boot


_SPEED_OFFSET_TH = -1.0  # m/s Maximum offset between speed limit and current speed for adapting state.
_LIMIT_ADAPT_ACC = -1.2  # Ideal acceleration for the adapting (braking) phase when approaching speed limits.
_MIN_SPEED_LIMIT = 8.33  # m/s, Minimum speed limit to provide as solution.

_MAX_MAP_DATA_AGE = 10.0  # s Maximum time to hold to map data, then consider it invalid.

_DEBUG = False

TurnSpeedControlState = log.LongitudinalPlan.SpeedLimitControlState


def _debug(msg):
  if not _DEBUG:
    return
  print(msg)


def _description_for_state(turn_speed_control_state):
  if turn_speed_control_state == TurnSpeedControlState.inactive:
    return 'INACTIVE'
  if turn_speed_control_state == TurnSpeedControlState.tempInactive:
    return 'TEMP INACTIVE'
  if turn_speed_control_state == TurnSpeedControlState.adapting:
    return 'ADAPTING'
  if turn_speed_control_state == TurnSpeedControlState.active:
    return 'ACTIVE'


class TurnSpeedController():
  def __init__(self):
    self._params = Params()
    self._last_params_update = 0.0
    self._is_enabled = self._params.get_bool("TurnSpeedControl")
    self._op_enabled = False
    self._v_ego = 0.0
    self._v_cruise_setpoint = 0.0

    self._v_offset = 0.0
    self._speed_limit = 0.0
    self._speed_limit_temp_inactive = 0.0
    self._distance = 0.0
    self._turn_sign = 0
    self._state = TurnSpeedControlState.inactive

    self._next_speed_limit_prev = 0.

    self._acc_limits = [0.0, 0.0]
    self._v_turn_limit = 0.0

  @property
  def v_turn_limit(self):
    return float(self._v_turn_limit) if self.is_active else self._v_cruise_setpoint

  @property
  def acc_limits(self):
    return self._acc_limits

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, value):
    if value != self._state:
      _debug(f'Turn Speed Controller state: {_description_for_state(value)}')

      if value == TurnSpeedControlState.tempInactive:
        # Track the speed limit value when controller was set to temp inactive.
        self._speed_limit_temp_inactive = self._speed_limit

    self._state = value

  @property
  def is_active(self):
    return self.state > TurnSpeedControlState.tempInactive

  @property
  def speed_limit(self):
    return max(self._speed_limit, _MIN_SPEED_LIMIT) if self._speed_limit > 0. else 0.

  @property
  def distance(self):
    return self._distance

  @property
  def turn_sign(self):
    return self._turn_sign

  def _get_limit_from_map_data(self, sm):
    """Provides the speed limit, distance and turn sign to it for turns based on map data.
    """
    # Ignore if no live map data
    sock = 'liveMapData'
    if sm.logMonoTime[sock] is None:
      _debug('TS: No map data for turn speed limit')
      return 0., 0., 0

    # Load map_data and initialize
    map_data = sm[sock]
    speed_limit = 0.

    # Calculate the age of the gps fix. Ignore if too old.
    gps_fix_age = time.time() - map_data.lastGpsTimestamp * 1e-3
    if gps_fix_age > _MAX_MAP_DATA_AGE:
      _debug(f'TS: Ignoring map data as is too old. Age: {gps_fix_age}')
      return 0., 0., 0

    # Load turn ahead sections info from map_data with distances corrected by gps_fix_age
    distance_since_fix = self._v_ego * gps_fix_age
    distances_to_sections_ahead = np.maximum(0., np.array(map_data.turnSpeedLimitsAheadDistances) - distance_since_fix)
    speed_limit_in_sections_ahead = map_data.turnSpeedLimitsAhead
    turn_sings_in_sections_ahead = map_data.turnSpeedLimitsAheadSigns

    # Ensure current speed limit is considered only if we are inside the section.
    if map_data.turnSpeedLimitValid and self._v_ego > 0.:
      speed_limit_end_time = (map_data.turnSpeedLimitEndDistance / self._v_ego) - gps_fix_age
      if speed_limit_end_time > 0.:
        speed_limit = map_data.turnSpeedLimit

    # When we have no ahead speed limit to consider or all are greater than current speed limit
    # or car has stopped, then provide current value and reset tracking.
    turn_sign = map_data.turnSpeedLimitSign if map_data.turnSpeedLimitValid else 0
    if len(speed_limit_in_sections_ahead) == 0 or self._v_ego <= 0. or \
       (speed_limit > 0 and np.amin(speed_limit_in_sections_ahead) > speed_limit):
      self._next_speed_limit_prev = 0.
      return speed_limit, 0., turn_sign

    # Calculated the time needed to adapt to the limits ahead and the corresponding distances.
    adapt_times = (np.maximum(speed_limit_in_sections_ahead, _MIN_SPEED_LIMIT) - self._v_ego) / _LIMIT_ADAPT_ACC
    adapt_distances = self._v_ego * adapt_times + 0.5 * _LIMIT_ADAPT_ACC * adapt_times**2
    distance_gaps = distances_to_sections_ahead - adapt_distances

    # We select as next speed limit, the one that have the lowest distance gap.
    next_idx = np.argmin(distance_gaps)
    next_speed_limit = speed_limit_in_sections_ahead[next_idx]
    distance_to_section_ahead = distances_to_sections_ahead[next_idx]
    next_turn_sign = turn_sings_in_sections_ahead[next_idx]
    distance_gap = distance_gaps[next_idx]

    # When we have a next_speed_limit value that has not changed from a provided next speed limit value
    # in previous resolutions, we keep providing it along with the udpated distance to it.
    if next_speed_limit == self._next_speed_limit_prev:
      return next_speed_limit, distance_to_section_ahead, next_turn_sign

    # Reset tracking
    self._next_speed_limit_prev = 0.

    # When we detect we are close enough, we provide the next limit value and track it.
    if distance_gap <= 0.:
      self._next_speed_limit_prev = next_speed_limit
      return next_speed_limit, distance_to_section_ahead, next_turn_sign

    # Otherwise we just provide the calculated speed_limit
    return speed_limit, 0., turn_sign

  def _update_params(self):
    time = sec_since_boot()
    if time > self._last_params_update + 5.0:
      self._is_enabled = self._params.get_bool("TurnSpeedControl")
      self._last_params_update = time

  def _update_calculations(self):
    # Update current velocity offset (error)
    self._v_offset = self.speed_limit - self._v_ego

  def _state_transition(self, sm):
    # In any case, if op is disabled, or turn speed limit control is disabled
    # or the reported speed limit is 0, deactivate.
    if not self._op_enabled or not self._is_enabled or self.speed_limit == 0.:
      self.state = TurnSpeedControlState.inactive
      return

    # In any case, we deactivate the speed limit controller temporarily
    # if gas is pressed (to support gas override implementations).
    if sm['carState'].gasPressed:
      self.state = TurnSpeedControlState.tempInactive
      return

    # inactive
    if self.state == TurnSpeedControlState.inactive:
      # If the limit speed offset is negative (i.e. reduce speed) and lower than threshold
      # we go to adapting state to quickly reduce speed, otherwise we go directly to active
      if self._v_offset < _SPEED_OFFSET_TH:
        self.state = TurnSpeedControlState.adapting
      else:
        self.state = TurnSpeedControlState.active
    # tempInactive
    elif self.state == TurnSpeedControlState.tempInactive:
      # if the speed limit recorded when going to temp Inactive changes
      # then set to inactive, activation will happen on next cycle
      if self._speed_limit != self._speed_limit_temp_inactive:
        self.state = TurnSpeedControlState.inactive
    # adapting
    elif self.state == TurnSpeedControlState.adapting:
      # Go to active once the speed offset is over threshold.
      if self._v_offset >= _SPEED_OFFSET_TH:
        self.state = TurnSpeedControlState.active
    # active
    elif self.state == TurnSpeedControlState.active:
      # Go to adapting if the speed offset goes below threshold.
      if self._v_offset < _SPEED_OFFSET_TH:
        self.state = TurnSpeedControlState.adapting

  def _update_solution(self):
    # Calculate acceleration limits and turn speed based on state.
    acc_limits = self._acc_limits
    v_turn_limit = self._v_cruise_setpoint

    # inactive or tempInactive state
    if self.state <= TurnSpeedControlState.tempInactive:
      # Preserve current values
      pass
    # adapting
    elif self.state == TurnSpeedControlState.adapting:
      # When adapting we target the turn speed limit speed with the adapt acceleration if lower than provided limits.
      v_turn_limit = self.speed_limit
      acc_limits[0] = min(_LIMIT_ADAPT_ACC, acc_limits[0])
    # active
    elif self.state == TurnSpeedControlState.active:
      v_turn_limit = self.speed_limit

    # update solution values.
    self._v_turn_limit = v_turn_limit
    self._acc_limits = acc_limits

  def update(self, enabled, v_ego, sm, acc_limits):
    self._op_enabled = enabled
    self._v_ego = v_ego
    self._acc_limits = acc_limits

    # Get the speed limit from Map Data
    self._speed_limit, self._distance, self._turn_sign = self._get_limit_from_map_data(sm)

    self._update_params()
    self._update_calculations()
    self._state_transition(sm)
    self._update_solution()
