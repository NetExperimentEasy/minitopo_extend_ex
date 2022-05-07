import csv

def get_distance(line, time):
    """
    line:['1','3','3','10','10','2']
    """
    with open(f'./range/range{time}.csv', newline='') as f:
        data =list(i for i in csv.reader(f))
        # print(data[0][13])    # 数据没有问题
        # print(float(data[0][13]))
        distance = 0
        for i,j in zip(line[::2],line[1::2]):
            distance += float(data[int(i)-1][int(j)-1])
    return distance

def get_rtt(line, time):
    c = 299792.458
    distance = get_distance(line, time)
    # print(distance)
    return distance/c



if __name__ == "__main__":
    with open('Data.txt','r') as f:
        readtag = True
        time = 0
        with open('srtt.csv','w') as w:
            write = csv.writer(w)
            while readtag:
                line = f.readline()
                if not line:
                    readtag = False
                splitedline = line.strip('\n').split(' 2 ')
                if splitedline == ['']:
                    continue
                line1, line2 = (splitedline[0]+' 2').split(' '), splitedline[1].split(' ')
                print(line1, '|', line2)
                print(time)
                rtt1 = get_rtt(line1, time)
                rtt2 = get_rtt(line2, time)
                time += 1
                write.writerow([rtt1, rtt2])


