# Probe planner
A tool to help plan where to implant electrodes, plobes and fibers.

Probeplanner uses [`brainrender`](https://github.com/brainglobe/brainrender) and [vedo](https://github.com/marcomusy/vedo) to create interactive 3D visualizations that allow you to plan where to implant electrodes and fibers. In addition to visualizing the brain and the brain regions that the probe goes through in the 3D viewer, probeplanner provides a terminal-based info panel showing you the current probe parameters and which of brain atlas's regions are touched by the probe. 

The probe parameters are:
* probe tip position: position in the anterio-posterior (AP), dorso-ventral (DV) and medio-lateral (ML) axes expressed in microns relative to the atlas' origin. In the terminal display the *approximate* coordinates relative to bregma are given, but these are intended just as an indication and not as precise coordinates.
* ML angle, the tilt of the probe's shaft in the ML plane. Positive values indicate the probe is tilting to the right (while looking at the brain from the top, as you would during surgery).
* AP angle, angle of the probe's shaft in the AP plane. Positive values indicate that the tip is more anterior than the top of the probe. 

Using the interactive `Planner` sliders can be used to adjust the probe's parameters. As the probe is moved around the display is updated to illustrate which brain regions are traversed by the shaft.
The `Planner` also lets you save the current parameters to a `yaml` file, which can be used later for easily loading probe parameters (either for user in the `Planner` itself or just to visualize a probe using the `Viewer` class)

<img src=screenshot.png></img>






## Installation
If you have a python environment with python >= 3.6:
```
    pip install probeplanner
```

## Usage
The easiest way to use probepanner is through the command line interface. In your terminal you can use:
```
probe plan
```
to lanch the interactive probe planner, or 
```
probe view
```
to use the probe visualizaer. 


The `--help` option can be used to visualize what options these commands accept:
```
(brainrender) ❯ probe plan --help
Usage: probe plan [OPTIONS]

Options:
  -plan, --p TEXT    Path to plan YAML
  -probe, --pp TEXT  Path to probe YAML
  -debug, --debug    Debug?  [default: False]
  --help             Show this message and exit.
```

### probe file
You can save probe parameters in a 'probe' YAML file:
``` yaml
length: 10000
radius: 70
color: 'k'

# ROIs can be used to select parts of the probe to use
# ROIs: 
#   - [0, 400]
#   - [5000, 6000]
ROIs:
```

`length` and `radius` are the geometric shape of the probe, expressed in micrometers. `ROIs` is a list of two tuples indicating regions' of interest
along the probe's shaft, counting from the tip. Each ROI is specified as a tuple of numbers indicating start/end of the ROI in microns. 
ROIs can be used if there's only part of the probe that is to be used (e.g. to see through which brain regions the ROI goes through). E.g. if all electrodes
are in the 500 micrometers closest to the tip you can specify an ROI as `(0, 500)`.

### plan file
A 'plan' YAML file can be used to specify planning parameters (e.g. where the probe should be).

``` yaml
# AIM at brain region
aim_at: 

# Probe angles
AP_angle: -21
ML_angle: 17

# Probe tip location
tip:
- 11327
- 6251
- 5306


# Highlight brain regions
highlight:
  - CUN
  - MOs
  - GRN
  - SCm
```

`aim_at` can be the name of a brain region, if that's passed the probe will be centered on the region's center.
The angles values indicate how the probe should be titled in the ML and AP planes. 
`tip` is a list of three values indicating the coordinate's (AP, DV, ML) of the probe's tip (if `aim_at` is not used). 
`highlight` is an optional list of brain regions to highlight in the viewer.