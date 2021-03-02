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
probe plane
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
  -aim-at, --at TEXT       Name of brain region to aim at
  -hemisphere, --h TEXT    target hemisphere
  -AP-angle, --AP INTEGER  angle on AP plane  [default: 0]
  -ML-angle, --ML INTEGER  angle on ML plane  [default: 0]
  -highlight, --hl TEXT    names of brain regions to highlight (separated by
                           space)  [default: ]

  -probe, --p TEXT         .yaml file with probe data
  -debug, --debug          Debug?  [default: False]
  --help        
```

The main arguments are:
- **aim-at** which lets you aim (i.e. position the probe tip) at a brain region by passing its name (e.g. 'CUN' will set the tip of the probe in the cuneiform)
- **AP** and **ML** let you specify the angle of the probe on the two main planes
- **highlight** lets you pass a list of regions names (e.g. 'CUN MOs SCm') to be highlighted during use.
- **probe_file** can be a path to a .yaml file with probe data (which you can generate with the planner's save probe button)

For `probe visualize` these are the arguemnts:
```
(brainrender) ❯ probe view --help     
Usage: probe view [OPTIONS] [PROBE_FILE]

Arguments:
  [PROBE_FILE]

Options:
  -highlight, --hl TEXT  names of brain regions to highlight (separated by
                         space)  [default: ]

  -debug, --debug        Debug?  [default: False]
  --help                 Show this message and exit.
```
