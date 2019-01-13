# -*- coding: utf-8 -*-

from zwift import Client
import pandas as pd

def generate(username, password, player_id, start_date=None):
    client = Client(username, password)
    activity = client.get_activity(player_id)

    start = 0
    done = False

    while not done:
        activities = activity.list(start=start, limit=50)

        for activity_data in activities:
            activity_id = activity_data['id']
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

    df = pd.DataFrame.from_dict(dict(generate(username, password, player_id, start_date)),
                                orient='index',
                                columns=columns)
    return df
