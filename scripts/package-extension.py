"""Package the unpacked extension; optionally sign CRX3 with an external RSA key."""
import argparse,base64,hashlib,io,json,pathlib,shutil,struct,zipfile
ROOT=pathlib.Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=pathlib.Path,default=ROOT/'dist')
parser.add_argument('--key',type=pathlib.Path,help='RSA PEM private key outside this repository; needs cryptography')
parser.add_argument('--crx',type=pathlib.Path,help='Existing signed release CRX matching this source version and public key')
args=parser.parse_args()
if args.key and args.crx:parser.error('Choose either --key or --crx.')
extension=ROOT/'browser-extension';manifest=json.loads((extension/'manifest.json').read_text(encoding='utf-8'))
version=(ROOT/'VERSION').read_text().strip()
if manifest['version']!=version:raise SystemExit('VERSION and extension manifest version differ.')
output=args.output_dir.resolve();output.mkdir(parents=True,exist_ok=True)
stem=f'HalabDownloadManager-{version}-BrowserExtension'
buffer=io.BytesIO()
with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
 for item in sorted(extension.iterdir()):
  if item.is_file() and item.name!='package.json':archive.write(item,item.name)
archive_bytes=buffer.getvalue();(output/(stem+'.zip')).write_bytes(archive_bytes)
if args.crx:
 with zipfile.ZipFile(args.crx) as archive:
  existing=json.loads(archive.read('manifest.json'))
  if existing['version']!=version or existing.get('key')!=manifest.get('key'):raise SystemExit('CRX version/public key does not match this source tree.')
 shutil.copyfile(args.crx,output/(stem+'.crx'))
if args.key:
 key_path=args.key.resolve()
 if key_path.is_relative_to(ROOT):raise SystemExit('Keep private signing keys outside the repository.')
 from cryptography.hazmat.primitives import hashes,serialization
 from cryptography.hazmat.primitives.asymmetric import padding
 key=serialization.load_pem_private_key(key_path.read_bytes(),password=None)
 public=key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
 if base64.b64encode(public).decode()!=manifest['key']:raise SystemExit('Signing key differs from manifest.key; update the public key and native-host allowed_origins together for your own extension identity.')
 def varint(value):
  result=bytearray()
  while value>127:result.append((value&127)|128);value>>=7
  return bytes(result)+bytes([value])
 def field(number,value):return varint(number*8+2)+varint(len(value))+value
 extension_id=hashlib.sha256(public).digest()[:16]
 signed=field(1,extension_id)
 payload=b'CRX3 SignedData\0'+struct.pack('<I',len(signed))+signed+archive_bytes
 signature=key.sign(payload,padding.PKCS1v15(),hashes.SHA256())
 key.public_key().verify(signature,payload,padding.PKCS1v15(),hashes.SHA256())
 header=field(2,field(1,public)+field(2,signature))+field(10000,signed)
 (output/(stem+'.crx')).write_bytes(b'Cr24'+struct.pack('<II',3,len(header))+header+archive_bytes)
public=base64.b64decode(manifest['key']);digest=hashlib.sha256(public).hexdigest()[:32]
print('Extension:',version,'ID:',''.join(chr(97+int(c,16)) for c in digest))
print('Unpacked ZIP:',output/(stem+'.zip'))
