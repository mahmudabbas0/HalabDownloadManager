(() => {
 let enabled=false;const inFlight=new Set();
 chrome.storage.local.get('captureDownloads').then(v=>{enabled=v.captureDownloads!==false;});
 chrome.storage.onChanged.addListener((changes,area)=>{if(area==='local'&&changes.captureDownloads)enabled=changes.captureDownloads.newValue!==false;});
 const fail=error=>{const notice=document.createElement('div');notice.textContent='Halab: '+String(error.message||error)+' — أعد المحاولة من أيقونة الإضافة / Retry from the extension.';notice.style.cssText='position:fixed;bottom:20px;right:20px;z-index:2147483647;background:#243a43;color:white;padding:16px;max-width:420px;border-radius:8px;font:14px Segoe UI';document.documentElement.append(notice);setTimeout(()=>notice.remove(),12000);};
 document.addEventListener('click',event=>{
  if(!enabled||event.defaultPrevented||event.button!==0)return;
  const link=event.target?.closest?.('a[href]');if(!link)return;
  let url;try{url=new URL(link.href,document.baseURI);}catch{return;}if(!/^https?:$/.test(url.protocol))return;
  if(event.altKey){event.preventDefault();event.stopImmediatePropagation();chrome.runtime.sendMessage({op:'bypass',url:url.href}).then(reply=>{if(!reply?.ok)throw new Error(reply?.error||'Bypass failed');window.location.assign(url.href);}).catch(fail);return;}
  if(!link.hasAttribute('download')&&!/\.(zip|rar|7z|tar|gz|bz2|xz|exe|msi|iso|dmg|apk|mp3|m4a|wav|flac|mp4|mkv|webm|avi|mov|csv|pdf)$/i.test(url.pathname))return;
  event.preventDefault();event.stopImmediatePropagation();if(inFlight.has(url.href))return;inFlight.add(url.href);
  chrome.runtime.sendMessage({op:'download',url:url.href,name:link.getAttribute('download')||url.pathname.split('/').pop()}).then(reply=>{if(!reply?.ok||!reply?.queued)throw new Error(reply?.error||'Download is waiting for Halab');}).catch(fail).finally(()=>inFlight.delete(url.href));
 },true);
})();
