import argparse
import subprocess

def ping_a_new_thread(ip, filename):
    # subprocess.call([f"ping {ip} -i 5 > ./not/{filename} &"],shell=True)
    # subprocess.call([f"ping {ip} -i 5 > ./have/{filename} &"],shell=True)
    subprocess.call([f"ping {ip} -i 5 > ./iperfall/{filename} &"],shell=True)

parse = argparse.ArgumentParser(description="ping_a_new_thread")
parse.add_argument("-ip", type=str, help="ip")
parse.add_argument("-name", type=str, help="filename")
args = parse.parse_args()
ping_a_new_thread(args.ip, args.name)


# 理论传播试验，计算得到的excel表格
# 两条链路有iperf，各5m/s，ping时延
# client->server,多路径传输文件，iperf5m/s,ping时延