# coding: utf-8
import json
import time

import src.speaker as speaker
from src.authorize import authorize
from src.iso_to_jstdt import iso_to_jstdt

URL_BASE = "https://www.googleapis.com/youtube/v3/"


class CommentReader:
    def __init__(self, volume=0.5, jp=False, chat_id=None):
        self.http = authorize()
        self.chat_id = chat_id
        self.page_token = None
        self.speaker = speaker.Speaker(volume=volume, jp=jp)

    def setup_from_channel_id(self, channel_id):
        video_id = self._search_video_id_on_air(channel_id)
        self.setup_from_video_id(video_id)

    def setup_from_video_id(self, video_id):
        self.chat_id = self._search_chat_id(video_id)

    def setup_from_video_url(self, url):
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(url).query)
        if 'v' in query:
            self.setup_from_video_id(query['v'][0])
        else:
            print("[ERROR] invalid video URL")

    def read_aloud(self):
        if self.chat_id is None:
            print("Comment Reader has not set up yet. "
                  "Use 'setup_from_channel_id(channel_id)', "
                  "'setup_from_video_id(video_id)' or "
                  "'setup_from_video_url(url)'")
            return

        if self.page_token is None:
            print("loading")
            self._set_page_token()
            time.sleep(10)

        while True:
            print("comment")
            comment_list = self._get_comment_list()
            self.speaker.read_comment_list(comment_list)
            time.sleep(3)

    def _set_page_token(self):
        url = URL_BASE + ("liveChat/messages?"
                          "part=id"
                          "&hl=ja"
                          "&maxResults=200"
                          "&profileImageSize=16"
                          "&liveChatId={}".format(self.chat_id))

        _, data_ = self.http.request(url)
        data = json.loads(data_)
        if 'nextPageToken' in data:
            self.page_token = data['nextPageToken']
        else:
            print(data_)

    def _get_comment_list(self):
        """
        Get comment list.
        comment list is defined as a list of dictionary
        keywords: text, author_id, delay
        :return:
        """
        url = URL_BASE + ("liveChat/messages?"
                          "part=authorDetails,snippet"
                          "&hl=ja"
                          "&maxResults=200"
                          "&profileImageSize=16"
                          "&liveChatId={chat_id}"
                          "&pageToken={page_token}".format(chat_id=self.chat_id, page_token=self.page_token))

        res, data_ = self.http.request(url)
        data = json.loads(data_)
        comment_list = []
        if self.page_token and 'items' in data:
            self.page_token = data['nextPageToken']

            if len(data['items']) > 0:
                base_time = iso_to_jstdt(data['items'][0]['snippet']['publishedAt'])
            else:
                print('no item')
                return comment_list

            for item in data['items']:
                name = item['authorDetails']['displayName']
                text = item['snippet']['textMessageDetails']['messageText']
                published_time = item['snippet']['publishedAt']
                channel_id = item['authorDetails']['channelId']

                author_id = sum(map(ord, list(channel_id)))
                delta_time = iso_to_jstdt(published_time) - base_time
                delay = float(delta_time.seconds) + float(delta_time.microseconds) / 10**6

                comment_list.append({'published_time': published_time,
                                     'name': name,
                                     'author_id': author_id,
                                     'text': text,
                                     'delay': delay})

            return comment_list
        else:
            print(data_)
            return comment_list

    def _search_video_id_on_air(self, channel_id):
        """
        search the Video ID now on air in the channel
        :param channel_id: Channel ID
        :return: Video ID now on air
        """
        url = URL_BASE + ("search?"
                          "eventType=live"
                          "&part=id"
                          "&channelId={}"
                          "&type=video".format(channel_id))
        _, data_ = self.http.request(url)
        data = json.loads(data_.decode())
        if 'items' in data:
            if data['items']:
                live_id = data['items'][0]['id']['videoId']
                return live_id
            else:
                print("[ERROR] Channel is NOT broadcasting live.")
                exit()

        else:
            print("[ERROR]")
            print(data_)
            exit()

    def _search_chat_id(self, video_id):
        """
        search the Chat ID in the Live Streaming
        :param video_id: Video ID now on air
        :return: Chat ID
        """
        url = URL_BASE + ("videos?"
                          "part=liveStreamingDetails"
                          "&id={}".format(video_id))
        _, data_ = self.http.request(url)
        data = json.loads(data_.decode())
        if 'items' in data:
            if data['items']:
                chat_id = data['items'][0]['liveStreamingDetails']['activeLiveChatId']
                return chat_id
            else:
                print("[ERROR] this video have NO item.")
                exit()
        else:
            print("[ERROR]")
            print(data_)
            exit()


if __name__ == "__main__":
    print("reader")
    reader = CommentReader(jp=True)
    print("reader setup")
    reader.setup_from_video_url("https://www.youtube.com/watch?v=qXDAClVbH7s")
    print("read aloud")
    reader.read_aloud()
