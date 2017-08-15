import os

from dotenv import load_dotenv

from models.buildings_generator import BuildingsGenerator

load_dotenv(os.path.join(os.getcwd(), '.env'))

if __name__ == '__main__':
    generator = BuildingsGenerator(
        -26.26,
        -12.24,
        62.48,
        67.25,
        os.environ['S3_BUCKET'],
        'iceland'
    )
    buildings = generator.generate()
    with open('output/iceland_buildings.geojson', 'w') as file_:
        file_.write(buildings)