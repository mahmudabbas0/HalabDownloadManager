(() => {
  const host=document.createElement('div');host.id='halab-download-overlay';
  host.style.cssText='position:fixed;z-index:2147483646;right:20px;top:90px;display:none;';
  const shadow=host.attachShadow({mode:'closed'});
  const style=document.createElement('style');style.textContent=`:host{all:initial}*{box-sizing:border-box;font:13px Segoe UI,Arial,sans-serif}button{background:#157f72;color:white;border:1px solid #73c2b0;border-radius:8px;padding:10px 14px;cursor:pointer}section{margin-top:6px;background:#172c3a;color:white;border:1px solid #3a596b;border-radius:10px;padding:14px;width:330px;box-shadow:0 8px 28px #0005}select{width:100%;padding:8px;background:#263e50;color:white;margin:10px 0;border:1px solid #577080}p{margin:6px 0;white-space:pre-wrap;overflow-wrap:anywhere}.small{font-size:11px;color:#b5cbd5}.close{float:right;padding:2px 7px;background:none}button:disabled{opacity:.5;cursor:default}`;
  shadow.append(style);const button=document.createElement('button');button.textContent='↓ Halab · تحميل الفيديو';shadow.append(button);
  const panel=document.createElement('section');panel.hidden=true;shadow.append(panel);document.documentElement.append(host);
  let current='',busy=false;
  function pageUrl(video){const direct=video.currentSrc||video.src;return /^https?:/i.test(direct||'') && !/youtube\.com|youtu\.be/.test(location.hostname)?direct:location.href;}
  function update(){const videos=[...document.querySelectorAll('video')];const video=videos.find(v=>{const r=v.getBoundingClientRect();return r.width>160&&r.height>90&&r.bottom>0&&r.top<innerHeight;});host.style.display=video?'block':'none';if(video&&!panel.hidden&&!busy&&current!==pageUrl(video)){panel.hidden=true;}}
  button.addEventListener('click',async()=>{
    if(!panel.hidden){panel.hidden=true;return;}const video=[...document.querySelectorAll('video')].find(v=>v.getBoundingClientRect().width>160);if(!video)return;
    current=pageUrl(video);panel.replaceChildren();panel.hidden=false;
    const close=document.createElement('button');close.className='close';close.textContent='×';close.onclick=()=>panel.hidden=true;panel.append(close);
    const label=document.createElement('p');label.textContent='Loading available formats… / جارٍ جلب الدقات';panel.append(label);
    const note=document.createElement('p');note.className='small';note.textContent='Only formats returned by the site are offered. Protected streams are not supported.';panel.append(note);
    busy=true;let result;try{result=await chrome.runtime.sendMessage({op:'formats',url:current,title:document.title});}catch(error){result={ok:false,error:error.message};}busy=false;
    if(!result?.ok){label.textContent=result?.error||'Desktop connection failed. Open the extension to check setup.';return;}
    label.textContent=result.title||document.title;
    const select=document.createElement('select');let formats=result.formats||[];
    formats=[...formats].sort((a,b)=>(b.height||0)-(a.height||0));
    for(const [index,f] of formats.entries()){const option=document.createElement('option');option.value=String(index);option.textContent=`${f.audioOnly?'Audio':f.height?f.height+'p':'Video'} · ${f.ext||''}${f.fps?' · '+f.fps+' fps':''}${f.needsMerge?' · video + audio':''}${!f.available?' (install video tools)':''}`;option.disabled=!f.available;select.append(option);}
    const first=formats.findIndex(f=>f.available);if(first>=0)select.value=String(first);panel.append(select);
    const download=document.createElement('button');download.textContent='Download / تنزيل';download.disabled=first<0;panel.append(download);
    download.onclick=async()=>{const chosen=formats[Number(select.value)];if(!chosen?.available)return;download.disabled=true;let response;try{response=await chrome.runtime.sendMessage({op:'video',url:current,title:result.title||document.title,formatId:chosen.id,needsMerge:chosen.needsMerge});}catch(error){response={ok:false,error:error.message};}note.textContent=response?.ok?'Added to Halab Download Manager / أُضيف إلى البرنامج':response?.error||'Download failed';download.disabled=false;};
  });
  new MutationObserver(update).observe(document.documentElement,{childList:true,subtree:true});setInterval(update,1600);addEventListener('scroll',update,{passive:true});addEventListener('yt-navigate-finish',update);update();
})();
