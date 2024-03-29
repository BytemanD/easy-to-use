from urllib import parse as urllib_parse

from . import client


class InfluxDBClient(client.RestClient):
    WRITE_URL = '/write'

    def __init__(self, host, database, port=8086,
                 user='', password='', presicion=None, **kwargs):
        super(InfluxDBClient, self).__init__(host, port, **kwargs)
        self.user = user
        self.password = password
        self.database = database
        # valid precision: [ns,u,ms,s,m,h]
        self.presicion = presicion

    def query(self, meansurement, fields, filters):
        sql = 'select {0} from {1} where {2}'.format(','.join(fields),
                                                     meansurement, filters)

        url = '/query?{0}'.format(
            urllib_parse.urlencode({'db': self.database, 'q': sql})
        )
        return self.get(url)

    def write(self, measurement, tags, fields, timestramp=None):
        """InfluxDB sql:
           insert into <policy> measurement,tags fields <timestamp>
           tags: tagsKey1=tagValue1,...
           fields: fieldKey1=fieldValue1,...
        """
        tags_list = ','.join(
            ['{0}={1}'.format(k, v) for k, v in tags.items()])
        fields_list = ','.join(
            ['{0}={1}'.format(k, v) for k, v in fields.items()])
        data_body = '{0},{1} {2}'.format(measurement, tags_list, fields_list)
        if timestramp:
            data_body += f' {timestramp}'
        url_params = self.get_write_url_params()
        if self.presicion:
            url_params.update(precision=self.presicion)
        url = '{0}?{1}'.format(self.WRITE_URL,
                               urllib_parse.urlencode(url_params))
        return self.post(url, data_body, headers=self.headers)

    def create_database(self):
        sql = 'CREATE DATABASE {0}'.format(self.database)
        url = '/query?{0}'.format(urllib_parse.urlencode({'q': sql}))
        return self.get(url)

    def get_write_url_params(self):
        return {'db': self.database}


class InfluxDBClientV2(InfluxDBClient):
    """Influxdb v2 Client
    E.g.

    >>> token = 'xtiFkVpkMSQmF6YtL6CjTOPDJ4BqIpDN2TSJrfROGwM0kbYT0aQt1m7xJ9bW'
    >>> client = InfluxDBClientV2('host1', 'test_bucket', 'test_bucket', token,
                                  precsion='s')
    >>> client.write('mem', {'host': 'host1'}, {'used_percent': 100})
    """
    BASE_URL = '/api/v2'
    WRITE_URL = '{0}/write'.format(BASE_URL)

    def __init__(self, host, bucket, org, token, **kwargs):
        super(InfluxDBClientV2, self).__init__(host, bucket,
                                               **kwargs)
        self.org = org
        self.token = token

    @property
    def bucket(self):
        return self.database

    @property
    def headers(self):
        return {"Content-Type": "application/json",
                'Authorization': 'Token {0}'.format(self.token)}

    def get_write_url_params(self):
        return {'org': self.org, 'bucket': self.bucket}
