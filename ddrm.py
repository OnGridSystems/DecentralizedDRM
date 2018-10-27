import sys
sys.path.insert(0, "nucypher")
from nucypher.characters.lawful import Alice as Author
from nucypher.characters.lawful import Bob as Subscriber
from nucypher.characters.lawful import Ursula
from nucypher.network.middleware import RestMiddleware
from nucypher.data_sources import DataSource
from umbral.keys import UmbralPublicKey
import os
import binascii
import shutil
import maya
import datetime
import requests

requests.packages.urllib3.disable_warnings()

class RawStream(object):
    class RawEpisode(object):
        def __init__(self, label, content):
            self.label = label
            self.content = content

    def __init__(self, author):
        self.author = author
        self.raw_episodes = [
            self.RawEpisode(b"Episode01", b"(C)opyrighted Content of Episode 01"),
            self.RawEpisode(b"Episode02", b"(C)opyrighted Content of Episode 02"),
            self.RawEpisode(b"Episode03", b"(C)opyrighted Content of Episode 03"),
            self.RawEpisode(b"Episode04", b"(C)opyrighted Content of Episode 04"),
            self.RawEpisode(b"Episode05", b"(C)opyrighted Content of Episode 05"),
            self.RawEpisode(b"Episode06", b"(C)opyrighted Content of Episode 06"),
            self.RawEpisode(b"Episode07", b"(C)opyrighted Content of Episode 07"),
            self.RawEpisode(b"Episode08", b"(C)opyrighted Content of Episode 08"),
            self.RawEpisode(b"Episode09", b"(C)opyrighted Content of Episode 09"),
            self.RawEpisode(b"Episode10", b"(C)opyrighted Content of Episode 10"),
            self.RawEpisode(b"Episode11", b"(C)opyrighted Content of Episode 11"),
            self.RawEpisode(b"Episode12", b"(C)opyrighted Content of Episode 12"),
            self.RawEpisode(b"Episode13", b"(C)opyrighted Content of Episode 13"),
            self.RawEpisode(b"Episode14", b"(C)opyrighted Content of Episode 14"),
            self.RawEpisode(b"Episode15", b"(C)opyrighted Content of Episode 15"),
            self.RawEpisode(b"Episode16", b"(C)opyrighted Content of Episode 16"),
        ]

class PublicEdekProtectedStream(object):
    class PublicEdekProtectedEpisode(object):
        def __init__(self, label, raw_episode, author, n=3, m=2):
            self.n = n
            self.m = m
            policy_end_datetime = maya.now() + datetime.timedelta(days=365)
            self.label = label
            self.author = author
            self.policy = self.author.grant(self.author, self.label, m=m, n=n,
                                            expiration=policy_end_datetime)
            self.data_source = DataSource(policy_pubkey_enc=self.policy.public_key, label=self.label)
            self.data_source_public_key = bytes(self.data_source.stamp)
            self.episode_message_kit, self.episode_signature = self.data_source.encapsulate_single_message(raw_episode)

        def grant(self, subscriber, hours=1):
            policy_end_datetime = maya.now() + datetime.timedelta(hours=hours)
            self.author.grant(subscriber, self.label, m=self.m, n=self.n,
                              expiration=policy_end_datetime)

    def __init__(self, raw_stream):
        self.author = raw_stream.author
        self.author_pubkey = bytes(self.author.stamp)
        # self.data_source = DataSource(policy_pubkey_enc=policy.public_key)
        # self.data_source_public_key = bytes(self.data_source.stamp)
        self.protected_episodes = []
        for raw_episode in raw_stream.raw_episodes:
            protected_episode = self.PublicEdekProtectedEpisode(raw_episode.label, raw_episode.content, self.author)
            self.protected_episodes.append(protected_episode)

    def grant_access_to_episodes(self, subscriber, hours=1, from_episode_id=0, to_episode_id=None):
        if to_episode_id == None:
            to_episode_id = len(self.protected_episodes)
        for episode in range(from_episode_id, to_episode_id):
            print("Grant %s access to episode %s" % (subscriber, episode))
            self.protected_episodes[episode].grant(subscriber, hours)


class StreamPlayer(object):
    def __init__(self, protected_stream, subscriber, author, start_from_episode_id=0):
        self.current_episode_id = start_from_episode_id
        self.protected_stream = protected_stream
        self.subscriber = subscriber
        self.author = author

    def fetch_next_episode(self):
        episode_id = self.current_episode_id
        episode = self.protected_stream.protected_episodes[episode_id]
        self.current_episode_id += 1
        return episode

    def decrypt_and_play_next_episode(self):
        episode_to_decrypt = self.fetch_next_episode()
        self.subscriber.join_policy(episode_to_decrypt.label,  # The label - he needs to know what data he's after.
                                    bytes(self.author.stamp),  # To verify the signature, he'll need Alice's public key.
                                    node_list=[("localhost", 3501)]
                                    )
        decrypted_episode = self.subscriber.retrieve(message_kit=episode_to_decrypt.episode_message_kit,
                                                data_source=episode_to_decrypt.data_source,
                                                alice_verifying_key=UmbralPublicKey.from_bytes(
                                                    bytes(self.author.stamp)))
        print(decrypted_episode)
        return decrypted_episode

teacher_rest_port = 3501
with open("nucypher/examples/examples-runtime-cruft/node-metadata-{}".format(teacher_rest_port), "r") as f:
    f.seek(0)
    teacher_bytes = binascii.unhexlify(f.read())
URSULA = Ursula.from_bytes(teacher_bytes, federated_only=True)
print("Will learn from {}".format(URSULA))
SHARED_CRUFTSPACE = "{}/nucypher/examples/examples-runtime-cruft".format(os.path.dirname(os.path.abspath(__file__)))
CRUFTSPACE = "{}/drm".format(SHARED_CRUFTSPACE)
CERTIFICATE_DIR = "{}/certs".format(CRUFTSPACE)
shutil.rmtree(CRUFTSPACE, ignore_errors=True)
os.mkdir(CRUFTSPACE)
os.mkdir(CERTIFICATE_DIR)
URSULA.save_certificate_to_disk(CERTIFICATE_DIR)

author = Author(network_middleware=RestMiddleware(),
                known_nodes=(URSULA,),
                federated_only=True,
                known_certificates_dir=CERTIFICATE_DIR,
                )
author.start_learning_loop(now=True)
raw_stream = RawStream(author)
protected_stream = PublicEdekProtectedStream(raw_stream)

subscriber = Subscriber(known_nodes=(URSULA,),
                        federated_only=True,
                        known_certificates_dir=CERTIFICATE_DIR)

protected_stream.grant_access_to_episodes(subscriber)

stream_player = StreamPlayer(protected_stream, subscriber, author)

for i in range(10):
    stream_player.decrypt_and_play_next_episode()