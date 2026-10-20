const HOST = 'com.mahmudabbas.halab';
const pending = new Set();
let failedWrites=Promise.resolve();
const groups=['zip|rar|exe|mp[34]|pdf','7z|tar|gz|bz2|xz','msi|iso|dmg|apk','m4a|wav|flac|mkv','webm|avi|mov|csv'];
export function captureRules(api){
 const redirect={type:'redirect',redirect:{regexSubstitution:api.runtime.getURL('handoff.html')+'?url=\\0'}};
 const files=groups.map((types,index)=>({id:index===0?1:index+2,priority:10,action:redirect,condition:{regexFilter:'^https?://.*\\.('+types+')(\\?.*)?$',resourceTypes:['main_frame','sub_frame'],requestMethods:['get']}}));
 const attachment={id:2,priority:9,action:redirect,condition:{regexFilter:'^https?://.*',resourceTypes:['main_frame','sub_frame'],requestMethods:['get'],responseHeaders:[{header:'content-disposition',values:['attachment*']},{header:'content-type',values:['application/octet-stream*','application/zip*','application/x-rar*','application/x-7z-compressed*','application/x-msdownload*']}]}};
 return [...files,attachment];
}
export async function syncCaptureRules(api){
 const settings=await api.storage.local.get('captureDownloads');
 await api.declarativeNetRequest.updateDynamicRules({removeRuleIds:[1,2,3,4,5,6],addRules:settings.captureDownloads===false?[]:captureRules(api)});if(api.downloads.setUiOptions)await api.downloads.setUiOptions({enabled:settings.captureDownloads===false});
}
async function rememberFailure(api,request,error){
 const save=async()=>{const data=await api.storage.local.get('failedHandoffs');const list=data.failedHandoffs||[];const key=JSON.stringify([request.op,request.url,request.formatId]);const next=list.filter(x=>JSON.stringify([x.op,x.url,x.formatId])!==key);next.push(request);await api.storage.local.set({failedHandoffs:next.slice(-100),lastError:String(error.message||error)});};
 failedWrites=failedWrites.then(save,save);await failedWrites;
}
export async function sendToDesktop(api,request){
 try {const reply=await api.runtime.sendNativeMessage(HOST,request);if(!reply?.ok||!reply?.queued)throw new Error(reply?.error||'Desktop did not acknowledge the download');const clear=async()=>{const data=await api.storage.local.get('failedHandoffs');const key=JSON.stringify([request.op,request.url,request.formatId]);const remaining=(data.failedHandoffs||[]).filter(x=>JSON.stringify([x.op,x.url,x.formatId])!==key);if(remaining.length!==(data.failedHandoffs||[]).length)await api.storage.local.set({failedHandoffs:remaining,lastError:remaining.length?'Some downloads are waiting for Halab.':''});};failedWrites=failedWrites.then(clear,clear);await failedWrites;return reply;}
 catch(error){await rememberFailure(api,request,error);return {ok:false,queued:false,error:String(error.message||error)};}
}
export async function allowBrowserOnce(api,url,tabId){
 if(!/^https?:\/\//i.test(url)||!Number.isInteger(tabId)||tabId<0||tabId>2000000000)throw new Error('Invalid bypass request');
 const ruleId=1000000+tabId,expires=Date.now()+30000;if(api.downloads.setUiOptions)await api.downloads.setUiOptions({enabled:true});
 const data=await api.storage.session.get('browserBypass');const list=(data.browserBypass||[]).filter(x=>x.expires>Date.now()&&x.tabId!==tabId);
 list.push({url,tabId,ruleId,expires});
 await api.declarativeNetRequest.updateSessionRules({removeRuleIds:[ruleId],addRules:[{id:ruleId,priority:1000,action:{type:'allow'},condition:{regexFilter:'^https?://',tabIds:[tabId],resourceTypes:['main_frame','sub_frame']}}]});
 await api.storage.session.set({browserBypass:list});await api.alarms.create('halab-bypass-expiry',{when:expires});return {ok:true};
}
export async function cleanExpiredBypasses(api){
 const data=await api.storage.session.get('browserBypass'),list=data.browserBypass||[],alive=list.filter(x=>x.expires>Date.now()),expired=list.filter(x=>x.expires<=Date.now());
 if(expired.length)await api.declarativeNetRequest.updateSessionRules({removeRuleIds:expired.map(x=>x.ruleId)});
 await api.storage.session.set({browserBypass:alive});if(alive.length)await api.alarms.create('halab-bypass-expiry',{when:Math.min(...alive.map(x=>x.expires))});
}
export async function consumeBypass(api,item){
 if(!api.storage.session)return false;
 const data=await api.storage.session.get('browserBypass');const list=data.browserBypass||[],index=list.findIndex(x=>x.expires>Date.now()&&(x.url===item.url||x.url===item.finalUrl));
 if(index<0)return false;const [entry]=list.splice(index,1);await api.storage.session.set({browserBypass:list});await api.declarativeNetRequest.updateSessionRules({removeRuleIds:[entry.ruleId]});return true;
}
export function isCapturable(item){return Number.isInteger(item.id)&&/^https?:\/\//i.test(item.finalUrl||item.url||'')&&!item.incognito&&item.state==='in_progress';}
async function cancelAndErase(api,id){try{await api.downloads.cancel(id);}catch(error){const rows=await api.downloads.search({id});if(rows[0]?.state==='complete'){await api.downloads.removeFile(id);}else if(rows[0]?.state!=='interrupted')throw error;}await api.downloads.erase({id});}
export async function handoffDownload(api,item,settings={}){
 if(settings.captureDownloads===false||!isCapturable(item)||pending.has(item.id)||item.byExtensionId===api.runtime.id||await consumeBypass(api,item))return false;
 pending.add(item.id);let accepted=false;
 const request={op:'download',url:item.finalUrl||item.url,name:(item.filename||'').split(/[\\/]/).pop(),referrer:item.referrer||''};
 try{
  await rememberFailure(api,request,'Sending download to Halab');
  if(api.downloads.setUiOptions)await api.downloads.setUiOptions({enabled:false});
  await cancelAndErase(api,item.id);
  const reply=await sendToDesktop(api,request);accepted=!!reply?.ok&&!!reply?.queued;
  return accepted;
 }catch(error){
  if(!accepted)await rememberFailure(api,request,error);
  await api.storage.local.set({lastError:String(error.message||error)});
  // Browser fallback is explicit (Alt+click or the popup button), never automatic.
  await cancelAndErase(api,item.id).catch(()=>{});return accepted;
 }finally{pending.delete(item.id);}
}
export function validatePageRequest(message,sender){return !!sender?.tab&&['formats','video','download','bypass'].includes(message?.op)&&/^https?:\/\//i.test(message.url||'')&&String(message.url).length<16384;}
if(typeof chrome!=='undefined'&&chrome.downloads){
 const update=()=>syncCaptureRules(chrome).catch(error=>chrome.storage.local.set({lastError:String(error.message||error)}));
 update();cleanExpiredBypasses(chrome).catch(()=>{});
 chrome.runtime.onInstalled.addListener(async()=>{const values=await chrome.storage.local.get('captureDownloads');if(values.captureDownloads===undefined)await chrome.storage.local.set({captureDownloads:true});await chrome.contextMenus.removeAll();chrome.contextMenus.create({id:'halab-link',title:'Download with Halab Download Manager',contexts:['link','video','audio']});await update();});
 chrome.runtime.onStartup.addListener(update);
 chrome.storage.onChanged.addListener((changes,area)=>{if(area==='local'&&changes.captureDownloads)update();});
 chrome.alarms.onAlarm.addListener(alarm=>{if(alarm.name==='halab-bypass-expiry')cleanExpiredBypasses(chrome).catch(()=>{});});
 chrome.downloads.onCreated.addListener(async item=>{const settings=await chrome.storage.local.get('captureDownloads');await handoffDownload(chrome,item,settings);});
 chrome.contextMenus.onClicked.addListener(async(info,tab)=>{const url=info.linkUrl||info.srcUrl;if(/^https?:\/\//i.test(url||''))await sendToDesktop(chrome,{op:'download',url,referrer:tab?.url||''});});
 chrome.runtime.onMessage.addListener((message,sender,respond)=>{
  const ownPage=sender.id===chrome.runtime.id&&sender.url?.startsWith(chrome.runtime.getURL(''));
  if(ownPage&&message?.op==='retryFailed'){
   (async()=>{const data=await chrome.storage.local.get('failedHandoffs');let remaining=[];for(const request of data.failedHandoffs||[]){const reply=await sendToDesktop(chrome,request);if(!reply.ok)remaining.push(request);}await chrome.storage.local.set({failedHandoffs:remaining,lastError:remaining.length?'Some downloads are waiting for Halab.':''});return {ok:remaining.length===0,remaining:remaining.length};})().then(respond,error=>respond({ok:false,error:String(error)}));return true;
  }
  if(!validatePageRequest(message,sender)&&!(ownPage&&['download','bypass'].includes(message?.op)&&/^https?:\/\//i.test(message.url||'')&&String(message.url).length<16384)){respond({ok:false,error:'Invalid request'});return false;}
  if(message.op==='bypass'){allowBrowserOnce(chrome,message.url,sender.tab?.id??message.tabId).then(respond,error=>respond({ok:false,error:String(error.message||error)}));return true;}
  const request={op:message.op,url:message.url,title:String(message.title||'').slice(0,200),name:String(message.name||'').slice(0,200)};
  if(message.op==='video'){request.formatId=String(message.formatId||'');request.needsMerge=!!message.needsMerge;}
  (message.op==='formats'?chrome.runtime.sendNativeMessage(HOST,request):sendToDesktop(chrome,request)).then(respond,error=>respond({ok:false,error:String(error.message||error)}));return true;
 });
}
