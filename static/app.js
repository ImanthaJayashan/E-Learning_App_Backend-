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
let latestResults = null;
// smoothing & debounce state
const SMOOTH_WINDOW = 5; // number of recent predictions to average
const CONSISTENT_REQUIRED = 3; // number of consecutive averaged-labels required to show
const MIN_CONFIDENCE = 0.55; // minimum averaged confidence to accept
const MIN_SEND_INTERVAL_MS = 200; // do not send more often than this
let probsHistory = [];
let lastAveragedLabel = null;
let consistentCount = 0;
let lastSendTime = 0;

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
    latestResults = results;
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
  const cropFace = document.getElementById('cropFace') ? document.getElementById('cropFace').checked : true;
  let sx = 0, sy = 0, sw = video.videoWidth, sh = video.videoHeight;
  if(latestResults && latestResults.multiFaceLandmarks && latestResults.multiFaceLandmarks.length){
    const face = latestResults.multiFaceLandmarks[0];
    // compute face bbox
    const xs = face.map(lm => lm.x * video.videoWidth);
    const ys = face.map(lm => lm.y * video.videoHeight);
    const minX = Math.max(Math.min(...xs) - 20, 0);
    const maxX = Math.min(Math.max(...xs) + 20, video.videoWidth);
    const minY = Math.max(Math.min(...ys) - 20, 0);
    const maxY = Math.min(Math.max(...ys) + 20, video.videoHeight);
    const faceBox = { x: Math.floor(minX), y: Math.floor(minY), w: Math.floor(maxX - minX), h: Math.floor(maxY - minY) };

    // prefer a tighter eye-region crop when possible (eyes give most signal for lazy-eye)
    try{
      const left_eye_idx = [33,7,163,144,145,153,154,155,133];
      const right_eye_idx = [263,249,390,373,374,380,381,382,362];
      const eyeIndices = left_eye_idx.concat(right_eye_idx);
      const ex = [];
      const ey = [];
      eyeIndices.forEach(i => {
        const lm = face[i];
        if(lm){ ex.push(lm.x * video.videoWidth); ey.push(lm.y * video.videoHeight); }
      });
      if(ex.length && ey.length){
        const eMinX = Math.max(Math.min(...ex) - 30, 0);
        const eMaxX = Math.min(Math.max(...ex) + 30, video.videoWidth);
        const eMinY = Math.max(Math.min(...ey) - 20, 0);
        const eMaxY = Math.min(Math.max(...ey) + 20, video.videoHeight);
        const eyeBox = { x: Math.floor(eMinX), y: Math.floor(eMinY), w: Math.floor(eMaxX - eMinX), h: Math.floor(eMaxY - eMinY) };
        // use eyeBox when it's reasonably sized compared to face box (avoid tiny crops)
        if(eyeBox.w > 30 && eyeBox.h > 20){
          sx = eyeBox.x; sy = eyeBox.y; sw = eyeBox.w; sh = eyeBox.h;
        } else {
          // fallback to face box when eye region too small
          if(cropFace){ sx = faceBox.x; sy = faceBox.y; sw = faceBox.w; sh = faceBox.h; }
        }
      } else {
        if(cropFace){ sx = faceBox.x; sy = faceBox.y; sw = faceBox.w; sh = faceBox.h; }
      }
    }catch(e){
      // if any issue using landmarks, fallback to face crop or full frame
      if(cropFace){ sx = faceBox.x; sy = faceBox.y; sw = faceBox.w; sh = faceBox.h; }
    }
    // if box too small, fallback to full frame
    if(sw < 20 || sh < 20){ sx = 0; sy = 0; sw = video.videoWidth; sh = video.videoHeight; }
  }

  canvas.width = sw;
  canvas.height = sh;
  const ctx = canvas.getContext('2d');
  try{
    ctx.drawImage(video, sx, sy, sw, sh, 0, 0, sw, sh);
  }catch(e){
    // fallback to full frame draw
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  }

    // Resize the crop to model input size before sending to server to match training preprocessing
    const MODEL_IMG_SIZE = 224;
    const resizeCanvas = document.createElement('canvas');
    resizeCanvas.width = MODEL_IMG_SIZE;
    resizeCanvas.height = MODEL_IMG_SIZE;
    const rctx = resizeCanvas.getContext('2d');
    rctx.drawImage(canvas, 0, 0, canvas.width, canvas.height, 0, 0, MODEL_IMG_SIZE, MODEL_IMG_SIZE);

    resizeCanvas.toBlob(async function(blob){
    try{
      const fd = new FormData();
      // send face crop with original video bbox metadata so server could optionally align
      fd.append('image', blob, 'frame.jpg');
      // include bbox coordinates to server (optional)
      if(!(sx === 0 && sy === 0 && sw === video.videoWidth && sh === video.videoHeight)){
        fd.append('bbox', JSON.stringify({sx, sy, sw, sh, vw: video.videoWidth, vh: video.videoHeight}));
      }
      const sendDebug = document.getElementById('sendDebug') ? document.getElementById('sendDebug').checked : false;
      const url = sendDebug ? '/predict?debug=1' : '/predict';
          // throttle send frequency to avoid network overload and noisy frames
          const now = Date.now();
          if(now - lastSendTime < MIN_SEND_INTERVAL_MS){
            // skip this send; schedule next
            scheduleSend();
            return;
          }
          lastSendTime = now;
          const res = await fetch(url, { method: 'POST', body: fd });
      if(!res.ok){
        const txt = await res.text();
        log('Server error: ' + txt);
      } else {
        const data = await res.json();
        // push probs into history for smoothing
        if(data.all_probs && Array.isArray(data.all_probs)){
          probsHistory.push(data.all_probs.map(p=>Number(p)));
          if(probsHistory.length > SMOOTH_WINDOW) probsHistory.shift();
        }

        // compute average probs over history
        let averaged = null;
        if(probsHistory.length){
          const L = probsHistory[0].length;
          const sums = new Array(L).fill(0);
          probsHistory.forEach(arr => {
            for(let i=0;i<L;i++) sums[i] += arr[i];
          });
          averaged = sums.map(s => s / probsHistory.length);
        }

        let displayLabel = '-';
        let displayConf = 0.0;
        if(averaged){
          // find argmax
          let maxIdx = 0; let maxVal = averaged[0];
          for(let i=1;i<averaged.length;i++){ if(averaged[i] > maxVal){ maxVal = averaged[i]; maxIdx = i; } }
          // debounce: require repeated averaged label
          const avgLabel = data.label || ('class_' + maxIdx);
          if(lastAveragedLabel === avgLabel){
            consistentCount += 1;
          } else {
            lastAveragedLabel = avgLabel;
            consistentCount = 1;
          }
          displayLabel = (consistentCount >= CONSISTENT_REQUIRED && maxVal >= MIN_CONFIDENCE) ? avgLabel : '-';
          displayConf = maxVal;
        } else {
          // fallback to immediate single-frame result
          displayLabel = data.label || '-';
          displayConf = data.confidence || 0.0;
        }

        // update UI
        labelEl.textContent = displayLabel;
        confEl.textContent = displayConf ? displayConf.toFixed(3) : '-';
        drawOverlay(displayLabel === '-' ? 'Waiting for stable result...' : `${displayLabel} (${(displayConf*100).toFixed(1)}%)`);

        // display debug image and logits if present
        const debugBox = document.getElementById('debugBox');
        const debugText = document.getElementById('debugText');
        if(debugBox){
          if(data.debug_image_b64){
            debugBox.innerHTML = '';
            const img = document.createElement('img');
            img.src = 'data:image/jpeg;base64,' + data.debug_image_b64;
            img.style.maxWidth = '200px';
            img.style.maxHeight = '200px';
            img.style.border = '1px solid #ccc';
            debugBox.appendChild(img);
          }
        }
        if(debugText && data.all_probs){
          debugText.textContent = `probs: ${data.all_probs.map(p=>p.toFixed(4)).join(', ')}`;
        }
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
