FROM python:3.7.1
RUN pip install pipenv
#RUN pip3 install apistar==0.5.42 sha3 py-solc maya eth_utils twisted web3 eth_tester appdirs pyOpenSSL hendrix kademlia sqlalchemy
#RUN git clone https://github.com/nucypher/constantSorrow.git
#RUN cd constantSorrow && pip3 install .
#RUN git clone https://github.com/nucypher/pyUmbral.git
#RUN cd pyUmbral && git checkout tags/v0.1.0-alpha.4 && pip3 install .
ADD nucypher /nucypher
RUN cd nucypher && pipenv install --dev --three --skip-lock --system
RUN cd nucypher && pip3 install -e .
ADD entrypoint.sh /entrypoint.sh
ADD ddrm.py /ddrm.py
CMD /entrypoint.sh
