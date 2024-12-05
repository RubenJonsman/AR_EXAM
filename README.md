Exam Project Advanced Robotics ITU 2024

https://learnit.itu.dk/pluginfile.php/400034/mod_resource/content/1/tag-project.pdf

### Project Report

https://www.overleaf.com/project/673c4f7d278835d18eba072d

---

### Set the hostName - Main robot

1. Hostname: RGA
2. Username: RGA
3. Password: RGA
4. Connect through this:

- ssh RGA@RGA.local
- ssh RGA@192.168.74.20

---

---

### Set the hostName - Second robot

1. Hostname: RGA2
2. Username: RGA2
3. Password: RGA2
4. Connect through this:

- ssh RGA2@RGA2.local
- ssh RGA2@192.168.74.24

---

### How to run

1. Start flatpack in one windows
   flatpak run --command=thymio-device-manager org.mobsya.ThymioSuite
2. Run the python command in the other one
   python3.11 dev_ir_debug.py

Todo:

- Robot

  - [x] Robot LED (What state it is in)

    - dev_LED_loop.py

  - [x] Robot InfraRed communication

    - dev_ir_debug.py

  - [x] Robot detect safe-zone

    - dev_senfloor.py

  - [X] Robot detect other robots

    - [ ] Based on ir signal and approx sensors?
    - [ ] Implement 360 spin and remember direction of the highest area found

  - [ ] Robot detect other robots state
    - Based on ir signal and color?
  - [ ] Update state based on infrared signal

- Simulation
  - [x] Make map
  - [x] Create robots
  - [x] Simulate floor sensor
  - [ ] Simulate camera sensor
  - [ ] Implement tag-and-avoid behavior
  - [ ] Make simulation as close to reality as possible, i.e how long the camera can see, how far the infrared can be detected

# Update date on raspberry pi

```bash
sudo date -s "2024-12-03 12:00:00"
```
