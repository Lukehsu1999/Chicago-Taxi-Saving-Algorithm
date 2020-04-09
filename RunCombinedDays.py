#version 5.0
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
def FeasibiltiyCheck(s, cur_C, dis, all_C, clock):
    # initialize variables
    node_eat = [9999999]*78
    todo_nodes, todo_cars, node_path  = range(1,78), cur_C[:], []
    for i in range(78):
        node_path.append([])

    # initialize node_eat
    todo_nodes.remove(s.s)
    t = True
    node_eat[s.s] = s.st
    for c in cur_C:
        if s.s in c.p and s.s != c.e:
            t = False
            todo_cars.remove(c)
            prev_n = c.p[c.p.index(s.s)+1]
            prev_eat = max(c.a[s.s][0], s.st) + dis[s.s][prev_n]
            if prev_eat >= clock:
                path = [(s.s, c.n, max(c.a[s.s][0], s.st, 0), c.a[s.s][1], 0)]
                for n in c.p[c.p.index(s.s)+1:]:
                    eat = max(prev_eat + dis[prev_n][n], c.a[n][0])
                    if node_eat[n] > eat and c.a[n][1] >= eat :
                        node_eat[n] = eat
                        path.append((n,c.n,eat,c.a[n][1], 0))
                        node_path[n] = path[:]
                    prev_eat, prev_n  = eat, n
    if t:
        s.ml = []
        return False
    while todo_nodes:
        #find the cur_node that has the smallest eat
        min_eat = 9999999+1
        cur_node = -1
        for n1 in todo_nodes:
             if node_eat[n1] < min_eat:
                min_eat = node_eat[n1]
                cur_node = n1
        #update the smallest eats of every node that is reachable from cur_node
        todo_nodes.remove(cur_node)
        for c in todo_cars: # how to prove this is todo_cars and not cur_C?
            if cur_node in c.p and cur_node!= c.e:
                todo_cars.remove(c)# does this have to put in the next if ?
                if node_eat[cur_node] <= c.a[cur_node][1]: #transfer order:  unloaing car eat <= loading car ldt
                    #loading car
                    prev_n = c.p[c.p.index(cur_node)+1]
                    prev_eat = max(c.a[cur_node][0], node_eat[cur_node]) + dis[cur_node][prev_n]
                    path = node_path[cur_node][:]
                    #update unloading car_ldt
                    (Tn, u_c, u_eat, u_ldt, t_time) = path[-1]
                    u_ldt = min(u_ldt,max(u_eat,c.a[Tn][0]))
                    path[-1] = (Tn, u_c, u_eat, u_ldt, t_time)
                    t_time +=1
                    #add laoding car on transfer point, is this necessary? YES due to the structure of UpdateTimeWindow
                    path.append((Tn, c.n, max(node_eat[Tn], c.a[Tn][0]), c.a[Tn][1], t_time))
                    for n in c.p[c.p.index(cur_node)+1:]:
                        eat = max(prev_eat + dis[prev_n][n], c.a[n][0])
                        if node_eat[n] > eat and c.a[n][1] >= eat:
                            node_eat[n] = eat
                            path.append((n,c.n,eat,c.a[n][1], t_time))
                            node_path[n] = path[:]
                            prev_eat, prev_n  = eat, n

    if node_eat[s.e] <= s.et:
        #(n,c,eat,ldt) = node_path[s.e].pop()
        #node_path[s.e].append((n,c,eat, min(s.et, all_C[c].a[n])))
        UpdateTimeWindow(node_path[s.e],all_C, dis)
        s.ml =  node_path[s.e]
        return True
    s.ml = []
    return False
def UpdateTimeWindow(sol, all_C, dis):
    affected_cars = {}
    # update late_departures for all affected_cars
    #update ldts
    prev_c = -1
    for i in sol[::-1]:
        c = all_C[i[1]]
        cur_node = i[0]
        if c != prev_c:
            next_a = {}
            for key in c.a:
                next_a[key] = c.a[key][:]
        cur_ldt = min(i[-1], next_a[cur_node][1])
        ass_b = c.p.index(cur_node)
        #update ldts
        while ass_b > -1:
            next_a[c.p[ass_b]][1] = cur_ldt - dis[c.p[ass_b]][cur_node]
            ass_b -= 1
        affected_cars[c.n] = next_a
        prev_c = c
    #update eats
    prev_c = -1
    for i in sol:
        c = all_C[i[1]]
        cur_node = i[0]
        if c != prev_c:
            next_a = {}
            for key in c.a:
                next_a[key] = c.a[key][:]
        cur_eat = max(i[2], next_a[cur_node][0])
        ass_f = c.p.index(cur_node)
        #update eats
        while ass_f < len(c.p):
            next_a[c.p[ass_f]][0] = cur_eat + dis[c.p[ass_f]][cur_node]
            ass_f += 1
        for j in next_a:
            affected_cars[c.n][j][0] = next_a[j][0]
        prev_c = c
    for ac in affected_cars:
        all_C[ac].a = affected_cars[ac]
def RunFile(file_in, portion):
    f = pickle.load(open(file_in,'rb'))
    #dis_database is a list such that dis_database[i][j] saves the shortest distance between vertex i and j
    #neighbor is a list such that neighbor[i] is a list of vertices that neighbors of vertex j
    dis = f["dis_database"]
    all_S, all_C = f['Requests'], f['Supplies']
    open(file_in,'rb').close()
    cur_sn, cur_cn = 0, 0
    cur_S, cur_C, carDensity = [], [], []
    clock, cpu_t = 0, []
    day_end = 24*60*60 # one day
    interval = 1 # take in data every second
    extreme_cases =[]
    n_feasible =0
    min_dis = 999999
    total_time = 0
    total_transfer = 0
    for i in dis:
        for j in i:
            min_dis = min(min_dis,j)
    count = 0
    while clock< day_end:
        #Delete Cars that had ended at ths time
        #print "clock time:",clock
        for i in cur_C:
            if clock >= i.a[i.p[-2]][1] - min_dis:
                cur_C.remove(i)
        #Add new Cars
        for i in all_C[cur_cn::portion]:
            if i.st == clock:
                cur_C.append(i)
                cur_cn += portion
            else:
                break
        #Add new Secondary requests
        carDensity.append(len(cur_C))
        for i in all_S[cur_sn::portion]:
            #print "we made it" ,i.st , len(cur_C)
            if i.st == clock:
                cpu_t1 = time.clock()
                feasible = FeasibiltiyCheck(i,cur_C, dis, all_C, clock)
                cpu_t2 = time.clock()
                cpu_t.append(cpu_t2 - cpu_t1)
                total_time += cpu_t[-1]
                if feasible:
                    n_feasible += 1
                    if len(i.ml)>0:
                        total_transfer += i.ml[-1][-1]
                    else:
                        print i.ml
                        print'WHAT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                if cpu_t[-1] >1:
                    extreme_cases.append(i.n)
                cur_sn += portion
            else:
                break
        count +=1
        if count ==5001:
            count =0
            print "request",i.n,"clock time", clock
        #Update time
        clock+=interval

    #save file pickle
    out_filename =  file_in[:-6] +'Finished_'+ str(portion) + file_in[-6:]
    out = open(out_filename,'wb')
    save = {'portion':portion,"total_transfer":total_transfer, "extreme_cases": extreme_cases,"n_feasible": n_feasible,"total_time":total_time,"Supplies":all_C, "Requests":all_S, "S_flex":1.2, "R_flex": 1.5, "carDensity": carDensity, "cpu_t":cpu_t}
    pickle.dump(save, out)
    out.close()
    print "saved pickle"
    #save file_in csv
    return save
