#!/usr/bin/python3

import argparse
import os
import re
import time
import socket

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

CLIENT_SECRETS_FILE = 'client_secret.json'

SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Аутентификация в два аккаунта с созданием локального веб-сервера на 2х разных портах 
def get_authenticated_service(export: bool):
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  if export:
    credentials = flow.run_local_server(port=8080)
  else:
    credentials = flow.run_local_server(port=8081)
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

# Вызов API youtube.subscriptions.list для постраничной выгрузки подписок
def get_chanellsid(target_channels):
  next_page_token = ''
  while True:
    get_chanellsid_response = youtube.subscriptions().list(
      part="snippet",
      mine=True,
      maxResults=50,
      pageToken=next_page_token
    ).execute()
    for channelid in get_chanellsid_response['items']:
      target_channels.append(channelid['snippet']['resourceId']['channelId'])
    if 'nextPageToken' in get_chanellsid_response:
      next_page_token = get_chanellsid_response['nextPageToken']
    else:
      break

# Вызов API youtube.subscriptions.insert для добавления подписки на канал
def add_subscription(youtube, channel_id):
  add_subscription_response = youtube.subscriptions().insert(
    part='snippet',
    body=dict(
      snippet=dict(
        resourceId=dict(
          channelId=channel_id
        )
      )
    )).execute()
  return add_subscription_response


if __name__ == '__main__':

  print()
  print(bcolors.WARNING + 'Login to Google-account for export!' + bcolors.ENDC)
  print()

  youtube = get_authenticated_service(export=True)
  export_account_channels = []
  get_chanellsid(export_account_channels)

  print()
  print(bcolors.WARNING + 'Login to Google-account for import!' + bcolors.ENDC)
  print()

  youtube = get_authenticated_service(export=False)
  import_account_channels = []
  get_chanellsid(import_account_channels)

  channels_to_add = list(set(export_account_channels) ^ set(import_account_channels)) # Извлечение еще неоформленных подписок на импорт-аккаунте
  channels_to_add_quantity = len(channels_to_add)

  if channels_to_add_quantity > 200:
    print()
    print(bcolors.WARNING + 'Channels quantity greater than API quota! Wait for the end of execution and try again next day!' + bcolors.ENDC)
    print()

  counter = 0
  try:
    for channel_id in channels_to_add:
      add_subscription(youtube, channel_id)
      counter += 1
  except HttpError as e:
    print(bcolors.FAIL + 'An HTTP error {} occurred:\n{}'.format(e.resp.status, e.content) + bcolors.ENDC)
    print()
    print('A subscriptions to ' + str(counter) + ' channels ' + 'was ' + bcolors.OKGREEN + 'added.' + bcolors.ENDC)
  else:
    print('A subscriptions to ' + str(counter) + ' channels ' + 'was ' + bcolors.OKGREEN + 'added.' + bcolors.ENDC)