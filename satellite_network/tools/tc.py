# tc qdisc add dev Client_2-eth0 root netem delay 200ms 20ms
import os
import argparse
import time

def set_tc(client, delay, jittor):
    print(client, delay, jittor)
    os.system(f'tc qdisc del dev {client} root')
    os.system(f'tc qdisc add dev {client} root netem delay {delay}ms {jittor}ms')

def fn(mean):
    nowstamp = time.mktime(time.localtime())
    add = 5*(int(nowstamp%100)-50)
    return mean+add

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="Input client interface:client, mean of delay:delay, jittor of delay:jittor")
    parse.add_argument("-client", type=str, help="interface name of the client")
    parse.add_argument("-delay", type=int, help="mean of delay: must bigger than 500")
    parse.add_argument("-jittor", type=int, help="jittor of delay")

    args = parse.parse_args()

    while True:
        time.sleep(2)
        set_tc(args.client, fn(args.delay), args.jittor)
    