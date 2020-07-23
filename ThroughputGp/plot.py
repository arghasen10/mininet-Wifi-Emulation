from matplotlib import pyplot as plt
import csv


def plot_graph(filename):
    aps, throughput, distance, times, handovers = ([] for i in range(5))
    flag=0
    for i in range(7):
        ap, thpt, dist, time, handover = ([] for i in range(5))
        with open(filename[i], 'r') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                ap.append(row[1])
                thpt.append(row[2])
                dist.append(row[3])
                time.append(row[4])
                handover.append(row[-1])
        aps.append(ap[1:])
        thpt = [float(item) for item in thpt[1:]]
        dist = [float(item) for item in dist[1:]]
        time = [float(item) for item in time[1:]]
        handover = handover[1:]
        throughput.append(thpt)
        distance.append(dist)
        times.append(time)
        handovers.append(handover)
        plt.plot(times[i], throughput[i], label='sta%s' % (i+1))
        plt.ylabel('Throughput(Mbps)')
        plt.xlabel('time(sec)')
        plt.title('Throughput vs time')
        plt.legend(loc='best')
        for j, ho in enumerate(handovers[i]):
            if ho == '1':
                if j == 0:
                    continue
                if flag == 0:
                    plt.plot(times[i][j], throughput[i][j], 'ro', label='Handover')
                    flag = 1
                plt.plot(times[i][j], throughput[i][j], 'ro')

    plt.show()


if __name__ == '__main__':
    file1 = "output90654_20200723sta1.csv"
    file2 = "output90654_20200723sta2.csv"
    file3 = "output90654_20200723sta3.csv"
    file4 = "output90654_20200723sta4.csv"
    file5 = "output90654_20200723sta5.csv"
    file6 = "output90654_20200723sta6.csv"
    file7 = "output90654_20200723sta7.csv"
    filename = [file1, file2, file3, file4, file5, file6, file7]
    plot_graph(filename)

