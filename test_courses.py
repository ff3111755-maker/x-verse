import json,concurrent.futures
from pathlib import Path
from code_runner import run_code
DATA=json.loads((Path(__file__).parent/'data/curriculum.json').read_text())
def test(l):
    r=run_code(l['track'],l['solution_html'])
    ok=r['exit_code']==0 and r['stdout'].strip()==l['expected_output'].strip()
    return dict(id=l['id'],passed=ok,**({} if ok else dict(result=r,expected=l['expected_output'])))
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(test,[l for l in DATA['lessons'] if l['track'] in ('java','javascript')]))
    print(json.dumps(results,indent=2))
    print('PASSED',sum(x['passed'] for x in results),'/',len(results))
    (Path(__file__).parent/'course-test-results.json').write_text(json.dumps(results,indent=2))
    if not all(r['passed'] for r in results):raise SystemExit(1)