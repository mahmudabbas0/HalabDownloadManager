import os,sys,json,struct,subprocess,pathlib,tempfile,http.server,threading,time,hashlib,socket
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).parent.parent
APP=pathlib.Path(os.environ.get('HALAB_TEST_APP',str(ROOT/'build/package/App')))
HOST=APP/'HalabNativeHost.exe'
ENV=os.environ.copy();ENV['QT_QPA_PLATFORM']='offscreen';ENV['PATH']=str(ROOT/'tools/ffmpeg/bin')+';'+ENV['PATH']
def native(message,env=ENV):
 payload=json.dumps(message).encode();r=subprocess.run([str(HOST)],input=struct.pack('<I',len(payload))+payload,capture_output=True,env=env,timeout=75);assert r.returncode==0,(r.returncode,r.stderr);assert len(r.stdout)>=4,(r.stdout,r.stderr);n=struct.unpack('<I',r.stdout[:4])[0];assert len(r.stdout)==n+4;return json.loads(r.stdout[4:])
assert native({'op':'ping'})['name']=='Halab Download Manager';print('PASS native messaging binary framing and brand')
assert not native({'op':'download','url':'file:///C:/test'})['ok'];print('PASS native connector rejects non-HTTP URLs')
assert not native({'op':'video','url':'https://example.com','formatId':'1; calc.exe'})['ok'];print('PASS format validation rejects shell-like values')
with tempfile.TemporaryDirectory(prefix='halab-bridge-test-') as temp:
 root=pathlib.Path(temp);files=root/'web';files.mkdir();downloads=root/'downloads';downloads.mkdir();profile=root/'profile';profile.mkdir()
 ffmpeg=ROOT/'tools/ffmpeg/bin/ffmpeg.exe'
 if not ffmpeg.exists():ffmpeg=next(APP.glob('tools/ffmpeg/**/ffmpeg.exe'),APP/'tools/ffmpeg/bin/ffmpeg.exe')
 video=files/'clip.mp4'
 subprocess.run([str(ffmpeg),'-loglevel','error','-f','lavfi','-i','testsrc=size=160x90:rate=10','-f','lavfi','-i','sine=frequency=500:sample_rate=44100','-t','1','-c:v','mpeg4','-c:a','aac','-shortest',str(video)],check=True,capture_output=True)
 data=bytes(range(256))*1024;(files/'file.bin').write_bytes(data)
 class Handler(http.server.SimpleHTTPRequestHandler):
  def __init__(self,*a,**kw):super().__init__(*a,directory=str(files),**kw)
  def log_message(self,*a):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 env=ENV.copy();env['HALAB_DATA_DIR']=str(profile);env['HALAB_DOWNLOAD_DIR']=str(downloads)
 log=open(root/'app.log','wb');app=subprocess.Popen([str(APP/'HalabDownloadManager.exe'),'--listen'],env=env,stdout=log,stderr=log)
 try:
  for _ in range(50):
   if (profile/'instance.lock').exists():break
   time.sleep(.1)
  time.sleep(.5);print('Desktop running:',app.poll() is None,flush=True)
  cfg=json.loads((profile/'connector.json').read_text());conn=socket.create_connection(('127.0.0.1',cfg['port']));conn.sendall(json.dumps({'op':'download','url':base+'/file.bin','_token':'invalid'}).encode()+b'\n');answer=json.loads(conn.makefile('rb').readline());conn.close();assert not answer['ok'];print('PASS loopback bridge rejects a request without its private token')
  result=native({'op':'download','url':base+'/file.bin','name':'file.bin'},env);assert result.get('queued'),(result,(root/'app.log').read_text(errors='replace'),(profile/'connector-diagnostic.json').read_text() if (profile/'connector-diagnostic.json').exists() else 'no server diagnostic',app.poll())
  target=downloads/'file.bin'
  for _ in range(100):
   if target.exists():break
   time.sleep(.1)
  assert target.read_bytes()==data;print('PASS native connector → existing desktop instance → exact downloaded bytes')
  result=native({'op':'formats','url':base+'/clip.mp4'},env);assert result.get('ok') and result['formats'],result
  fmt=next(f for f in result['formats'] if f['available']);print('PASS actual yt-dlp extraction of local MP4 formats:',fmt['id'])
  result=native({'op':'video','url':base+'/clip.mp4','title':'Local video test','formatId':fmt['id'],'needsMerge':fmt['needsMerge']},env);assert result.get('queued'),result
  output=[]
  for _ in range(150):
   output=list(downloads.glob('*.mp4'))
   if output and not any(downloads.glob('*.part')):break
   time.sleep(.1)
  assert output, list(downloads.iterdir())
  assert hashlib.sha256(output[0].read_bytes()).digest()==hashlib.sha256(video.read_bytes()).digest();print('PASS actual yt-dlp video download through desktop queue, SHA-256 matches')
  history=json.loads((profile/'downloads.json').read_text(encoding='utf-8'));assert len(history['jobs'])==2;assert any(j['mediaJob'] for j in history['jobs']);print('PASS native/video jobs persist in one queue')
 finally:
  app.terminate()
  try:app.wait(timeout=5)
  except subprocess.TimeoutExpired:app.kill();app.wait()
  server.shutdown();log.close()
version=subprocess.run([str(APP/'tools/yt-dlp.exe'),'--version'],capture_output=True,text=True,timeout=10);assert version.returncode==0
print('ALL BROWSER CONNECTOR AND LOCAL VIDEO CHECKS PASSED')
