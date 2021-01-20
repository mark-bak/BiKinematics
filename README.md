### BiKinematics
Application to analyse mtb suspension kinematics.

Written as a project to learn Python :)

## Installation
Ideally setup a [Python 3.7.0 virtual environment](https://medium.com/swlh/how-to-run-a-different-version-of-python-from-your-terminal-fe744276ff22) - later python versions should work however I haven't tested.

# Install requirements:

'''
pip install -r requirements.txt #Python reqs

garden install matplotlib #Kivy - matplotlib addon
'''

## Usage
# Run app:
'''
py BiKinematics.py
'''
# Guide/Workflow:
To be added when I have time
## Features
# Current features 
Background image import
Simulated motion of following (tested!) suspension systems - can probably handle more, solver is reasonably general:
- Horst Link
- DW Link
- Split Pivot (Devinci)
- Single Pivot
Axle Path 
Leverage ratio calculation
Results Plotting 

# To add
Other suspension systems (whatever tf yeti is doing)
Anti-squat calculations (Including with Idler pulley)
Pedal kickback calculations
Improved results plotting and graph image saving
Slicker UI

