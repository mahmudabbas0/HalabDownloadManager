import sys
sys.stdout.reconfigure(encoding="utf-8")
import http.server,threading,tempfile,pathlib,subprocess,os,io,zipfile,re,time,struct
ROOT=pathlib.Path(__file__).parent
EXE=pathlib.Path(os.environ.get('HALAB_TEST_EXE',str(ROOT.parent/'build/package/App/HalabDownloadManager.exe')))
stream=io.BytesIO()
with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('hello.txt','Halab archive integrity test')
ZIP=stream.getvalue()
# MPEG-1 Layer III frames with a valid header, used for byte-preservation tests.
MP3=b'ID3\x04\x00\x00\x00\x00\x00\x00'+(bytes.fromhex('fffb9064')+bytes(413))*3
big=io.BytesIO()
with zipfile.ZipFile(big,'w',zipfile.ZIP_STORED) as z:z.writestr('data.bin',bytes(range(256))*12288)
BIGZIP=big.getvalue()
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_HEAD(self):self.respond(False)
 def do_GET(self):self.respond(True)
 def respond(self,body):
  path=self.path
  if path=='/redirect':self.send_response(302);self.send_header('Location','/archive-final.zip');self.end_headers();return
  if path=='/nohead' and not body:self.send_response(405);self.end_headers();return
  data=MP3 if path in ('/mime-mp3','/nohead','/get-different') else BIGZIP if path=='/resume' else ZIP
  mime='application/octet-stream' if path=='/sniff' else 'audio/mpeg' if data==MP3 else 'application/zip'
  names={'/disposition':'attachment; filename="report.zip"','/encoded':"attachment; filename=\"fallback.zip\"; filename*=UTF-8''%D9%85%D9%84%D9%81%20%D8%A7%D9%84%D8%A7%D8%AE%D8%AA%D8%A8%D8%A7%D8%B1.zip",'/unsafe':'attachment; filename="../../escape.zip"','/collision':'attachment; filename="same.zip"','/nohead':'attachment; filename="audio.mp3"','/resume':'attachment; filename="resumed.zip"','/get-different':'attachment; filename="right.mp3"' if body else 'attachment; filename="wrong.zip"'}
  if path in ('/bad-html','/bad-signature'):data=b'<html>login page</html>';mime='text/html' if path=='/bad-html' else 'application/zip';names[path]='attachment; filename="archive.zip"'
  start,end=0,len(data)-1;range_header=self.headers.get('Range')
  if range_header:start,end=map(int,re.fullmatch(r'bytes=(\d+)-(\d+)',range_header).groups());self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{len(data)}')
  else:self.send_response(200)
  self.send_header('Content-Length',str(end-start+1));self.send_header('Content-Type',mime)
  if path in names:self.send_header('Content-Disposition',names[path])
  if path=='/resume':self.send_header('Accept-Ranges','bytes');self.send_header('ETag','"stable-zip"')
  self.end_headers()
  if body:
   try:
    for pos in range(start,end+1,8192):self.wfile.write(data[pos:min(end+1,pos+8192)]);self.wfile.flush();time.sleep(.002 if path=='/resume' else 0)
   except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen'
base=f'http://127.0.0.1:{server.server_port}'
def fetch(route,target,*extra,code=0):
 result=subprocess.run([str(EXE),'--fetch',base+route,str(target),'--auto-name',*extra],env=env,capture_output=True,text=True,encoding="utf-8",timeout=25)
 assert result.returncode==code,(route,result.returncode,result.stdout,result.stderr)
 if code==0:return pathlib.Path(next(line[5:] for line in result.stdout.splitlines() if line.startswith('FILE=')))
with tempfile.TemporaryDirectory(prefix='halab-names-') as temp:
 root=pathlib.Path(temp)
 cases=[('/sniff','download.zip',ZIP),('/disposition','report.zip',ZIP),('/encoded','ملف الاختبار.zip',ZIP),('/mime-mp3','download.mp3',MP3),('/redirect','archive-final.zip',ZIP),('/nohead','audio.mp3',MP3),('/unsafe','escape.zip',ZIP),('/get-different','right.mp3',MP3)]
 for i,(route,name,data) in enumerate(cases):
  folder=root/str(i);folder.mkdir();result=fetch(route,folder/'download');assert result.name==name,(route,result);assert result.parent==folder;assert result.read_bytes()==data
  if result.suffix=='.zip':assert zipfile.ZipFile(result).testzip() is None
  print('PASS server filename / content / safe path:',route,name)
 folder=root/'collision';folder.mkdir();(folder/'same.zip').write_bytes(b'existing');result=fetch('/collision',folder/'download');assert result.name=='same (1).zip';assert (folder/'same.zip').read_bytes()==b'existing';assert result.read_bytes()==ZIP;print('PASS collision: original file preserved')
 for route in ('/bad-html','/bad-signature'):
  folder=root/route[1:];folder.mkdir();fetch(route,folder/'download',code=1);assert not (folder/'archive.zip').exists();print('PASS invalid archive rejected:',route)
 folder=root/'resume';folder.mkdir();fetch('/resume',folder/'download','--pause-after','100',code=3);assert not (folder/'resumed.zip').exists();result=fetch('/resume',folder/'download');assert result.name=='resumed.zip';assert result.read_bytes()==BIGZIP;assert zipfile.ZipFile(result).testzip() is None;print('PASS named ZIP pause/resume and archive CRC')
 for flag in ('--ui-check','--language-check'):
  result=subprocess.run([str(EXE),flag],env=env,capture_output=True,text=True,encoding="utf-8",timeout=20);assert result.returncode==0,(flag,result.stdout,result.stderr);print(result.stdout.strip())
 pe=EXE.read_bytes();pe_offset=struct.unpack_from('<I',pe,0x3c)[0];subsystem=struct.unpack_from('<H',pe,pe_offset+24+68)[0];assert subsystem==2,subsystem;print('PASS Windows GUI subsystem: no console window')
server.shutdown()
print('ALL NAMING, FILE INTEGRITY, LANGUAGE AND GUI CHECKS PASSED')
