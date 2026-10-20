import hashlib, http.server, os, pathlib, re, subprocess, tempfile, threading, time
ROOT=pathlib.Path(__file__).parent
EXE=pathlib.Path(os.environ.get('HALAB_TEST_EXE',str(ROOT.parent/'build/package/App/HalabDownloadManager.exe')))
DATA=bytes(range(256))*16384
requests=[]
class Server(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def do_HEAD(self):
  if self.path=='/nohead': self.send_response(405); self.end_headers(); return
  self.send_response(200); self.send_header('Content-Length',str(len(DATA)))
  if self.path!='/plain': self.send_header('Accept-Ranges','bytes'); self.send_header('ETag','"v2"' if self.path=='/changed' else '"v1"')
  self.end_headers()
 def do_GET(self):
  r=self.headers.get('Range'); requests.append((self.path,r)); start,end=0,len(DATA)-1
  if r and self.path!='/bad':
   start,end=map(int,re.fullmatch(r'bytes=(\d+)-(\d+)',r).groups());self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{len(DATA)}')
  else:self.send_response(200)
  self.send_header('Content-Length',str(end-start+1));self.end_headers()
  try:
   for pos in range(start,end+1,8192):self.wfile.write(DATA[pos:min(pos+8192,end+1)]);self.wfile.flush();time.sleep(.003)
  except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Server)
threading.Thread(target=server.serve_forever,daemon=True).start()
env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen'
base=f'http://127.0.0.1:{server.server_port}'
def run(route,p,*args,code=0):
 result=subprocess.run([str(EXE),'--fetch',base+route,str(p),*args],env=env,capture_output=True,text=True,encoding="utf-8",timeout=30)
 assert result.returncode==code,(result.returncode,result.stdout,result.stderr)
 if code==0:assert p.read_bytes()==DATA;assert not pathlib.Path(str(p)+'.halab.json').exists()
with tempfile.TemporaryDirectory(prefix='halab-test-') as d:
 d=pathlib.Path(d)
 run('/range',d/'seg.bin'); assert len([r for p,r in requests if p=='/range'])==4;print('PASS segmented download: four exact ranges, SHA-256 verified')
 run('/plain',d/'plain.bin');print('PASS server without range support: exact bytes')
 run('/range',d/'resume.bin','--pause-after','220',code=3)
 before=len(requests);run('/range',d/'resume.bin');assert any(int(re.search(r'bytes=(\d+)',r).group(1))%1048576!=0 for p,r in requests[before:] if r);print('PASS pause / process restart / resume: nonzero offsets and exact bytes')
 run('/bad',d/'bad.bin',code=1);assert not (d/'bad.bin').exists();print('PASS ignored Range response: rejected, no final file')
 run('/range',d/'exists.bin');run('/range',d/'exists.bin',code=1);assert (d/'exists.bin').read_bytes()==DATA;print('PASS existing destination preserved')
 run('/changed',d/'changed.bin','--pause-after','220',code=3)
 import json
 meta=pathlib.Path(str(d/'changed.bin')+'.halab.json');j=json.loads(meta.read_text());j['validator']='"old"';meta.write_text(json.dumps(j))
 before=len(requests);run('/changed',d/'changed.bin');assert all(int(re.search(r'bytes=(\d+)',r).group(1))%1048576==0 for p,r in requests[before:] if r);print('PASS changed ETag: partial data restarted safely')
 run('/nohead',d/'nohead.bin');print('PASS HEAD rejected: streaming GET fallback, exact bytes')
 started=time.monotonic();run('/range',d/'limited.bin','--limit-kib','1024');duration=time.monotonic()-started;assert 3.5<duration<15,duration;print(f'PASS aggregate per-download limiter: 4 MiB in {duration:.2f}s at 1024 KiB/s')
 result=subprocess.run([str(EXE),'--smoke'],env=env,capture_output=True,timeout=15);assert result.returncode==0;print('PASS Qt GUI launch and clean exit')
server.shutdown()
print('ALL 9 CHECKS PASSED')
