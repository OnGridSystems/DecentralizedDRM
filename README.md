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

The subscriber now can decrypt the individual EDEK' with its private Ethereum key then the episodes can be decrypted with
individual EDEK'.

### Artifacts
ddrm.py library implements a set of abstractions:
* RawStream made of RawEpisodes. Kept in secrect by the author, never exposed publicly
* ProtectedStream 
* ProtectedEpisodes with granular access-control (grant) method
* StreamPlayer - subscriber's device or program which fetches and decodes the stream.

### CallFlow
In progress

### Build
```
docker build -t ddrm .
```

### Run dockerized

```
docker -it run ddrm
```

#### Run without docker

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

