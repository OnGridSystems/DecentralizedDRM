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
    """Raw copyrighted stream. Never exposed publicly.

    Attributes:
        raw_episodes: An ordered list of the episodes
        author: The author character who owns the data
    """
    class RawEpisode(object):
        """The raw episode of the stream.
        Can be the frame/scene of the film/stream.
        Never exposed publicly unencrypted.

        Attributes:
            label: The metadata which helps to find the related policy on Ursulas
            content: The raw content to be encrypted
        """
        def __init__(self, label, content):
            self.label = label
            self.content = content

    def __init__(self, author):
        """The content gets initialised as a set of ordered episodes"""
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
    """Keeps the stream metadata and the ordered set of episodes.
    The content of episodes is encrypted so this object can be published
    or publicly streamed.

    Attributes:
        author_pubkey: The author pubkey to authenticate the stream on receiver
        protected_episodes: The set of the episodes where the content is encrypted.
    """
    class PublicEdekProtectedEpisode(object):
        """Keeps the individual episode label, data and policy configuration.
        Data is encrypted so it's absolutely secure to keep it public

        Attributes:
            label: public unencrypted label used in search on Ursulas
            policy: policy on Ursula (provisione for each episode)
            data_source: the decryption abstraction, see pyUmbral docs
            episode_message_kit: the capsule providing the reencryption capabilities, see pyUmbral docs
        """
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
            """Access can be granted on per-subscriber per-episode basis with time limits.
            1 hour by default which is pretty enough for streaming app"""
            policy_end_datetime = maya.now() + datetime.timedelta(hours=hours)
            self.author.grant(subscriber, self.label, m=self.m, n=self.n,
                              expiration=policy_end_datetime)
            print("DDRM:Stream:Episode: access granted for the subscriber {} for {} hours".format(subscriber,hours))

    def __init__(self, raw_stream):
        self.author = raw_stream.author
        self.author_pubkey = bytes(self.author.stamp)
        self.protected_episodes = []
        for raw_episode in raw_stream.raw_episodes:
            protected_episode = self.PublicEdekProtectedEpisode(raw_episode.label, raw_episode.content, self.author)
            self.protected_episodes.append(protected_episode)

    def grant_access_to_episodes(self, subscriber, hours=1, from_episode_id=0, to_episode_id=None):
        """Grants access for the set of episodes for given time"""
        if to_episode_id == None:
            to_episode_id = len(self.protected_episodes)
        for episode in range(from_episode_id, to_episode_id):
            print("DDRM:Stream:Episode: Grant access for the subscriber {} to episode {}".format(subscriber, episode))
            self.protected_episodes[episode].grant(subscriber, hours)


class StreamPlayer(object):
    """The subscriber's player device or program which fetches data (episodes) by given url
    then decrypts, decodes and plays them.

        Attributes:
            current_episode_id: The next episode to play
            protected_stream: The protected stream (stream URI)
            subscriber: the person for whom the EDEKs will be reencrypted
    """
    def __init__(self, protected_stream, subscriber, author, start_from_episode_id=0):
        self.current_episode_id = start_from_episode_id
        self.protected_stream = protected_stream
        self.subscriber = subscriber
        self.author = author

    def fetch_next_episode(self):
        """Return the next protected episode from the stream"""
        episode_id = self.current_episode_id
        episode = self.protected_stream.protected_episodes[episode_id]
        self.current_episode_id += 1
        return episode

    def decrypt_and_play_next_episode(self):
        """Decrypts and plays the next episode.

                Attributes:
                    episode_to_decrypt: The next episode to decrypt
                    decrypted_episode: The raw content of the episode, this data to be played then discarded
        """
        episode_to_decrypt = self.fetch_next_episode()
        self.subscriber.join_policy(episode_to_decrypt.label,
                                    bytes(self.author.stamp),
                                    node_list=[("localhost", 3501)]
                                    )
        print("DDRM:Player: retrieves the episode {}".format(episode_to_decrypt.label))
        decrypted_episode = self.subscriber.retrieve(message_kit=episode_to_decrypt.episode_message_kit,
                                                data_source=episode_to_decrypt.data_source,
                                                alice_verifying_key=UmbralPublicKey.from_bytes(
                                                    bytes(self.author.stamp)))
        return decrypted_episode

teacher_rest_port = 3501
with open("nucypher/examples/examples-runtime-cruft/node-metadata-{}".format(teacher_rest_port), "r") as f:
    f.seek(0)
    teacher_bytes = binascii.unhexlify(f.read())
URSULA = Ursula.from_bytes(teacher_bytes, federated_only=True)
print("DDRM: Will learn from {}".format(URSULA))
SHARED_CRUFTSPACE = "{}/nucypher/examples/examples-runtime-cruft".format(os.path.dirname(os.path.abspath(__file__)))
CRUFTSPACE = "{}/drm".format(SHARED_CRUFTSPACE)
CERTIFICATE_DIR = "{}/certs".format(CRUFTSPACE)
shutil.rmtree(CRUFTSPACE, ignore_errors=True)
os.mkdir(CRUFTSPACE)
os.mkdir(CERTIFICATE_DIR)
URSULA.save_certificate_to_disk(CERTIFICATE_DIR)

print("DDRM: Instantiating the stream author")
author = Author(network_middleware=RestMiddleware(),
                known_nodes=(URSULA,),
                federated_only=True,
                known_certificates_dir=CERTIFICATE_DIR,
                )
print("DDRM: Author instantiated {}".format(author))
author.start_learning_loop(now=True)
print("DDRM: Instantiating raw unprotected stream to keep in secret")
raw_stream = RawStream(author)
print("DDRM: Raw unprotected stream instantiated {}".format(raw_stream))
print("DDRM: Encyphering the stream for publishing")
protected_stream = PublicEdekProtectedStream(raw_stream)
print("DDRM: Stream encrypted and published {}".format(protected_stream))
print("DDRM: Instantiating the Subscriber")
subscriber = Subscriber(known_nodes=(URSULA,),
                        federated_only=True,
                        known_certificates_dir=CERTIFICATE_DIR)
print("DDRM: Subscriber instantiated {}".format(subscriber))
print("DDRM: grant access Subscriber to the stream (its episodes)")
protected_stream.grant_access_to_episodes(subscriber)
print("DDRM: Subscriber was given access to the episodes")
print("DDRM: Instantiate subscriber's player and connect to the stream")
stream_player = StreamPlayer(protected_stream, subscriber, author)
print("DDRM: Subscriber's player instantiated {}".format(stream_player))
print("DDRM: Start stream play loop")
for i in range(10):
    print("DDRM:Player: Play the stream episode {}".format(i))
    raw_episode = stream_player.decrypt_and_play_next_episode()
    print("DDRM:Player: Decrypted episode is {}".format(raw_episode))