# BiKinematics
Application to analyse mtb suspension kinematics.

Written as a project to learn Python :)

Uses the following main packages:
* Kivy - GUI
* Numpy/Scipy - Linkage Simulation
* Matplotlib - Plotting

## Installation

1. Ideally setup a [Python 3.7.0 virtual environment](https://medium.com/swlh/how-to-run-a-different-version-of-python-from-your-terminal-fe744276ff22) - later python versions should work however I haven't tested.

1. Install requirements

```
pip install -r requirements.txt #Python reqs
  
garden install matplotlib #Kivy - matplotlib addon
```

## Usage
### Run app

```
py BiKinematics.py
```
### Guide/Workflow:
Typical workflow for analysing bike image

1. Add image (Add.. menu)
- Closer cropped the better
<img src = ReadmeImages/AddImage.PNG>

2. Add points
- Ground points do not move (in x,y) as linkage does (typically attached to front triangle)
- Linkage points will move relative to front triangle as suspension compresses
- Front and rear wheel should be pretty obvious...

<img src = ReadmeImages/AddPoint.PNG>

3. Add links between points
- Add links between any points on the same member/rigidly connected to each other
- Add shock between shock mountings

4. Add wheelbase in User Parameters
- Allows scaling from px to mm, gives accurate travel distance in simulation
- Either get from datasheet or adjust until shock eye- eye length (mm) is correct
<img src = ReadmeImages/Bike.PNG>

5. Simulate for desired travel
<img src = ReadmeImages/SimMenu.PNG>

6. Select data and desired characteristics
- Note all sim results saved can be loaded in, and multiple different bikes can be compared
<img src = ReadmeImages/Plot.PNG>

There are also numerous examples in SaveFiles that can be loaded in using the Load/Save... menu
## Features
### Current features 
Background image import
Simulated motion of following (tested!) suspension systems - can probably handle more, solver is reasonably general:
- Horst Link
- DW Link
- Split Pivot (Devinci)
- Single Pivot
Axle Path 
Leverage ratio calculation
Results Plotting 

### To add
- Other suspension systems (whatever tf yeti is doing)
- Anti-squat calculations (Including with Idler pulley)
- Pedal kickback calculations
- Improved results plotting (axis ranges, data normalising to zero etc..) and graph image saving
- Slicker UI

