# usage

## experiments dir
mpquic.py:<br>
注册了一个动态网络试验<br>
把该文件放到 minitopo 项目对应 experiments 目录

## exper dir
试验目录<br>
#### minitopo
cd 到output目录进行试验
```
mprun -t ../topos/topo_2paths -x ../exams/xp_mpquic_rtt
```

## tools dir
mpquic.py实验中用到的脚本<br>
注意修改mpquic中这些脚本的绝对地址

## convert dir
数据处理脚本<br>
根据卫星路径节点数据和实时距离矩阵计算传播路径,rtt.csv