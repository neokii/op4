import math
from selfdrive.car.interfaces import CarInterfaceBase
from selfdrive.car.hyundai.interface import CarInterface
from selfdrive.controls.lib.latcontrol_indi import LatControlINDI
from common.numpy_fast import clip, interp
import numpy as np
import os
from cereal import car
from common.realtime import DT_CTRL
from selfdrive.car import apply_std_steer_torque_limits
from selfdrive.car.hyundai.hyundaican import create_lkas11, create_clu11, \
  create_scc11, create_scc12, create_scc13, create_scc14, \
  create_mdps12, create_lfahda_mfc, create_hda_mfc, create_spas11, create_spas12, create_ems_366
from selfdrive.car.hyundai.scc_smoother import SccSmoother
from selfdrive.car.hyundai.values import Buttons, CAR, FEATURES, CarControllerParams, FEATURES
from opendbc.can.packer import CANPacker
from selfdrive.config import Conversions as CV
from common.params import Params

from selfdrive.controls.lib.longcontrol import LongCtrlState
from selfdrive.road_speed_limiter import road_speed_limiter_get_active

VisualAlert = car.CarControl.HUDControl.VisualAlert

###### SPAS ######
STEER_ANG_MAX = 250         # SPAS Max Angle
# nissan limits values
ANGLE_DELTA_BP = [0., 5., 15.]
ANGLE_DELTA_V = [5., .8, .15]     # windup limit
ANGLE_DELTA_VU = [5., 3.5, 0.4]   # unwind limit

#STEER = (0, 30, 60, 90, 120) # Steering angle
#TQ = (2.5, 3.0, 3.5, 4.0, 4.5)
TQ = 1.2 * 100 # Nm * 100 is unit of measure for wheel.
SPAS_SWITCH = 45 * CV.MPH_TO_MS #MPH
###### SPAS #######

EventName = car.CarEvent.EventName


def accel_hysteresis(accel, accel_steady):
  # for small accel oscillations within ACCEL_HYST_GAP, don't change the accel command
  if accel > accel_steady + CarControllerParams.ACCEL_HYST_GAP:
    accel_steady = accel - CarControllerParams.ACCEL_HYST_GAP
  elif accel < accel_steady - CarControllerParams.ACCEL_HYST_GAP:
    accel_steady = accel + CarControllerParams.ACCEL_HYST_GAP
  accel = accel_steady

  return accel, accel_steady


SP_CARS = [CAR.GENESIS, CAR.GENESIS_G70, CAR.GENESIS_G80,
           CAR.GENESIS_EQ900, CAR.GENESIS_EQ900_L, CAR.K9, CAR.GENESIS_G90]

def process_hud_alert(enabled, fingerprint, visual_alert, left_lane, right_lane,
                      left_lane_depart, right_lane_depart):

  sys_warning = (visual_alert in [VisualAlert.steerRequired, VisualAlert.ldw])

  # initialize to no line visible
  sys_state = 1
  if left_lane and right_lane or sys_warning:  # HUD alert only display when LKAS status is active
    sys_state = 3 if enabled or sys_warning else 4
  elif left_lane:
    sys_state = 5
  elif right_lane:
    sys_state = 6

  # initialize to no warnings
  left_lane_warning = 0
  right_lane_warning = 0
  if left_lane_depart:
    left_lane_warning = 1 if fingerprint in SP_CARS else 2
  if right_lane_depart:
    right_lane_warning = 1 if fingerprint in SP_CARS else 2

  return sys_warning, sys_state, left_lane_warning, right_lane_warning


class CarController():
  def __init__(self, dbc_name, CP, VM):
    self.car_fingerprint = CP.carFingerprint
    self.packer = CANPacker(dbc_name)
    self.accel_steady = 0
    self.apply_steer_last = 0

    self.LA1 = 0 
    self.LA2 = 0
    self.LA3 = 0
    self.LA4 = 0
    self.LA5 = 0
    self.LA6 = 0
    self.LA7 = 0
    self.LA8 = 0
    self.LA9 = 0
    self.LA10 = 0
    self.LA11 = 0 
    self.LA12 = 0
    self.LA13 = 0
    self.LA14 = 0
    self.LA15 = 0
    self.LA16 = 0
    self.LA17 = 0
    self.LA18 = 0
    self.LA19 = 0
    self.LA20 = 0
    self.LA21 = 0 
    self.LA22 = 0
    self.LA23 = 0
    self.LA24 = 0
    self.LA25 = 0
    self.LA26 = 0
    self.LA27 = 0
    self.LA28 = 0
    self.LA29 = 0
    self.LA30 = 0
    self.LA31 = 0 
    self.LA32 = 0
    self.LA33 = 0
    self.LA34 = 0
    self.LA35 = 0
    self.LA36 = 0
    self.LA37 = 0
    self.LA38 = 0
    self.LA39 = 0
    self.LA40 = 0
    self.LA41 = 0 
    self.LA42 = 0
    self.LA43 = 0
    self.LA44 = 0
    self.LA45 = 0
    self.LA46 = 0
    self.LA47 = 0
    self.LA48 = 0
    self.LA49 = 0
    self.LA50 = 0
    self.LA51 = 0 
    self.LA52 = 0
    self.LA53 = 0
    self.LA54 = 0
    self.LA55 = 0
    self.LA56 = 0
    self.LA57 = 0
    self.LA58 = 0
    self.LA59 = 0
    self.LA60 = 0
    self.LA61 = 0 
    self.LA62 = 0
    self.LA63 = 0
    self.LA64 = 0
    self.LA65 = 0
    self.LA66 = 0
    self.LA67 = 0
    self.LA68 = 0
    self.LA69 = 0
    self.LA70 = 0
    self.LA71 = 0 
    self.LA72 = 0
    self.LA73 = 0
    self.LA74 = 0
    self.LA75 = 0
    self.LA76 = 0
    self.LA77 = 0
    self.LA78 = 0
    self.LA79 = 0
    self.LA80 = 0
    self.LA81 = 0 
    self.LA82 = 0
    self.LA83 = 0
    self.LA84 = 0
    self.LA85 = 0
    self.LA86 = 0
    self.LA87 = 0
    self.LA88 = 0
    self.LA89 = 0
    self.LA90 = 0
    self.LA91 = 0 
    self.LA92 = 0
    self.LA93 = 0
    self.LA94 = 0
    self.LA95 = 0
    self.LA96 = 0
    self.LA97 = 0
    self.LA98 = 0
    self.LA99 = 0
    self.LA100 = 0
    self.LA101 = 0 
    self.LA102 = 0
    self.LA103 = 0
    self.LA104 = 0
    self.LA105 = 0
    self.LA106 = 0
    self.LA107 = 0
    self.LA108 = 0
    self.LA109 = 0
    self.LA110 = 0
    self.LA111 = 0 
    self.LA112 = 0
    self.LA113 = 0
    self.LA114 = 0
    self.LA115 = 0
    self.LA116 = 0
    self.LA117 = 0
    self.LA118 = 0
    self.LA119 = 0
    self.LA120 = 0
    self.LA121 = 0 
    self.LA122 = 0
    self.LA123 = 0
    self.LA124 = 0
    self.LA125 = 0
    self.LA126 = 0
    self.LA127 = 0
    self.LA128 = 0
    self.LA129 = 0
    self.LA130 = 0
    self.LA131 = 0 
    self.LA132 = 0
    self.LA133 = 0
    self.LA134 = 0
    self.LA135 = 0
    self.LA136 = 0
    self.LA137 = 0
    self.LA138 = 0
    self.LA139 = 0
    self.LA140 = 0
    self.LA141 = 0 
    self.LA142 = 0
    self.LA143 = 0
    self.LA144 = 0
    self.LA145 = 0
    self.LA146 = 0
    self.LA147 = 0
    self.LA148 = 0
    self.LA149 = 0
    self.LA150 = 0
    self.LA151 = 0
    self.LA152 = 0
    self.LA153 = 0
    self.LA154 = 0
    self.LA155 = 0
    self.LA156 = 0
    self.LA157 = 0
    self.LA158 = 0
    self.LA159 = 0
    self.LA160 = 0
    self.LA161 = 0
    self.LA162 = 0
    self.LA163 = 0
    self.LA164 = 0
    self.LA165 = 0
    self.LA166 = 0
    self.LA167 = 0
    self.LA168 = 0
    self.LA169 = 0
    self.LA170 = 0
    self.steer_rate_limited = False
    self.lkas11_cnt = 0
    self.scc12_cnt = 0
    self.cnt = 0
    self.resume_cnt = 0
    self.last_lead_distance = 0
    self.resume_wait_timer = 0

    self.turning_signal_timer = 0
    self.longcontrol = CP.openpilotLongitudinalControl
    self.scc_live = not CP.radarOffCan
    self.accel_steady = 0
    self.mad_mode_enabled = Params().get_bool('MadModeEnabled')

    if CP.spasEnabled:
      self.en_cnt = 0
      self.last_apply_angle = 0.0
      self.en_spas = 3
      self.mdps11_stat_last = 0
      self.spas_always = Params().get_bool('spasAlways')
      
    self.ldws_opt = Params().get_bool('IsLdwsCar')
    self.stock_navi_decel_enabled = Params().get_bool('StockNaviDecelEnabled')

    # gas_factor, brake_factor
    # Adjust it in the range of 0.7 to 1.3
    self.scc_smoother = SccSmoother()
  
  def update(self, enabled, CS, frame, CC, actuators, pcm_cancel_cmd, visual_alert,
             left_lane, right_lane, left_lane_depart, right_lane_depart, set_speed, lead_visible, controls):

    # *** compute control surfaces ***

    # gas and brake
    apply_accel = actuators.gas - actuators.brake
    apply_accel, self.accel_steady = accel_hysteresis(apply_accel, self.accel_steady)
    apply_accel = self.scc_smoother.get_accel(CS, controls.sm, apply_accel)
    apply_accel = clip(apply_accel * CarControllerParams.ACCEL_SCALE,
                       CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX)

    # Steering Torque
    new_steer = int(round(actuators.steer * CarControllerParams.STEER_MAX))
    apply_steer = apply_std_steer_torque_limits(new_steer, self.apply_steer_last, CS.out.steeringTorque,
                                                CarControllerParams)

    self.steer_rate_limited = new_steer != apply_steer
    # SPAS limit angle extremes for safety
    if CS.spas_enabled:
      apply_angle = actuators.steeringAngleDeg
      if self.last_apply_angle * apply_angle > 0. and abs(apply_angle) > abs(self.last_apply_angle):
        rate_limit = interp(CS.out.vEgo, ANGLE_DELTA_BP, ANGLE_DELTA_V)
      else:
        rate_limit = interp(CS.out.vEgo, ANGLE_DELTA_BP, ANGLE_DELTA_VU)
        apply_angle1 = clip(apply_angle, self.last_apply_angle - rate_limit, self.last_apply_angle + rate_limit) 
        apply_angle = (apply_angle1 + self.last_apply_angle + self.LA1 + self.LA2 + self.LA3 + self.LA4 + self.LA5 + self.LA6 + self.LA7 + self.LA8 + self.LA9 + self.LA10 + self.LA11 + self.LA12 + self.LA13 + self.LA14 + self.LA15 + self.LA16 + self.LA17 + self.LA18 + self.LA19 + self.LA20
                      + self.LA21 + self.LA22 + self.LA23 + self.LA24 + self.LA25 + self.LA26 + self.LA27 + self.LA28 + self.LA29 + self.LA30 + self.LA31 + self.LA32 + self.LA33 + self.LA34 + self.LA35 + self.LA36 + self.LA37 + self.LA38 + self.LA39 + self.LA40
                      + self.LA41 + self.LA42 + self.LA43 + self.LA44 + self.LA45 + self.LA46 + self.LA47 + self.LA48 + self.LA49 + self.LA50 + self.LA51 + self.LA52 + self.LA53 + self.LA54 + self.LA55 + self.LA56 + self.LA57 + self.LA58 + self.LA59 + self.LA60
                      + self.LA61 + self.LA62 + self.LA63 + self.LA64 + self.LA65 + self.LA66 + self.LA67 + self.LA68 + self.LA69 + self.LA70 + self.LA71 + self.LA72 + self.LA73 + self.LA74 + self.LA75 + self.LA76 + self.LA77 + self.LA78 + self.LA79 + self.LA80
                      + self.LA81 + self.LA82 + self.LA83 + self.LA84 + self.LA85 + self.LA86 + self.LA87 + self.LA88 + self.LA89 + self.LA90 + self.LA91 + self.LA92 + self.LA93 + self.LA94 + self.LA95 + self.LA96 + self.LA97 + self.LA98 + self.LA99 + self.LA100 
                      + self.LA101 + self.LA102 + self.LA103 + self.LA104 + self.LA105 + self.LA106 + self.LA107 + self.LA108 + self.LA109 + self.LA110 + self.LA111 + self.LA112 + self.LA113 + self.LA114 + self.LA115 + self.LA116 + self.LA117 + self.LA118 + self.LA119 + self.LA120
                      + self.LA121 + self.LA122 + self.LA123 + self.LA124 + self.LA125 + self.LA126 + self.LA127 + self.LA128 + self.LA129 + self.LA130 + self.LA131 + self.LA132 + self.LA133 + self.LA134 + self.LA135 + self.LA136 + self.LA137 + self.LA138 + self.LA139 + self.LA140 
                      + self.LA141 + self.LA142 + self.LA143 + self.LA144 + self.LA145 + self.LA146 + self.LA147 + self.LA148 + self.LA149 + self.LA150 + self.LA151 + self.LA152 + self.LA153 + self.LA154 + self.LA155 + self.LA156 + self.LA156 + self.LA157 + self.LA158 + self.LA159 
                      + self.LA160 + self.LA161 + self.LA162 + self.LA163 + self.LA164 + self.LA165 + self.LA166 + self.LA167 + self.LA168 + self.LA169 + self.LA170) / 172
        self.last_apply_angle = apply_angle1

    spas_active = CS.spas_enabled and enabled and (self.spas_always or CS.out.vEgo < SPAS_SWITCH)
    lkas_active = enabled and abs(CS.out.steeringAngleDeg) < CS.CP.maxSteeringAngleDeg and not spas_active

    Driver_Torque_Threshold = TQ #np.interp(CS.out.steeringAngleDeg, STEER, TQ)
    if enabled and spas_active and -Driver_Torque_Threshold < CS.out.steeringWheelTorque > Driver_Torque_Threshold and enabled:
      spas_active = False
      lkas_active = False
      #self.DO = True    
      
    elif enabled and -Driver_Torque_Threshold > CS.out.steeringWheelTorque < Driver_Torque_Threshold or self.spas_always and enabled and -Driver_Torque_Threshold > CS.out.steeringWheelTorque < Driver_Torque_Threshold:
      #self.DO = False
      spas_active = True

    elif not lkas_active:
      apply_steer = 0
 

    UseSMDPS = Params().get_bool('UseSMDPSHarness')
    if Params().get_bool('LongControlEnabled'):
      min_set_speed = 0 * CV.KPH_TO_MS
    else:
      min_set_speed = 30 * CV.KPH_TO_MS
    # fix for Genesis hard fault at low speed
	  # Use SMDPS and Min Steer Speed limits - JPR
    if UseSMDPS == True:
      min_set_speed = 0 * CV.KPH_TO_MS
    else:
      if CS.out.vEgo < 55 * CV.KPH_TO_MS and self.car_fingerprint == CAR.GENESIS or self.car_fingerprint == CAR.GENESIS_G80 and not CS.mdps_bus:
        lkas_active = False
        min_set_speed = 55 * CV.KPH_TO_MS
      if CS.out.vEgo < 16.09 * CV.KPH_TO_MS and self.car_fingerprint == CAR.NIRO_HEV and not CS.mdps_bus:
        lkas_active = False
        min_set_speed = 16.09 * CV.KPH_TO_MS
      if CS.out.vEgo < 30 * CV.KPH_TO_MS and self.car_fingerprint == CAR.ELANTRA and not CS.mdps_bus:
        lkas_active = False
        min_set_speed = 30 * CV.KPH_TO_MS


    # Disable steering while turning blinker on and speed below 60 kph
    if CS.out.leftBlinker or CS.out.rightBlinker:
      self.turning_signal_timer = 0.5 / DT_CTRL  # Disable for 0.5 Seconds after blinker turned off
    if self.turning_indicator_alert: # set and clear by interface
      lkas_active = False
      spas_active = False
      if not self.turning_indicator_alert:
        spas_active = True


    if self.turning_signal_timer > 0:
      self.turning_signal_timer -= 1

    if not lkas_active:
      apply_steer = 0
      

    self.apply_accel_last = apply_accel
    self.apply_steer_last = apply_steer

    sys_warning, sys_state, left_lane_warning, right_lane_warning = \
      process_hud_alert(enabled, self.car_fingerprint, visual_alert,
                        left_lane, right_lane, left_lane_depart, right_lane_depart)

    clu11_speed = CS.clu11["CF_Clu_Vanz"]
    enabled_speed = 38 if CS.is_set_speed_in_mph else 60
    if clu11_speed > enabled_speed or not lkas_active:
      enabled_speed = clu11_speed

    controls.clu_speed_ms = clu11_speed * CS.speed_conv_to_ms

    if not (min_set_speed < set_speed < 255 * CV.KPH_TO_MS):
      set_speed = min_set_speed
    set_speed *= CV.MS_TO_MPH if CS.is_set_speed_in_mph else CV.MS_TO_KPH

    if frame == 0:  # initialize counts from last received count signals
      self.lkas11_cnt = CS.lkas11["CF_Lkas_MsgCount"]
      self.scc12_cnt = CS.scc12["CR_VSM_Alive"] + 1 if not CS.no_radar else 0

      # TODO: fix this
      # self.prev_scc_cnt = CS.scc11["AliveCounterACC"]
      # self.scc_update_frame = frame

    # check if SCC is alive
    # if frame % 7 == 0:
    # if CS.scc11["AliveCounterACC"] == self.prev_scc_cnt:
    # if frame - self.scc_update_frame > 20 and self.scc_live:
    # self.scc_live = False
    # else:
    # self.scc_live = True
    # self.prev_scc_cnt = CS.scc11["AliveCounterACC"]
    # self.scc_update_frame = frame

    self.prev_scc_cnt = CS.scc11["AliveCounterACC"]

    self.lkas11_cnt = (self.lkas11_cnt + 1) % 0x10
    self.scc12_cnt %= 0xF

    can_sends = []
    can_sends.append(create_lkas11(self.packer, frame, self.car_fingerprint, apply_steer, lkas_active,
                                   CS.lkas11, sys_warning, sys_state, enabled, left_lane, right_lane,
                                   left_lane_warning, right_lane_warning, 0))

    if CS.mdps_bus or CS.scc_bus == 1:  # send lkas11 bus 1 if mdps or scc is on bus 1
      can_sends.append(create_lkas11(self.packer, frame, self.car_fingerprint, apply_steer, lkas_active,
                                     CS.lkas11, sys_warning, sys_state, enabled, left_lane, right_lane,
                                     left_lane_warning, right_lane_warning, 1))

    if frame % 2 and CS.mdps_bus: # send clu11 to mdps if it is not on bus 0
      can_sends.append(create_clu11(self.packer, frame, CS.mdps_bus, CS.clu11, Buttons.NONE, enabled_speed))

    if pcm_cancel_cmd and (self.longcontrol and not self.mad_mode_enabled):
      can_sends.append(create_clu11(self.packer, frame % 0x10, CS.scc_bus, CS.clu11, Buttons.CANCEL, clu11_speed))
    else:
      can_sends.append(create_mdps12(self.packer, frame, CS.mdps12))

    # fix auto resume - by neokii
    if CS.out.cruiseState.standstill and not CS.out.gasPressed:

      if self.last_lead_distance == 0:
        self.last_lead_distance = CS.lead_distance
        self.resume_cnt = 0
        self.resume_wait_timer = 0

      # scc smoother
      elif self.scc_smoother.is_active(frame):
        pass

      elif self.resume_wait_timer > 0:
        self.resume_wait_timer -= 1

      elif abs(CS.lead_distance - self.last_lead_distance) > 0.01:
        can_sends.append(create_clu11(self.packer, self.resume_cnt, CS.scc_bus, CS.clu11, Buttons.RES_ACCEL, clu11_speed))
        self.resume_cnt += 1
        if self.resume_cnt >= 8:
          self.resume_cnt = 0
          self.resume_wait_timer = SccSmoother.get_wait_count() * 2

    # reset lead distnce after the car starts moving
    elif self.last_lead_distance != 0:
      self.last_lead_distance = 0

    if CS.mdps_bus: # send mdps12 to LKAS to prevent LKAS error
      can_sends.append(create_mdps12(self.packer, frame, CS.mdps12))
	  
    # scc smoother
    self.scc_smoother.update(enabled, can_sends, self.packer, CC, CS, frame, apply_accel, controls)

    controls.apply_accel = apply_accel
    aReqValue = CS.scc12["aReqValue"]
    controls.aReqValue = aReqValue

    if aReqValue < controls.aReqValueMin:
      controls.aReqValueMin = controls.aReqValue

    if aReqValue > controls.aReqValueMax:
      controls.aReqValueMax = controls.aReqValue

    # send scc to car if longcontrol enabled and SCC not on bus 0 or ont live
    if self.longcontrol and CS.cruiseState_enabled and (CS.scc_bus or not self.scc_live) and frame % 2 == 0:

      if self.stock_navi_decel_enabled:
        controls.sccStockCamAct = CS.scc11["Navi_SCC_Camera_Act"]
        controls.sccStockCamStatus = CS.scc11["Navi_SCC_Camera_Status"]
        apply_accel, stock_cam = self.scc_smoother.get_stock_cam_accel(apply_accel, aReqValue, CS.scc11)
      else:
        controls.sccStockCamAct = 0
        controls.sccStockCamStatus = 0
        stock_cam = False

      can_sends.append(create_scc12(self.packer, apply_accel, enabled, self.scc12_cnt, self.scc_live, CS.scc12))
      can_sends.append(create_scc11(self.packer, frame, enabled, set_speed, lead_visible, self.scc_live, CS.scc11,
                                    self.scc_smoother.active_cam, stock_cam))

      if frame % 20 == 0 and CS.has_scc13:
        can_sends.append(create_scc13(self.packer, CS.scc13))
      if CS.has_scc14:
        if CS.out.vEgo < 2.:
          long_control_state = controls.LoC.long_control_state
          acc_standstill = True if long_control_state == LongCtrlState.stopping else False
        else:
          acc_standstill = False

        lead = self.scc_smoother.get_lead(controls.sm)

        if lead is not None:
          d = lead.dRel
          obj_gap = 1 if d < 25 else 2 if d < 40 else 3 if d < 60 else 4 if d < 80 else 5
        else:
          obj_gap = 0

        can_sends.append(create_scc14(self.packer, enabled, CS.out.vEgo, acc_standstill, apply_accel, CS.out.gasPressed,
                                      obj_gap, CS.scc14))
      self.scc12_cnt += 1

    # 20 Hz LFA MFA message
    if frame % 5 == 0:
      activated_hda = road_speed_limiter_get_active()
      # activated_hda: 0 - off, 1 - main road, 2 - highway
      if self.car_fingerprint in FEATURES["send_lfa_mfa"]:
        can_sends.append(create_lfahda_mfc(self.packer, enabled, activated_hda))
      elif CS.mdps_bus == 0:
        state = 2 if self.car_fingerprint in FEATURES["send_hda_state_2"] else 1
        can_sends.append(create_hda_mfc(self.packer, activated_hda, state))
    
    if CS.spas_enabled:
      if CS.mdps_bus:
        spas_active_stat = CS.mdps11_stat == 4 or CS.mdps11_stat == 5
        can_sends.append(create_ems_366(self.packer, CS.ems_366, spas_active_stat))
      if (frame % 2) == 0:
        if CS.mdps11_stat == 7 and not self.mdps11_stat_last == 7:
          self.en_spas == 7
          self.en_cnt = 0

        if self.en_spas == 7 and self.en_cnt >= 8 or CS.mdps11_stat == 6: # if MDPS stat 7 or 6 start new request. JPR
          self.en_spas = 3 # previously 3 but we need to start a new request with state 2. JPR
          self.en_cnt = 0

        #if CS.mdps11_stat == 2: # when MDPS stat change to 2, it's processed new request state and ready to move to state 3 SPAS ready. JPR
        #  self.en_spas = 3 # we need to change from starting a new request with state 2 to a spas ready state which is state 3. JPR
        #  self.en_cnt = 0

        if self.en_cnt < 8 and spas_active:
          self.en_spas = 4
        elif self.en_cnt >= 8 and spas_active:
          self.en_spas = 5

        if not spas_active:
          apply_angle = CS.mdps11_strang
          self.en_spas = 3
          self.en_cnt = 0

        self.mdps11_stat_last = CS.mdps11_stat
        self.en_cnt += 1
        can_sends.append(create_spas11(self.packer, self.car_fingerprint, (frame // 2), self.en_spas, apply_angle, CS.mdps_bus))

      # SPAS12 20Hz
      if (frame % 5) == 0:
        can_sends.append(create_spas12(CS.mdps_bus))
        
      self.LA1 = self.last_apply_angle
      self.LA2 = self.LA1
      self.LA3 = self.LA1
      self.LA4 = self.LA3
      self.LA5 = self.LA4
      self.LA6 = self.LA5
      self.LA7 = self.LA6
      self.LA8 = self.LA7
      self.LA9 = self.LA8
      self.LA10 = self.LA9
      self.LA11 = self.LA10
      self.LA12 = self.LA11
      self.LA13 = self.LA12
      self.LA14 = self.LA13
      self.LA15 = self.LA14
      self.LA16 = self.LA15
      self.LA17 = self.LA16
      self.LA18 = self.LA17
      self.LA19 = self.LA18
      self.LA20 = self.LA19
      self.LA21 = self.LA20
      self.LA22 = self.LA21
      self.LA23 = self.LA22
      self.LA24 = self.LA23
      self.LA25 = self.LA24
      self.LA26 = self.LA25
      self.LA27 = self.LA26
      self.LA28 = self.LA27
      self.LA29 = self.LA28
      self.LA30 = self.LA29
      self.LA31 = self.LA30
      self.LA32 = self.LA31
      self.LA33 = self.LA32
      self.LA34 = self.LA33
      self.LA35 = self.LA34
      self.LA36 = self.LA35
      self.LA37 = self.LA36
      self.LA38 = self.LA37
      self.LA39 = self.LA38
      self.LA40 = self.LA39
      self.LA41 = self.LA40
      self.LA42 = self.LA41
      self.LA43 = self.LA42
      self.LA44 = self.LA43
      self.LA45 = self.LA44
      self.LA46 = self.LA45
      self.LA47 = self.LA46
      self.LA48 = self.LA47
      self.LA49 = self.LA48
      self.LA50 = self.LA49
      self.LA51 = self.LA50
      self.LA52 = self.LA51
      self.LA53 = self.LA52
      self.LA54 = self.LA53
      self.LA55 = self.LA54
      self.LA56 = self.LA55
      self.LA57 = self.LA56
      self.LA58 = self.LA57
      self.LA59 = self.LA58
      self.LA60 = self.LA59
      self.LA61 = self.LA60
      self.LA62 = self.LA61
      self.LA63 = self.LA62
      self.LA64 = self.LA63
      self.LA65 = self.LA64
      self.LA66 = self.LA65
      self.LA67 = self.LA66
      self.LA68 = self.LA67
      self.LA69 = self.LA68
      self.LA70 = self.LA69
      self.LA71 = self.LA70
      self.LA72 = self.LA71
      self.LA73 = self.LA72
      self.LA74 = self.LA73
      self.LA75 = self.LA74
      self.LA76 = self.LA75
      self.LA77 = self.LA76
      self.LA78 = self.LA77
      self.LA79 = self.LA78
      self.LA80 = self.LA79
      self.LA81 = self.LA80
      self.LA82 = self.LA81
      self.LA83 = self.LA82
      self.LA84 = self.LA83
      self.LA85 = self.LA84
      self.LA86 = self.LA85
      self.LA87 = self.LA86
      self.LA88 = self.LA87
      self.LA89 = self.LA88
      self.LA90 = self.LA89
      self.LA91 = self.LA90
      self.LA92 = self.LA91
      self.LA93 = self.LA92
      self.LA94 = self.LA93
      self.LA95 = self.LA94
      self.LA96 = self.LA95
      self.LA97 = self.LA96
      self.LA98 = self.LA97
      self.LA99 = self.LA98
      self.LA100 = self.LA99
      self.LA101 = self.LA100
      self.LA102 = self.LA101
      self.LA103 = self.LA102
      self.LA104 = self.LA103
      self.LA105 = self.LA104
      self.LA106 = self.LA105
      self.LA107 = self.LA106
      self.LA108 = self.LA107
      self.LA109 = self.LA108
      self.LA110 = self.LA109
      self.LA111 = self.LA110
      self.LA112 = self.LA111
      self.LA113 = self.LA112
      self.LA114 = self.LA113
      self.LA115 = self.LA114
      self.LA116 = self.LA115
      self.LA117 = self.LA116
      self.LA118 = self.LA117
      self.LA119 = self.LA118
      self.LA120 = self.LA119
      self.LA121 = self.LA120
      self.LA122 = self.LA121
      self.LA123 = self.LA122
      self.LA124 = self.LA123
      self.LA125 = self.LA124
      self.LA126 = self.LA125
      self.LA127 = self.LA126
      self.LA128 = self.LA127
      self.LA129 = self.LA128
      self.LA130 = self.LA129
      self.LA131 = self.LA130
      self.LA132 = self.LA131
      self.LA133 = self.LA132
      self.LA134 = self.LA133
      self.LA135 = self.LA134
      self.LA136 = self.LA135
      self.LA137 = self.LA136
      self.LA138 = self.LA137
      self.LA139 = self.LA138
      self.LA140 = self.LA139
      self.LA141 = self.LA140
      self.LA142 = self.LA141
      self.LA143 = self.LA142
      self.LA144 = self.LA143
      self.LA145 = self.LA144
      self.LA146 = self.LA145
      self.LA147 = self.LA146
      self.LA148 = self.LA147
      self.LA149 = self.LA148
      self.LA150 = self.LA149
      self.LA151 = self.LA150
      self.LA152 = self.LA151
      self.LA153 = self.LA152
      self.LA154 = self.LA153
      self.LA155 = self.LA154
      self.LA156 = self.LA155
      self.LA157 = self.LA156
      self.LA158 = self.LA157
      self.LA159 = self.LA158
      self.LA160 = self.LA159
      self.LA161 = self.LA160
      self.LA162 = self.LA161
      self.LA163 = self.LA162
      self.LA164 = self.LA163
      self.LA165 = self.LA164
      self.LA166 = self.LA165
      self.LA167 = self.LA166
      self.LA168 = self.LA167
      self.LA169 = self.LA168
      self.LA170 = self.LA169

    return can_sends
