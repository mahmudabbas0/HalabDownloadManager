import json,os,pathlib,shutil,zipfile
ROOT=pathlib.Path(__file__).resolve().parent.parent
run=pathlib.Path(os.environ['HALAB_E2E_ROOT']);run.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'browser-extension',run/'extension')
f=run/'extension/background.js'
f.write_text(f.read_text(encoding='utf-8').replace("const HOST = 'com.mahmudabbas.halab'","const HOST = '"+os.environ['HALAB_E2E_HOST']+"'"),encoding='utf-8')
with zipfile.ZipFile(run/'fixture.zip','w',zipfile.ZIP_STORED) as z:z.writestr('payload.bin',bytes(range(256))*4096)
app=ROOT/'build/package/App'
if not (app/'HalabNativeHost.exe').exists():raise SystemExit('Build the deployable application first.')
manifest=json.loads((ROOT/'installer/com.mahmudabbas.halab.json').read_text(encoding='utf-8'))
manifest['name']=os.environ['HALAB_E2E_HOST'];manifest['path']=str(app/'HalabNativeHost.exe')
(run/'native.json').write_text(json.dumps(manifest),encoding='utf-8')
