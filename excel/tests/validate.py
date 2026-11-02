"""Run independent mechanics checks and verify recalculated Excel values.
Usage: python excel/tests/validate.py <recalculated.xlsx> [label]
"""
import sys
from pathlib import Path
import json
import numpy as np
from openpyxl import load_workbook
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from frame import solve, local_stiffness, consistent, rotation

RESULTS=[]

def check(name,actual,expected,rtol=1e-7,atol=1e-6):
    a=np.asarray(actual,dtype=float);e=np.asarray(expected,dtype=float)
    delta=float(np.max(np.abs(a-e))) if a.size else 0
    passed=bool(np.allclose(a,e,rtol=rtol,atol=atol))
    RESULTS.append({'name':name,'passed':passed,'maximum_absolute_difference':delta,'rtol':rtol,'atol':atol,
                    'expected':e.tolist() if e.size<15 else 'full numeric reference in frame.solve',
                    'actual':a.tolist() if a.size<15 else 'full workbook vector/matrix compared'})
    if not passed:raise AssertionError((name,delta,a,e))


def analytical():
    l=3000.;e=11000.;g=690.;b=45.;h=145.;a=b*h;iy=b*h**3/12;iz=h*b**3/12;j=1e6
    k=local_stiffness(l,e,g,a,iy,iz,j)
    check('symmetric element stiffness',k,k.T)
    check('rigid translation has zero strain',k@np.array([1,2,3,0,0,0]*2),np.zeros(12),atol=1e-7)
    free=np.arange(6,12)
    def response(f):
        u=np.zeros(12);u[free]=np.linalg.solve(k[np.ix_(free,free)],f[free]);return u,k@u-f
    f=np.zeros(12);f[8]=-1000
    u,r=response(f)
    check('cantilever tip force deflection',u[8],-1000*l**3/(3*e*iy))
    check('cantilever tip force reactions',[r[2],r[4]],[1000,-1000*l])
    f=consistent([0,0,-.5],l);u,r=response(f)
    check('cantilever uniform load deflection',u[8],-.5*l**4/(8*e*iy))
    check('cantilever uniform load reactions',[r[2],r[4]],[.5*l,-.5*l*l/2])
    f=np.zeros(12);f[6]=1000;u,r=response(f)
    check('axial extension',u[6],1000*l/(e*a))
    f=np.zeros(12);f[9]=1000000;u,r=response(f)
    check('torsional rotation',u[9],1000000*l/(g*j))
    # Simply supported under qy, only end bending rotations free. Midspan exact particular solution.
    ids=[5,11];q=.5;f=consistent([0,q,0],l);u=np.zeros(12);u[ids]=np.linalg.solve(k[np.ix_(ids,ids)],f[ids])
    vmid=l*(.125*u[5]-.125*u[11])+q*l**4*.0625/(24*e*iz)
    check('simply supported exact midspan deflection',vmid,5*q*l**4/(384*e*iz))
    for direction in [([0,0,0],[0,0,1]),([0,0,0],[2,3,4]),([0,0,0],[1,0,0])]:
        ll,rr,tt=rotation(*direction);check('orthonormal coordinate transformation',rr@rr.T,np.eye(3))


def validate(path,label='baseline'):
    w=load_workbook(path,data_only=True)
    errors=[(s.title,c.coordinate,c.value) for s in w for row in s for c in row if c.data_type=='e']
    if errors:raise AssertionError(('Excel error cells',len(errors),errors[:10]))
    RESULTS.append({'name':label+': no Excel error cells','passed':True,'count':0})
    for code in 'AB':
        s=w['MODEL '+code];me=w['MES '+code];ld=w['OBCIĄŻENIA '+code]
        nodes=np.array([[s.cell(7+n,3+a).value for a in range(3)] for n in range(6)],float)
        supports=np.array([[s.cell(7+n,6+a).value for a in range(6)] for n in range(6)],int)
        members=[(int(s.cell(17+m,3).value)-1,int(s.cell(17+m,4).value)-1,int(s.cell(17+m,5).value)) for m in range(7)]
        props=np.array([[s.cell(17+m,6+a).value for a in range(4)] for m in range(7)],float)
        if s['M7'].value!=1 or me['B1245'].value!=1:
            check(label+code+': invalid geometry blocks active rows',w['ŚCIANA – OBLICZENIA' if code=='A' else 'WYSUWNICA – OBLICZENIA']['D7'].value,0)
            continue
        check(label+code+': invertible model',me['B1245'].value,1)
        data=w['ŚCIANA – DANE' if code=='A' else 'WYSUWNICA – DANE']
        if code=='A':
            check(label+code+': stud x coordinates',nodes[:3,0],[0,data['F23'].value/2,data['F23'].value])
            area=data['F23'].value*(nodes[3,2]+2*nodes[4,2]+nodes[5,2])/4e6
        else:
            check(label+code+': station coordinates',nodes[:3,0],[-data['F25'].value,0,data['F23'].value])
            check(label+code+': roof inclination',[nodes[3,1],nodes[3,2]],data['F27'].value*np.array([np.cos(np.radians(data['F29'].value)),np.sin(np.radians(data['F29'].value))]))
            area=(data['F23'].value+data['F25'].value)*data['F27'].value/1e6
        self_weight=sum(s.cell(17+m,10).value*props[m,0]*props[m,1]*np.linalg.norm(nodes[j]-nodes[i])*9.80665/1e9 for m,(i,j,active) in enumerate(members) if active)
        numeric_cases=[]
        for case,name in enumerate(['G','S','W+','W−','H','Q']):
            line=np.array([[ld.cell(7+m,3+case*3+a).value for a in range(3)] for m in range(7)],float)
            nodal=np.array([[ld.cell(19+case*6+n,4+a).value*(1000 if a<3 else 1e6) for a in range(6)] for n in range(6)])
            u,react,forces,k,f=solve(nodes,members,supports,props,line,nodal)
            numeric_cases.append((u,forces,line))
            expected_total=np.zeros(3)
            if case==0:expected_total[2]=-data['F36'].value*area*1000-self_weight
            elif case==1:expected_total[2]=-data['F38'].value*area*1000*(1 if code=='A' else np.cos(np.radians(data['F29'].value)))
            elif case in [2,3]:
                pressure=data['F40' if case==2 else 'F42'].value
                sign=1 if case==2 else -1
                if code=='A':expected_total[1]=sign*pressure*area*1000
                else:
                    alpha=np.radians(data['F29'].value)
                    expected_total[1]=sign*pressure*area*1000*np.sin(alpha)
                    expected_total[2]=-sign*pressure*area*1000*np.cos(alpha)
            elif case==4:expected_total[0]=data['M36'].value*area*1000
            else:expected_total[2]=-data['M38'].value*area*1000
            check(label+code+name+': independent tributary area load sum',f.reshape(6,6)[:,:3].sum(axis=0),expected_total+nodal[:,:3].sum(axis=0),atol=1e-5)
            ue=np.array([me.cell(1151+i,2+case).value for i in range(36)],float)
            re=np.array([me.cell(1201+i,2+case).value for i in range(36)],float)
            check(label+code+name+': all 36 displacements',ue,u,atol=1e-7)
            check(label+code+name+': all 36 reactions',re,react,atol=1e-4)
            ke=np.array([[me.cell(601+i,2+j).value for j in range(36)] for i in range(36)],float)
            check(label+code+name+': assembled 36x36 stiffness',ke,k,atol=.01)
            for m in range(7):
                er=10+m*75
                fe=[me.cell(er+64+a,2+case).value for a in range(12)]
                check(label+code+name+f': 12 end forces E{m+1}',fe,forces[m],atol=1e-4)
            # 3 force and 3 moment equilibrium about global origin, includes applied nodal moments.
            total=(react+f).reshape(6,6)
            check(label+code+name+': force equilibrium',total[:,:3].sum(axis=0),np.zeros(3),atol=1e-5)
            check(label+code+name+': moment equilibrium',(total[:,3:]+np.cross(nodes,total[:,:3])).sum(axis=0),np.zeros(3),atol=.01)
        # Reference sum for simultaneous directions: verify actual Excel combination forces after enabling ULS.
        for ci in range(26):
            cr=7+ci
            weights=np.array([w['KOMBINACJE'].cell(cr,5+c).value or 0 for c in range(6)],float)
            ca=w['ŚCIANA – OBLICZENIA' if code=='A' else 'WYSUWNICA – OBLICZENIA']
            for m in range(7):
                rr=7+ci*7+m;er=10+m*75
                for a in [0,1,2,4,5]:
                    expected=sum(weights[c]*me.cell(er+64+a,2+c).value for c in range(6))
                    check(label+code+f': combination {ci} E{m+1} force {a}',ca.cell(rr,22+a).value,expected,atol=1e-4)
                if ca.cell(rr,4).value==1:
                    ew=weights.copy()
                    if ci==25:
                        kd=w['MATERIAŁY'].cell(16+int(data['F32'].value),8).value
                        ew[0]+=kd;ew[1]+=kd*(w['NORMY']['G61'].value or 0);ew[2]+=kd*(w['NORMY']['G62'].value or 0)
                        ew[3:]=0
                    i,j,active=members[m];length,rot,trans=rotation(nodes[i],nodes[j])
                    combined_u=sum(ew[c]*numeric_cases[c][0] for c in range(6))
                    dofs=np.r_[np.arange(i*6,i*6+6),np.arange(j*6,j*6+6)]
                    ul=trans@combined_u[dofs]
                    qlocal=rot@sum(ew[c]*numeric_cases[c][2][m] for c in range(6))
                    b,h,e,g=props[m];area=b*h;iy=b*h**3/12;iz=h*b**3/12
                    values=[]
                    for t in np.linspace(0,1,21):
                        h1=1-3*t*t+2*t**3;h2=t*(1-t)**2;h3=3*t*t-2*t**3;h4=-t*t*(1-t)
                        uu=(1-t)*ul[0]+t*ul[6]+qlocal[0]*length**2*t*(1-t)/(2*e*area)
                        vv=h1*ul[1]+h2*length*ul[5]+h3*ul[7]+h4*length*ul[11]+qlocal[1]*length**4*t*t*(1-t)**2/(24*e*iz)
                        ww=h1*ul[2]-h2*length*ul[4]+h3*ul[8]-h4*length*ul[10]+qlocal[2]*length**4*t*t*(1-t)**2/(24*e*iy)
                        values.append(np.linalg.norm([uu,vv,ww]))
                    check(label+code+f': combination {ci} E{m+1} internal displacement maximum',ca.cell(rr,20).value,max(values),atol=1e-7)
                    ff=sum(weights[c]*numeric_cases[c][1][m] for c in range(6))
                    qq=rot@sum(weights[c]*numeric_cases[c][2][m] for c in range(6))
                    for idx,qidx,vidx,sign,output in [(4,2,2,-1,8),(5,1,1,1,9)]:
                        xs=[0,length]
                        if qq[qidx]!=0:xs.append(max(0,min(length,-ff[vidx]/qq[qidx])))
                        maximum=max(abs(-ff[idx]+sign*ff[vidx]*x+sign*qq[qidx]*x*x/2) for x in xs)
                        check(label+code+f': combination {ci} E{m+1} exact bending envelope {idx}',ca.cell(rr,output).value,maximum,atol=1e-4)

    for cr in range(7,33):
        assert not ((w['KOMBINACJE'].cell(cr,7).value or 0) and (w['KOMBINACJE'].cell(cr,8).value or 0)), ('mutually exclusive winds',cr)
    RESULTS.append({'name':label+': pressure and suction never combined','passed':True})
    if label=='overload':
        assert all(w[sn]['G6'].value=='NIE SPEŁNIA' for sn in ['ŚCIANA – WYNIKI','WYSUWNICA – WYNIKI'])
        RESULTS.append({'name':'overload: actual exceedance detected','passed':True})
    for name in ['ŚCIANA – WYNIKI','WYSUWNICA – WYNIKI']:
        assert w[name]['G6'].value in ['NIEZWERYFIKOWANE','NIE SPEŁNIA']
    RESULTS.append({'name':label+': never false global SPEŁNIA','passed':True})


if __name__=='__main__':
    analytical();validate(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'baseline')
    dest=Path(__file__).parent/(Path(sys.argv[1]).stem+'-results.json')
    dest.write_text('{\n  \"passed\": '+str(len(RESULTS))+',\n  \"failed\": 0,\n  \"checks\": [\n'+',\n'.join('    '+json.dumps(c,ensure_ascii=False,separators=(',',':')) for c in RESULTS)+'\n  ]\n}\n')
    print(f'{len(RESULTS)} checks passed -> {dest}')
