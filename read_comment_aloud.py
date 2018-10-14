# coding: utf-8
import argparse

import src.comment_reader as comment_reader

SETUP_TYPE = ['channel', 'video', 'url']


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method',
                        type=str,
                        choices=SETUP_TYPE,
                        default='channel',
                        help="Specifying method. channel, video or url"
                        )
    parser.add_argument('-i', '--id',
                        type=str,
                        default='UC__IB9dJtrMrSjWc75YeCOA',
                        help="Channel ID, Video ID or Video URL"
                        )
    parser.add_argument('-j', '--jp',
                        action='store_true',
                        help="Japanese voices only"
                        )
    parser.add_argument('-v', '--volume',
                        type=float,
                        default=0.7,
                        help="voice volume"
                        )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    arg = parse_args()
    reader = comment_reader.CommentReader(volume=arg.volume, jp=arg.jp)
    if arg.method == 'channel':
        reader.setup_from_channel_id(arg.id)
    elif arg.method == 'video':
        reader.setup_from_video_id(arg.id)
    elif arg.method == 'url':
        reader.setup_from_video_url(arg.id)
    else:
        print("argument error: method")
        exit()

    reader.read_aloud()
