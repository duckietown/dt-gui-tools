# How to run it

## Run in docker
From root project folder
````
	dts devel build
	dts devel run -X
	dt-launcher-editor
````

or

````
	dts devel build
	dts map editor --image <image name>
````
image name has format like this: duckietown/dt-gui-tools:<branch name>-amd64
branch name may be "ente" or "main" or other

## Run locally
From packages/map_editor/ folder
````
	pip3 install -r requirements.txt
	python3 main.py
````
