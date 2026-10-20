import hashlib,http.server,json,os,pathlib,re,socket,subprocess,tempfile,threading,time
EXE=pathlib.Path(os.environ.get('HALAB_TEST_EXE',str(pathlib.Path(__file__).resolve().parent.parent/'build/package/App/HalabDownloadManager.exe')));DATA=bytes(range(251))*40000;requests=[];cut_once=True
DATE='Mon, 19 Oct 2026 10:00:00 GMT'
class Server(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def common(self):
  if self.path not in ['/hidden','/nohead','/nolength']:self.send_header('Accept-Ranges','bytes')
  if self.path in ['/modified','/weak']:self.send_header('Last-Modified',DATE)
  if self.path not in ['/novalidator','/modified','/weak']:self.send_header('ETag','"version-2"' if self.path=='/moving' and self.command=='GET' else '"version-1"')
  if self.path=='/weak':self.send_header('ETag','W/"weak-version"')
 def do_HEAD(self):
  requests.append((self.path,'HEAD',None,None))
  if self.path=='/nohead':self.send_response(405);self.end_headers();return
  self.send_response(200)
  if self.path!='/nolength':self.send_header('Content-Length',str(len(DATA)))
  self.common();self.end_headers()
 def do_GET(self):
  global cut_once
  value=self.headers.get('Range');requests.append((self.path,'GET',value,self.headers.get('If-Range')));start=0;end=len(DATA)-1
  if value:
   start,end=map(int,re.fullmatch(r'bytes=(\d+)-(\d+)',value).groups());self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{len(DATA)}')
  else:self.send_response(200)
  self.send_header('Content-Length',str(end-start+1));self.common();self.end_headers()
  cut=self.path=='/cut' and value and end-start>100000 and cut_once
  if cut:cut_once=False
  try:
   for pos in range(start,end+1,8192):
    self.wfile.write(DATA[pos:min(pos+8192,end+1)]);self.wfile.flush();time.sleep(.004)
    if cut and pos-start>=131072:self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
  except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError,OSError):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Server);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen'
def run(route,path,*args,code=0):
 r=subprocess.run([str(EXE),'--fetch',base+route,str(path),*args],env=env,capture_output=True,text=True,encoding='utf-8',timeout=45)
 assert r.returncode==code,(route,r.returncode,r.stdout,r.stderr)
 if code==0:assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(DATA).digest()
 return r
with tempfile.TemporaryDirectory(prefix='halab-resume-proof-') as directory:
 root=pathlib.Path(directory)
 for route in ['/modified','/weak','/hidden','/nohead','/nolength','/novalidator']:
  path=root/(route[1:]+'.bin');run(route,path,'--pause-after','250',code=3)
  meta=json.loads(pathlib.Path(str(path)+'.halab.json').read_text());assert meta['ranged'],(route,meta)
  sizes=[pathlib.Path(str(path)+f'.halab.part{i}').stat().st_size for i in range(len(meta['parts']))];assert max(sizes)>65536
  before=len(requests);run(route,path);following=[r for r in requests[before:] if r[1]=='GET' and r[2] and r[2]!='bytes=0-0']
  starts=[int(re.search(r'bytes=(\d+)',r[2]).group(1)) for r in following];original=[int(p['start']) for p in meta['parts']]
  assert any(a>b for a,b in zip(starts,original)),(route,starts,original,sizes)
  if route in ['/modified','/weak']:assert all(r[3]==DATE for r in following)
  print('PASS actual process restart resumes saved offsets with exact SHA-256:',route)
 path=root/'cut.bin';run('/cut',path,code=1);before=len(requests);run('/cut',path);assert any(r[2] and int(re.search(r'bytes=(\d+)',r[2]).group(1))%2510000!=0 for r in requests[before:] if r[1]=='GET');print('PASS real TCP disconnect retains partial bytes and resumes to exact SHA-256')
 path=root/'tampered.bin';run('/novalidator',path,'--pause-after','250',code=3)
 part=pathlib.Path(str(path)+'.halab.part0');data=bytearray(part.read_bytes());data[-1]^=1;part.write_bytes(data)
 r=run('/novalidator',path,code=1);assert 'changed near the resume point' in r.stdout;assert not path.exists();print('PASS no-validator overlap mismatch prevents publishing a corrupted file')
with tempfile.TemporaryDirectory(prefix='halab-legacy-resume-') as directory:
 path=pathlib.Path(directory)/'legacy.bin';prefix=500000
 pathlib.Path(str(path)+'.halab.part0').write_bytes(DATA[:prefix])
 pathlib.Path(str(path)+'.halab.json').write_text(json.dumps({'url':base+'/novalidator','total':str(len(DATA)),'validator':'','ranged':False,'parts':[{'start':'0','end':'-1'}]}))
 before=len(requests);run('/novalidator',path);following=[r for r in requests[before:] if r[1]=='GET' and r[2]];assert following[0][2].startswith(f'bytes={prefix-65536}-');print('PASS legacy single-stream checkpoint is upgraded and resumed instead of restarted')
 path=pathlib.Path(directory)/'moving.bin';r=run('/moving',path,code=1);assert 'remote file changed during' in r.stdout;assert not path.exists();print('PASS representation change between HEAD and GET is rejected before publication')
server.shutdown();print('ALL 10 RESUME AND INTEGRITY SCENARIOS PASSED')
