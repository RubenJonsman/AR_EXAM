Exam Project Advanced Robotics ITU 2024

https://learnit.itu.dk/pluginfile.php/400034/mod_resource/content/1/tag-project.pdf

------------------------------
### Set the hostName - Main robot
1. Hostname: RGA
2. Username: RGA
3. Password: RGA
4. Connect through this:
- ssh RGA@RGA.local
- ssh RGA@192.168.74.20

------------------------------

------------------------------
### Set the hostName - Second robot
1. Hostname: RGA2
2. Username: RGA2
3. Password: RGA2
4. Connect through this:
- ssh RGA2@RGA2.local
- ssh RGA2@192.168.74.17

------------------------------

### How to run

1. Start flatpack in one windows
'flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite'
2. Run the python command in the other one
'python3.11 dev_LED.py'


IP address:

Todo:
- Robot

    - [x] Robot LED (What state it is in)

    - [!!!] Robot InfraRed communication
		- Still doesnt work
		- Approx sensor are reading: irsensing.py
		- use the original code: ir_test_original.py

    - [ ] Robot detect safe-zone

    - [ ] Robot detect other robots

    - [ ] Robot detect other robots state

- Simulation
    - [x] Make map
    - [x] Create robots
    - [x] Simulate floor sensor
    - [ ] Simulate camera sensor
    - [ ] Implement tag-and-avoid behavior
    - [ ] Make simulation as close to reality as possible, i.e how long the camera can see, how far the infrared can be detected
