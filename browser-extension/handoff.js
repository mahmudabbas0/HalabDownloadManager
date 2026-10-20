let url=(location.search.startsWith('?url=')?location.search.slice(5):location.hash.slice(1));const acceptedUrls=new Set(),status=document.querySelector('#status');
async function transfer(){if(acceptedUrls.has(url)){status.textContent='تم إرسال هذا التنزيل إلى Halab / Already sent to Halab';return;}if(!/^https?:\/\//i.test(url)||url.length>16384){status.textContent='رابط غير صالح / Invalid URL';return;}status.textContent='جارٍ إرسال التنزيل إلى البرنامج…';try{const result=await chrome.runtime.sendMessage({op:'download',url});if(!result?.ok||!result?.queued)throw new Error(result?.error||'Connection failed');acceptedUrls.add(url);status.textContent='تم إرسال التنزيل إلى البرنامج / Download sent to Halab';}catch(error){status.textContent='التنزيل محفوظ لإعادة المحاولة. افتح Halab ثم اضغط إعادة المحاولة. / Open Halab and retry. '+String(error.message||error);}}
document.querySelector('#retry').onclick=transfer;
document.querySelector('#browser').onclick=async()=>{const tab=await chrome.tabs.getCurrent();const result=await chrome.runtime.sendMessage({op:'bypass',url,tabId:tab.id});if(result?.ok)location.replace(url);else status.textContent=result?.error||'Bypass failed';};
transfer();

window.addEventListener('hashchange',()=>{url=(location.search.startsWith('?url=')?location.search.slice(5):location.hash.slice(1));transfer();});
document.querySelector('#back').onclick=()=>history.back();
