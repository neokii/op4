**OpenPilot 0.8.12 Community Fork for Hyundai, Kia, and Genesis!**
------------------

**The software sources are after the install section.**

**This fork is Community Supported!**
------------------------

We **appreciate** all help! Anywhere we get it! 
To get involved join us on discord or Contribute to the project with code or help support the project by donating.

- https://discord.gg/zWSnqJ6rKD

- Donating helps me dedicate more time and effort into this project. It also gives me more time to make for helping people.

- https://www.patreon.com/Circuit_Pro

<a href="https://www.paypal.com/donate?business=NRFAJ6FYRLT2Y&no_recurring=0&item_name=Contribute+to+help+progress+JPR%27s+HKG+Fork&currency_code=USD" 
target="_blank">
<img src="https://www.paypalobjects.com/en_US/GB/i/btn/btn_donateCC_LG.gif" alt="PayPal this" 
title="PayPal – The safer, easier way to pay online!" border="0" />
</a>

**Liability**
------------

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

**DO NOT USE SPAS WITHOUT UNDERSTANDING, HOW IT WORKS AND WHAT IT DOES, YOU ACCEPT ALL LIABILITY.**

**It is open source and inherits MIT license.  By installing this software you accept all responsibility for anything that might occur while you use it.  All contributors to this fork are not liable.**  <b>Use at your own risk.</b>

**By using this software you are responsible for anything that occurs while OpenPilot is engaged or disengaged. Be ready to take over at any moment. Fork contributers assumes no liability for your use of this software and any hardware.**

**Please join our Discord!**
---------------

https://discord.gg/zWSnqJ6rKD

**Submit issues on the issues page or in a detailed report on GitHub issues page. For quick help post in issues channel on our discord server.**

**Longitudinal Info**
----------------------

This fork has full long control for all HKG with radar harness and Harnessless for older 2015 & 2016 Genesis G80(Fixed SMDPS) without any radar harness mod. All other cars should require scc to be moved to bus 2 from bus 0 for full long control.

- Reach out to **johnpr#5623** on discord to buy a radar harness. 1 & 1/2 week lead time depending on location of parts.

**SPAS**
-------------
Before! testing SPAS steering, ↓↑ !BE SURE TO READ ALL OF THE SPAS SECTION AND UNDERSTAND HOW IT WORKS! ↑↓; Be aware of all the safety concerns with USING ALL OF THE TORQUE that the MDPS/EPS motor can provide! ! KEEP HANDS ON WHEEL AND EYES ON ROAD AT ALL TIMES ! You are responsible for actions of car engaged or not engaged!

<td><a href="https://www.youtube.com/watch?v=hTuvA6o6gjY&t=49s" title="YouTube - SPAS and OSM Demonstration Video" rel="noopener"><img src="https://github.com/Circuit-Pro/openpilot/blob/main/PICS/SPAS%20thumbnail.png"></a></td>

SPAS stands for Smart Parking Assist System. Your vehicle does not need to be equiped with this feature to use it. To use this an MDPS harness is required! 
Most H.K.G. MDPS will accept these messages. This is currently reported to be working on vehicles 2019 and under, with newer vehicles needing more work due to tighter tolerances on logic, more checks, and new checksums. To get a new vehicle working you need to set the `ret.emsType = _` for your vehicle if one is not set. 

**Which EMS am I?**

Register your device to RetroPilot. Then go for a short drive and grab a cabana for your car, Then use the "Kia_Hyundai_Generic" DBC. Search for EMS and see which EMS your vehicle uses. Then set `ret.emsType = ` : N/A = 0 : EMS366 = 1 : EMS11 = 2 : E_EMS11 = 3 :
Reach out with any questions or to get help with EMS types not listed, join our discord and ask in the spas channel.

 - To use this an MDPS harness is required.
 - MDPS stands for Motor Driven Power Steering.
 - Panda safety is in a working state and needs more testing and edge case tuning, I.E. The rate limit's for the steering wheel SPAS is set conservatively and may need some increasing. 
 - Just because there is panda safety code **PLEASE** do not ever fully assume it is safe, especially since this is so new! Remember this is using the **ENTIRE** force of the MDPS/EPS Motor! 
 - This works by faking the vehicle speed **ONLY** to the MDPS when it's in state 5 (SPAS Steer/Assist) and sending an angle to MDPS to execute.
 - OpenPilot currently switches to LKAS steering at 38MPH automatically. If the tune of LKAS steering is not good and stable there can be a noticeable transition on a curve. Although if your vehicle is properly tuned you should have no issues, In all of my testing. - IN PROGRESS - make this dynamic based on numerous factors like steer angle and steer staturation. For steer saturation it will need testing to see if feasible and safe to do this transfer when lkas already saturated; will probably need to have a rate limit upwind from current angle rather than straight to desired angle.
 - When LKAS is not active, the controlers are being reset to prevent upwind or unwind issues.
 - OpenPilot and Panda are monitoring driver torque from MDPS11. The correct one for use with SPAS. When OpenPilot detects a force being applied to wheel that's greater than the set limit of 2.85Nm. Panda will call a violation and controls not allowed if this higher limit is reached. Panda's limit is set greater than OpenPilots so it won't cause controls mismatch and interference due to it blocking signals when this is violated. - PANDA DRIVER TORQUE MONITORING TEMPORARILY DISABLED - Need to send MDPS into state 7 first before tx = 0 from panda not Openpilot
 - OpenPilot is appying a rate limit up and down to the sent steering angles and Panda is enforcing this. NOTE Panda's SPAS up and down rate limits are set conservatively and may require some adjusting.
 - Panda is enforcing that SPAS is off when controls not allowed or not engaged.
 - If driver torque is detected above set limit with SPAS on and under 38Mph, OpenPilot will disengage.
 - **! KEEP HANDS ON WHEEL AND EYES ON ROAD AT ALL TIMES !**
 - SPAS is available for testing on the `dev` branch.
 
**Before!** testing SPAS steering, **↓↑ !BE SURE TO READ ALL OF THE SPAS SECTION AND UNDERSTAND HOW IT WORKS! ↑↓**; Be aware of all the safety concerns with **USING ALL OF THE TORQUE** that the MDPS/EPS motor can provide! **! KEEP HANDS ON WHEEL AND EYES ON ROAD AT ALL TIMES !** You are **responsible** for actions of car engaged or not engaged!

***Open Street Maps!***
---------------------
   - Speed limit wrong or missing? Contribute to Open Street Maps in your area! https://www.openstreetmap.org
   - Special Thanks to the Move-Fast Team for all the help and hard work with OSM!
   - With an active internet connection, and HKG Long, OpenPilot can plan ahead using vision and map data to slow for curves and adjust the longitudinal plan for speed limit and other factors.
   - Cruise speed does not adjust SCC max set speed, OSM instead adjusts longitudinal plan. So for it to work set max SCC speed higher than speed limit. To override speed limit tap on speed limit symbol on screen in top left corner next to max speed.
   - All Settings are under `Toggles` in `Settings`.
   - We have the correct DBC for newer Hyundais; 2019+ with built in navigation. To pull the speed limit information from head unit over can bus. Toggle `Pull Hyundai Navigation Speed Limit` to the ON position and OSM will use both the OSM API and the cars Head Unit GPS/Navigation reported speed limit information to decide the speed limit.
   - https://www.youtube.com/watch?v=hTuvA6o6gjY

***HKG Long control toggle. (radar + vision)***
-----------------------------------------------
   - When toggled on, replaces the default Hyundai / Kia / Genesis factory longitudinal control system (SCC) with the openpilot system.
   - Lead markers are not available unless you have HKG long toggle on; this is not a method to determine if longitudinal is working.
   - Radar harness or mod is needed.
     - Move SCC ECU / RADAR to bus 2.

***RetroPilot***
----------------

This fork uses RetroPilot for logging and online services.  https://api.retropilot.org/useradmin

Make sure "Upload Raw Logs" and "Enable Logger / Uploader" are both ON for this to work. 

**Performance**
---------------

The Comma 3 has great performance with this fork.

The **Comma 2** has **POOR** performance with logging and uploader enabled so it's disabled by default. You can change that in `Settings` under `Community`.

**Hardware**
------------

**MDPS Harness** are available if you have the newer style plug and or 2015 - 2016 Genesis. Contact johnpr#5623 on discord for more information.

- 2015 - 2016 Genesis requires some work to install please review this guide from Ahmed Barnawi. This guide is centered around SMDPS but from page (2 - 7) is no different for MDPS harness installation. If you have a MDPS Harness kit skip right on past step 1, 2, & 3 of "Execution" on page 2 and start from there. The MDPS harness connects between comma power and RJ45 from the Car Harness Box. https://github.com/Circuit-Pro/openpilot/blob/main/Guides/Hyundai_MDPS_Comma_Harness.pdf 

- Newer style plug for MDPS ECU located in cabin (Most likely up under the steering wheel.) is plug and play. MDPS harness connects between comma power and RJ45 from the Car Harness Box. The MDPS ECU data connector(CAN L, H, and IGN) gets unplugged from MDPS ECU and this connector that just got unplugged gets plugged into female of harness and the male MDPS harness connector will replace where the MDPS ECU data connector(CAN L, H, and IGN) **originally** was. I.E. MDPS ECU Data female socket. Avoid touching MDPS ECU Power connector and any others. 
- <img src="https://github.com/Circuit-Pro/openpilot/blob/main/PICS/MDPS%20ECU%20view%201.png" width="350"></img> <img> <img src="https://github.com/Circuit-Pro/openpilot/blob/main/PICS/MDPS%20ECU%20view%202.png" width="250"></img> <img>

**Radar Harness** for Kia Stinger, G70, Niro, and Ioniq are available. Varying lead time based on location of radar connector. Contact johnpr#5623 on discord for more information.

**Notes**
---------

Make sure to **shut off** auto start stop or you will get steering temporarily unavailable if the engine shuts off.

**Screen Recordings** 

- Comma 2 Storage Location. `/storage/emulated/0/videos`

- Comma 2 Storage Location. `/data/media/0/videos`

**Features**
------------

**Click** any of the settings to get a breif description in OpenPilot settings.

**Loading Logo**

The loading logo is automatically set to your HKG cars brand after the first boot, first car start, first reboot, and resets on update.

***nTune***

- nTune Auto Tunes lateral LQR steering and some SCC/Long settings like accuation delay upper and lower bounds, gas factor, and brake factor.=

Run **nTune** in middle of drive: Use this command `cd selfdrive && python ntune.py` or use the button in `Settings` under `Device`. (make sure your not driving!)

**Delete UI Screen Recordings button in `Settings` under `Device`.**

**Toggles**

- Toggles are in `Settings` under `Community` & `Device`.

***Cluster Speed***

   - Uses the speed of the gauge cluster instead GPS speed.

***LDWS toggle***

   - under `Community` in `Settings`. For cars with LDWS but not SCC.

***Show Debug UI***

   - I feel like you should understand what “debugging” and a “UI” are before you can use openpilot

***Use SMDPS Harness***

   - Use of MDPS Harness to enable openpilot steering down to 0 MPH
  
***On screen blinkers and blind spot alerts.***

 - Your choice of Neokii or Crwusiz on screen blinkers with Crwusiz on-screen Blind Spot Monitoring indicators.

***Enable Lane Change Assist***

  - allows openpilot to change lanes. Driver is responsible for ensuring that it is SAFE to change lanes. Requires signal, and steering wheel nudge.

***Auto Lane Change with Blind spot monitoring toggle (No Nudge).***

  - Same as the original, now with 100% less nudge.

***Sync Speed on Gas Press***

  - openpilot will sync cruise control set speed to match last attained speed automatically

***Make sure to reboot with toggle changes.***

Then give it a spin.

***Behavior Notes***
--------------------

OpenPilot HKG Long will not see totally stopped cars yet until E2E comes in 0.9 so do not trust it to see and stop for a COMPLETLY stopped car.

If Collision Warning is beeping at you OpenPilot has calculated it can't stop quick enough due to safety limitations on unintentional braking. Please apply brakes to avoid collision.

***Install***
------------

**Comma 3**

Put this url during setup for Stable `https://smiskol.com/fork/Circuit-Pro/stable`

Put this url during setup for Stable Open Street Maps `https://smiskol.com/fork/Circuit-Pro/stable_OSM`

**Comma 2**

Put this url during setup for Stable `https://smiskol.com/fork/Circuit-Pro/stable`

***If you installed from SSH***

- make sure too run `rm /data/params/d/DongleId` to reset your dongle ID.

**Panda Issues**
----------------
If you get "Invalid DFU Signature" unplug comma for 5 min and plug it back in and run `./recover.sh` again.

**Comma 3**

Try this first; refer to instructions above, if this does not work. - `pkill -f openpilot; cd panda/board; ./recover.sh; sudo reboot`

`pkill -f openpilot; cd panda/board; ./flash.sh; sudo reboot`

**Comma 2**

Try this first; refer to instructions above, if this does not work. - `pkill -f openpilot; cd panda/board; ./recover.sh; reboot`

`pkill -f openpilot; cd panda/board; ./flash.sh; reboot`

**xx979xx's Debugging Tools:**
--------------------------
To print debug info for Panda and Harness issue:

`python panda/tests/debug_console.py`
To print Opentpilot live data:

`python selfdrive/debug/dump.py <category>`
replace <category> with any one of these: `health carState carControl controlsState carParams sendcan can`

**This is based on xx979xx & Neokii's & crwusiz's fork and is tuned best 2.0L Kia Stinger, and works on others... Please submit a tune to our discord if you find a better one.**

**Software Sources!**
----------------------------

https://github.com/neokii/op4

https://github.com/xx979xx/openpilot

https://github.com/crwusiz/openpilot

https://github.com/move-fast/openpilot

**Extras**
---------------

**Unlimited data, data only simcard compatible with C2.**

https://www.amazon.com/dp/B07JCTZ3BF/ref=cm_sw_r_u_apa_glt_fabc_SNA9EVB27NT0DPRMEY3Q?psc=1

Run `adb shell am start -a android.settings.SETTINGS` and go too `"SIM cards"` and under `Cellular network settings` choose either "SIM 1 settings" or "SIM 2 settings" (based on which slot you have your non comma sim installed in.) Then go to `Access Point Names` add and set APN name correctly for sim provider(for the one i'm using and linked above the APN username is `m2mglobal` leave everything else default or blank. (MCC 310, MNC 260)

**Parts**
----------

Kia Niro MDPS ECU - http://www.kniro.net/schematic_diagrams-1321.html

MDPS Connectors

Male
- https://www.mouser.com/ProductDetail/aptiv/15420151/?qs=WTe5OP3w0Koiy%252bx6KqjpIQ%3D%3D&countrycode=CA&currencycode=CAD&bm-verify=AAQAAAAD_____xGvBoTAT_yusRfcDbPOvmmaN_N4VgvTUsLpnvbpGb1zClm2LRJZFYrTQaCWy30sxMrw5LMiUOXCn06a49I1B8zA96meyl7U7I8EteiPj05-qHB8w3slUdlaiAvam3Y96_Xsl81g3qPzp08LwevFanhLa8jvAmcmYyFsMkQVmB5o-bjjk2E3sWqFDi3jINO2kCMPiDZ2BYdawKzl7yPNrkc_dq8iwl-oyNoa242w_dFKI5z1ucS22Etf-_dT-L09e7XFLzVQ307lPqcZrR0mu1gqEY94MN4p9yj71EYVH8SrUJAFu9UOAa0l9ATl01niGRC6afmOr91rzh087B1Bj6RXGml62nkMWgBDkGsiWU7DRkPUjfVJZu00hioYwl-A758CMrxFB3GHEQm-V7oT8kdHI7i-9TH5oxRgrArVhcDlAGasgzhKrWwJ0CXP9okjrQbhlcFZeVPvfQW4RP3WJkHUJnUna-wRSzX2J4Fr7jJBRKDsu7oGqJNSIbsioIlbHsb5-B5Zoi_bLnA0

Female 
- https://www.mouser.com/ProductDetail/aptiv/15406142/?qs=xyz6lfZ1ktKtmezTNc3DLw%3D%3D&countrycode=CA&currencycode=CAD
- https://www.mouser.com/ProductDetail/aptiv/15401440-l/?qs=NKHyz0HolODmWpNAvMSDSg%3D%3D&countrycode=CA&currencycode=CAD

Black Panda
- https://github.com/Circuit-Pro/openpilot/blob/main/648E3090-698D-4568-BCEE-E723442B3C00.jpeg

RJ45 female connectors
- https://www.amazon.com/dp/B07JRD69V6/ref=cm_sw_r_cp_api_glt_fabc_WTRZRMNRG20KSPHKRQSX?_encoding=UTF8&psc=1

RJ45 black panda and comma power adapter
- https://github.com/Circuit-Pro/openpilot/blob/main/C50DC3FD-B803-4B67-A435-AA857EF2396B.png


It is open source and inherits MIT license.  By installing this software you accept all responsibility for anything that might occur while you use it.  All contributors to this fork are not liable.  <b>Use at your own risk.</b>
------------------------------------------------------




![](https://user-images.githubusercontent.com/37757984/127420744-89ca219c-8f8e-46d3-bccf-c1cb53b81bb1.png)

Table of Contents
=======================

* [What is openpilot?](#what-is-openpilot)
* [Running in a car](#running-in-a-car)
* [Running on PC](#running-on-pc)
* [Community and Contributing](#community-and-contributing)
* [User Data and comma Account](#user-data-and-comma-account)
* [Safety and Testing](#safety-and-testing)
* [Directory Structure](#directory-structure)
* [Licensing](#licensing)

---

What is openpilot?
------

[openpilot](http://github.com/commaai/openpilot) is an open source driver assistance system. Currently, openpilot performs the functions of Adaptive Cruise Control (ACC), Automated Lane Centering (ALC), Forward Collision Warning (FCW) and Lane Departure Warning (LDW) for a growing variety of [supported car makes, models and model years](docs/CARS.md). In addition, while openpilot is engaged, a camera based Driver Monitoring (DM) feature alerts distracted and asleep drivers. See more about [the vehicle integration](docs/INTEGRATION.md) and [limitations](docs/LIMITATIONS.md).

<table>
  <tr>
    <td><a href="https://www.youtube.com/watch?v=mgAbfr42oI8" title="YouTube" rel="noopener"><img src="https://i.imgur.com/kAtT6Ei.png"></a></td>
    <td><a href="https://www.youtube.com/watch?v=394rJKeh76k" title="YouTube" rel="noopener"><img src="https://i.imgur.com/lTt8cS2.png"></a></td>
    <td><a href="https://www.youtube.com/watch?v=1iNOc3cq8cs" title="YouTube" rel="noopener"><img src="https://i.imgur.com/ANnuSpe.png"></a></td>
    <td><a href="https://www.youtube.com/watch?v=Vr6NgrB-zHw" title="YouTube" rel="noopener"><img src="https://i.imgur.com/Qypanuq.png"></a></td>
  </tr>
  <tr>
    <td><a href="https://www.youtube.com/watch?v=Ug41KIKF0oo" title="YouTube" rel="noopener"><img src="https://i.imgur.com/3caZ7xM.png"></a></td>
    <td><a href="https://www.youtube.com/watch?v=NVR_CdG1FRg" title="YouTube" rel="noopener"><img src="https://i.imgur.com/bAZOwql.png"></a></td>
    <td><a href="https://www.youtube.com/watch?v=tkEvIdzdfUE" title="YouTube" rel="noopener"><img src="https://i.imgur.com/EFINEzG.png"></a></td>
    <td><a href="https://www.youtube.com/watch?v=_P-N1ewNne4" title="YouTube" rel="noopener"><img src="https://i.imgur.com/gAyAq22.png"></a></td>
  </tr>
</table>


Running in a car
------

To use openpilot in a car, you need four things
* This software. It's free and available right here.
* One of [the 140+ supported cars](docs/CARS.md). We support Honda, Toyota, Hyundai, Nissan, Kia, Chrysler, Lexus, Acura, Audi, VW, and more. If your car is not supported, but has adaptive cruise control and lane keeping assist, it's likely able to run openpilot.
* A supported device to run this software. This can be a [comma two](https://comma.ai/shop/products/two), [comma three](https://comma.ai/shop/products/three), or if you like to experiment, a [Ubuntu computer with webcams](https://github.com/commaai/openpilot/tree/master/tools/webcam).
* A way to connect to your car. With a comma two or three, you need only a [car harness](https://comma.ai/shop/products/car-harness). With an EON Gold or PC, you also need a [black panda](https://comma.ai/shop/products/panda).

We have detailed instructions for [how to install the device in a car](https://comma.ai/setup).

Running on PC
------

All of openpilot's services can run as normal on a PC, even without special hardware or a car. To develop or experiment with openpilot you can run openpilot on recorded or simulated data.

With openpilot's tools you can plot logs, replay drives and watch the full-res camera streams. See [the tools README](tools/README.md) for more information.

You can also run openpilot in simulation [with the CARLA simulator](tools/sim/README.md). This allows openpilot to drive around a virtual car on your Ubuntu machine. The whole setup should only take a few minutes, but does require a decent GPU.


Community and Contributing
------

openpilot is developed by [comma](https://comma.ai/) and by users like you. We welcome both pull requests and issues on [GitHub](http://github.com/commaai/openpilot). Bug fixes and new car ports are encouraged. Check out [the contributing docs](docs/CONTRIBUTING.md).

Documentation related to openpilot development can be found on [docs.comma.ai](https://docs.comma.ai). Information about running openpilot (e.g. FAQ, fingerprinting, troubleshooting, custom forks, community hardware) should go on the [wiki](https://github.com/commaai/openpilot/wiki).

You can add support for your car by following guides we have written for [Brand](https://blog.comma.ai/how-to-write-a-car-port-for-openpilot/) and [Model](https://blog.comma.ai/openpilot-port-guide-for-toyota-models/) ports. Generally, a car with adaptive cruise control and lane keep assist is a good candidate. [Join our Discord](https://discord.comma.ai) to discuss car ports: most car makes have a dedicated channel.

Want to get paid to work on openpilot? [comma is hiring](https://comma.ai/jobs/).

And [follow us on Twitter](https://twitter.com/comma_ai).

User Data and comma Account
------

By default, openpilot uploads the driving data to our servers. You can also access your data through [comma connect](https://connect.comma.ai/). We use your data to train better models and improve openpilot for everyone.

openpilot is open source software: the user is free to disable data collection if they wish to do so.

openpilot logs the road facing cameras, CAN, GPS, IMU, magnetometer, thermal sensors, crashes, and operating system logs.
The driver facing camera is only logged if you explicitly opt-in in settings. The microphone is not recorded.

By using openpilot, you agree to [our Privacy Policy](https://comma.ai/privacy). You understand that use of this software or its related services will generate certain types of user data, which may be logged and stored at the sole discretion of comma. By accepting this agreement, you grant an irrevocable, perpetual, worldwide right to comma for the use of this data.

Safety and Testing
----

* openpilot observes ISO26262 guidelines, see [SAFETY.md](docs/SAFETY.md) for more details.
* openpilot has software in the loop [tests](.github/workflows/selfdrive_tests.yaml) that run on every commit.
* The code enforcing the safety model lives in panda and is written in C, see [code rigor](https://github.com/commaai/panda#code-rigor) for more details.
* panda has software in the loop [safety tests](https://github.com/commaai/panda/tree/master/tests/safety).
* Internally, we have a hardware in the loop Jenkins test suite that builds and unit tests the various processes.
* panda has additional hardware in the loop [tests](https://github.com/commaai/panda/blob/master/Jenkinsfile).
* We run the latest openpilot in a testing closet containing 10 comma devices continuously replaying routes.

Directory Structure
------
    .
    ├── cereal              # The messaging spec and libs used for all logs
    ├── common              # Library like functionality we've developed here
    ├── docs                # Documentation
    ├── opendbc             # Files showing how to interpret data from cars
    ├── panda               # Code used to communicate on CAN
    ├── third_party         # External libraries
    ├── pyextra             # Extra python packages
    └── selfdrive           # Code needed to drive the car
        ├── assets          # Fonts, images, and sounds for UI
        ├── athena          # Allows communication with the app
        ├── boardd          # Daemon to talk to the board
        ├── camerad         # Driver to capture images from the camera sensors
        ├── car             # Car specific code to read states and control actuators
        ├── common          # Shared C/C++ code for the daemons
        ├── controls        # Planning and controls
        ├── debug           # Tools to help you debug and do car ports
        ├── locationd       # Precise localization and vehicle parameter estimation
        ├── logcatd         # Android logcat as a service
        ├── loggerd         # Logger and uploader of car data
        ├── modeld          # Driving and monitoring model runners
        ├── proclogd        # Logs information from proc
        ├── sensord         # IMU interface code
        ├── test            # Unit tests, system tests, and a car simulator
        └── ui              # The UI

Licensing
------

openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.

Any user of this software shall indemnify and hold harmless Comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.

**THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
NO WARRANTY EXPRESSED OR IMPLIED.**

---

<img src="https://d1qb2nb5cznatu.cloudfront.net/startups/i/1061157-bc7e9bf3b246ece7322e6ffe653f6af8-medium_jpg.jpg?buster=1458363130" width="75"></img> <img src="https://cdn-images-1.medium.com/max/1600/1*C87EjxGeMPrkTuVRVWVg4w.png" width="225"></img>

[![openpilot tests](https://github.com/commaai/openpilot/workflows/openpilot%20tests/badge.svg?event=push)](https://github.com/commaai/openpilot/actions)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/context:python)
[![Language grade: C/C++](https://img.shields.io/lgtm/grade/cpp/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/context:cpp)
[![codecov](https://codecov.io/gh/commaai/openpilot/branch/master/graph/badge.svg)](https://codecov.io/gh/commaai/openpilot)
