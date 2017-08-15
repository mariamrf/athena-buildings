# athena-buildings
A script that queries OpenStreetMap using AWS Athena for buildings in a given bounding box.

## Install

1. Setup the virtualenv
  ```bash
    $ virtualenv -p python3 venv
  ```
2. Install the requirements
  ```bash
    $ pip install -r requirements.txt
  ```
3. Copy the `.env` file and fill it
  ```bash
    $ cp .env.example .env
  ```

## Run
```bash
  $ python get_buildings.py
```
This gets the buildings in Iceland and stores it into a local GeoJSON file (in `output`).
The class that actually gets the data is in [models/buildings_generator.py](models/buildings_generator.py).
