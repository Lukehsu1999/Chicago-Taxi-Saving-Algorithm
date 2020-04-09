import pickle
import time
import csv
class Supply:
    def __init__ (self,number,start,end,stime, etime, path, capacity, assignments):
        self.n = number # an integer
        self.s = start #  a vertex
        self.e = end # a vertex
        self.st = stime # a tuple of two integers
        self.et = etime
        self.p = path
        self.c = capacity # the available capacity
        self.a = assignments
class Request:
    def __init__ (self,number,start,end,stime, etime, volume , matchlist):
        self.n = number # an integer
        self.s = start #  a vertex
        self.e = end # a vertex
        self.st = stime # a tuple of two integers
        self.et = etime
        self.v = volume
        self.ml = matchlist

csv_out = open('carDensity.csv',"wb")
out_rows = csv.writer(csv_out)

for i in range(1,2):
    out_rows.writerow(["day%d"%i])
    out_rows.writerow([" ","time","NumAvailableCar"])
    for x in range(1,2):
        S_flex = 1+x/10.0
        for y in range(1,2):
            R_flex = 1+y/10.0
            tag = "_"+str(S_flex)+"_"+str(R_flex)
            file_name = "ChicagoTaxi2014\Finished_day%d"%i + tag + '.picke'
            result = pickle.load(open(file_name,'rb'))
            open(file_name,'rb').close()
            #save to csv
            R = result['Requests']
            feasible_time = []
            for r in R:
                if (len(r.ml) > 0:
                    feasible_time.append((r.st+r.et)/2)
                    if r.ml[-1][-1] >0:

            print result.keys()
            print S_flex,R_flex,"result updated in csv"
            print
csv_out.close()
