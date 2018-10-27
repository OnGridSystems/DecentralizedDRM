cd nucypher/examples
rm -rf examples-runtime-cruft
mkdir examples-runtime-cruft
# run seed node in background
bash -c "while sleep 1; do python3 run_federated_ursula.py 3500; done" &
sleep 5
bash -c "while sleep 1; do python3 run_federated_ursula.py 3501 3500; done" &
sleep 5
bash -c "while sleep 1; do python3 run_federated_ursula.py 3502 3500; done" &
sleep 5
cd ../..
while sleep 1; do python3 ddrm.py; done