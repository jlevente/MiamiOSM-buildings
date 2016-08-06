Miami-Dade County Building Import Tutorial
=============

**This import tutorial is inspired by and largely based on the work of the awesome people behind [LA County imports](https://github.com/osmlab/labuildings/blob/master/IMPORTING.md)**

### About this import

This import aims to put nearly 100,000 buildings on the map in Miami-Dade County from Miami-Dade County's open data repository.
We believe this will be a good asset for the community. Since the building count in OSM was very low prior to this import,
a huge number of them could have been imported automatically but obviously, a lot of buildings need to be reviewed by actual mappers. This is where your help is needed!


## Getting started

Before jumping into map editing, here are some info we'd like you to read.

### Creating an import account

First off, since data imports can be significantly different from what people would otherwise map, the common consensus requres you to create a dedicated import account,
so other people will instantly know that the data you insterted is from another source. Creating an import account also helps us monitor the progress.
The best is putting `_imports` (or `_miamibuildings`, etc.) after your existing OSM username (e.g. `jlevente_imports`).


### Getting familiar with OSM

If you are not familiar with OpenStreetMap and the JOSM editor, please check out these guides first and make sure you have a basic understanding of mapping.
To contribute to this project, you need to use the JOSM editor. Here are some resources to get you started:

- Download JOSM - https://josm.openstreetmap.de/wiki/Download
- LearnOSM - http://learnosm.org/en/josm/
- Mapbox Mapping wiki - https://www.mapbox.com/blog/making-the-most-josm/

### Getting familiar with the Tasking Manager

The tasks are organized on Tasking Manager (http://tasks.osm.jlevente.com). Check it out.

## Import workflow

### Install auto-tools plugin in JOSM

The good folks at Mapbox created a plugin to merge building shapes sliced by parcel boundaries. You can find it [here](https://github.com/mapbox/auto-tools).

Open JOSM and install it at **Edit -> Preferences -> Plugins**

![install auto-tools](img/autotools_install.jpg)

### Activate JOSM remote control

The remote control is used to load data layers to JOSM directly from the Tasking Manager.

Open JOSM and activate Remote Control at **Edit -> Prefernces -> Remote Control**

![activate remote](img/activate_remote.jpg)

### Select a task in the Tasking Manager

- Navigate to http://tasks.osm.jlevente.com and choose an area to work on.
- Click on **Start Mapping** (Now the task is locked and others know you're working on it)
- Download current OSM data by selecting **Edit in JOSM** (JOSM needs to be running) This will create a layer called `Data Layer 1` in JOSM
- Download the `*.osm` file specific to your task under the **Extra Instrucitons**. These are the buildings from our import set. A second layer called `mia_buildings_####.osm` will appear in JOSM.
![select task](img/select_task.jpg)
![edit with josm](img/edit_with_josm.jpg)

- Click on **Imagery** and load a background layer. You can use **Bing** or **USGS Large Scale Imagery** that are both of decent quality.
- Your JOSM should look similar to this, with at least 2 data layers. `Data Layer 1` holds the current OSM data (greyed out if not Active) and `mia_building_####.osm` with the buildings to be reviewed.

![josm_sample](img/layers_in_josm.jpg)

### Combining data layers

- Run the Validator and check for potential conflicts in each layer. Try to solve them.
- Select both layers in JOSM and merge them via **Right click -> Merge**. Target layer should be `**mia_building_####.osm`. This step combines the 2 layers. You have to be very careful from this step on as now you have overlapping buildings.



