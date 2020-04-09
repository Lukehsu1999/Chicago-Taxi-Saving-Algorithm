#version 3.0
from random import randrange
import csv
import json
import math
#Create neighbor
f_in = open("ChicagoCommunityProperties.csv","r")
in_rows = csv.reader(f_in, delimiter=',')
neighbor = []
for i in range(78):
    neighbor.append([])

for i in in_rows:
    z = i[3].split(',')
    for j in z:
        neighbor[int(i[0])].append(int(j))
f_in.close()

# Take created dis_database and path_database
import pickle
f = pickle.load(open("ChicagoCommunityAreas_path_dis_database.picke",'rb'))
#dis_database is a list such that dis_database[i][j] saves the shortest distance between vertex i and j
#path_database is a list such that path_database[i][j] saves the shortest path between vertex i and j
dis_database, path_database = f["dis_database"], f["path_database"]
open("ChicagoCommunityAreas_path_dis_database.picke",'rb').close()


#create Supply and Requests
import csv
def CombineDays():#Generate the supplies and requests for everyday between day_start and day_end
    file_names =[]
    for i in range(3,29,7):
        file_name = "ChicagoTaxi2014\RawData\day%d.csv" %i
        file_names.append(file_name)
    S_flex = 1.2
    R_flex = 1.5
    Generator(file_names,S_flex,R_flex) #file_name, S_flex, R_flex
def Generator(file_names,S_flex,R_flex):
    S_R_ratio = 2
    time= 0
    a = 0
    TempSupplies = [ ]
    TempRequests = [ ]
    count = 0
    for file_name in file_names:
        f_in = open(file_name,"rb")
        in_rows = csv.reader(f_in, delimiter=',')
        for i in in_rows:
            if i[0] !="pickup_community_area" and i[0]!=i[1]:
                count+=1
                s, e = int(i[0]), int(i[1])
                st = int(i[2])*60+randrange(60*15)#since the Chicago dataset rounds the time to the nearest 15 minutes, I will reverse it to seconds
                et = int(math.ceil(st + dis_database[s][e]*S_flex))
                time += dis_database[s][e]
                a+=1
                if a > S_R_ratio:
                    a = 0
                    et = int(math.ceil(st + dis_database[s][e]*R_flex))
                    TempRequests.append((st,et,s,e))
                else:
                    TempSupplies.append((st,et,s,e))
    TempSupplies.sort()
    TempRequests.sort()

    class Supply:
        def __init__(self,number,start,end,stime, etime, path, assigments):
            self.n = number # an integer
            self.s = start #  a vertex
            self.e = end # a vertex
            self.st = stime # a tuple of two integers
            self.et = etime
            self.p = path
            self.a = assigments
    class Request:
        def __init__ (self,number,start,end,stime, etime, volume, path, matchlist):
            self.n = number # an integer
            self.s = start #  a vertex
            self.e = end # a vertex
            self.st = stime # a tuple of two integers
            self.et = etime
            self.v = volume
            self.p = path
            self.ml = matchlist
    Supplies = []
    Requests = []
    rn, sn = 0,0

    for i in TempSupplies:
        assignments = {}
        for v in path_database[i[2]][i[3]]:
            assignments[v] = [i[0]+dis_database[i[2]][v], i[1]-dis_database[v][i[3]]]
        Supplies.append(Supply(sn,i[2],i[3],i[0],i[1],path_database[i[2]][i[3]],assignments))
        sn+=1
    for i in TempRequests:
        path = []
        for v in path_database[i[2]][i[3]]:
            path.append((v,i[0]+dis_database[i[2]][v], i[1]-dis_database[v][i[3]]))
        Requests.append(Request(rn,i[2],i[3],i[0],i[1],1,[],path))
        rn+=1

    #save file

    out_filename = 'CombineDays.picke'
    out = open(out_filename,'wb')
    save = {"dis_database":dis_database,"Supplies":Supplies, "Requests":Requests, "S_flex":S_flex, "R_flex": R_flex}
    pickle.dump(save, out)
    out.close()

    #savefile Txt
    out = open('CombineDays.txt','w')
    out.write("Numcases %d\n"%(sn+rn))
    out.write("suppy to request ratio %d\n"%S_R_ratio)
    out.write("Supply FLexibility %d\n"%S_flex)
    out.write("Request FLexibility %d\n"%R_flex)
    out.write("\n")
    out.write("%d Secondary Requests(index, start, end, start time, end time)\n"%sn)
    for i in Supplies:
        line =  repr(i.n).ljust(6) + repr(i.s).ljust(3) + repr(i.e).ljust(3) + repr(i.st).ljust(6) + repr(i.et).ljust(6) +'\n'
        out.write(line)

    out.write("%d Secondary Requests(index, start, end, start time, end time)\n"%rn)
    for i in Requests:
        line =  repr(i.n).ljust(6) + repr(i.s).ljust(3) + repr(i.e).ljust(3) + repr(i.st).ljust(6) + repr(i.et).ljust(6) +'\n'
        out.write(line)
    out.close()
    print "processed"

CombineDays()
