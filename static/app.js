const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const labelEl = document.getElementById('label');
const confEl = document.getElementById('conf');
const logEl = document.getElementById('log');
const intervalInput = document.getElementById('interval');

let stream = null;
let timer = null;

async function startCamera(){
  try{
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    await video.play();
    overlay.width = video.videoWidth;
    overlay.height = video.videoHeight;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    scheduleSend();
  }catch(e){
    log('Camera error: ' + e.message);
  }
}

function stopCamera(){
  if(stream){
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
  if(timer){
    clearTimeout(timer);
    timer = null;
  }
  startBtn.disabled = false;
  stopBtn.disabled = true;
}

function log(msg){
  const p = document.createElement('div');
  p.textContent = msg;
  logEl.prepend(p);
}

function scheduleSend(){
  const ms = parseInt(intervalInput.value) || 600;
  timer = setTimeout(sendFrame, ms);
}

function drawOverlay(text){
  const ctx = overlay.getContext('2d');
  ctx.clearRect(0,0,overlay.width, overlay.height);
  ctx.fillStyle = 'rgba(0,0,0,0.4)';
  ctx.fillRect(0, overlay.height - 40, overlay.width, 40);
  ctx.fillStyle = '#fff';
  ctx.font = '20px Arial';
  ctx.fillText(text, 10, overlay.height - 12);
}

async function sendFrame(){
  if(!stream) return;
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(async function(blob){
    try{
      const fd = new FormData();
      fd.append('image', blob, 'frame.jpg');
      const res = await fetch('/predict', { method: 'POST', body: fd });
      if(!res.ok){
        const txt = await res.text();
        log('Server error: ' + txt);
      } else {
        const data = await res.json();
        labelEl.textContent = data.label;
        confEl.textContent = (data.confidence).toFixed(3);
        drawOverlay(`${data.label} (${(data.confidence*100).toFixed(1)}%)`);
      }
    }catch(e){
      log('Send error: ' + e.message);
    } finally {
      scheduleSend();
    }
  }, 'image/jpeg', 0.8);
}

startBtn.addEventListener('click', startCamera);
stopBtn.addEventListener('click', stopCamera);

// automatically size overlay when video metadata loads
video.addEventListener('loadedmetadata', ()=>{
  overlay.width = video.videoWidth;
  overlay.height = video.videoHeight;
});
