const box=document.querySelector('#capture'),status=document.querySelector('#status');
chrome.storage.local.get(['captureDownloads','lastError']).then(value=>{box.checked=value.captureDownloads!==false;status.textContent=value.lastError||'';});
box.addEventListener('change',()=>chrome.storage.local.set({captureDownloads:box.checked}));
document.querySelector('#check').onclick=async()=>{try{const result=await chrome.runtime.sendNativeMessage('com.mahmudabbas.halab',{op:'ping'});status.textContent=result.ok?'Connected / متصل':'Connection failed';}catch(error){status.textContent=error.message;}};

document.querySelector("#retry").onclick=async()=>{const result=await chrome.runtime.sendMessage({op:"retryFailed"});status.textContent=result?.ok?"تم الإرسال / Downloads sent":"تنزيلات بانتظار البرنامج / Waiting for Halab";};
