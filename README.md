# BiKinematics
Application to analyse mtb suspension kinematics.

Written as a project to learn Python :)

Uses the following main packages:
* Kivy - GUI
* Numpy/Scipy - Linkage Simulation
* Matplotlib - Plotting
* bikinematicsolver - A library I made to analyse bike supsensions
* Jupyter - Development/prototyping of solver eqns/maths

## Installation

1. Ideally setup a [Python 3.7.0 virtual environment](https://medium.com/swlh/how-to-run-a-different-version-of-python-from-your-terminal-fe744276ff22) - later python versions should work however I haven't tested.

1. Install requirements

```
pip install -r requirements.txt #Python reqs
pip install git+https://github.com/mark-bak/bikinematicsolver.git #Solver module - not on PyPi yet - will probably get an error when dling requirement.txt because of this - haven't tested this yet
  
garden install matplotlib #Kivy - matplotlib addon
```
## Usage
### Run app

```
py BiKinematics.py
```

## Features
### Current features 
- Background image import
- Simulated motion of following (tested!) suspension systems - can probably handle more, solver is reasonably general (handles any system that is a single-piv or a 4-bar arrangement with slightly different placed pivots (seems like >80% of suspension despite all the different names/trademarks):
  - Horst Link
  - DW Link
  - Split Pivot (Devinci)
  - Single Pivot
- Axle Path 
- Leverage ratio calculation
- Anti squat calculation
- Results Plotting 

### To add
- Other suspension systems (whatever tf yeti is doing, specialised demo/canyon sender with the extra links for shock)
- Idler pulley support (solver side is almost there, not much more work to be done)
- Pedal kickback calculations
- Improved results plotting (axis ranges, data normalising to zero etc..) and graph image saving
- Slicker UI
- Write specific optimised solvers for each layout (4 bar, single piv etc)

### Guide/Workflow (Slightly out of date - best to load up an example and see what it contains):
Typical workflow for analysing bike image

1. Add image
<img src = ReadmeImages/AddImage.PNG>

2. Add points
- Click add point, then click on screen where you want to place it
- Ground points do not move relative to front triangle (usually attachment to front triangle)
- Linkage points will move relative to front triangle as suspension compresses
- Front and rear wheel should be pretty obvious...
- Note points can be dragged around after placement

<img src = ReadmeImages/AddPoint.PNG>

3. Add links between points
- Click add link, then click the points to add between in turn
- Add links between any points on the same member (rigidly connected to each other)
- Add shock between shock mountings

4. Add wheelbase in User Parameters
- Allows scaling from px to mm, gives accurate travel distance in simulation
- Either get from datasheet or adjust until shock eye- eye length (mm) is correct
<img src = ReadmeImages/Bike.PNG>

5. Save model if desired
- Will save all geometry and wheelbase values in /SaveFiles/ in json format
- Note - there are some examples of bikes I have been testing with already in SaveFiles

6. Simulate for desired travel
- The results will be saved in /Results/Filename.csv
<img src = ReadmeImages/SimMenu.PNG>

7. In plotting screen, select data and desired characteristics to be plotted
- Note all simulated results saved can be loaded in, so multiple different bikes can be compared
<img src = ReadmeImages/Plot.PNG>



