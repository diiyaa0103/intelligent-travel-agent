import streamlit as st
import heapq
from collections import deque
from math import inf

st.set_page_config(page_title='VoyageMind', page_icon='🧭', layout='wide')

# A distinct South India travel network; demonstration estimates only.
CITIES = {
    'Bengaluru': {'hotel':1800,'food':700,'theme':'City & Technology','attractions':[('Cubbon Park','Nature',0,2),('Bangalore Palace','History',300,2),('Lalbagh Botanical Garden','Nature',80,2.5),('Food Street','Food',350,2)]},
    'Mysuru': {'hotel':1500,'food':550,'theme':'Heritage','attractions':[('Mysore Palace','History',200,2.5),('Chamundi Hill','Sightseeing',0,2),('Brindavan Gardens','Nature',100,2.5),('Mysuru Food Trail','Food',300,2)]},
    'Coorg': {'hotel':1900,'food':600,'theme':'Nature & Adventure','attractions':[('Abbey Falls','Nature',50,2),('Coffee Estate Walk','Nature',250,3),('River Rafting','Adventure',900,3),('Kodava Food Experience','Food',400,2)]},
    'Ooty': {'hotel':2100,'food':650,'theme':'Hills & Nature','attractions':[('Ooty Lake','Nature',150,2),('Botanical Garden','Nature',80,2.5),('Nilgiri Mountain Railway','Adventure',700,4),('Tea Factory Visit','Sightseeing',250,2)]},
    'Chennai': {'hotel':1900,'food':700,'theme':'Coastal City','attractions':[('Marina Beach','Nature',0,2),('Fort St. George','History',100,2),('Kapaleeshwarar Temple','History',0,1.5),('Chennai Food Trail','Food',350,2)]},
    'Pondicherry': {'hotel':2200,'food':750,'theme':'Coastal & Relaxation','attractions':[('Promenade Beach','Nature',0,2),('French Quarter Walk','Sightseeing',150,2.5),('Auroville','Relaxation',100,3),('Cafe & Bakery Trail','Food',400,2)]},
    'Madurai': {'hotel':1400,'food':500,'theme':'Temple Heritage','attractions':[('Meenakshi Temple','History',0,2.5),('Nayakkar Palace','History',100,2),('Gandhi Museum','Sightseeing',50,1.5),('Madurai Food Trail','Food',300,2)]},
    'Kochi': {'hotel':2000,'food':650,'theme':'Coastal Heritage','attractions':[('Fort Kochi','History',0,2.5),('Chinese Fishing Nets','Sightseeing',0,1.5),('Kathakali Performance','Culture',500,2),('Kerala Food Experience','Food',450,2)]},
    'Munnar': {'hotel':2300,'food':650,'theme':'Tea Hills','attractions':[('Tea Museum','Sightseeing',150,2),('Tea Plantation Walk','Nature',300,3),('Eravikulam National Park','Nature',250,3),('Spice Garden Visit','Food',200,2)]},
}

# from, to, hours, fare/person, transport
EDGES = [
    ('Bengaluru','Mysuru',3,450,'Train'),('Bengaluru','Coorg',5.5,700,'Bus'),
    ('Bengaluru','Ooty',6.5,800,'Bus'),('Bengaluru','Chennai',6,900,'Train'),
    ('Mysuru','Coorg',3,400,'Bus'),('Mysuru','Ooty',4,500,'Bus'),
    ('Coorg','Ooty',4.5,600,'Car'),('Coorg','Kochi',6,850,'Bus'),
    ('Ooty','Chennai',7,900,'Bus'),('Chennai','Pondicherry',3,350,'Bus'),
    ('Chennai','Madurai',7,750,'Train'),('Pondicherry','Madurai',5.5,650,'Bus'),
    ('Madurai','Kochi',5,650,'Train'),('Madurai','Munnar',4,550,'Bus'),
    ('Kochi','Munnar',4,500,'Bus')]

GRAPH = {c:[] for c in CITIES}
for a,b,h,f,m in EDGES:
    GRAPH[a].append({'city':b,'hours':h,'fare':f,'mode':m})
    GRAPH[b].append({'city':a,'hours':h,'fare':f,'mode':m})

def nbrs(city, transport):
    return [e for e in GRAPH[city] if transport=='Any' or e['mode']==transport]

def reconstruct(parent,start,goal):
    if start==goal: return [start]
    if goal not in parent: return None
    r=[goal]
    while r[-1]!=start: r.append(parent[r[-1]])
    return r[::-1]

def bfs(start,goal,transport):
    q=deque([start]); seen={start}; parent={}; expanded=0
    while q:
        u=q.popleft(); expanded+=1
        if u==goal: return reconstruct(parent,start,goal),expanded
        for e in nbrs(u,transport):
            v=e['city']
            if v not in seen: seen.add(v); parent[v]=u; q.append(v)
    return None,expanded

def dfs(start,goal,transport):
    stack=[start]; seen=set(); parent={}; expanded=0
    while stack:
        u=stack.pop()
        if u in seen: continue
        seen.add(u); expanded+=1
        if u==goal: return reconstruct(parent,start,goal),expanded
        for e in reversed(nbrs(u,transport)):
            v=e['city']
            if v not in seen: parent[v]=u; stack.append(v)
    return None,expanded

def ucs(start,goal,transport):
    pq=[(0,start)]; best={start:0}; parent={}; expanded=0
    while pq:
        g,u=heapq.heappop(pq)
        if g!=best.get(u): continue
        expanded+=1
        if u==goal: return reconstruct(parent,start,goal),expanded
        for e in nbrs(u,transport):
            v=e['city']; ng=g+e['fare']
            if ng<best.get(v,inf): best[v]=ng; parent[v]=u; heapq.heappush(pq,(ng,v))
    return None,expanded

# Same-unit heuristic: estimated remaining fare.
H={
 ('Bengaluru','Mysuru'):450,('Bengaluru','Coorg'):700,('Bengaluru','Ooty'):800,('Bengaluru','Chennai'):900,
 ('Mysuru','Coorg'):400,('Mysuru','Ooty'):500,('Mysuru','Chennai'):850,('Mysuru','Madurai'):1150,
 ('Coorg','Ooty'):600,('Coorg','Kochi'):850,('Coorg','Munnar'):900,('Ooty','Chennai'):900,
 ('Ooty','Madurai'):1100,('Ooty','Kochi'):1200,('Ooty','Munnar'):950,('Chennai','Pondicherry'):350,
 ('Chennai','Madurai'):750,('Chennai','Kochi'):1200,('Chennai','Munnar'):1300,('Pondicherry','Madurai'):650,
 ('Pondicherry','Kochi'):1000,('Pondicherry','Munnar'):1100,('Madurai','Kochi'):650,('Madurai','Munnar'):550,
 ('Kochi','Munnar'):500}
def h(city,goal): return 0 if city==goal else H.get((city,goal),H.get((goal,city),0))

def greedy(start,goal,transport):
    pq=[(h(start,goal),start)]; seen=set(); parent={}; expanded=0
    while pq:
        _,u=heapq.heappop(pq)
        if u in seen: continue
        seen.add(u); expanded+=1
        if u==goal: return reconstruct(parent,start,goal),expanded
        for e in nbrs(u,transport):
            v=e['city']
            if v not in seen: parent[v]=u; heapq.heappush(pq,(h(v,goal),v))
    return None,expanded

def astar(start,goal,transport):
    pq=[(h(start,goal),0,start)]; best={start:0}; parent={}; expanded=0
    while pq:
        f,g,u=heapq.heappop(pq)
        if g!=best.get(u): continue
        expanded+=1
        if u==goal: return reconstruct(parent,start,goal),expanded
        for e in nbrs(u,transport):
            v=e['city']; ng=g+e['fare']
            if ng<best.get(v,inf): best[v]=ng; parent[v]=u; heapq.heappush(pq,(ng+h(v,goal),ng,v))
    return None,expanded

SEARCH={'BFS':bfs,'DFS':dfs,'UCS':ucs,'Greedy Best-First':greedy,'A*':astar}

def all_routes(start,goal,transport,max_hops=6):
    out=[]
    def walk(u,path):
        if len(path)-1>max_hops: return
        if u==goal: out.append(path.copy()); return
        for e in nbrs(u,transport):
            v=e['city']
            if v not in path: path.append(v); walk(v,path); path.pop()
    walk(start,[start]); return out

def metrics(route,travellers):
    hours=0; fare=0; legs=[]
    for a,b in zip(route,route[1:]):
        e=next(e for e in GRAPH[a] if e['city']==b)
        hours+=e['hours']; fare+=e['fare']*travellers; legs.append((a,b,e['mode'],e['hours'],e['fare']*travellers))
    return hours,fare,legs

def attractions(goal,interests,days):
    p=CITIES[goal]['attractions']
    return sorted(p,key=lambda x:(x[1] not in interests,x[2],x[0]))[:max(1,days*2)]

def evaluate(route,goal,days,travellers,budget,interests,max_time):
    hours,travel,legs=metrics(route,travellers)
    places=attractions(goal,interests,days)
    hotel=CITIES[goal]['hotel']*max(0,days-1)*travellers
    food=CITIES[goal]['food']*days*travellers
    activity=sum(p[2] for p in places)*travellers
    total=travel+hotel+food+activity
    budget_score=1 if total<=budget else max(0,1-(total-budget)/budget)
    pref=sum(p[1] in interests for p in places)/len(places) if places else 0
    simplicity=1/max(1,len(route)-1); time_score=max(0,1-hours/20)
    utility=round(100*(.45*budget_score+.30*pref+.15*simplicity+.10*time_score),2)
    return {'route':route,'hours':hours,'travel':travel,'hotel':hotel,'food':food,'activity':activity,'total':total,'utility':utility,'legs':legs,'places':places,'feasible':total<=budget and hours<=max_time}

def comparison(start,goal,transport,budget,max_time,days,travellers,interests):
    rows=[]
    for name,fn in SEARCH.items():
        route,expanded=fn(start,goal,transport)
        if route:
            p=evaluate(route,goal,days,travellers,budget,interests,max_time)
            rows.append({'Algorithm':name,'Route':' → '.join(route),'Cost (₹)':round(p['total']),'Time (h)':round(p['hours'],1),'Nodes expanded':expanded,'Feasible':'Yes' if p['feasible'] else 'No'})
    return rows

def utility_agent(start,goal,transport,budget,max_time,days,travellers,interests):
    candidates=[evaluate(r,goal,days,travellers,budget,interests,max_time) for r in all_routes(start,goal,transport)]
    candidates.sort(key=lambda p:(p['feasible'],p['utility']),reverse=True)
    return (candidates[0] if candidates else None),candidates

# ---------------- UI ----------------
st.title('🧭 VoyageMind')
st.caption('An Intelligent Travel Planning Agent — graph search + goal reasoning + utility-based itinerary selection.')

with st.sidebar:
    st.header('Travel Mission')
    start=st.selectbox('Starting location',list(CITIES))
    goal=st.selectbox('Destination',[c for c in CITIES if c!=start])
    transport=st.selectbox('Allowed transport',['Any','Bus','Train','Car'])
    budget=st.number_input('Total budget (₹)',500.0,50000.0,10000.0,500.0)
    max_time=st.number_input('Maximum travel time (hours)',1.0,50.0,15.0,1.0)
    days=st.number_input('Trip duration (days)',1,10,3,1)
    travellers=st.number_input('Travellers',1,10,2,1)
    interests=st.multiselect('Interests',['Nature','History','Adventure','Sightseeing','Food','Relaxation','Culture'],['Nature','Sightseeing'])
    mode=st.radio('Planning mode',['Compare Search Algorithms','Goal-Based Agent','Utility-Based Agent','Tourism Itinerary Planner'])
    run=st.button('Plan My Journey',type='primary',use_container_width=True)

if not run:
    c1,c2,c3=st.columns(3)
    c1.info('**Knowledge Base**\n\n9 destinations, attractions, accommodation, food and transport data.')
    c2.info('**Search Lab**\n\nBFS, DFS, UCS, Greedy Best-First and A* are implemented independently.')
    c3.info('**Agents**\n\nGoal-based and utility-based planning produce explainable decisions.')
    st.divider(); st.subheader('Travel network overview')
    st.write(f'**{len(CITIES)} locations · {len(EDGES)} undirected connections · {len(EDGES)*2} graph edges**')
    with st.expander('View knowledge base'):
        for city,d in CITIES.items():
            st.markdown(f'**{city}** — {d["theme"]} · hotel ₹{d["hotel"]:,}/night')
            st.write(', '.join(f'{x[0]} ({x[1]})' for x in d['attractions']))
    st.info('All travel costs and times are illustrative academic estimates, not live booking data.')
else:
    if start==goal: st.error('Choose different locations.'); st.stop()
    if mode=='Compare Search Algorithms':
        st.header(f'Search Lab — {start} → {goal}')
        rows=comparison(start,goal,transport,budget,max_time,days,travellers,interests)
        st.dataframe(rows,use_container_width=True,hide_index=True)
        st.subheader('How the algorithms differ')
        st.write('**BFS:** fewest edges.  **DFS:** depth-first exploration.  **UCS:** lowest accumulated fare.  **Greedy:** lowest heuristic estimate.  **A*:** lowest f(n) = g(n) + h(n).')
        astar=next((r for r in rows if r['Algorithm']=='A*'),None)
        if astar: st.success(f'A* route: {astar["Route"]} | Cost: ₹{astar["Cost (₹)"]:,} | Nodes expanded: {astar["Nodes expanded"]}')
    elif mode=='Goal-Based Agent':
        st.header(f'Goal-Based Agent — {start} → {goal}')
        alg=st.selectbox('Search strategy',['BFS','DFS','UCS','Greedy Best-First','A*'])
        route,expanded=SEARCH[alg](start,goal,transport)
        if not route: st.error('Goal cannot be reached with this transport.'); st.stop()
        p=evaluate(route,goal,days,travellers,budget,interests,max_time)
        a,b,c,d=st.columns(4); a.metric('Total',f'₹{p["total"]:,.0f}'); b.metric('Time',f'{p["hours"]:.1f} h'); c.metric('Nodes expanded',expanded); d.metric('Utility',f'{p["utility"]}/100')
        st.success(f'Goal reached: {" → ".join(route)}')
        st.write('The destination is treated as the goal state; the agent stops when the goal is reached.')
        st.subheader('Itinerary')
        for day in range(days):
            st.markdown(f'**Day {day+1}**')
            for x in p['places'][day*2:(day+1)*2]: st.write(f'- {x[0]} · {x[1]} · ₹{x[2]}/person')
    elif mode=='Utility-Based Agent':
        st.header(f'Utility-Based Agent — {start} → {goal}')
        best,candidates=utility_agent(start,goal,transport,budget,max_time,days,travellers,interests)
        if not best: st.error('No travel sequence found.'); st.stop()
        a,b,c,d=st.columns(4); a.metric('Selected cost',f'₹{best["total"]:,.0f}'); b.metric('Time',f'{best["hours"]:.1f} h'); c.metric('Utility',f'{best["utility"]}/100'); d.metric('Feasible','Yes' if best['feasible'] else 'No')
        st.success(f'Selected plan: {" → ".join(best["route"])}')
        st.subheader('Candidate route comparison')
        st.dataframe([{'Rank':i+1,'Route':' → '.join(p['route']),'Cost (₹)':round(p['total']),'Time (h)':round(p['hours'],1),'Utility':p['utility'],'Feasible':'Yes' if p['feasible'] else 'No'} for i,p in enumerate(candidates[:12])],use_container_width=True,hide_index=True)
        st.write('Utility = 45% budget fit + 30% interest match + 15% route simplicity + 10% travel-time score.')
    else:
        st.header(f'Tourism Itinerary — {start} → {goal}')
        route,expanded=astar(start,goal,transport)
        if not route: st.error('No route found.'); st.stop()
        p=evaluate(route,goal,days,travellers,budget,interests,max_time)
        a,b,c,d=st.columns(4); a.metric('Estimated total',f'₹{p["total"]:,.0f}'); b.metric('Travel time',f'{p["hours"]:.1f} h'); c.metric('Route stops',len(route)); d.metric('Utility',f'{p["utility"]}/100')
        st.success(f'Recommended route: {" → ".join(route)}')
        for day in range(days):
            st.markdown(f'**Day {day+1}**')
            if day==0: st.write('Arrive and settle in.')
            for x in p['places'][day*2:(day+1)*2]: st.write(f'- **{x[0]}** · {x[1]} · ₹{x[2]}/person · {x[3]:g} h')
            if day==days-1: st.write('Prepare for departure.')
        st.subheader('Transport legs')
        st.dataframe([{'From':a,'To':b,'Mode':m,'Hours':h,'Fare (₹)':f} for a,b,m,h,f in p['legs']],use_container_width=True,hide_index=True)

st.divider()
st.caption('VoyageMind is an academic demonstration of classical AI search and intelligent-agent decision making. Prices and durations are illustrative.')
