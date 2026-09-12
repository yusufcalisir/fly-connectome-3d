/**
 * FlyConnectome 3D - Main Interactive Application
 *
 * Implements:
 * 1. Three.js 3D Observation Chamber with anatomical Drosophila rig & floating smartphone
 * 2. Real-time canvas stimulus generator (Watermelon, Looming Shadow, Spider, Foliage)
 * 3. Bidirectional WebSocket telemetry streaming to ConnectomeBrain engine
 * 4. Central Complex EPG compass HUD and live neurochemical oscilloscope waveforms
 */

// ============================================================================
// 1. STIMULUS GENERATOR (VIRTUAL PHONE DISPLAY)
// ============================================================================

class StimulusGenerator {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.preset = 'fruit';
    this.time = 0;
    this.loomingProgress = 0;
    this.isLoomingActive = false;

    this.presetsInfo = {
      fruit: {
        title: 'Sweet Ripe Watermelon',
        desc: 'High-sugar olfactory & visual chromatic target.',
        tag: 'APPETITIVE',
        tagClass: 'appetitive',
      },
      shadow: {
        title: 'Looming Predator Disc',
        desc: 'Rapidly expanding visual shadow triggering LC4 threat circuits.',
        tag: 'LOOM THREAT',
        tagClass: 'threat',
      },
      spider: {
        title: 'Predatory Spider',
        desc: 'High-contrast predatory threat with arachnid appendages.',
        tag: 'PREDATOR',
        tagClass: 'threat',
      },
      neutral: {
        title: 'Forest Foliage Canopy',
        desc: 'Ambient natural green leaves providing calm baseline input.',
        tag: 'BASELINE',
        tagClass: '',
      },
    };
  }

  setPreset(preset) {
    if (this.presetsInfo[preset]) {
      this.preset = preset;
      this.loomingProgress = 0;
      this.isLoomingActive = (preset === 'shadow');

      const info = this.presetsInfo[preset];
      document.getElementById('current-photo-title').textContent = info.title;
      document.getElementById('current-photo-desc').textContent = info.desc;
      const tagEl = document.getElementById('stimulus-type-tag');
      tagEl.textContent = info.tag;
      tagEl.className = 'overlay-tag ' + info.tagClass;
    }
  }

  triggerLoomingPulse() {
    this.loomingProgress = 0.05;
    this.isLoomingActive = true;
  }

  render(dt = 0.016) {
    this.time += dt;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const ctx = this.ctx;

    ctx.save();
    ctx.clearRect(0, 0, w, h);

    switch (this.preset) {
      case 'fruit':
        this._renderFruit(ctx, w, h);
        break;
      case 'shadow':
        this._renderShadow(ctx, w, h, dt);
        break;
      case 'spider':
        this._renderSpider(ctx, w, h);
        break;
      case 'neutral':
        this._renderNeutral(ctx, w, h);
        break;
    }

    ctx.restore();
  }

  _renderFruit(ctx, w, h) {
    // Rich juicy watermelon slice on dark phone background
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, '#0c0512');
    bgGrad.addColorStop(1, '#1b081e');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // Glowing appetitive ambient aura
    const aura = ctx.createRadialGradient(w / 2, h / 2, 10, w / 2, h / 2, 70);
    aura.addColorStop(0, 'rgba(255, 30, 80, 0.35)');
    aura.addColorStop(1, 'rgba(255, 30, 80, 0.0)');
    ctx.fillStyle = aura;
    ctx.fillRect(0, 0, w, h);

    // Watermelon rind (green arc)
    ctx.save();
    ctx.translate(w / 2, h / 2 + 15);
    const bob = Math.sin(this.time * 2.5) * 3;
    ctx.translate(0, bob);

    // Dark green outer rind
    ctx.beginPath();
    ctx.arc(0, 0, 36, 0.15 * Math.PI, 0.85 * Math.PI, false);
    ctx.lineWidth = 9;
    ctx.strokeStyle = '#1e7534';
    ctx.stroke();

    // White inner rind
    ctx.beginPath();
    ctx.arc(0, 0, 32, 0.16 * Math.PI, 0.84 * Math.PI, false);
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#e6f7df';
    ctx.stroke();

    // Vibrant red watermelon flesh
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, 30, 0.18 * Math.PI, 0.82 * Math.PI, false);
    ctx.closePath();
    ctx.fillStyle = '#ff1744';
    ctx.fill();

    // Black seeds
    const seeds = [
      [-12, 14], [12, 14], [0, 20], [-8, 22], [8, 22], [0, 10]
    ];
    ctx.fillStyle = '#111';
    for (const [sx, sy] of seeds) {
      ctx.beginPath();
      ctx.ellipse(sx, sy, 1.8, 3.2, 0.2 * (sx < 0 ? -1 : 1), 0, Math.PI * 2);
      ctx.fill();
    }

    // Dripping sweet sugar droplet
    const dripY = 32 + ((this.time * 25) % 35);
    ctx.fillStyle = 'rgba(255, 100, 150, 0.9)';
    ctx.beginPath();
    ctx.arc(0, dripY, 2.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  _renderShadow(ctx, w, h, dt) {
    // Looming threat stimulus: expanding dark shadow on bright high-contrast arena
    ctx.fillStyle = '#f0f4f8';
    ctx.fillRect(0, 0, w, h);

    if (this.isLoomingActive) {
      this.loomingProgress += dt * 1.5;
      if (this.loomingProgress > 1.2) {
        this.loomingProgress = 0.05; // Loop the looming cycle
      }
    } else {
      this.loomingProgress = 0.15;
    }

    // Exponential looming expansion radius: r = r0 * e^(k * t)
    const maxR = Math.hypot(w, h) * 0.7;
    const currentR = 5 + Math.pow(this.loomingProgress, 2.4) * maxR;

    // Dark predator shadow casting sudden looming contrast
    const shadowGrad = ctx.createRadialGradient(w / 2, h / 2, currentR * 0.7, w / 2, h / 2, currentR);
    shadowGrad.addColorStop(0, '#020306');
    shadowGrad.addColorStop(0.85, '#090b12');
    shadowGrad.addColorStop(1, 'rgba(10, 15, 25, 0.2)');

    ctx.fillStyle = shadowGrad;
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, currentR, 0, Math.PI * 2);
    ctx.fill();

    // Alert indicators on screen
    if (this.loomingProgress > 0.4) {
      ctx.fillStyle = 'rgba(255, 0, 0, 0.7)';
      ctx.font = 'bold 10px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('! THREAT DETECTED !', w / 2, 22);
    }
  }

  _renderSpider(ctx, w, h) {
    // High-contrast predator on dim surface
    ctx.fillStyle = '#10141a';
    ctx.fillRect(0, 0, w, h);

    ctx.save();
    ctx.translate(w / 2, h / 2);
    const crawl = Math.sin(this.time * 6) * 4;
    ctx.translate(0, crawl);

    // Spider abdomen & cephalothorax
    ctx.fillStyle = '#1c1b24';
    ctx.strokeStyle = '#852028';
    ctx.lineWidth = 1.5;

    // Abdomen
    ctx.beginPath();
    ctx.ellipse(0, 12, 14, 20, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Cephalothorax
    ctx.beginPath();
    ctx.ellipse(0, -6, 10, 11, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Glowing venomous red chelicerae eyes
    ctx.fillStyle = '#ff1133';
    ctx.beginPath();
    ctx.arc(-3, -12, 2, 0, Math.PI * 2);
    ctx.arc(3, -12, 2, 0, Math.PI * 2);
    ctx.fill();

    // 8 Articulated crawling legs
    ctx.strokeStyle = '#2d2d38';
    ctx.lineWidth = 2;
    for (let i = 0; i < 4; i++) {
      const sideY = -12 + i * 8;
      const legPhase = this.time * 8 + i * 1.2;
      const legOffset = Math.sin(legPhase) * 6;

      // Left leg
      ctx.beginPath();
      ctx.moveTo(-7, sideY);
      ctx.lineTo(-24, sideY - 10 + legOffset);
      ctx.lineTo(-38, sideY + 12 + legOffset);
      ctx.stroke();

      // Right leg
      ctx.beginPath();
      ctx.moveTo(7, sideY);
      ctx.lineTo(24, sideY - 10 - legOffset);
      ctx.lineTo(38, sideY + 12 - legOffset);
      ctx.stroke();
    }

    ctx.restore();
  }

  _renderNeutral(ctx, w, h) {
    // Natural swaying green leaves (ambient baseline)
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, '#06170d');
    bgGrad.addColorStop(1, '#0e2d19');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    ctx.save();
    for (let i = 0; i < 5; i++) {
      const sway = Math.sin(this.time * 2 + i) * 6;
      const lx = 20 + i * 15;
      const ly = 30 + i * 22;

      ctx.save();
      ctx.translate(lx, ly);
      ctx.rotate(0.2 * Math.sin(this.time + i) + (i % 2 === 0 ? 0.3 : -0.3));

      ctx.fillStyle = i % 2 === 0 ? '#1b5e20' : '#2e7d32';
      ctx.beginPath();
      ctx.ellipse(0, 0, 18, 9, 0.4, 0, Math.PI * 2);
      ctx.fill();

      // Vein
      ctx.strokeStyle = 'rgba(255,255,255,0.15)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(-16, 0);
      ctx.lineTo(16, 0);
      ctx.stroke();

      ctx.restore();
    }
    ctx.restore();
  }

  getBase64Frame() {
    return this.canvas.toDataURL('image/png');
  }
}

// ============================================================================
// 2. THREE.JS 3D OBSERVATION CHAMBER & ANATOMICAL DROSOPHILA RIG
// ============================================================================

class ObservationChamber3D {
  constructor(containerId, stimulusCanvas) {
    this.container = document.getElementById(containerId);
    this.stimulusCanvas = stimulusCanvas;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.clock = new THREE.Clock();

    // 3D Objects
    this.flyGroup = null;
    this.leftWing = null;
    this.rightWing = null;
    this.legs = [];
    this.brainSparkSystem = null;
    this.phoneScreenMesh = null;
    this.phoneLight = null;
    this.phoneTexture = null;

    // Kinematic states
    this.forwardDrive = 0.0;
    this.steeringDeflection = 0.0;
    this.jumpTriggered = false;
    this.jumpY = 0;
    this.jumpVy = 0;

    this._initScene();
    this._buildEnvironment();
    this._buildProceduralFly();
    this._buildVirtualSmartphone();
    this._setupEventListeners();
  }

  _initScene() {
    const w = this.container.clientWidth || 600;
    const h = this.container.clientHeight || 500;

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x06080d);
    this.scene.fog = new THREE.FogExp2(0x06080d, 0.04);

    // Camera
    this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
    this.camera.position.set(0, 3.2, 5.5);

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(w, h);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;
    this.container.appendChild(this.renderer.domElement);

    // Controls (OrbitControls from CDN)
    if (window.THREE && window.THREE.OrbitControls) {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.08;
      this.controls.minDistance = 1.8;
      this.controls.maxDistance = 12.0;
      this.controls.maxPolarAngle = Math.PI / 2 - 0.05;
      this.controls.target.set(0, 0.9, 0);
    }

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x1a243b, 1.2);
    this.scene.add(ambientLight);

    const stageLight = new THREE.SpotLight(0x00f0ff, 2.5);
    stageLight.position.set(2, 6, 4);
    stageLight.angle = 0.55;
    stageLight.penumbra = 0.6;
    stageLight.castShadow = true;
    this.scene.add(stageLight);

    const rimLight = new THREE.DirectionalLight(0xff0055, 1.0);
    rimLight.position.set(-4, 3, -4);
    this.scene.add(rimLight);
  }

  _buildEnvironment() {
    // Circular cybernetic observation stage
    const floorGeo = new THREE.CylinderGeometry(3.5, 3.8, 0.25, 48);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x0c111a,
      roughness: 0.4,
      metalness: 0.8,
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.position.y = -0.125;
    floor.receiveShadow = true;
    this.scene.add(floor);

    // Neon concentric ring grid on stage
    const ringGeo = new THREE.RingGeometry(1.4, 1.44, 48);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, side: THREE.DoubleSide });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.005;
    this.scene.add(ring);

    const outerRingGeo = new THREE.RingGeometry(2.8, 2.83, 48);
    const outerRingMat = new THREE.MeshBasicMaterial({ color: 0x334466, side: THREE.DoubleSide });
    const outerRing = new THREE.Mesh(outerRingGeo, outerRingMat);
    outerRing.rotation.x = -Math.PI / 2;
    outerRing.position.y = 0.005;
    this.scene.add(outerRing);

    // Spherical air-cushioned treadmill ball (classic Seelig & Jayaraman neurobiology setup)
    const ballGeo = new THREE.SphereGeometry(0.55, 32, 32);
    const ballMat = new THREE.MeshStandardMaterial({
      color: 0x182030,
      roughness: 0.6,
      metalness: 0.3,
      wireframe: false,
    });
    this.treadmillBall = new THREE.Mesh(ballGeo, ballMat);
    this.treadmillBall.position.set(0, 0.42, 0);
    this.treadmillBall.castShadow = true;
    this.treadmillBall.receiveShadow = true;
    this.scene.add(this.treadmillBall);

    // Translucent glass dome
    const domeGeo = new THREE.SphereGeometry(3.5, 32, 24, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeMat = new THREE.MeshPhysicalMaterial({
      color: 0x88ccff,
      transparent: true,
      opacity: 0.12,
      roughness: 0.1,
      metalness: 0.1,
      transmission: 0.85,
      ior: 1.45,
      side: THREE.BackSide,
    });
    const dome = new THREE.Mesh(domeGeo, domeMat);
    dome.position.y = 0;
    this.scene.add(dome);
  }

  _buildProceduralFly() {
    this.flyGroup = new THREE.Group();
    this.flyGroup.position.set(0, 1.05, 0); // Positioned atop spherical treadmill

    // Materials
    const chitinMat = new THREE.MeshStandardMaterial({
      color: 0x3d2716, // Rich dark amber drosophila cuticle
      roughness: 0.35,
      metalness: 0.3,
    });

    const abdomenMat = new THREE.MeshStandardMaterial({
      color: 0x2b1c11,
      roughness: 0.45,
      metalness: 0.2,
    });

    const eyeMat = new THREE.MeshStandardMaterial({
      color: 0xaa0022, // Deep ruby red drosophila compound eye
      emissive: 0x44000b,
      roughness: 0.2,
      metalness: 0.4,
    });

    const wingMat = new THREE.MeshPhysicalMaterial({
      color: 0xc8e6ff,
      transparent: true,
      opacity: 0.45,
      roughness: 0.1,
      metalness: 0.1,
      transmission: 0.7,
      ior: 1.3,
      side: THREE.DoubleSide,
    });

    // 1. Thorax
    const thoraxGeo = new THREE.SphereGeometry(0.35, 18, 14);
    thoraxGeo.scale(0.85, 1.0, 1.3);
    const thorax = new THREE.Mesh(thoraxGeo, chitinMat);
    thorax.castShadow = true;
    this.flyGroup.add(thorax);

    // 2. Abdomen (curved posterior)
    const abdomenGeo = new THREE.SphereGeometry(0.42, 18, 14);
    abdomenGeo.scale(0.8, 0.75, 1.6);
    this.abdomen = new THREE.Mesh(abdomenGeo, abdomenMat);
    this.abdomen.position.set(0, -0.08, -0.75);
    this.abdomen.rotation.x = -0.22;
    this.abdomen.castShadow = true;
    this.flyGroup.add(this.abdomen);

    // 3. Head Capsule (articulated)
    this.head = new THREE.Group();
    this.head.position.set(0, 0.08, 0.55);

    const headGeo = new THREE.SphereGeometry(0.24, 16, 12);
    headGeo.scale(1.2, 1.0, 0.9);
    const headMesh = new THREE.Mesh(headGeo, chitinMat);
    this.head.add(headMesh);

    // 4. Compound Eyes (Left & Right)
    const eyeGeo = new THREE.SphereGeometry(0.14, 14, 12);
    eyeGeo.scale(0.9, 1.3, 1.1);

    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.20, 0.04, 0.08);
    leftEye.rotation.set(0.1, 0.35, -0.2);
    this.head.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.20, 0.04, 0.08);
    rightEye.rotation.set(0.1, -0.35, 0.2);
    this.head.add(rightEye);

    // 5. Proboscis (feeding mouthparts)
    const proboscisGeo = new THREE.CylinderGeometry(0.03, 0.06, 0.22, 10);
    const proboscis = new THREE.Mesh(proboscisGeo, chitinMat);
    proboscis.position.set(0, -0.22, 0.08);
    proboscis.rotation.x = 0.35;
    this.head.add(proboscis);

    // 6. Neural Sparks (inside head capsule)
    const sparkGeo = new THREE.BufferGeometry();
    const sparkCount = 64;
    const positions = new Float32Array(sparkCount * 3);
    const colors = new Float32Array(sparkCount * 3);

    for (let i = 0; i < sparkCount; i++) {
      positions[i * 3 + 0] = (Math.random() - 0.5) * 0.28;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 0.22;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 0.22;

      // Cyan / Golden bio-luminescence
      colors[i * 3 + 0] = 0.0;
      colors[i * 3 + 1] = 0.95;
      colors[i * 3 + 2] = 0.85;
    }

    sparkGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    sparkGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const sparkMat = new THREE.PointsMaterial({
      size: 0.04,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
    });
    this.brainSparkSystem = new THREE.Points(sparkGeo, sparkMat);
    this.head.add(this.brainSparkSystem);

    this.flyGroup.add(this.head);

    // 7. Wings (Translucent with venation silhouette)
    const wingGeo = new THREE.PlaneGeometry(0.48, 1.25);
    wingGeo.translate(0, 0.6, 0); // Rotate from base hinge

    this.leftWing = new THREE.Mesh(wingGeo, wingMat);
    this.leftWing.position.set(-0.16, 0.28, -0.15);
    this.leftWing.rotation.set(Math.PI / 2 - 0.1, -0.4, 0.3);
    this.leftWing.castShadow = true;
    this.flyGroup.add(this.leftWing);

    this.rightWing = new THREE.Mesh(wingGeo, wingMat);
    this.rightWing.position.set(0.16, 0.28, -0.15);
    this.rightWing.rotation.set(Math.PI / 2 - 0.1, 0.4, -0.3);
    this.rightWing.castShadow = true;
    this.flyGroup.add(this.rightWing);

    // 8. Six Articulated Legs
    this.legs = [];
    const legConfigs = [
      { side: -1, z: 0.22, name: 'pro_L' },
      { side: 1, z: 0.22, name: 'pro_R' },
      { side: -1, z: -0.02, name: 'meso_L' },
      { side: 1, z: -0.02, name: 'meso_R' },
      { side: -1, z: -0.28, name: 'meta_L' },
      { side: 1, z: -0.28, name: 'meta_R' },
    ];

    const legMat = new THREE.MeshStandardMaterial({
      color: 0x24170d,
      roughness: 0.5,
    });

    for (let i = 0; i < legConfigs.length; i++) {
      const cfg = legConfigs[i];
      const legRoot = new THREE.Group();
      legRoot.position.set(cfg.side * 0.26, -0.12, cfg.z);

      // Femur
      const femurGeo = new THREE.CylinderGeometry(0.025, 0.02, 0.38, 8);
      femurGeo.translate(0, -0.19, 0);
      const femur = new THREE.Mesh(femurGeo, legMat);
      femur.rotation.z = cfg.side * 0.7;
      femur.rotation.x = (cfg.z > 0 ? 0.3 : -0.3);

      // Tibia / Tarsus
      const tibiaGeo = new THREE.CylinderGeometry(0.018, 0.012, 0.45, 8);
      tibiaGeo.translate(0, -0.22, 0);
      const tibia = new THREE.Mesh(tibiaGeo, legMat);
      tibia.position.set(0, -0.36, 0);
      tibia.rotation.z = -cfg.side * 0.9;
      femur.add(tibia);

      legRoot.add(femur);
      this.flyGroup.add(legRoot);

      this.legs.push({
        group: legRoot,
        femur: femur,
        side: cfg.side,
        phase: i * 1.05,
        defaultRotZ: femur.rotation.z,
      });
    }

    this.scene.add(this.flyGroup);
  }

  _buildVirtualSmartphone() {
    // 3D Smartphone held at 35° tilt directly in front of the fly
    const phoneGroup = new THREE.Group();
    phoneGroup.position.set(0, 1.25, 1.35);
    phoneGroup.rotation.x = -0.35; // Tilted towards the fly's compound eyes

    // Phone body chassis
    const bodyGeo = new THREE.BoxGeometry(0.85, 1.5, 0.06);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0x111622,
      roughness: 0.25,
      metalness: 0.85,
    });
    const phoneBody = new THREE.Mesh(bodyGeo, bodyMat);
    phoneBody.castShadow = true;
    phoneGroup.add(phoneBody);

    // Screen mapped from HTML5 Canvas texture
    this.phoneTexture = new THREE.CanvasTexture(this.stimulusCanvas);
    this.phoneTexture.minFilter = THREE.LinearFilter;
    this.phoneTexture.magFilter = THREE.LinearFilter;

    const screenGeo = new THREE.PlaneGeometry(0.78, 1.42);
    const screenMat = new THREE.MeshBasicMaterial({
      map: this.phoneTexture,
      toneMapped: false,
    });
    this.phoneScreenMesh = new THREE.Mesh(screenGeo, screenMat);
    this.phoneScreenMesh.position.z = 0.032;
    phoneGroup.add(this.phoneScreenMesh);

    // Screen light casting glow directly onto fly's eyes
    this.phoneLight = new THREE.PointLight(0xff2255, 1.5, 2.5);
    this.phoneLight.position.set(0, 0, 0.2);
    phoneGroup.add(this.phoneLight);

    // Modern smartphone camera notch & speaker slit
    const notchGeo = new THREE.BoxGeometry(0.18, 0.04, 0.02);
    const notchMat = new THREE.MeshBasicMaterial({ color: 0x05070a });
    const notch = new THREE.Mesh(notchGeo, notchMat);
    notch.position.set(0, 0.68, 0.033);
    phoneGroup.add(notch);

    this.scene.add(phoneGroup);
  }

  _setupEventListeners() {
    window.addEventListener('resize', () => {
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      if (w && h && this.camera && this.renderer) {
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
      }
    });

    // Camera view toggle buttons
    const btnFly = document.getElementById('view-fly');
    const btnPhone = document.getElementById('view-phone');
    const btnBrain = document.getElementById('view-brain');

    if (btnFly) {
      btnFly.addEventListener('click', () => {
        this._setCameraPreset('fly');
        this._updateViewButtons(btnFly);
      });
    }
    if (btnPhone) {
      btnPhone.addEventListener('click', () => {
        this._setCameraPreset('phone');
        this._updateViewButtons(btnPhone);
      });
    }
    if (btnBrain) {
      btnBrain.addEventListener('click', () => {
        this._setCameraPreset('brain');
        this._updateViewButtons(btnBrain);
      });
    }
  }

  _updateViewButtons(activeBtn) {
    document.querySelectorAll('.view-toggle-btn').forEach(btn => btn.classList.remove('active'));
    activeBtn.classList.add('active');
  }

  _setCameraPreset(preset) {
    if (!this.camera || !this.controls) return;

    if (preset === 'fly') {
      // Perspective viewing fly and phone together
      this.camera.position.set(1.8, 2.2, 3.4);
      this.controls.target.set(0, 1.1, 0.4);
    } else if (preset === 'phone') {
      // Over the fly's shoulder looking at the phone screen
      this.camera.position.set(0, 1.45, -0.4);
      this.controls.target.set(0, 1.25, 1.35);
    } else if (preset === 'brain') {
      // Close up macro view into the fly's head capsule
      this.camera.position.set(0.4, 1.3, 0.95);
      this.controls.target.set(0, 1.15, 0.55);
    }
  }

  updateFromTelemetry(telemetry) {
    if (!telemetry) return;

    const motor = telemetry.motor || {};
    this.forwardDrive = (motor.forward_drive_pct || 0) / 100;
    this.steeringDeflection = motor.steering_deflection || 0;

    // Check Giant Fiber escape jump reflex
    if (motor.giant_fiber_jump && !this.jumpTriggered) {
      this.jumpTriggered = true;
      this.jumpVy = 0.16; // Upward impulse
    }

    // Update brain spark particles intensity
    const totalSpikes = telemetry.spike_counts?.total_spikes || 0;
    if (this.brainSparkSystem) {
      const p = this.brainSparkSystem.geometry.attributes.position;
      const count = p.count;
      for (let i = 0; i < count; i++) {
        if (Math.random() < Math.min(totalSpikes / 60, 0.4)) {
          p.setY(i, (Math.random() - 0.5) * 0.26);
        }
      }
      p.needsUpdate = true;
      this.brainSparkSystem.material.size = 0.03 + Math.min(totalSpikes * 0.001, 0.06);
    }

    // Dynamic phone light color based on stimulus
    if (this.phoneLight && telemetry.hormones) {
      const da = telemetry.hormones.dopamine_nm || 5.0;
      const oa = telemetry.hormones.octopamine_nm || 2.0;
      if (oa > 4.5) {
        this.phoneLight.color.setHex(0xff1122); // High stress threat
      } else if (da > 8.0) {
        this.phoneLight.color.setHex(0x00f0ff); // Rewarding
      } else {
        this.phoneLight.color.setHex(0x22cc88); // Natural
      }
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    const dt = this.clock.getDelta();
    const time = this.clock.getElapsedTime();

    // 1. Update phone screen texture
    if (this.phoneTexture) {
      this.phoneTexture.needsUpdate = true;
    }

    // 2. Animate legs according to tripod gait & forward drive
    if (this.legs && this.legs.length) {
      const stepFreq = 4.0 + this.forwardDrive * 12.0;
      for (const leg of this.legs) {
        const angle = Math.sin(time * stepFreq + leg.phase) * (0.15 + this.forwardDrive * 0.25);
        leg.femur.rotation.x = angle + (leg.side * this.steeringDeflection * 0.3);
      }
    }

    // 3. Rotate treadmill sphere under fly's feet
    if (this.treadmillBall) {
      this.treadmillBall.rotation.x += this.forwardDrive * 0.08;
      this.treadmillBall.rotation.y += this.steeringDeflection * 0.04;
    }

    // 4. Wing flutter
    if (this.leftWing && this.rightWing) {
      if (this.jumpTriggered || this.forwardDrive > 0.6) {
        const flutter = Math.sin(time * 65) * 0.45;
        this.leftWing.rotation.z = 0.3 + flutter;
        this.rightWing.rotation.z = -0.3 - flutter;
      } else {
        // Subtle resting breath
        const breath = Math.sin(time * 3) * 0.04;
        this.leftWing.rotation.z = 0.2 + breath;
        this.rightWing.rotation.z = -0.2 - breath;
      }
    }

    // 5. Giant Fiber Escape Jump Physics
    if (this.jumpTriggered) {
      this.jumpY += this.jumpVy;
      this.jumpVy -= 0.009; // Gravity
      if (this.jumpY <= 0) {
        this.jumpY = 0;
        this.jumpVy = 0;
        this.jumpTriggered = false;
      }
      this.flyGroup.position.y = 1.05 + this.jumpY;
      this.flyGroup.position.z = -this.jumpY * 0.8; // Backward leap!
    } else {
      this.flyGroup.position.y = 1.05;
      this.flyGroup.position.z = 0;
    }

    // 6. Abdomen breathing contraction
    if (this.abdomen) {
      const abdPulse = 1.0 + Math.sin(time * 4) * 0.03;
      this.abdomen.scale.set(0.8 * abdPulse, 0.75 * abdPulse, 1.6);
    }

    // 7. Update Controls & Render
    if (this.controls) {
      this.controls.update();
    }

    this.renderer.render(this.scene, this.camera);
  }
}

// ============================================================================
// 3. CENTRAL COMPLEX (EPG) COMPASS & NEUROCHEMICAL COCKPIT VISUALIZERS
// ============================================================================

class CockpitVisualizers {
  constructor() {
    this.compassCanvas = document.getElementById('compass-canvas');
    this.compassCtx = this.compassCanvas.getContext('2d');

    this.dopamineCanvas = document.getElementById('dopamine-chart');
    this.dopamineCtx = this.dopamineCanvas.getContext('2d');

    this.rasterCanvas = document.getElementById('raster-canvas');
    this.rasterCtx = this.rasterCanvas.getContext('2d');

    this.headingDeg = 0;
  }

  drawEPGCompass(headingDeg = 0) {
    this.headingDeg = headingDeg;
    const ctx = this.compassCtx;
    const w = this.compassCanvas.width;
    const h = this.compassCanvas.height;
    const cx = w / 2;
    const cy = h / 2;
    const radius = 38;

    ctx.clearRect(0, 0, w, h);

    // Background circle
    ctx.fillStyle = 'rgba(10, 15, 25, 0.85)';
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fill();

    // 16 Wedge sectors of Protocerebral Bridge (PB) / Ellipsoid Body (EB)
    const sectors = 16;
    for (let i = 0; i < sectors; i++) {
      const a1 = (i / sectors) * Math.PI * 2;
      const a2 = ((i + 1) / sectors) * Math.PI * 2;
      const sectorDeg = (i / sectors) * 360;

      // Angular distance to active compass heading
      const diff = Math.abs((((sectorDeg - headingDeg) + 180) % 360) - 180);
      const intensity = Math.max(0.1, 1.0 - diff / 60);

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, radius - 4, a1, a2);
      ctx.closePath();
      ctx.fillStyle = `rgba(0, 240, 255, ${intensity * 0.85})`;
      ctx.fill();

      // Divider line
      ctx.strokeStyle = 'rgba(20, 30, 45, 0.9)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Outer Neon Ring
    ctx.strokeStyle = '#00f0ff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.stroke();

    // Active Compass Needle (Ring Attractor Bump)
    const rad = (headingDeg - 90) * (Math.PI / 180);
    const nx = cx + Math.cos(rad) * (radius - 8);
    const ny = cy + Math.sin(rad) * (radius - 8);

    ctx.strokeStyle = '#ff9d00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(nx, ny);
    ctx.stroke();

    // Center hub
    ctx.fillStyle = '#ff9d00';
    ctx.beginPath();
    ctx.arc(cx, cy, 3.5, 0, Math.PI * 2);
    ctx.fill();
  }

  drawDopamineWaveform(history = []) {
    const ctx = this.dopamineCtx;
    const w = this.dopamineCanvas.width;
    const h = this.dopamineCanvas.height;

    ctx.clearRect(0, 0, w, h);

    // Dark grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.lineWidth = 1;
    for (let y = 20; y < h; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    if (!history || history.length < 2) return;

    // Plot dopamine Hz curve
    const maxHz = Math.max(40, ...history.map(pt => pt.dopamine_hz || 0));
    const stepX = w / (history.length - 1);

    // Fill gradient
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, 'rgba(255, 157, 0, 0.35)');
    grad.addColorStop(1, 'rgba(255, 157, 0, 0.0)');

    ctx.beginPath();
    ctx.moveTo(0, h);

    for (let i = 0; i < history.length; i++) {
      const x = i * stepX;
      const val = history[i].dopamine_hz || 0;
      const y = h - (val / maxHz) * (h - 10) - 5;
      if (i === 0) ctx.lineTo(x, y);
      else ctx.lineTo(x, y);
    }

    ctx.lineTo((history.length - 1) * stepX, h);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Stroke line
    ctx.strokeStyle = '#ff9d00';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < history.length; i++) {
      const x = i * stepX;
      const val = history[i].dopamine_hz || 0;
      const y = h - (val / maxHz) * (h - 10) - 5;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  drawSpikeRaster(history = []) {
    const ctx = this.rasterCtx;
    const w = this.rasterCanvas.width;
    const h = this.rasterCanvas.height;

    ctx.clearRect(0, 0, w, h);

    if (!history || !history.length) return;

    const cols = history.length;
    const colWidth = w / cols;
    const rows = 32;
    const rowHeight = h / rows;

    for (let c = 0; c < cols; c++) {
      const pt = history[c];
      const spikes = pt.total_spikes || 0;
      const x = c * colWidth;

      // Deterministic pseudo-raster visualization from spike count
      const activeUnits = Math.min(rows, Math.floor(spikes / 3));
      for (let r = 0; r < activeUnits; r++) {
        const neuronId = (r * 17 + c * 7) % rows;
        const y = neuronId * rowHeight;

        ctx.fillStyle = (r % 3 === 0) ? '#00f0ff' : '#00ff88';
        ctx.fillRect(x, y, Math.max(1.5, colWidth - 0.5), rowHeight - 0.8);
      }
    }
  }
}

// ============================================================================
// 4. BIDIRECTIONAL TELEMETRY & ENGINE ORCHESTRATOR
// ============================================================================

class ConnectomeApp {
  constructor() {
    this.stimulus = new StimulusGenerator('virtual-phone-canvas');
    this.chamber = new ObservationChamber3D('three-container', this.stimulus.canvas);
    this.visualizers = new CockpitVisualizers();

    this.ws = null;
    this.isStreaming = false;
    this.frameInterval = null;

    this._initDomBindings();
    this._initWebSocket();
    this._startObservationLoop();
  }

  _initDomBindings() {
    // Stimulus buttons
    document.querySelectorAll('.stim-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.stim-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const preset = btn.getAttribute('data-preset');
        this.stimulus.setPreset(preset);
      });
    });

    // Wirehead button (+20 mV dopamine surge)
    const wireheadBtn = document.getElementById('wirehead-btn');
    if (wireheadBtn) {
      wireheadBtn.addEventListener('click', () => {
        this.triggerWirehead(20.0);
      });
    }

    // Looming threat button
    const threatBtn = document.getElementById('threat-btn');
    if (threatBtn) {
      threatBtn.addEventListener('click', () => {
        this.stimulus.triggerLoomingPulse();
      });
    }
  }

  _initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || '127.0.0.1:8000';
    const wsUrl = `${protocol}//${host}/ws/telemetry`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[Connectome WS] Connected to biophysical engine');
        const statusEl = document.getElementById('engine-status');
        if (statusEl) statusEl.textContent = '60 FPS LIVE';
      };

      this.ws.onmessage = (event) => {
        try {
          const snapshot = JSON.parse(event.data);
          this._handleTelemetrySnapshot(snapshot);
        } catch (err) {
          console.error('[Connectome WS] Parse error:', err);
        }
      };

      this.ws.onerror = (err) => {
        console.warn('[Connectome WS] WebSocket error, fallback to REST observe:', err);
      };

      this.ws.onclose = () => {
        console.log('[Connectome WS] Disconnected. Reconnecting in 2s...');
        setTimeout(() => this._initWebSocket(), 2000);
      };
    } catch (e) {
      console.warn('[Connectome WS] WebSocket init failed:', e);
    }
  }

  _startObservationLoop() {
    // 20 FPS observation loop (every 50ms matching biological simulation chunk)
    setInterval(() => {
      // 1. Render stimulus canvas frame
      this.stimulus.render(0.05);

      // 2. Transmit frame to engine
      const frameB64 = this.stimulus.getBase64Frame();

      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          command: 'observe',
          image_base64: frameB64,
          duration_ms: 50.0,
        }));
      } else {
        // Fallback REST endpoint
        fetch('/api/observe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: frameB64,
            duration_ms: 50.0,
          }),
        })
          .then(res => res.json())
          .then(data => this._handleTelemetrySnapshot(data))
          .catch(() => {});
      }
    }, 50);
  }

  triggerWirehead(currentMv = 20.0) {
    console.log(`[Connectome] Injecting +${currentMv} mV dopamine wirehead`);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        command: 'wirehead',
        current_mv: currentMv,
      }));
    } else {
      fetch('/api/wirehead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_mv: currentMv }),
      }).catch(err => console.error(err));
    }
  }

  _handleTelemetrySnapshot(snapshot) {
    if (!snapshot || !snapshot.latest) return;
    const t = snapshot.latest;

    // 1. Update 3D Chamber
    this.chamber.updateFromTelemetry(t);

    // 2. Header metrics
    document.getElementById('sim-time').textContent = `${(t.sim_time_ms || 0).toFixed(1)} ms`;
    document.getElementById('total-spikes').textContent = (t.spike_counts?.total_spikes || 0).toLocaleString();

    // 3. Hormones
    const h = t.hormones || {};
    const da = h.dopamine_nm || 5.0;
    const oa = h.octopamine_nm || 2.0;
    const st = h.serotonin_nm || 8.0;

    const daHz = t.spike_counts?.dopamine_hz || 0;
    const oaHz = t.spike_counts?.octopamine_hz || 0;
    const stHz = t.spike_counts?.serotonin_hz || 0;

    document.getElementById('da-hz').textContent = daHz.toFixed(1);
    document.getElementById('da-nm').textContent = da.toFixed(2);
    document.getElementById('da-fill').style.width = `${Math.min(100, (da / 35) * 100)}%`;

    document.getElementById('oa-hz').textContent = oaHz.toFixed(1);
    document.getElementById('oa-nm').textContent = oa.toFixed(2);
    document.getElementById('oa-fill').style.width = `${Math.min(100, (oa / 30) * 100)}%`;

    document.getElementById('st-hz').textContent = stHz.toFixed(1);
    document.getElementById('st-nm').textContent = st.toFixed(2);
    document.getElementById('st-fill').style.width = `${Math.min(100, (st / 25) * 100)}%`;

    // 4. Motor Decoders
    const m = t.motor || {};
    const steer = m.steering_deflection || 0;
    const drive = m.forward_drive_pct || 0;

    document.getElementById('steering-val').textContent = (steer >= 0 ? '+' : '') + steer.toFixed(2);
    const steerPercent = 50 + (steer * 45);
    document.getElementById('steering-indicator').style.left = `${Math.max(5, Math.min(95, steerPercent))}%`;

    document.getElementById('drive-val').textContent = `${drive.toFixed(0)}%`;
    document.getElementById('drive-fill').style.width = `${Math.max(0, Math.min(100, drive))}%`;

    // Alert pills
    const badgeRetreat = document.getElementById('badge-retreat');
    if (badgeRetreat) {
      if (m.moonwalker_retreat) badgeRetreat.classList.add('active');
      else badgeRetreat.classList.remove('active');
    }

    const badgeJump = document.getElementById('badge-jump');
    if (badgeJump) {
      if (m.giant_fiber_jump) badgeJump.classList.add('active');
      else badgeJump.classList.remove('active');
    }

    // EPG Compass
    const heading = m.compass_heading_deg || 0;
    document.getElementById('heading-deg').textContent = `${heading.toFixed(1)}°`;
    this.visualizers.drawEPGCompass(heading);

    // Plasticity index
    const plast = h.plasticity_index || 0;
    document.getElementById('plasticity-val').textContent = (plast >= 0 ? '+' : '') + plast.toFixed(3);

    // Charts
    if (snapshot.history) {
      this.visualizers.drawDopamineWaveform(snapshot.history);
      this.visualizers.drawSpikeRaster(snapshot.history);
    }
  }

  start() {
    this.chamber.animate();
  }
}

// Bootstrap on DOM ready
window.addEventListener('DOMContentLoaded', () => {
  window.app = new ConnectomeApp();
  window.app.start();
});
