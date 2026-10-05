const $=s=>document.querySelector(s), url=$("#url"), status=$("#status"), result=$("#result"), channelPanel=$("#channelPanel");
let mode="single", channelData=[];
document.querySelectorAll(".mode").forEach(b=>b.onclick=()=>{
 document.querySelectorAll(".mode").forEach(x=>x.classList.remove("active"));b.classList.add("active");mode=b.dataset.mode;
 result.classList.add("hidden");channelPanel.classList.add("hidden");
 url.placeholder=mode==="single"?"Dán liên kết Facebook vào đây...":"Dán URL Page / mục Video / Reels công khai...";
 $("#go").textContent=mode==="single"?"⬇ TẢI VIDEO":"🔎 QUÉT KÊNH / PAGE";status.textContent="";
});
$("#paste").onclick=async()=>{try{url.value=await navigator.clipboard.readText();status.textContent="✓ Đã dán liên kết."}catch{status.textContent="Hãy dán liên kết thủ công."}};
$("#go").onclick=()=>mode==="single"?analyze():scanChannel();
url.addEventListener("keydown",e=>{if(e.key==="Enter")$("#go").click()});
function size(n){if(!n)return "";let u=["B","KB","MB","GB"],i=0;while(n>1024&&i<3){n/=1024;i++}return n.toFixed(1)+" "+u[i]}
async function analyze(){
 const v=url.value.trim();if(!v){status.textContent="⚠ Hãy dán liên kết Facebook.";return}
 result.classList.add("hidden");status.textContent="⏳ Đang phân tích video...";
 try{const r=await fetch("/api/info?url="+encodeURIComponent(v)),d=await r.json();if(!r.ok)throw new Error(d.detail||"Không thể phân tích.");
 $("#thumb").src=d.thumbnail||"";$("#title").textContent=d.title;$("#meta").textContent=[d.uploader,d.duration?Math.floor(d.duration/60)+":"+String(d.duration%60).padStart(2,"0"):""].filter(Boolean).join(" · ");
 const a=[],s=new Set();for(const f of d.formats){if(!s.has(f.height)){s.add(f.height);a.push(f)}}if(!a.length)throw new Error("Không tìm thấy định dạng.");
 $("#formats").innerHTML=a.map(f=>`<div class="tr"><span><b>${f.quality}</b>${f.filesize?` · ${size(f.filesize)}`:""}</span><span>${(f.ext||"mp4").toUpperCase()}</span><span>${f.has_audio?"Có":"Tự ghép"}</span><a class="dl" href="/api/download?url=${encodeURIComponent(v)}&height=${f.height}">⬇ TẢI XUỐNG</a></div>`).join("");
 result.classList.remove("hidden");status.textContent="✓ Phân tích hoàn tất.";result.scrollIntoView({behavior:"smooth",block:"center"});
 }catch(e){status.textContent="⚠ "+e.message}}
async function scanChannel(){
 const v=url.value.trim();if(!v){status.textContent="⚠ Hãy dán URL Page/kênh Facebook.";return}
 channelPanel.classList.add("hidden");status.textContent="⏳ Đang quét tối đa 20 video công khai...";
 try{const r=await fetch("/api/channel?limit=20&url="+encodeURIComponent(v)),d=await r.json();if(!r.ok)throw new Error(d.detail||"Không thể quét.");
 channelData=d.videos||[];if(!channelData.length)throw new Error("Không tìm thấy video. Hãy thử URL mục Video/Reels của Page.");
 $("#channelTitle").textContent=d.title||"Facebook Page";$("#channelCount").textContent=`Tìm thấy ${channelData.length} video trong đợt quét này`;
 $("#channelVideos").innerHTML=channelData.map((x,i)=>`<label class="video-card"><input class="pick" type="checkbox" data-i="${i}" checked><img src="${x.thumbnail||""}" onerror="this.style.visibility='hidden'"><div><b>${escapeHtml(x.title||"Facebook Video")}</b><span>${x.duration?Math.floor(x.duration/60)+":"+String(x.duration%60).padStart(2,"0"):"Video công khai"}</span></div></label>`).join("");
 channelPanel.classList.remove("hidden");status.textContent="✓ Quét hoàn tất.";channelPanel.scrollIntoView({behavior:"smooth",block:"start"});
 }catch(e){status.textContent="⚠ "+e.message}}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
$("#selectAll").onclick=()=>{const p=[...document.querySelectorAll(".pick")],all=p.every(x=>x.checked);p.forEach(x=>x.checked=!all);$("#selectAll").textContent=all?"✓ Chọn tất cả":"✕ Bỏ chọn tất cả"};
$("#batchDownload").onclick=async()=>{
 const picks=[...document.querySelectorAll(".pick:checked")].map(x=>channelData[+x.dataset.i].url);if(!picks.length){status.textContent="⚠ Chưa chọn video.";return}
 if(picks.length>20){status.textContent="⚠ Tối đa 20 video mỗi lượt.";return}
 status.textContent=`⏳ Đang tải và đóng gói ${picks.length} video. Không đóng trang...`;$("#batchDownload").disabled=true;
 try{const r=await fetch("/api/batch-download",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({urls:picks,height:+$("#batchQuality").value})});
 if(!r.ok){let d=await r.json();throw new Error(d.detail||"Tải hàng loạt thất bại.")}const blob=await r.blob(),a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="TAI_LE_MMO_FACEBOOK_BATCH.zip";document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),5000);status.textContent="✓ Đã tạo gói ZIP. Trình duyệt đang tải xuống.";
 }catch(e){status.textContent="⚠ "+e.message}finally{$("#batchDownload").disabled=false}}
