from wordcloud import WordCloud
from urlextract import URLExtract
from stopwordsiso import stopwords
from collections import Counter

import pandas as pd
import emoji

extract = URLExtract()

def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df =  df[df['users'] == selected_user]
    # fetch number of messages
    num_messages = df.shape[0]
    # fetch number of words
    words = []
    for message in df['messages']:
        words.extend(message)
    # fetch number of media messages
    num_media_messages = df[df['messages'] == '<Media omitted>'].shape[0]
    # fetch number of links shared
    links = []
    for message in df['messages']:
        links.extend(extract.find_urls(message))


    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['users'].value_counts()[:5]
    df = round((df['users'].value_counts()/df.shape[0])*100,2).reset_index().rename(
        columns={'index':'index','users':'name'})
    return x, df


def remove_stopwords(df, messages_column):
    # Get stopwords for Telugu, English, Hindi, Tamil, and Kannada 
    telugu_stopwords = set(stopwords(['te']))
    english_stopwords = set(stopwords(['en']))
    hindi_stopwords = set(stopwords(['hi']))
    tamil_stopwords = set(stopwords(['ta']))
    kannada_stopwords = set(stopwords(['kn']))
    custom_english_stopwords = english_stopwords | {"ha", "kk", "hmm", "hmmm", "haaa", "haa", "group_notification"}
    # Combine all the stopwords into a single set
    all_stopwords = telugu_stopwords | custom_english_stopwords | hindi_stopwords | tamil_stopwords | kannada_stopwords
    # Filter out specific messages and users using the 'apply' function
    df = df[~df['messages'].apply(lambda message: message.strip() in ["<Media omitted>", "message deleted"]) & 
            (df['users'] != 'group_notification')]
    filtered_messages = []
    for message in df[messages_column]:
        # Tokenize the message into individual words
        words = message.split()
        filtered_words = [word for word in words if word.lower() not in all_stopwords]
        # Join the filtered words back into a message
        filtered_message = ' '.join(filtered_words)
        filtered_messages.append(filtered_message)
    # Filter out 'message deleted' from the list
    filtered_messages = [message for message in filtered_messages if message.strip() and
                          message != 'message deleted']
    
    return filtered_messages


def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]
        filtered_messages = remove_stopwords(df, 'messages')
        filtered_text = ' '.join(filtered_messages)
    else:
        filtered_messages = remove_stopwords(df, 'messages')
        filtered_text = ' '.join(filtered_messages)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='black')
    df_wc = wc.generate(filtered_text)

    return df_wc


def most_common_words(selected_user, df, messages_column):
    if selected_user != 'Overall':
        df =  df[df['users'] == selected_user]
        
    words = remove_stopwords(df,messages_column)
    filtered_messages = pd.DataFrame(Counter(words).most_common(20))

    return filtered_messages


def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    emojis = []
    for message in df['messages']:
        for char in message:
            if emoji.is_emoji(char):
                emojis.append(char)

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df


def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    df['date'] = pd.to_datetime(df['date'])
    df['day_name'] = df['date'].dt.day_name()
    monthly_totals = df.groupby(['year', 'month'])['messages'].count().reset_index()
    yearly_totals = df.groupby('year')['messages'].count().reset_index()
    daily_totals = df.groupby('date')['messages'].count().reset_index()
    busy_day = df['day_name'].value_counts()

    return monthly_totals, yearly_totals, daily_totals


def weekly_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    df['day_name'] = df['date'].dt.day_name()

    return df['day_name'].value_counts()


def monthly_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]
    
    month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    df['month_name'] = df['month'].map(month_names)

    return df['month_name'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + '-' + str('00'))
        elif hour == 0:
            period.append(str('00') + '-' + str(hour + 1))
        else:
            period.append(str(hour) + '-' + str(hour + 1))

    df['period'] = period  
    df['day_name'] = df['date'].dt.day_name()
    pivot_table = df.pivot_table(index='day_name', columns='period', values='messages', aggfunc='count').fillna(0)

    return pivot_table

