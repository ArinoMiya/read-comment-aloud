# coding: utf-8
import os
import httplib2
from oauth2client import tools, client
from oauth2client.file import Storage

key_path = os.path.dirname(__file__) + "/../../Key/ReadCommentAloud/"
credentials_path = key_path + "credentials.json"


def authorize():
    if os.path.exists(credentials_path):
        store = Storage(credentials_path)
        credentials = store.get()

    else:
        key = key_path + "client.json"
        scope = "https://www.googleapis.com/auth/youtube.readonly"
        flow = client.flow_from_clientsecrets(key, scope)
        flow.user_agent = "developer"
        credentials = tools.run_flow(flow, Storage(credentials_path))

    http = credentials.authorize(httplib2.Http())
    return http
