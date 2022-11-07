#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install --upgrade google-api-python-client


# In[2]:


import pandas as pd
import seaborn as sns
from googleapiclient.discovery import build


# In[3]:


api_key = 'AIzaSyD6kDYAmM56TvcSPao_UhSunFhaW7moeG8'
channel_ids = [
            'UCe0EaCUquEbwZ4pfJnSKcrg',
               'UCeZOywU-zg9j3SxYG0FdLtw',
               'UCZSNzBgFub_WWil6TOTYwAg',
               'UC5ZiUaIJ2b5dYBYGf5iEUrA',
               'UCzi3g9ade6lq-nGjShQOJJg',
               'UCMw2QZuFUZxfFAFZ0hOLrZg'
              ]

youtube = build('youtube', 'v3', developerKey=api_key)


# ## Function to get channel statistics

# In[4]:


def channel_stats(youtube, channel_ids):
    request = youtube.channels().list(part ='snippet,contentDetails,statistics', id=','.join(channel_ids))
    response = request.execute()

    return response


# In[5]:


channel_stats(youtube, channel_ids)


# In[6]:


def channel_spec(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=','.join(channel_ids))
    response = request.execute() 
    
    for i in range(len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet']['title'],
                    Subscribers = response['items'][i]['statistics']['subscriberCount'],
                    Views = response['items'][i]['statistics']['viewCount'],
                    Total_videos = response['items'][i]['statistics']['videoCount'],
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)
    
    return all_data


# In[7]:


channel_spec(youtube, channel_ids)


# In[8]:


channel_stats = channel_spec(youtube, channel_ids)


# In[9]:


data = pd.DataFrame(channel_stats)


# In[10]:


data
# data.dtypes


# In[11]:


playlist_id = data.loc[data['Channel_name']=='Netflix Nordic', 'playlist_id'].iloc[0]


# In[12]:


data['Subscribers'] = pd.to_numeric(data['Subscribers'])
data['Views'] = pd.to_numeric(data['Views'])
data['Total_videos'] = pd.to_numeric(data['Total_videos'])
data.dtypes


# In[13]:


sns.set(rc={'figure.figsize':(10,8)})
ax = sns.barplot(x='Channel_name', y='Subscribers', data = data) 
ax.bar_label(ax.containers[0])


# In[14]:


ax = sns.barplot(x='Channel_name', y='Views', data = data)
ax.bar_label(ax.containers[0])


# In[15]:


ax = sns.barplot(x='Channel_name', y='Total_videos', data = data)
ax.bar_label(ax.containers[0])


# # Video details from Netflix Nordic channel
# 

# In[16]:


channel_spec


# In[17]:


def get_videos_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId = playlist_id,
        maxResults = 50)
    response = request.execute()
    
    video_ids = []
    
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50,
                pageToken = next_page_token)
            response = request.execute()
            
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
            next_page_token = response.get('nextPageToken')
            
    return video_ids 


# In[18]:


video_ids = get_videos_ids(youtube, playlist_id)


# In[19]:


video_ids


# # Function to get video details

# In[28]:


def get_video_details(youtube, video_ids):
    all_video_stats = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids[i:i+50]))
        response = request.execute()
        
        for video in response['items']:
            video_stats = dict(Title = video['snippet']['title'],
                               Published_date = video['snippet']['publishedAt'],
                               Views = video['statistics']['viewCount'],
                               Likes = video['statistics']['likeCount'],
                               )
            all_video_stats.append(video_stats)
    
    return all_video_stats


# In[29]:


video_details = get_video_details(youtube, video_ids)


# In[30]:


video_data = pd.DataFrame(video_details)


# In[33]:


video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data


# In[36]:


top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)
top10_videos


# In[38]:


ax1 = sns.barplot(x='Views', y='Title', data=top10_videos)

