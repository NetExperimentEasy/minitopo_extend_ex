import csv
import argparse
import os
import time

path = '/home/seclee/NetExmHub/experiment/satellite_mpquic'

def set_tc(client, delay, jittor):
    # 只需要修改和delay有关的参数
    # print(client, delay, jittor)
    os.system(f'tc qdisc del dev {client} root')
    os.system(f'tc qdisc add dev {client} root netem delay {delay}ms {jittor}ms')
    # os.system(f'tc qdisc del dev {client} ingress')
    # os.system(f'tc qdisc add dev {client} root handle 10: netem  delay {delay}ms {jittor}ms limit 50000')

def fn(rtt_list):
    nowstamp = time.mktime(time.localtime())
    return rtt_list[int(nowstamp%4000)]

def load_rtt():
    with open(f'{path}/srtt.csv', 'r') as f:
        data = csv.reader(f)
        rtt1 = []
        rtt2 = []
        for row in data:
            rtt1.append(row[0])
            rtt2.append(row[1])
    return rtt1, rtt2

def fn1(mean):
    nowstamp = time.mktime(time.localtime())
    add = 5*(int(nowstamp%100)-50)
    return mean+add

if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="Input client interface:client, mean of delay:delay, jittor of delay:jittor")
    parse.add_argument("-client", type=str, help="interface name of the client")
    parse.add_argument("-line", type=int, help="which line, 1 ? 2")

    args = parse.parse_args()

    rtt_list1, rtt_list2 = load_rtt()
    
    # TC 设置的是单向延迟
    i=0
    while True:
        if args.line == 1:
            delay = rtt_list1[i]
        else:
            delay = rtt_list2[i]
        print(delay)
        set_tc(args.client, delay, 0) 
        time.sleep(4.9)
        i += 5


