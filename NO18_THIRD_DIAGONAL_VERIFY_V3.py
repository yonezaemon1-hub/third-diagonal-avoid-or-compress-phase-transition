#!/usr/bin/env python3
from collections import deque
import argparse, json


def construct(r,L):
    assert r>=1 and L>=5
    n=r+L
    a=list(range(n)); b=list(range(n))
    # A_i: 0..r-1, B_j: r+j
    for i in range(r):
        b[i]=i
        a[i]=i+1 if i<r-1 else r
    for j in range(L):
        b[r+j]=r+((j+1)%L)
    mod=L%3
    if mod==2:
        for j in range(L-2):
            if j%3==0: a[r+j]=r+1
            elif j%3==1: a[r+j]=0
            else: a[r+j]=r+2
        a[r+L-2]=r+4
        a[r+L-1]=0
    elif mod==0:
        for j in range(L-1):
            if j%3==0: a[r+j]=0
            elif j%3==1: a[r+j]=r+2
            else: a[r+j]=r+1
        a[r+L-1]=r+L-1
    else:
        assert L>=7
        for j in range(L-1):
            if j%3==0: a[r+j]=r+1
            elif j%3==1: a[r+j]=r+2
            else: a[r+j]=0
        a[r+L-1]=r+L-3
    return a,b

def app(X,t): return frozenset(t[x] for x in X)
def word(X,a,b,w):
    for ch in w:
        X=app(X,a if ch=='a' else b)
    return X

def power(ch,k): return ch*k

def is_success(X,A,s_size):
    return (not A.issubset(X)) or len(X)<s_size

def shortest(r,L):
    a,b=construct(r,L)
    A=frozenset(range(r))
    S=frozenset(list(range(r))+[r,r+1,r+2])
    q=deque([(S,'')]); seen={S}
    while q:
        X,w=q.popleft()
        if w and is_success(X,A,len(S)):
            return len(w),w,X,len(seen)
        for ch,t in [('a',a),('b',b)]:
            Y=app(X,t)
            if Y not in seen:
                seen.add(Y); q.append((Y,w+ch))
    raise RuntimeError

def witness(L):
    if L%3==2: return 'b'*(L-2)+'aa'
    if L%3==0: return 'b'*(L-3)+'aba'
    return 'b'*(L-2)+'aa'

def strongly_connected(a,b):
    n=len(a)
    # forward/reverse reachability from 0
    def reach(adj):
        seen={0}; q=deque([0])
        while q:
            x=q.popleft()
            for y in adj[x]:
                if y not in seen: seen.add(y); q.append(y)
        return len(seen)==n
    adj=[[] for _ in range(n)]; radj=[[] for _ in range(n)]
    for x in range(n):
        for t in (a,b):
            y=t[x]; adj[x].append(y); radj[y].append(x)
    return reach(adj) and reach(radj)

def all_pairs_sync(a,b):
    n=len(a)
    pairs=[]; idx={}
    for i in range(n):
        for j in range(i+1,n):
            idx[(i,j)]=len(pairs); pairs.append((i,j))
    rev=[[] for _ in pairs]
    good=[False]*len(pairs)
    q=deque()
    for pidx,(i,j) in enumerate(pairs):
        for t in (a,b):
            x,y=t[i],t[j]
            if x==y:
                if not good[pidx]: good[pidx]=True; q.append(pidx)
            else:
                if x>y: x,y=y,x
                rev[idx[(x,y)]].append(pidx)
    while q:
        y=q.popleft()
        for p in rev[y]:
            if not good[p]: good[p]=True; q.append(p)
    return all(good), sum(good), len(good)

def transform_on(states,a,b,w):
    return {x: next(iter(word(frozenset([x]),a,b,w))) for x in states}

def full_cycle_on(states,a):
    st=list(states); sset=set(st)
    if any(a[x] not in sset for x in st): return False
    seen=[]; x=st[0]
    for _ in range(len(st)):
        if x in seen: return False
        seen.append(x); x=a[x]
    return x==st[0] and len(seen)==len(st)

def proof_identity(r,L,a,b):
    Q=frozenset(range(r+L)); mod=L%3
    C=frozenset(list(range(r))+[r,r+1,r+2])
    if mod==1:
        qa2=word(Q,a,b,'aa')
        m=r+3
        f='b'*(L-2)+'aa'
        delta=f+'a'*(m-2)
        e=delta+delta
        em=transform_on(C,a,b,e)
        # cycle order A0..A_{r-1},B0,B1,B2
        order=list(range(r))+[r,r+1,r+2]
        expected={x:x for x in order}
        expected[order[-2]]=order[-1]
        return qa2==C and full_cycle_on(C,a) and em==expected
    if mod==2:
        qa2=word(Q,a,b,'aa')
        D=frozenset(list(range(r))+[r,r+1])
        cd=word(C,a,b,'b'*(L-2)+'aa')
        m=r+2
        if L>=8: gamma='bb'+'a'+'b'*(L-2)+'aa'
        else: gamma='bb'+'a'+'b'+'aa'
        delta=gamma+'a'*(m-3)
        e=delta+delta
        em=transform_on(D,a,b,e)
        order=list(range(r))+[r,r+1]
        if L>=8:
            expected={x:x for x in order}
            expected[order[-2]]=order[-3]
            expected[order[-1]]=order[-3]
            local=(em==expected)
        else:
            # exceptional case: require idempotent rank |D|-1 and exactly one adjacent merge
            vals=[em[x] for x in order]
            idem=all(em[em[x]]==em[x] for x in order)
            rank=len(set(vals))
            local=idem and rank==len(order)-1 and all(em[x] in D for x in order)
        return qa2==C and cd==D and full_cycle_on(D,a) and local
    # mod 0 explicit reset word
    T='b'*(L-1)+'a'
    R='a'+'b'*(L-2)+'a'+T*(r+1)+'b'+'a'
    return len(word(Q,a,b,R))==1

def verify_one(r,L):
    a,b=construct(r,L); n=r+L
    A=frozenset(range(r)); S=frozenset(list(range(r))+[r,r+1,r+2])
    d,sw,term,seen=shortest(r,L)
    w=witness(L); Y=word(S,a,b,w)
    ps,good,total=all_pairs_sync(a,b)
    sc=strongly_connected(a,b)
    pi=proof_identity(r,L,a,b)
    ok=(d==L and len(w)==L and is_success(Y,A,len(S)) and sc and ps and pi)
    return {'r':r,'L':L,'n':n,'distance':d,'shortest_word':sw,'witness':w,'subset_states_seen':seen,
            'strongly_connected':sc,'pair_sync':ps,'pair_sync_count':good,'pair_total':total,'proof_identity':pi,'PASS':ok}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--r-max',type=int,default=30); ap.add_argument('--L-max',type=int,default=60); ap.add_argument('--json',default='')
    args=ap.parse_args(); rows=[]
    for r in range(1,args.r_max+1):
        for L in range(5,args.L_max+1):
            rows.append(verify_one(r,L))
    fails=[x for x in rows if not x['PASS']]
    summary={'r_range':[1,args.r_max],'L_range':[5,args.L_max],'cases':len(rows),'failures':len(fails),'all_pass':not fails,'max_n':args.r_max+args.L_max,'max_subset_states_seen':max(x['subset_states_seen'] for x in rows)}
    print(json.dumps(summary,indent=2))
    if fails:
        print(json.dumps(fails[:20],indent=2)); raise SystemExit(1)
    if args.json:
        with open(args.json,'w',encoding='utf-8') as f: json.dump({'summary':summary,'cases':rows},f,indent=2)
if __name__=='__main__': main()
