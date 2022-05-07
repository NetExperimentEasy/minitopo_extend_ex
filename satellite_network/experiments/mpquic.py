from core.experiment import Experiment, ExperimentParameter
import logging
import os


class PQUICParameter(ExperimentParameter):
    PLUGINS = "pquicPlugins"
    CLIENT_PLUGINS = "pquicClientPlugins"
    SERVER_PLUGINS = "pquicServerPlugins"
    SIZE = "pquicSize"

    def __init__(self, experiment_parameter_filename):
        super(PQUICParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            PQUICParameter.PLUGINS: "",
            PQUICParameter.CLIENT_PLUGINS: "",
            PQUICParameter.SERVER_PLUGINS: "",
            PQUICParameter.SIZE: 10240000,
        })


class MPQUIC(Experiment):
    NAME = "mpquic"
    PARAMETER_CLASS = PQUICParameter

    # BIN = "~/pquic/picoquicdemo"
    # CERT_FILE = "~/pquic/certs/cert.pem"
    # KEY_FILE = "~/pquic/certs/key.pem"
    BIN = "/home/seclee/NetExmHub/pquic/picoquicdemo"
    CERT_FILE = "/home/seclee/NetExmHub/pquic/certs/cert.pem"
    KEY_FILE = "/home/seclee/NetExmHub/pquic/certs/key.pem"
    SERVER_LOG = "mppquic_server.log"
    CLIENT_LOG = "mppquic_client.log"
    SERVER_DIR = "/home/seclee/NetExmHub/experiment/satellite_mpquic/SERVER_DIR/"
    RECEIVED_DIR = "/home/seclee/NetExmHub/experiment/satellite_mpquic/RECEIVED_DIR/"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super().__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        super().load_parameters()
        self.plugins = self.experiment_parameter.get(PQUICParameter.PLUGINS)
        self.client_plugins = self.experiment_parameter.get(PQUICParameter.CLIENT_PLUGINS)
        self.server_plugins = self.experiment_parameter.get(PQUICParameter.SERVER_PLUGINS)
        self.size = int(self.experiment_parameter.get(PQUICParameter.SIZE))

    def prepare(self):
        super().prepare()
        self.topo.command_to(self.topo_config.client, "rm {}".format(MPQUIC.CLIENT_LOG))
        self.topo.command_to(self.topo_config.server, "rm {}".format(MPQUIC.SERVER_LOG))

    def get_plugin_cmd(self, client=False):
        device_plugins = self.client_plugins if client else self.server_plugins
        device_plugins = self.plugins if len(device_plugins) == 0 else device_plugins
        if len(device_plugins) == 0:
            return ""

        plugins = device_plugins.split(",")
        return " ".join([" -P {} ".format(p) for p in plugins])

    def get_pquic_server_cmd(self):
        s = "{} {} -c {} -k {} &> {} &".format(MPQUIC.BIN, self.get_plugin_cmd(),
            MPQUIC.CERT_FILE, MPQUIC.KEY_FILE, MPQUIC.SERVER_LOG)
        # s = "{} {} -c {} -k {} -w {} &> {} &".format(MPQUIC.BIN, self.get_plugin_cmd(),
        #     MPQUIC.CERT_FILE, MPQUIC.KEY_FILE, MPQUIC.SERVER_DIR, MPQUIC.SERVER_LOG)
        logging.info(s)
        return s

    def get_pquic_client_cmd(self):
        # s = "{} {} -o {} -4 -G {} {} 4443 &> {}".format(MPQUIC.BIN, self.get_plugin_cmd(client=True), MPQUIC.RECEIVED_DIR, self.size,
        #     self.topo_config.get_server_ip(), MPQUIC.CLIENT_LOG)
        s = "{} {} -4 -G {} {} 4443 &> {}".format(MPQUIC.BIN, self.get_plugin_cmd(client=True), self.size,
            self.topo_config.get_server_ip(), MPQUIC.CLIENT_LOG)
        logging.info(s)
        return s

    def clean(self):
        super().clean()

    def run(self):
        
        self.topo.command_to(self.topo_config.router, "tcpdump -i any -w router.pcap &")
        # First run main mpquic servers
        cmd = self.get_pquic_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)


        logging.info("This experiment last about 1 minute. Please wait...")

        # 获取节点信息
        cmd = "nodes"
        logging.info(self.topo_config.clients)
        logging.info(self.topo_config.servers)
        cmd = "echo client1 {}, server1 {}".format(self.topo_config.clients[1], self.topo_config.get_server_ip(interface_index=1))
        self.topo.command_to(self.topo_config.clients[1], cmd)
        cmd = "echo client2 {}, server2 {}".format(self.topo_config.clients[2], self.topo_config.get_server_ip(interface_index=2))
        self.topo.command_to(self.topo_config.clients[2], cmd)
        # 看一下所有的ip状态
        # cmd = "echo client {}".format(self.topo_config.topo.c2r_links[0])
        # result = self.topo.command_to(self.topo_config.topo.c2r_links[0].bs1, cmd)
        logging.info(self.topo_config.topo.c2r_links[0].bs1)
        logging.info(self.topo_config.topo.c2r_links[0].bs2)
        
        # 测试TC
        # TC是在端模拟延迟，链路并没有改变
        # result = self.topo.command_to(self.topo_config.client, 'tc qdisc show')
        # logging.info(result)
        # result = self.topo.command_to(self.topo_config.clients[1], 'tc qdisc show')
        # logging.info(result)
        # result = self.topo.command_to(self.topo_config.clients[1], 'tc qdisc add dev Client_1-eth0 root netem delay 100ms 10ms')
        # logging.info(result)
        # result = self.topo.command_to(self.topo_config.clients[2], 'tc qdisc show')
        # logging.info(result)
        # result = self.topo.command_to(self.topo_config.clients[2], 'tc qdisc add dev Client_2-eth0 root netem delay 200ms 20ms')
        # logging.info(result)

        # 所有客户端同步，运行TC脚本，改变延迟的mean和jittor
        mean = 500
        jittor = 10
        # for host in self.topo_config.clients[:1]:
        path = '/home/seclee/NetExmHub/experiment/satellite_mpquic'
        # TC 设置的是单向延迟
        # 手动模拟的链路波动:设置客户端的方法
        # self.topo.command_to(self.topo_config.client, f'python /home/seclee/NetExmHub/experiment/satellite_mpquic/tc.py -client={self.topo_config.client}-eth0 -delay={mean} -jittor={jittor} &')
        # self.topo.command_to(self.topo_config.client, f'python /home/seclee/NetExmHub/experiment/satellite_mpquic/tc.py -client={self.topo_config.client}-eth1 -delay={mean-100} -jittor={jittor+40} &')
        # self.topo.command_to(self.topo_config.clients[1], f'python /home/seclee/NetExmHub/experiment/satellite_mpquic/tc.py -client={self.topo_config.clients[1]}-eth0 -delay={mean} -jittor={jittor} &')
        # self.topo.command_to(self.topo_config.clients[2], f'python /home/seclee/NetExmHub/experiment/satellite_mpquic/tc.py -client={self.topo_config.clients[2]}-eth0 -delay={mean-100} -jittor={jittor+40} &')

        # self.topo.command_to(self.topo_config.topo.c2r_links[0].bs1, f'python {path}/tc.py -client={self.topo_config.topo.c2r_links[0].bs1}-eth2 -delay={mean} -jittor={jittor} &')
        # self.topo.command_to(self.topo_config.topo.c2r_links[0].bs2, f'python {path}/tc.py -client={self.topo_config.topo.c2r_links[0].bs2}-eth1 -delay={mean-100} -jittor={jittor+40} &')
        # self.topo.command_to(self.topo_config.topo.c2r_links[1].bs1, f'python {path}/tc.py -client={self.topo_config.topo.c2r_links[1].bs1}-eth2 -delay={mean} -jittor={jittor} &')
        # self.topo.command_to(self.topo_config.topo.c2r_links[1].bs2, f'python {path}/tc.py -client={self.topo_config.topo.c2r_links[1].bs2}-eth1 -delay={mean-100} -jittor={jittor+40} &')

        # 卫星数据链路波动:设置客户端的方法
        # self.topo.command_to(self.topo_config.client, f'python {path}/sate_rtt.py -client={self.topo_config.client}-eth0 -line=1 &')
        # self.topo.command_to(self.topo_config.client, f'python {path}/sate_rtt.py -client={self.topo_config.client}-eth1 -line=2 &')
        # self.topo.command_to(self.topo_config.clients[1], f'python {path}/sate_rtt.py -client={self.topo_config.clients[1]}-eth0 -line=1 &')
        # self.topo.command_to(self.topo_config.clients[2], f'python {path}/sate_rtt.py -client={self.topo_config.clients[2]}-eth0 -line=2 &')

        # 卫星数据链路波动:修改瓶颈链路方法
        self.topo.command_to(self.topo_config.topo.c2r_links[0].bs1, f'python {path}/sate_rtt.py -client=bs_c2r_0_1-eth2 -line=1 &')
        self.topo.command_to(self.topo_config.topo.c2r_links[0].bs2, f'python {path}/sate_rtt.py -client=bs_c2r_0_2-eth1 -line=1 &')
        self.topo.command_to(self.topo_config.topo.c2r_links[1].bs1, f'python {path}/sate_rtt.py -client=bs_c2r_1_1-eth2 -line=2 &')
        self.topo.command_to(self.topo_config.topo.c2r_links[1].bs2, f'python {path}/sate_rtt.py -client=bs_c2r_1_2-eth1 -line=2 &')

        # 开启iperf
        # self.topo.command_to(self.topo_config.servers[1], f'iperf -s -u >> {path}/minitopo/output/iperfs1.txt &')
        # self.topo.command_to(self.topo_config.servers[2], f'iperf -s -u >> {path}/minitopo/output/iperfs2.txt &')
        # self.topo.command_to(self.topo_config.clients[1], f'iperf -c {self.topo_config.get_server_ip(interface_index=1)} -u -b 5m -i 5 -t 500 >> {path}/minitopo/output/iperfc1.txt &')
        # self.topo.command_to(self.topo_config.clients[2], f'iperf -c {self.topo_config.get_server_ip(interface_index=2)} -u -b 5m -i 5 -t 500 >> {path}/minitopo/output/iperfc2.txt &')
        # 完全阻塞设置 200m
        self.topo.command_to(self.topo_config.servers[1], f'iperf -s -u >> {path}/minitopo/output/iperfs1.txt &')
        self.topo.command_to(self.topo_config.servers[2], f'iperf -s -u >> {path}/minitopo/output/iperfs2.txt &')
        self.topo.command_to(self.topo_config.clients[1], f'iperf -c {self.topo_config.get_server_ip(interface_index=1)} -u -b 200m -i 5 -t 500 >> {path}/minitopo/output/iperfc1.txt &')
        self.topo.command_to(self.topo_config.clients[2], f'iperf -c {self.topo_config.get_server_ip(interface_index=2)} -u -b 200m -i 5 -t 500 >> {path}/minitopo/output/iperfc2.txt &')


        # client1 ping server1
        self.topo.command_to(self.topo_config.clients[1], 'python {}/ping_t.py -ip={} -name=pinglog1-1.log&'.format(path, self.topo_config.get_server_ip(interface_index=1)))
        # client2 ping server2
        self.topo.command_to(self.topo_config.clients[2], 'python {}/ping_t.py -ip={} -name=pinglog2-2.log&'.format(path, self.topo_config.get_server_ip(interface_index=2)))
        # client0 ping server0
        self.topo.command_to(self.topo_config.client, 'python {}/ping_t.py -ip={} -name=pinglog0-0.log&'.format(path, self.topo_config.get_server_ip()))
        # client0 ping server1
        self.topo.command_to(self.topo_config.client, 'python {}/ping_t.py -ip={} -name=pinglog0-1.log&'.format(path, self.topo_config.get_server_ip(interface_index=1)))
        # client0 ping server2
        self.topo.command_to(self.topo_config.client, 'python {}/ping_t.py -ip={} -name=pinglog0-2.log&'.format(path, self.topo_config.get_server_ip(interface_index=2)))
        # result = self.topo.command_to(self.topo_config.client, 'ping {} -c 6'.format(self.topo_config.get_server_ip()))
        # logging.info(result)
        
        # 客户端连接服务端
        # self.topo.command_to(self.topo_config.client, "sleep 2")

        # 接受文件
        # cmd = self.get_pquic_client_cmd()
        # self.topo.command_to(self.topo_config.client, cmd)
        # self.topo.command_to(self.topo_config.client, cmd)
        # self.topo.command_to(self.topo_config.client, cmd)
        # self.topo.command_to(self.topo_config.client, cmd)
        # self.topo.command_to(self.topo_config.client, cmd)
        # self.topo.command_to(self.topo_config.client, cmd)
        # self.topo.command_to(self.topo_config.client, cmd)


        self.topo.command_to(self.topo_config.client, "sleep 1500")

        # 当前试验 ，完全阻塞的iperf 无多路径任务
