# coding: utf-8
import os
import time
from concurrent import futures

import pygame
from google.cloud import texttospeech

from . import romaji


class Speaker:
    def __init__(self, volume=0.5, jp=False):
        self.client = texttospeech.TextToSpeechClient()
        self.VOICE_LIST = self.client.list_voices().voices
        self.jp = jp
        if jp:
            self.VOICE_LIST = [voice for voice in self.VOICE_LIST if voice.language_codes[0] == 'ja-JP']

        self.NUM_VOICE = len(self.VOICE_LIST)
        self.VOICE_PATH = "./tmp/"
        self.volume = volume
        os.makedirs(self.VOICE_PATH, exist_ok=True)
        pygame.mixer.init()

    def read_comment_list(self, comment_list):
        num_comment = len(comment_list)
        print(num_comment)
        if num_comment == 0:
            return

        with futures.ThreadPoolExecutor(num_comment) as executor:
            executor.map(self.comment_to_speech, comment_list)

    def comment_to_speech(self, comment):
        published_time = comment['published_time']
        name = comment['name']
        text = comment['text']
        delay = comment['delay']
        author_id = comment['author_id']
        print(f"{published_time} {name} {text}")

        path = self.VOICE_PATH + f'tmp_{name}_{delay}.wav'
        self.make_wav(path, text=text, author_id=author_id, delay=delay)
        sound = pygame.mixer.Sound(path)
        sound.set_volume(self.volume)
        sound.play()
        os.remove(path)

    def make_wav(self, path, text, author_id=0, delay=0.):
        time.sleep(delay)

        voice_id = author_id % self.NUM_VOICE
        voice = self.VOICE_LIST[voice_id]


        if not self.jp:
            # exclude Japanese speaker
            while(voice.language_codes[0] == 'ja-JP'):
                voice_id = (voice_id + 1) % self.NUM_VOICE
                voice = self.VOICE_LIST[voice_id]

        language_code = voice.language_codes[0]
        name = voice.name

        threshold = 350. if language_code == 'ja-JP' else 500.
        speaking_rate = max(1., len(text)/threshold)

        text_ = ''.join(text.split())
        if language_code != 'ja-JP':
            text_ = romaji.convert(text)

        input_text = texttospeech.types.SynthesisInput(text=text_)

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
            speaking_rate=speaking_rate)

        voice = texttospeech.types.VoiceSelectionParams(
            language_code=language_code, name=name)

        response = self.client.synthesize_speech(input_text, voice, audio_config)

        with open(path, 'wb') as out:
            out.write(response.audio_content)

        return path


if __name__ == "__main__":
    test_text = """
    こんにちは、有野です
    """

    copipe = """
ルイズ！ルイズ！ルイズ！ルイズぅぅうううわぁああああああああああああああああああああああん！！！ 
あぁああああ…ああ…あっあっー！あぁああああああ！！！ルイズルイズルイズぅううぁわぁああああ！！！ 
あぁクンカクンカ！クンカクンカ！スーハースーハー！スーハースーハー！いい匂いだなぁ…くんくん 
んはぁっ！ルイズ・フランソワーズたんの桃色ブロンドの髪をクンカクンカしたいお！クンカクンカ！あぁあ！！ 
間違えた！モフモフしたいお！モフモフ！モフモフ！髪髪モフモフ！カリカリモフモフ…きゅんきゅんきゅい！！ 
小説12巻のルイズたんかわいかったよぅ！！あぁぁああ…あああ…あっあぁああああ！！ふぁぁあああんんっ！！ 
アニメ2期放送されて良かったねルイズたん！あぁあああああ！かわいい！ルイズたん！かわいい！あっああぁああ！ 
コミック2巻も発売されて嬉し…いやぁああああああ！！！にゃああああああああん！！ぎゃああああああああ！！ 
ぐあああああああああああ！！！コミックなんて現実じゃない！！！！あ…小説もアニメもよく考えたら… 
ル イ ズ ち ゃ ん は 現実 じ ゃ な い？にゃあああああああああああああん！！うぁああああああああああ！！ 
そんなぁああああああ！！いやぁぁぁあああああああああ！！はぁああああああん！！ハルケギニアぁああああ！！ 
この！ちきしょー！やめてやる！！現実なんかやめ…て…え！？見…てる？表紙絵のルイズちゃんが僕を見てる？ 
表紙絵のルイズちゃんが僕を見てるぞ！ルイズちゃんが僕を見てるぞ！挿絵のルイズちゃんが僕を見てるぞ！！ 
アニメのルイズちゃんが僕に話しかけてるぞ！！！よかった…世の中まだまだ捨てたモンじゃないんだねっ！ 
いやっほぉおおおおおおお！！！僕にはルイズちゃんがいる！！やったよケティ！！ひとりでできるもん！！！ 
あ、コミックのルイズちゃああああああああああああああん！！いやぁあああああああああああああああ！！！！ 
あっあんああっああんあアン様ぁあ！！シ、シエスター！！アンリエッタぁああああああ！！！タバサｧぁあああ！！ 
ううっうぅうう！！俺の想いよルイズへ届け！！ハルケギニアのルイズへ届け！ 
    """

    # ja-JP id: 2, 31
    speaker = Speaker()

    print(speaker.VOICE_LIST)

    _comment_list = list()
    _comment_list.append({'published_time': 'yymmddhhmmss',
                          'name': '有野',
                          'text': test_text,
                          'author_id': 2,
                          'delay': 1.})

    _comment_list.append({'published_time': 'yymmddhhmmss',
                          'name': '有野',
                          'text': test_text,
                          'author_id': 31,
                          'delay': 0.})
    speaker.read_comment_list(_comment_list)
    print("read")
    time.sleep(3)

    _comment_list = list()
    _comment_list.append({'published_time': 'published_time',
                          'name': 'miya',
                          'text': 'おやすみ',
                          'author_id': 32,
                          'delay': 0.})
    speaker.read_comment_list(_comment_list)
    print("read")
    time.sleep(3)
