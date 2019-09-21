import time
import random
import math
import sys
import gmpy2
import os

modulo = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
order  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


PG = Point(Gx,Gy)
Z = Point(0,0) # zero-point, infinite in real x,y - plane
    
def mul2(P, p = modulo):
    R = Point()
    c = 3*P.x*P.x*gmpy2.invert(2*P.y, p) % p
    R.x = (c*c-2*P.x) % p
    R.y = (c*(P.x - R.x)-P.y) % p
    return R


def addk(Pk, Qk, Nn, p = modulo):
    R = Point()
    Rk=[]
    for k in range(Nn):
        P=Pk[k]
        Q=Qk[k]
        R=add(P, Q)
        Rk.append(R)
    return Rk

def add(P, Q, p = modulo):
    R = Point()
    dx = Q.x - P.x
    dy = Q.y - P.y
    c = dy * gmpy2.invert(dx, p) % p
    R.x = (c*c - P.x - Q.x) % p
    R.y = (c*(P.x - R.x) - P.y) % p
    return R # 6 sub, 3 mul, 1 inv

def mulk(k, P = PG, p = modulo):
    if k == 0: return Z
    elif k == 1: return P
    elif (k % 2 == 0):
        return mulk(k>>1, mul2(P, p), p)
    else:
        return add(P, mulk( (k-1)>>1, mul2(P, p), p), p)

def X2Y(X, p = modulo):
    if p % 4 != 3:
        print ('prime must be 3 modulo 4')
        return 0
    X = (X**3+7)%p
    pw = (p + 1) // 4
    Y = 1
    for w in range(256):
        if (pw >> w) & 1 == 1:
            tmp = X
            for k in range(w):
                tmp = (tmp**2)%p
            Y *= tmp
            Y %= p
    return Y

def comparator(A,B,Ak,Bk):
    result = list(set(A) & set(B))
    if len(result) > 0:
        sol_kt = A.index(result[0])
        sol_kw = B.index(result[0])
        d = Ak[sol_kt] - Bk[sol_kw]
        print ('total time: %.2f sec' % (time.time()-starttime ))
        print ('SOLVED: %64X' % d + '\n')
        file = open("results.txt",'a')
        file.write(('%X'%(Ak[sol_kt] - Bk[sol_kw])) + ' - total time: %.2f sec' % (time.time()-starttime) +'\n')
        file.write("---------------\n")
        file.close()
        return True
    else:
        return False


Ptable = [PG]
for k in range(255): Ptable.append(mul2(Ptable[k]))
print ('P-table prepared')

def search():
    global solved
    s=(ka+kb)>>1
    d=(kb-ka)
    problem=int(math.log(d,2))
    DP_rarity = 1 << ((problem -  kangoo_powerT - kangoo_powerW)//2 - 2)
    hop_modulo = (problem-1 + kangoo_powerT+kangoo_powerW)//2
    T, t, dt = [], [], []
    W, w, dw = [], [], []
    PW,PT = [],[]
    buft,bufw,buftk,bufwk = [],[],[],[]
    for k in range(Nt):
        qt=s+random.randint(1,d)
        t.append(qt)
        T.append(mulk(t[k]))
        PT.append(W0)
        dt.append(0)
    for k in range(Nw):
        qw=random.randint(1, d)
        w.append(qw)
        W.append(add(W0,mulk(w[k])))
        PW.append(W0)
        dw.append(0)
    print ('tame and wild herds are prepared')
    oldtime = time.time()
    starttime = oldtime
    Hops, Hops_old = 0, 0
    t0 = time.time()
    oldtime = time.time()
    starttime = oldtime
    while (1):
        for k in range(Nt):
            Hops += 1
            ptk = T[k].x
            if ptk % (DP_rarity) == 0:
                buft.append(ptk)
                buftk.append(t[k])
            pw = ptk % hop_modulo
            dt[k] = 1 << pw
            t[k] += dt[k]
            PT[k] = Ptable[pw]
        T=addk(PT, T, Nt)
        for k in range(Nw):
            Hops += 1
            pwk = W[k].x
            if pwk % (DP_rarity) == 0:
                bufw.append(pwk)
                bufwk.append(w[k])
            pw = pwk % hop_modulo
            dw[k] = 1 << pw
            w[k] += dw[k]
            PW[k] = Ptable[pw]
        W=addk(PW, W, Nw)
        t1 = time.time()
        if (Hops % Cycle) == 0:
            hopsp = (Hops-Hops_old)/(t1-t0)
            print('Total rate %d h/s, Total W %d, Total T %d' % (hopsp,len(bufw),len(buft)))
            if comparator(buft,bufw,buftk,bufwk) :
                solved=1
                return
            t0 = t1
            Hops_old = Hops
    return
	
s=sys.argv[1]
sa = sys.argv[2]
sb = sys.argv[3]
skw = sys.argv[4]
skt = sys.argv[5]
scyc = sys.argv[6]
#
ka = int(sa, 16)
kb = int(sb, 16)
#
kangoo_powerT = int(skt, 10)
kangoo_powerW = int(skw, 10)
Cycle = 10**(int(scyc,10))

Nt = 2**kangoo_powerT
Nw = 2**kangoo_powerW
X = int(s, 16)
Y = X2Y(X % (2**256))
if Y % 2 != (X >> 256) % 2: Y = modulo - Y
X = X % (2**256)
W0 = Point(X,Y)

starttime = oldtime = time.time()
Hops = 0
random.seed()
solved=0
search()
print('Done ...')


#python kangroom.py 0348e843dc5b1bd246e6309b4924b81543d02b16c8083df973a89ce2c7eb89a10d 7496cbb87cab44f 13C96A3742F64906 3 3 6
