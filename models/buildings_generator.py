from io import StringIO

import boto3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

from models.utils import AthenaWaiter, download_file_from_s3


class BuildingsGenerator(object):

    def __init__(self, min_x, max_x, min_y, max_y, bucket, folder):
        self.min_x, self.max_x = min_x, max_x
        self.min_y, self.max_y = min_y, max_y
        self.bucket = bucket
        self.folder = folder

    def get_query_string(self):
        return "WITH nodes_in_bbox AS( "\
                "   SELECT id, lat, lon, type, tags FROM planet "\
                "   WHERE type='node' "\
                "   AND lon BETWEEN {0} AND {1} "\
                "   AND lat BETWEEN {2} AND {3} "\
                "), "\
                "ways AS( "\
                "   SELECT type, id, tags, nds FROM planet "\
                "   WHERE type='way' "\
                "), "\
                "relation_ways AS( "\
                "   SELECT r.id, r.tags, way.ref, way.role, way_position "\
                "   FROM planet r "\
                "   CROSS JOIN UNNEST(r.members) "\
                "   WITH ORDINALITY AS m (way, way_position) "\
                "   WHERE r.type='relation' "\
                "   AND element_at(r.tags, 'type')='multipolygon' "\
                "   AND way.role='outer' AND way.type='way' "\
                ") "\
                "SELECT w.id AS way_id, "\
                "   n.id AS node_id, "\
                "   r.id AS relation_id, "\
                "   COALESCE(r.id, w.id) AS building_id, "\
                "   n.lon, n.lat, "\
                "   node_position, "\
                "   COALESCE(r.tags['name'], w.tags['name']) AS name "\
                "FROM ways w "\
                "CROSS JOIN UNNEST(w.nds) "\
                "WITH ORDINALITY AS t (nd, node_position) "\
                "JOIN nodes_in_bbox n ON n.id = nd.ref "\
                "LEFT OUTER JOIN relation_ways r ON w.id=r.ref "\
                "WHERE element_at(COALESCE(r.tags, w.tags), 'building')  "\
                "   IS NOT NULL "\
                "ORDER BY relation_id, way_position, way_id, node_position "\
                .format(self.min_x, self.max_x, self.min_y, self.max_y)

    def get_query_id(self):
        client = boto3.client(
            'athena',
            region_name='us-east-1'
        )
        response = client.start_query_execution(
            QueryString=self.get_query_string(),
            QueryExecutionContext={
                'Database': 'default'
            },
            ResultConfiguration={
                'OutputLocation': 's3://{0}/{1}'.format(
                    self.bucket,
                    self.folder
                )
            }
        )
        return response['QueryExecutionId']

    def get_results_key(self, query_id):
        return '{0}/{1}.csv'.format(self.folder, query_id)

    def get_results_df(self, query_id):
        waiter = AthenaWaiter(max_tries=100)
        waiter.wait(
            bucket=self.bucket,
            key=self.get_results_key(query_id),
            query_id=query_id
        )
        raw_result = StringIO(
            download_file_from_s3(
                self.get_results_key(query_id),
                self.bucket
            )
        )
        return pd.read_csv(raw_result, encoding='utf-8')

    @staticmethod
    def create_polygon(way):
        node_list = list(zip(way.lon, way.lat))
        return Polygon(node_list) if len(node_list) >= 3 \
            else None

    def generate(self):
        all_buildings = gpd.GeoDataFrame()
        query_id = self.get_query_id()
        results = self.get_results_df(query_id)
        ways = results.groupby(by=['building_id', 'way_id'])
        for _, way in ways:
            polygon = self.create_polygon(way)
            if polygon:
                metadata = way.iloc[0]
                building_gdf = gpd.GeoDataFrame(
                    [[
                        metadata['name'],
                        polygon
                    ]],
                    columns=[
                        'name',
                        'geometry'
                    ]
                )
                all_buildings = all_buildings.append(building_gdf)
        return all_buildings.to_json(ensure_ascii=False)
