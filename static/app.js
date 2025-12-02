const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const labelEl = document.getElementById('label');
const confEl = document.getElementById('conf');
const logEl = document.getElementById('log');
const intervalInput = document.getElementById('interval');
const requireEyesCb = document.getElementById('requireEyes');

let stream = null;
let timer = null;
let faceMesh = null;
let eyesDetected = false;

function log(msg){
  const p = document.createElement('div');
  p.textContent = msg;
  logEl.prepend(p);
}

async function startCamera(){
  try{
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    await video.play();
    overlay.width = video.videoWidth;
    overlay.height = video.videoHeight;
    startBtn.disabled = true;
    stopBtn.disabled = false;

    initFaceMesh();
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
  if(faceMesh){
    faceMesh.close();
    faceMesh = null;
  }
  startBtn.disabled = false;
  stopBtn.disabled = true;
}

function scheduleSend(){
  const ms = parseInt(intervalInput.value) || 600;
  timer = setTimeout(sendFrame, ms);
}

function drawOverlay(text, results){
  const ctx = overlay.getContext('2d');
  ctx.clearRect(0,0,overlay.width, overlay.height);
  if(results && results.multiFaceLandmarks){
    // draw landmarks
    ctx.fillStyle = 'rgba(255,0,0,0.8)';
    results.multiFaceLandmarks.forEach(face => {
      face.forEach(lm => {
        const x = lm.x * overlay.width;
        const y = lm.y * overlay.height;
        ctx.fillRect(x-1, y-1, 2, 2);
      });
    });
  }
  ctx.fillStyle = 'rgba(0,0,0,0.4)';
  ctx.fillRect(0, overlay.height - 40, overlay.width, 40);
  ctx.fillStyle = '#fff';
  ctx.font = '20px Arial';
  ctx.fillText(text, 10, overlay.height - 12);
}

function hasEyes(results){
  if(!results || !results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) return false;
  // indices approximate as used in Python script
  const left_eye_idx = [33,7,163,144,145,153,154,155,133];
  const right_eye_idx = [263,249,390,373,374,380,381,382,362];
  const face = results.multiFaceLandmarks[0];
  let vis = 0;
  const total = left_eye_idx.length + right_eye_idx.length;
  left_eye_idx.concat(right_eye_idx).forEach(i => {
    const lm = face[i];
    if(lm && lm.x >= 0 && lm.x <= 1 && lm.y >= 0 && lm.y <=1) vis++;
  });
  return (vis / total) >= 0.3;
}

function initFaceMesh(){
  if(typeof faceMesh !== 'undefined' && faceMesh) return;
  const FaceMeshClass = window.FaceMesh || window.faceMesh || null;
  if(!FaceMeshClass){
    log('MediaPipe FaceMesh not loaded; falling back to sending frames without eye gating.');
    return;
  }

  faceMesh = new FaceMeshClass({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
  });
  faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
  });
  faceMesh.onResults((results) => {
    eyesDetected = hasEyes(results);
    // draw overlay (landmarks + text handled in sendFrame when we update)
    // we don't call drawOverlay here because sendFrame will draw current text
    // but for more real-time landmarks we draw them here too
    const txt = eyesDetected ? 'Eyes detected' : 'No eyes detected';
    drawOverlay(txt, results);
  });

  // Use MediaPipe Camera util if available for better performance
  const CameraClass = window.Camera || window.camera || null;
  if(CameraClass){
    try{
      // width/height may not be available immediately; Camera handles sizing
      const camera = new CameraClass(video, {
        onFrame: async () => {
          await faceMesh.send({image: video});
        },
        width: video.videoWidth || 640,
        height: video.videoHeight || 480
      });
      camera.start();
      // store camera so we can stop it on teardown
      faceMesh._cameraInstance = camera;
    }catch(e){
      // fallback to manual loop if Camera util fails
      async function faceLoop(){
        if(!stream || !faceMesh) return;
        try{ await faceMesh.send({image: video}); }catch(e){}
        requestAnimationFrame(faceLoop);
      }
      requestAnimationFrame(faceLoop);
    }
  }else{
    // manual loop
    async function faceLoop(){
      if(!stream || !faceMesh) return;
      try{ await faceMesh.send({image: video}); }catch(e){}
      requestAnimationFrame(faceLoop);
    }
    requestAnimationFrame(faceLoop);
  }
}

async function sendFrame(){
  if(!stream) return;
  // If requireEyes is checked and FaceMesh is available, only send when eyesDetected
  const requireEyes = requireEyesCb ? requireEyesCb.checked : true;
  if(requireEyes && typeof faceMesh !== 'undefined' && faceMesh && !eyesDetected){
    // update UI and schedule next
    labelEl.textContent = '-';
    confEl.textContent = '-';
    drawOverlay('No face/eyes detected — no result');
    scheduleSend();
    return;
  }

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
