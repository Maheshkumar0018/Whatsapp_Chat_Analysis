import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def preprocess(data):

    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s*(?:\u202f)?[APap][Mm]\s*-\s'

    messages = re.split(pattern,data)[1:]
    dates = re.findall(pattern,data)

    dates = [date.replace('\u202f', '') for date in dates]
    df = pd.DataFrame({'user_messages':messages,'date':dates})
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y, %I:%M%p - ', errors='coerce')
    df['date'] = df['date'].dt.strftime('%Y-%m-%d %I:%M:%S %p')
    
    users = []
    messages = []

    for message in df['user_messages']:
        message_parts = message.split(':', 1)
        if len(message_parts) > 1:
            users.append(message_parts[0].strip())
            messages.append(message_parts[1].strip())
        else:
            users.append('group_notification')
            messages.append(message_parts[0].strip())

    df['users'] = users
    df['messages'] = messages
    df.drop(columns=['user_messages'], inplace=True)

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %I:%M:%S %p')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day

    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['am_pm'] = df['date'].dt.strftime('%p')


    return df




