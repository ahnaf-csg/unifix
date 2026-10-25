import re,glob,os
HERE=os.path.dirname(os.path.abspath(__file__))
D={os.path.basename(f):open(f,encoding='utf-8').read() for f in sorted(glob.glob(os.path.join(HERE,'[01][0-9]_*.md')))}
allt='\n'.join(D.values())
def defined(prefix,src):
    return set(re.findall(r'^\| ('+prefix+r'-\d+) \|',src,re.M))
defs={'C':defined('C',D['02_requirements.md']),'OP':defined('OP',D['02_requirements.md']),'VR':defined('VR',D['02_requirements.md']),
'NFR':defined('NFR',D['02_requirements.md']),'UC':defined('UC',D['06_diagram_blueprint.md']),'FB':defined('FB',D['08_iteration_log.md']),'CR':defined('CR',D['08_iteration_log.md'])}
scr=set(re.findall(r'^### ((?:P|S|A|SA)-\d+)',D['04_screens.md'],re.M))
for x in re.findall(r'^### A-06 Notifications · (A-07)',D['04_screens.md'],re.M): scr.add(x)
print('Screens defined:',len(scr),sorted(scr))
issues=[]
for fn,t in D.items():
    for m in re.finditer(r'\b(C|OP|VR|NFR|UC|FB|CR)-(\d+)\b',t):
        k=m.group(0)
        if k not in defs[m.group(1)]: issues.append(f'{fn}: undefined {k}')
    for m in re.finditer(r'\b((?:SA|S|A|P)-\d\d)\b',t):
        if m.group(1) not in scr: issues.append(f'{fn}: undefined screen {m.group(1)}')
# URL names in 04 vs 05
u05=set(re.findall(r'^\| (\w+) \| `(\w+)` \|',D['05_data_dictionary.md'],re.M)); u05={f'{a}:{b}' for a,b in u05}
u04=set(re.findall(r'`(\w+:\w+)`',D['04_screens.md']))
print('URL names 05:',len(u05)); 
for u in sorted(u04-u05): issues.append(f'04 uses URL {u} not in 05')
# statuses
st03=re.findall(r'^\| `(\w+)` \| [A-Z]',D['03_workflow.md'],re.M)
badge=set(re.findall(r'^\| (\w+) \| `badge-',D['05_data_dictionary.md'],re.M))
print('Statuses 03:',st03)
for s in st03:
    if s not in badge: issues.append(f'status {s} has no badge in 05')
# ComplaintUpdate actions vs 03 effect table
acts=re.search(r'`action` \| CharField choices \| (.*?) \|',D['05_data_dictionary.md']).group(1)
acts=set(re.findall(r'`(\w+)`',acts))
used=set(re.findall(r'ComplaintUpdate\(action=(\w+)',D['03_workflow.md']))
for a in used-acts: issues.append(f'03 uses ComplaintUpdate action {a} not in 05')
# notification events
ev=set(re.findall(r'`(\w+)`',re.search(r'`event` \| CharField choices \| (.*?) \|',D['05_data_dictionary.md']).group(1)))
print('Events:',ev)
# fields referenced in 03 effect table for Complaint
fields05=set(re.findall(r'^\| `(\w+)`',D['05_data_dictionary.md'],re.M))|{'verified_at','resolved_at','closed_at','created_at','updated_at','from_status','to_status','from_department','to_department'}
for f in set(re.findall(r'`(\w+)=',D['03_workflow.md'])):
    if f not in fields05: issues.append(f'03 sets field {f} not in 05')
print('\nISSUES:'); print('\n'.join(sorted(set(issues))) or 'none')
