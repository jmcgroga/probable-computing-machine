# -*- coding: utf-8 -*-

import pickle
from zipfile import ZipFile

from zwift import Client
import pandas as pd
from pandas.compat import cPickle as pkl

class ZwiftGenerator(object):
    def __init__(self, username, password, player_id, start_date=None):
        self._username = username
        self._password = password
        self._player_id = player_id
        self._start_date = start_date
        self._metadata = {}

    def generate(self):
        client = Client(self._username, self._password)
        activity = client.get_activity(self._player_id)
        start_date = self._start_date

        start = 0
        done = False

        while not done:
            activities = activity.list(start=start, limit=50)

            for activity_data in activities:
                activity_id = activity_data['id']
                self._metadata[activity_id] = activity_data
                try:
                    for a in activity.get_data(activity_id):
                        if not start_date or (start_date and start_date <= a['time']):
                            a['id'] = activity_id
                            yield a['time'], pd.Series(a)
                        elif start_date:
                            done = True
                            break
                except Exception as e:
                    metadata = activity.get_activity(activity_id)
                    print('Exception: %s (%d/ Saved: %s/Duration: %s)' % (e, activity_id, str(metadata['lastSaveDate']), metadata['duration']))

                if done:
                    break

            if len(activities) < 50:
                done = True
            start += 50

def ZwiftDataFrame(username, password, player_id, start_date=None):
    columns = [
        'id',
        'lat',
        'lng',
        'altitude',
        'distance',
        'speed',
        'power',
        'cadence',
        'heartrate'
    ]

    generator = ZwiftGenerator(username, password, player_id, start_date)

    df = pd.DataFrame.from_dict(dict(generator.generate()),
                                orient='index',
                                columns=columns)
    df.zwift.metadata = generator._metadata

    return df

@pd.api.extensions.register_dataframe_accessor("zwift")
class ZwiftAccessor(object):
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self._metadata = None

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    def resample_agg(self, rule, zwift_agg_func='mean', *args, **kws):
        if rule.upper() == 'ZA':
            resampled = self._obj.groupby('id')
        else:
            resampled = self._obj.resample(rule, *args, **kws)
        
        return resampled.agg({
            'id' : 'last',
            'lat' : 'last',
            'lng' : 'last',
            'altitude' : 'last',
            'distance' : 'last',
            'speed' : zwift_agg_func,
            'power' : zwift_agg_func,
            'cadence' : zwift_agg_func,
            'heartrate' : zwift_agg_func
        })

    def plot(self):
        return self._obj.plot.line(y=['power', 'cadence', 'heartrate'])

    def id(self, _id):
        return self._obj[self._obj['id'] == _id]

    def write_file(self, filename):
        with ZipFile(filename, 'w') as zipfile:
            zipfile.writestr('dataframe', pkl.dumps(self._obj))
            if self._metadata:
                zipfile.writestr('metadata', pickle.dumps(self._metadata))

    @classmethod
    def read_file(cls, filename):
        df = None
        with ZipFile(filename, 'r') as zipfile:
            with zipfile.open('dataframe') as infile:
                df = pkl.loads(infile.read())
            with zipfile.open('metadata') as infile:
                df.zwift.metadata = pickle.loads(infile.read())
        return df
