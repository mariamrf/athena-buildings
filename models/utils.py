from time import sleep

import boto3
import botocore
from botocore.client import Config
import click

def get_s3_client():
    return boto3.client(
        's3', 'us-east-1', config=Config(
            s3={'addressing_style': 'path'}
        )
    )


def download_file_from_s3(key, bucket):
    s3_client = get_s3_client()
    data = s3_client.get_object(
        Bucket=bucket,
        Key=key
    )
    return data['Body'].read().decode("utf-8")


class AthenaWaiterException(Exception):
    pass


class AthenaWaiter(object):
    """Not only can wait more than the AWS S3 waiter,
    but it also checks if the query has failed
    or was canceled and stops instead of waiting
    until it times out.
    """

    def __init__(self, max_tries=30, interval=5):
        self.s3_client = get_s3_client()
        self.athena_client = boto3.client(
            'athena',
            region_name='us-east-1'
        )
        self.max_tries = max_tries
        self.interval = interval

    def object_exists(self, bucket='', key=''):
        exists = True
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
        except botocore.exceptions.ClientError as exc:
            if exc.response['Error']['Code'] == '404':
                exists = False
            else:
                raise
        return exists

    def check_status(self, query_id):
        status = self.athena_client.get_query_execution(
            QueryExecutionId=query_id
        )['QueryExecution']['Status']
        if status['State'] in ['FAILED', 'CANCELLED']:
            raise AthenaWaiterException(
                'Query Error: {0}'
                .format(status['StateChangeReason'])
            )

    def wait(self, bucket='', key='', query_id=''):
        click.echo(
            'Waiting for file ({0}) in {1}'
            .format(key, bucket),
            nl=False
        )
        success = False
        for _ in range(self.max_tries):
            if self.object_exists(bucket=bucket, key=key):
                success = True
                click.echo('')
                break
            self.check_status(query_id)
            click.echo('.', nl=False)
            sleep(self.interval)
        if not success:
            raise AthenaWaiterException(
                'Exceeded the maximum number of tries ({0})'
                .format(self.max_tries)
            )