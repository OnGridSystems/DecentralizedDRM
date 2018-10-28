# Decentralized Digital Rights Management (DDRM) 
Prototype illustrating the principles of copyrighted media control for [SerialHack Hackathon](http://serialhack.io).

## Problem
Propose the digital rights management (DDRM) solution for decentralized application stack.

## Requirements
* MUST be delivered in Docker container with all requirements whould be resolved
* If Smart-Contract proposed, it MUST be deployed in the Testnet or Mainnet
* README describing the proposal MUST be provided
* CLI tools to test the code should be provided
* MUST be delivered as the Project on GitLab

## Proposed Solution
The DDRM system controls the use and distribution of high-bandwidth multimedia content (like
HD-streams) in scalable and author-controlled way.

In contrast to centralized DRM services, the access can be granted by a smart-contract with conditional
reencryption tokens released upon a payment. Access can be granted in time-based, channel-based,
frame-based way be single-use or revocable.

[NyCypher](https://github.com/nucypher) is a decentralised Key-Management System (KMS) and cryptographic access control layer for DApps 
encrypting each episode/frame/scene of the stream with a random Ephemeral DEcryption Key (EDEK) both for publishing via 
open transports like public RTSP endpoints, HTTPs streamers, Storage Buckets, IPFS or swarm URIs. 

To decrypt the stream, Subscriber pays for the content (deposits given amount of tokens or native Ethers to the contract) 
and their Ethereum public key gets access to the stream for given time/episodes. The special decentralized service 
"Ursulas" delegates decryption rights for the Subscriber converting common EDEK to Subscriber's individual EDEK' key and 
encrypts it with Subscriber public key.

This example relies on the decentralised self-incentivised Ursula network to implement the Global content sharing 
policies and implement key Re-encyption process.

The subscriber now can decrypt the individual EDEK' with its private Ethereum key then the episodes can be decrypted with
individual EDEK'.

### Artifacts
ddrm.py library implements a set of abstractions:
* RawStream made of RawEpisodes. Kept in secrect by the author, never exposed publicly
* ProtectedStream 
* ProtectedEpisodes with granular access-control (grant) method
* StreamPlayer - subscriber's device or program which fetches and decodes the stream.

[ddrm.py](ddrm.py) is concentrated purely on interaction between Subscriber and Author (actions 1-3, 8-4 from the list below) playing
the media stream. As underlying Ursula network we were recommended to use ["Finnegan's Wake" federated example](https://github.com/nucypher/nucypher/tree/federated)
which illustrates the main principles of such decentralised reencryption service.

### CallFlow
Real-world call-flow of decentralised content marketplace could look like this
1. Author of the stream breaks the data into objects like episodes/scenes/frames and encrypts each chunk with random 
key EDEK. Each EDEK for each episode then gets encrypted with Author's public key.
2. The resulting set of encrypted scenes with Author-encrypted EDEKs get stored in the distributed storage (swarm/ipfs), 
cloud (AWS S3, GCP bucket) or get queued with 0mq/rabbitmq or plain UDP/tcp streams (depending on codec requirements).
 and converts its raw content into encrypted object (for streaming it should be iterable set of objects).
3. Each of the chunks gets its own policy for access control (each registered and announced over set of Ursulas)
4. Author knows URI of the encrypted set or stream endpoint and able to publish and sell access to the media.
5. Author publishes its proposal via DApp marketplace (metadata, labels, screenshots, descriptions, trailers) and declares
the price for single use playing or any kind of subscribtion policy resulting in payable Smart-contract on the network
6. The marketplace visitor sees the poster and gets interested in the content (say, blogger's live stream). It deposits
the given amount of tokens (ERC-223 or other supporting token fallback) to the contract and reports its public key.
7. Upon receiving the token contract it gets sinked to the author and access delegation event emitted on the contract.
8. The event of access delegation gets enforced into Ursulas (Subscriber joins policy). The Ursulas are the decentralised
 self-incentivised network implementing the Global search graph of policies and Re-encyption engine for access delegation.
For details of its operation see ["Finnegan's Wake" federated example](https://github.com/nucypher/nucypher/tree/federated).
9. Subscriber receives the stream URI (common for all subscribers) and starts retrieval. Thogh the decryption EDEK key is 
encrypted with Author's key, Subscriber has no way to decrypt it.
10. Subscriber requests the Ursulas network to reencrypt the EDEK for it. Regarding the Re-Encryption/Recapsulation 
principles see nuCypher [whitepaper](https://github.com/nucypher/whitepaper/blob/master/whitepaper.pdf) and reference 
implementations in their [repos](https://github.com/nucypher/).
11. Ursulas find the requested object in the global map of policies and, if found, Subscriber's player receives the 
recapsulated EDEK decryptable with its public key.
12. Upon EDEK' receival Subscriber's player decrypts copyrighted material (scene/episode/frame) and plays it.
14. Then Subscriber's player fetches the next episode and makes the same reencryption requests (9-12) until the end of 
the stream or policy expiration/revocation. To make this process smooth, tha data can be retrieved and decoded in advance
(employing standard media caching principles).
15. After revocation/expiration of the subscription (policy) the Ursula will be unable to find the Subscriber's 
reencryption public key in the map returning the error and Subscriber's player redirects to marketplace for subscribtion 
renewal. 


### Build
Builds the docker container with batteries included (the network of three Ursulas and ddrm.py illustrating subscription 
and playing flow)
```
docker build -t ddrm .
```

### Run dockerized
Output of all the components redirected to the stdout. Sorry fo the messy output, ddrm.py output marked with the keywords.
```
docker -it run ddrm
```

#### Run without docker
If you need to debug the components in isolation:
```
cd nucypher/
pipenv install --dev --three --skip-lock
pipenv shell
# in different terminals run Ursulas
cd examples 
python3 run_federated_ursula.py 3500
python3 run_federated_ursula.py 3501 3500
python3 run_federated_ursula.py 3502 3500
# run script illustrating DDRM operation
cd ..
python3 ddrm.py
```

## Related work

During the exploration of NuCypher re-encryption patterns and playing with federated "Finnegan's Wake": we 
* discovered annoying bug [unexpected kwarg 'always_be_learning' #487](https://github.com/nucypher/nucypher/issues/487) 
* fixed it with [Pull-Request #488](https://github.com/nucypher/nucypher/commit/0c83bcba95db1d832641552134d5dc889b653dac).
* [actualised "Finnegan's Wake" manual](https://github.com/nucypher/nucypher/tree/federated)
* had a good time discussing the Proxy Reencryption patterns in [Discord chat](https://discordapp.com/channels/411401661714792449/411401661714792451) 
and in [Russian facebook thread](https://www.facebook.com/kirill.varlamov.12/posts/1419317941532736)

Many thanks to brilliant nuCypher team and [Michael Egorov](https://github.com/michwill) personally.

## Authors

* [Kirill Varlamov](https://github.com/ongrid), [OnGrid Systems](https://github.com/OnGridSystems)

