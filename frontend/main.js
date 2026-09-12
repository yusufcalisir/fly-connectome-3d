/**
 * FlyConnectome 3D - High-Fidelity Photorealistic Electrophysiology Rig & Fly Rig
 *
 * Implements:
 * 1. Procedural High-Fidelity Drosophila Melanogaster:
 *    - Anatomical chitin cuticle with clearcoat & setae (sensory bristles)
 *    - Hexagonal ommatidial facet bump-mapped compound eyes
 *    - Authentic wing venation (Costa, R, M, Cu crossveins)
 *    - Feathered aristae antennae, articulated proboscis, and 5-segment jointed legs
 * 2. Real Electrophysiology Laboratory Rig:
 *    - Stainless steel optical breadboard table with tapped M6 hole grid
 *    - Air-cushioned spherical treadmill with flotation nozzle & dual optical sensors
 *    - Micromanipulator stage with glass recording micropipette
 *    - Overhead stereomicroscope turret with fiber-optic LED ring illuminator
 * 3. Corrected Virtual Smartphone:
 *    - Display quad directly facing the fly's ommatidia
 *    - Dynamic retinal light casting screen photons onto the fly's face
 *    - Angled 3/4 perspective allowing simultaneous view of screen image & fly
 * 4. 3D Neuropils (Optic Lobes, Mushroom Body, Central Complex, Giant Fiber Tract)
 * 5. Internationalization (i18n): Sleek EN / TR language switcher
 */

// ============================================================================
// 0. INTERNATIONALIZATION (i18n) DICTIONARY
// ============================================================================

const TRANSLATIONS = {
  en: {
    header_engine: 'ENGINE:',
    header_sim_time: 'SIM TIME:',
    header_spikes: 'TOTAL SPIKES:',
    panel_stimulus: 'STIMULUS ARENA',
    tag_phone_feed: 'Virtual Phone Feed',
    label_presets: 'Select Stimulus Preset:',
    preset_fruit: '🍉 Sugar Fruit (Appetitive)',
    preset_shadow: '⚠️ Looming Shadow (Panic)',
    preset_spider: '🕷️ Predatory Spider (Threat)',
    preset_foliage: '🌿 Forest Foliage (Calm)',
    preset_upload: '📷 Upload Custom Photo',
    label_target_pos: 'Spatial Target Position (Phototaxis):',
    pos_left: 'Left',
    pos_center: 'Center',
    pos_right: 'Right',
    btn_wirehead_title: 'WIREHEAD',
    btn_wirehead_sub: 'Inject +20mV Dopamine',
    btn_threat_title: 'LOOM THREAT',
    btn_threat_sub: 'Trigger Giant Fiber',
    btn_swipe_title: 'LEG SWIPE',
    btn_swipe_sub: 'Front-Leg Screen Touch',
    title_motor: 'DESCENDING MOTOR OUTPUTS',
    title_vnc_hexapod: 'VNC THORACIC HEXAPOD GAIT',
    tag_vnc_cpg: 'CPG Alternating Tripod',
    label_steering: 'Steering (DNa02 L/R):',
    label_retinal_asym: 'Retinal Asymmetry (L/R):',
    label_drive: 'Forward Drive (DNp09):',
    pill_retreat: 'MDN MOONWALKER',
    pill_jump: 'GIANT FIBER JUMP',
    compass_title: 'CENTRAL COMPLEX (EPG)',
    view_fly: 'Fly View',
    view_phone: 'Phone Angle',
    view_brain: 'Neural Synapses',
    panel_cockpit: 'NEUROCHEMICAL COCKPIT',
    tag_kinetics: 'Kinetics',
    h_da: 'DOPAMINE (PAM11)',
    h_da_hint: 'Appetitive reward, pleasure & associative plasticity',
    h_oa: 'OCTOPAMINE (TDC2)',
    h_oa_hint: 'Insect adrenaline, acute stress & fight-or-flight',
    h_st: 'SEROTONIN (5-HT)',
    h_st_hint: 'Baseline calm, motor patience & satiety',
    h_ei: "E/I BALANCE (Dale's Law)",
    h_ei_hint: "Synaptic balance: ACh excitation vs GABA/Glu/Histamine inhibition",
    chart_dopamine: 'DOPAMINE WAVEFORM (Hz)',
    chart_raster: 'SPIKE RASTER STREAM (Matrix Waterfall)',
    chart_cns_activity: 'CNS / NEURAL ACTIVITY',
    cns_drag_hint: 'Drag to rotate 3D',
    badge_biophysics: 'MaleCNS v1.0 Biophysics',
    badge_somas: '141.8K Somas 3D',
    chart_scale_frames: '120 frames',
    chart_scale_landmarks: '64 landmarks',
    label_plasticity: 'Learned Association Drift (KC ──► MBON):',
    live_neural_activity: 'LIVE NEURAL ACTIVITY',
    dopamine_activity: 'DOPAMINE ACTIVITY',
    pam11_neurons_count: '15 PAM11 neurons',
    pam11_firing_rate: 'PAM11 FIRING RATE',
    octopamine_activity: 'OCTOPAMINE ACTIVITY',
    tdc2_neurons_count: 'TDC2 stress circuit',
    tdc2_firing_rate: 'TDC2 FIRING RATE',
    serotonin_activity: 'SEROTONIN ACTIVITY',
    serotonin_sub: '5-HT satiety / calm',
    serotonin_firing_rate: '5-HT FIRING RATE',
    ei_activity: 'E/I BALANCE',
    ei_sub: "Dale's Law: ACh vs GABA",
    ei_firing_rate: 'EXCITATION RATIO (E/I)',
    fly_spikes: 'FLY SPIKES',
    neural_time_sub: 'in 50 ms',
    h_da_short: 'DOPAMINE',
    h_oa_short: 'OCTOPAMINE',
    h_st_short: 'SEROTONIN',
    h_ei_short: 'E/I BALANCE',
    h_da_sub: 'Reward & Plasticity',
    h_oa_sub: 'Stress & Flight',
    h_st_sub: 'Satiety & Motor Calm',
    h_ei_sub: "Dale's Law: ACh vs GABA",
    nav_3d: '3D View',
    nav_stimulus: 'Stimulus',
    nav_cockpit: 'Cockpit',
  },
  tr: {
    header_engine: 'MOTOR:',
    header_sim_time: 'SİM SÜRESİ:',
    header_spikes: 'TOPLAM SPİKE:',
    badge_biophysics: 'MaleCNS v1.0 Biyofizik',
    badge_somas: '141.8K Gerçek Soma 3D',
    panel_stimulus: 'UYARAN ARENASI',
    tag_phone_feed: 'Sanal Telefon Yayını',
    label_presets: 'Uyaran Şablonu Seçin:',
    preset_fruit: '🍉 Şekerli Meyve (Ödül)',
    preset_shadow: '⚠️ Yaklaşan Gölge (Panik)',
    preset_spider: '🕷️ Avcı Örümcek (Tehdit)',
    preset_foliage: '🌿 Orman Yeşilliği (Dingin)',
    preset_upload: '📷 Özel Fotoğraf Yükle',
    label_target_pos: 'Uzamsal Hedef Konumu (Fototaksi):',
    pos_left: 'Sol',
    pos_center: 'Merkez',
    pos_right: 'Sağ',
    btn_wirehead_title: 'DOPAMİN ŞOKU',
    btn_wirehead_sub: '+20mV Dopamin Enjekte Et',
    btn_threat_title: 'AVCI TEHDİDİ',
    btn_threat_sub: 'Giant Fiber Refleksi',
    btn_swipe_title: 'BACAKLA KAYDIR',
    btn_swipe_sub: 'Ön Bacakla Ekrana Dokun',
    title_motor: 'İNEN MOTOR ÇIKTILARI',
    title_vnc_hexapod: 'VNC THORAKS HEKSAPOD YÜRÜYÜŞÜ',
    tag_vnc_cpg: 'CPG Alternatif Tripod',
    label_steering: 'Dümenleme (DNa02 S/S):',
    label_retinal_asym: 'Retinal Asimetri (S/S):',
    label_drive: 'İleri Yürüyüş (DNp09):',
    pill_retreat: 'MDN GERİ YÜRÜYÜŞ',
    pill_jump: 'GİANT FİBER SIÇRAMA',
    compass_title: 'MERKEZİ KOMPLEKS (EPG)',
    view_fly: 'Sinek Görünümü',
    view_phone: 'Telefon Açısı',
    view_brain: 'Sinirsel Sinapslar',
    panel_cockpit: 'NÖROKİMYASAL KOKPİT',
    tag_kinetics: 'Kinetik',
    h_da: 'DOPAMİN (PAM11)',
    h_da_hint: 'Ödül, haz ve ilişkisel plastisite',
    h_oa: 'OKTOPAMİN (TDC2)',
    h_oa_hint: 'Böcek adrenalini, ani stres ve kaçış',
    h_st: 'SEROTONİN (5-HT)',
    h_st_hint: 'Dinginlik, hareket sabrı ve tokluk',
    h_ei: "E/I DENGESİ (Dale Yasası)",
    h_ei_hint: "Sinaptik denge: Asetilkolin eksitasyonu vs GABA/Glutamat/Histamin inhibisyonu",
    chart_dopamine: 'DOPAMİN DALGA FORMU (Hz)',
    chart_raster: 'SPİKE ŞELALESİ (Matris Akışı)',
    chart_cns_activity: 'CNS / CANLI SİNİRSEL AKTİVİTE',
    cns_drag_hint: '3D döndürmek için sürükleyin',
    label_plasticity: 'Öğrenilmiş Çağrışım Kayması (KC ──► MBON):',
    live_neural_activity: 'CANLI NÖRAL AKTİVİTE',
    dopamine_activity: 'DOPAMİN AKTİVİTESİ',
    pam11_neurons_count: '15 PAM11 nöronu',
    pam11_firing_rate: 'PAM11 ATEŞLEME HIZI',
    octopamine_activity: 'OKTOPAMİN AKTİVİTESİ',
    tdc2_neurons_count: 'TDC2 stres devresi',
    tdc2_firing_rate: 'TDC2 ATEŞLEME HIZI',
    serotonin_activity: 'SEROTONİN AKTİVİTESİ',
    serotonin_sub: '5-HT doygunluk / sükunet',
    serotonin_firing_rate: '5-HT ATEŞLEME HIZI',
    ei_activity: 'E/I DENGESİ',
    ei_sub: 'Dale Yasası: ACh vs GABA',
    ei_firing_rate: 'UYANMA ORANI (E/I)',
    fly_spikes: 'SİNEK SPİKELARI',
    neural_time_sub: '50 ms içinde',
    h_da_short: 'DOPAMİN',
    h_oa_short: 'OKTOPAMİN',
    h_st_short: 'SEROTONİN',
    h_ei_short: 'E/I DENGESİ',
    h_da_sub: 'Ödül & Plastisite',
    h_oa_sub: 'Stres & Kaçış Refleksi',
    h_st_sub: 'Doygunluk & Motor Sabrı',
    h_ei_sub: 'Dale Yasası: ACh vs GABA',
    chart_scale_frames: '120 kare',
    chart_scale_landmarks: '64 referans',
    nav_3d: '3D Görünüm',
    nav_stimulus: 'Uyaran',
    nav_cockpit: 'Kokpit',
  },
};

// ============================================================================
// 1. PROCEDURAL TEXTURE GENERATORS
// ============================================================================

function generateWingTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 1024;
  const ctx = canvas.getContext('2d');

  ctx.clearRect(0, 0, 512, 1024);

  const grad = ctx.createLinearGradient(0, 0, 512, 1024);
  grad.addColorStop(0, 'rgba(215, 235, 255, 0.45)');
  grad.addColorStop(0.5, 'rgba(230, 245, 255, 0.35)');
  grad.addColorStop(1, 'rgba(200, 225, 250, 0.3)');
  ctx.fillStyle = grad;

  ctx.beginPath();
  ctx.moveTo(256, 40);
  ctx.bezierCurveTo(460, 150, 490, 600, 360, 920);
  ctx.bezierCurveTo(280, 1000, 200, 980, 120, 850);
  ctx.bezierCurveTo(40, 600, 60, 220, 256, 40);
  ctx.fill();

  ctx.strokeStyle = 'rgba(60, 40, 25, 0.85)';
  ctx.lineWidth = 7;
  ctx.stroke();

  ctx.strokeStyle = 'rgba(75, 50, 30, 0.75)';
  ctx.lineWidth = 4;

  // L1
  ctx.beginPath();
  ctx.moveTo(256, 50);
  ctx.quadraticCurveTo(340, 250, 420, 450);
  ctx.stroke();

  // L2
  ctx.beginPath();
  ctx.moveTo(256, 50);
  ctx.quadraticCurveTo(320, 350, 380, 720);
  ctx.stroke();

  // L3 (Central stem)
  ctx.beginPath();
  ctx.moveTo(256, 50);
  ctx.quadraticCurveTo(280, 450, 300, 930);
  ctx.stroke();

  // L4
  ctx.beginPath();
  ctx.moveTo(256, 50);
  ctx.quadraticCurveTo(220, 400, 200, 900);
  ctx.stroke();

  // L5
  ctx.beginPath();
  ctx.moveTo(240, 80);
  ctx.quadraticCurveTo(140, 400, 130, 760);
  ctx.stroke();

  // Crossveins
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(270, 420);
  ctx.lineTo(225, 450);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(285, 620);
  ctx.lineTo(210, 650);
  ctx.stroke();

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  return texture;
}

function generateOmmatidiaTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#808080';
  ctx.fillRect(0, 0, 256, 256);

  const r = 8;
  const h = r * Math.sqrt(3);
  ctx.strokeStyle = '#202020';
  ctx.lineWidth = 1.5;

  for (let y = -h; y < 256 + h; y += h) {
    for (let x = -r * 3; x < 256 + r * 3; x += r * 3) {
      drawHex(ctx, x, y, r);
      drawHex(ctx, x + 1.5 * r, y + h / 2, r);
    }
  }

  function drawHex(c, cx, cy, rad) {
    c.beginPath();
    for (let i = 0; i < 6; i++) {
      const a = (i * Math.PI) / 3;
      const hx = cx + rad * Math.cos(a);
      const hy = cy + rad * Math.sin(a);
      if (i === 0) c.moveTo(hx, hy);
      else c.lineTo(hx, hy);
    }
    c.closePath();
    c.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(6, 6);
  return texture;
}

function generateBreadboardTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = '#14171d';
  ctx.fillRect(0, 0, 512, 512);

  ctx.fillStyle = 'rgba(255, 255, 255, 0.025)';
  for (let i = 0; i < 600; i++) {
    const y = Math.random() * 512;
    ctx.fillRect(0, y, 512, 1);
  }

  const step = 64;
  for (let y = step / 2; y < 512; y += step) {
    for (let x = step / 2; x < 512; x += step) {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.beginPath();
      ctx.arc(x, y, 9, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#06080b';
      ctx.beginPath();
      ctx.arc(x, y, 7, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(6, 6);
  return texture;
}

// ============================================================================
// 2. STIMULUS GENERATOR (VIRTUAL PHONE DISPLAY)
// ============================================================================

class StimulusGenerator {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.preset = 'neutral'; // Default: Forest Foliage (Calm baseline)
    this.time = 0;
    this.loomingProgress = 0;
    this.isLoomingActive = false;
    this.customImage = null;
    this.customImageValence = null;
    this.targetPosition = 'center';
    this.targetOffsetFactor = 0.0;
    this.targetOffsetCurrent = 0.0;

    this.presetsInfo = {
      fruit: {
        title: { en: 'Sweet Ripe Watermelon', tr: 'Tatlı Olgun Karpuz' },
        desc: { en: 'High-sugar olfactory & visual chromatic target.', tr: 'Yüksek şekerli koku ve görsel kromatofor hedefi.' },
        tag: { en: 'APPETITIVE', tr: 'ÖDÜL' },
        tagClass: 'appetitive',
      },
      shadow: {
        title: { en: 'Looming Predator Disc', tr: 'Yaklaşan Avcı Diski' },
        desc: { en: 'Rapidly expanding visual shadow triggering LC4 threat circuits.', tr: 'LC4 tehdit devrelerini tetikleyen genişleyen gölge.' },
        tag: { en: 'LOOM THREAT', tr: 'AVCI TEHDİDİ' },
        tagClass: 'threat',
      },
      spider: {
        title: { en: 'Predatory Spider', tr: 'Avcı Örümcek' },
        desc: { en: 'High-contrast predatory threat with arachnid appendages.', tr: 'Eklem bacaklı uzantılara sahip yüksek kontrastlı avcı.' },
        tag: { en: 'PREDATOR', tr: 'AVCI' },
        tagClass: 'threat',
      },
      neutral: {
        title: { en: 'Forest Foliage Canopy', tr: 'Orman Yeşilliği Örtüsü' },
        desc: { en: 'Ambient natural green leaves providing calm baseline input.', tr: 'Dingin taban çizgisi sağlayan doğal yeşil yapraklar.' },
        tag: { en: 'BASELINE', tr: 'DİNGİN' },
        tagClass: '',
      },
      custom: {
        title: { en: 'Custom User Photo', tr: 'Özel Kullanıcı Fotoğrafı' },
        desc: { en: 'User-provided visual stimulus mapped directly onto retina.', tr: 'Doğrudan retinaya yansıtılan kullanıcı görseli.' },
        tag: { en: 'CUSTOM', tr: 'ÖZEL' },
        tagClass: '',
      },
    };

    // Sync card info immediately on construction so overlay text matches canvas
    // (called after presetsInfo is defined so updateCardInfo can read it)
    this.updateCardInfo();
  }

  setPreset(preset) {
    if (this.presetsInfo[preset]) {
      this.preset = preset;
      this.loomingProgress = 0;
      this.isLoomingActive = preset === 'shadow';
      this.updateCardInfo();
    }
  }

  setPosition(pos) {
    if (pos === 'left') {
      this.targetPosition = 'left';
      this.targetOffsetFactor = -1.0;
    } else if (pos === 'right') {
      this.targetPosition = 'right';
      this.targetOffsetFactor = 1.0;
    } else {
      this.targetPosition = 'center';
      this.targetOffsetFactor = 0.0;
    }
  }

  updateCardInfo() {
    const lang = window.currentLang || 'en';
    const info = this.presetsInfo[this.preset];
    if (!info) return;

    if (this.preset === 'custom' && this.customImageValence) {
      const v = this.customImageValence;
      const tagText = typeof v.tag === 'object' ? v.tag[lang] : v.tag;
      const descText = typeof v.desc === 'object' ? v.desc[lang] : v.desc;
      document.getElementById('current-photo-desc').textContent = descText;
      const tagEl = document.getElementById('stimulus-type-tag');
      tagEl.textContent = tagText;
      tagEl.className = 'overlay-tag ' + v.tagClass;
      return;
    }

    const title = typeof info.title === 'object' ? info.title[lang] : info.title;
    const desc = typeof info.desc === 'object' ? info.desc[lang] : info.desc;
    const tag = typeof info.tag === 'object' ? info.tag[lang] : info.tag;

    document.getElementById('current-photo-title').textContent = title;
    document.getElementById('current-photo-desc').textContent = desc;
    const tagEl = document.getElementById('stimulus-type-tag');
    tagEl.textContent = tag;
    tagEl.className = 'overlay-tag ' + info.tagClass;
  }

  loadCustomImage(imgElement, fileName = 'User Upload') {
    this.customImage = imgElement;
    this.preset = 'custom';
    this.loomingProgress = 0;
    this.isLoomingActive = false;

    this._analyzeSpectralValence(imgElement);

    document.getElementById('current-photo-title').textContent = fileName;
    this.updateCardInfo();
  }

  _analyzeSpectralValence(img) {
    const scratch = document.createElement('canvas');
    scratch.width = 90;
    scratch.height = 160;
    const sctx = scratch.getContext('2d');
    sctx.drawImage(img, 0, 0, 90, 160);
    const data = sctx.getImageData(0, 0, 90, 160).data;

    let totalR = 0,
      totalG = 0,
      totalB = 0;
    let totalLum = 0;
    const count = data.length / 4;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      totalR += r;
      totalG += g;
      totalB += b;
      totalLum += 0.299 * r + 0.587 * g + 0.114 * b;
    }

    const meanR = totalR / count;
    const meanG = totalG / count;
    const meanLum = totalLum / count;

    if (meanR > 1.25 * meanG && meanR > 80) {
      this.customImageValence = {
        tag: { en: 'APPETITIVE CUE', tr: 'ÖDÜL İŞARETİ' },
        tagClass: 'appetitive',
        desc: {
          en: `Spectral: High red wavelength (R/G=${(meanR / Math.max(1, meanG)).toFixed(2)}). Triggers PAM11 reward pathway.`,
          tr: `Spektral: Yüksek kırmızı dalga boyu (K/Y=${(meanR / Math.max(1, meanG)).toFixed(2)}). PAM11 ödül yolunu uyarır.`,
        },
      };
    } else if (meanLum < 45) {
      this.customImageValence = {
        tag: { en: 'THREAT / LOOM', tr: 'TEHDİT / GÖLGE' },
        tagClass: 'threat',
        desc: {
          en: `Spectral: Low luminance (Y=${meanLum.toFixed(1)}). Triggers LC4 threat & Giant Fiber escape circuits.`,
          tr: `Spektral: Düşük parlaklık (Y=${meanLum.toFixed(1)}). LC4 tehdit ve Giant Fiber kaçış devrelerini tetikler.`,
        },
      };
    } else {
      this.customImageValence = {
        tag: { en: 'NATURAL CALM', tr: 'DOĞAL DİNGİNLİK' },
        tagClass: '',
        desc: {
          en: `Spectral: Balanced ambient spectrum (Y=${meanLum.toFixed(1)}). Promotes 5-HT serotonergic stability.`,
          tr: `Spektral: Dengeli ortam tayfı (Y=${meanLum.toFixed(1)}). 5-HT serotonin kararlılığını destekler.`,
        },
      };
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

    // Smoothly interpolate target position offset (-1.0 to +1.0)
    this.targetOffsetCurrent += (this.targetOffsetFactor - this.targetOffsetCurrent) * Math.min(1.0, dt * 10.0);
    const targetX = w / 2 + this.targetOffsetCurrent * (w * 0.28);

    ctx.save();
    ctx.clearRect(0, 0, w, h);

    switch (this.preset) {
      case 'fruit':
        this._renderFruit(ctx, w, h, targetX);
        break;
      case 'shadow':
        this._renderShadow(ctx, w, h, dt, targetX);
        break;
      case 'spider':
        this._renderSpider(ctx, w, h, targetX);
        break;
      case 'neutral':
        this._renderNeutral(ctx, w, h);
        break;
      case 'custom':
        this._renderCustom(ctx, w, h);
        break;
    }

    ctx.restore();
  }

  _renderFruit(ctx, w, h, targetX = w / 2) {
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, '#0c0512');
    bgGrad.addColorStop(1, '#1b081e');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    const aura = ctx.createRadialGradient(targetX, h / 2, 80, targetX, h / 2, 560);
    aura.addColorStop(0, 'rgba(255, 30, 80, 0.40)');
    aura.addColorStop(0.5, 'rgba(255, 30, 80, 0.15)');
    aura.addColorStop(1, 'rgba(255, 30, 80, 0.0)');
    ctx.fillStyle = aura;
    ctx.fillRect(0, 0, w, h);

    ctx.save();
    ctx.translate(targetX, h / 2 + 120);
    const bob = Math.sin(this.time * 2.5) * 24;
    ctx.translate(0, bob);

    // High-resolution vector watermelon slice
    // 1. Outer glossy green rind
    ctx.beginPath();
    ctx.arc(0, 0, 288, 0.15 * Math.PI, 0.85 * Math.PI, false);
    ctx.lineWidth = 72;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#156526';
    ctx.stroke();

    // 2. Inner crisp lime-white rind layer
    ctx.beginPath();
    ctx.arc(0, 0, 256, 0.16 * Math.PI, 0.84 * Math.PI, false);
    ctx.lineWidth = 32;
    ctx.strokeStyle = '#e2f7dd';
    ctx.stroke();

    // 3. Juicy crimson/coral gradient flesh
    const fleshGrad = ctx.createRadialGradient(0, 0, 40, 0, 0, 240);
    fleshGrad.addColorStop(0, '#ff1744');
    fleshGrad.addColorStop(0.8, '#f50057');
    fleshGrad.addColorStop(1, '#c51162');

    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, 240, 0.18 * Math.PI, 0.82 * Math.PI, false);
    ctx.closePath();
    ctx.fillStyle = fleshGrad;
    ctx.fill();

    // 4. Glossy seeds with specular highlights
    const seedCoords = [
      [-96, 112],
      [96, 112],
      [0, 160],
      [-64, 176],
      [64, 176],
      [0, 80],
      [-48, 120],
      [48, 120],
    ];
    for (const [sx, sy] of seedCoords) {
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(0.2 * (sx < 0 ? -1 : 1));
      ctx.fillStyle = '#0a0a0e';
      ctx.beginPath();
      ctx.ellipse(0, 0, 14, 25, 0, 0, Math.PI * 2);
      ctx.fill();

      // Seed highlight
      ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
      ctx.beginPath();
      ctx.ellipse(-3, -6, 4, 8, -0.2, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // 5. Sweet glowing juice drops
    const dripY = 256 + ((this.time * 200) % 280);
    const dropGrad = ctx.createRadialGradient(0, dripY, 2, 0, dripY, 20);
    dropGrad.addColorStop(0, 'rgba(255, 80, 140, 0.95)');
    dropGrad.addColorStop(1, 'rgba(255, 30, 80, 0.0)');
    ctx.fillStyle = dropGrad;
    ctx.beginPath();
    ctx.arc(0, dripY, 20, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  _renderShadow(ctx, w, h, dt, targetX = w / 2) {
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, '#f8fafc');
    bgGrad.addColorStop(1, '#e2e8f0');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    if (this.isLoomingActive) {
      this.loomingProgress += dt * 1.5;
      if (this.loomingProgress > 1.2) {
        this.loomingProgress = 0.05;
      }
    } else {
      this.loomingProgress = 0.15;
    }

    const maxR = Math.hypot(w, h) * 0.75;
    const currentR = 40 + Math.pow(this.loomingProgress, 2.4) * maxR;

    const shadowGrad = ctx.createRadialGradient(targetX, h / 2, currentR * 0.65, targetX, h / 2, currentR);
    shadowGrad.addColorStop(0, '#020306');
    shadowGrad.addColorStop(0.7, '#070910');
    shadowGrad.addColorStop(0.9, '#111522');
    shadowGrad.addColorStop(1, 'rgba(15, 23, 42, 0)');

    ctx.fillStyle = shadowGrad;
    ctx.beginPath();
    ctx.arc(targetX, h / 2, currentR, 0, Math.PI * 2);
    ctx.fill();

    if (this.loomingProgress > 0.35) {
      ctx.save();
      ctx.fillStyle = 'rgba(239, 68, 68, 0.92)';
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 4;
      ctx.font = '800 36px "Outfit", system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const lang = window.currentLang || 'en';
      const text = lang === 'tr' ? '⚠ AVCI TEHDİDİ TESPİT EDİLDİ ⚠' : '⚠ PREDATOR THREAT DETECTED ⚠';
      ctx.strokeText(text, w / 2, 160);
      ctx.fillText(text, w / 2, 160);
      ctx.restore();
    }
  }

  _renderSpider(ctx, w, h, targetX = w / 2) {
    const bgGrad = ctx.createRadialGradient(targetX, h / 2, 50, targetX, h / 2, h * 0.7);
    bgGrad.addColorStop(0, '#151922');
    bgGrad.addColorStop(1, '#080a0f');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // Subtle ambient web strands
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 0); ctx.lineTo(w, h);
    ctx.moveTo(w, 0); ctx.lineTo(0, h);
    ctx.moveTo(targetX, 0); ctx.lineTo(targetX, h);
    ctx.stroke();

    ctx.save();
    ctx.translate(targetX, h / 2);
    const crawl = Math.sin(this.time * 6) * 32;
    ctx.translate(0, crawl);

    // High-resolution arachnid body
    // Abdomen
    const abdGrad = ctx.createRadialGradient(0, 80, 20, 0, 80, 160);
    abdGrad.addColorStop(0, '#2d2c38');
    abdGrad.addColorStop(0.7, '#15141c');
    abdGrad.addColorStop(1, '#09080d');
    ctx.fillStyle = abdGrad;
    ctx.strokeStyle = '#991b1b';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.ellipse(0, 96, 110, 160, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Cephalothorax
    const cephGrad = ctx.createRadialGradient(0, -48, 15, 0, -48, 90);
    cephGrad.addColorStop(0, '#353444');
    cephGrad.addColorStop(1, '#111018');
    ctx.fillStyle = cephGrad;
    ctx.strokeStyle = '#7f1d1d';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.ellipse(0, -48, 80, 90, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Glowing predator eyes (multiple ocelli)
    const eyeGlow = ctx.createRadialGradient(0, -96, 5, 0, -96, 40);
    eyeGlow.addColorStop(0, 'rgba(255, 20, 50, 0.8)');
    eyeGlow.addColorStop(1, 'rgba(255, 20, 50, 0)');
    ctx.fillStyle = eyeGlow;
    ctx.beginPath();
    ctx.arc(0, -96, 40, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#ff1744';
    const eyes = [[-24, -96, 14], [24, -96, 14], [-10, -112, 9], [10, -112, 9], [-38, -92, 8], [38, -92, 8]];
    for (const [ex, ey, er] of eyes) {
      ctx.beginPath();
      ctx.arc(ex, ey, er, 0, Math.PI * 2);
      ctx.fill();
    }

    // 8 Articulated jointed legs with highlights
    for (let i = 0; i < 4; i++) {
      const sideY = -90 + i * 64;
      const legPhase = this.time * 8 + i * 1.2;
      const legOffset = Math.sin(legPhase) * 48;

      // Left Leg
      ctx.strokeStyle = '#374151';
      ctx.lineWidth = 14;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.beginPath();
      ctx.moveTo(-56, sideY);
      ctx.lineTo(-190, sideY - 80 + legOffset);
      ctx.lineTo(-300, sideY + 95 + legOffset);
      ctx.stroke();

      // Left claw
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(-300, sideY + 95 + legOffset);
      ctx.lineTo(-325, sideY + 120 + legOffset);
      ctx.stroke();

      // Right Leg
      ctx.strokeStyle = '#374151';
      ctx.lineWidth = 14;
      ctx.beginPath();
      ctx.moveTo(56, sideY);
      ctx.lineTo(190, sideY - 80 - legOffset);
      ctx.lineTo(300, sideY + 95 - legOffset);
      ctx.stroke();

      // Right claw
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(300, sideY + 95 - legOffset);
      ctx.lineTo(325, sideY + 120 - legOffset);
      ctx.stroke();
    }

    ctx.restore();
  }

  _renderNeutral(ctx, w, h) {
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, '#041309');
    bgGrad.addColorStop(0.5, '#072412');
    bgGrad.addColorStop(1, '#0c3d1f');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // Ambient floating dust motes
    ctx.fillStyle = 'rgba(167, 243, 208, 0.25)';
    for (let m = 0; m < 16; m++) {
      const mx = (m * 47 + this.time * 15) % w;
      const my = (m * 83 + Math.sin(this.time + m) * 40) % h;
      ctx.beginPath();
      ctx.arc(mx, my, (m % 3) + 2, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.save();
    for (let i = 0; i < 6; i++) {
      const lx = 140 + (i % 3) * 220;
      const ly = 240 + Math.floor(i / 3) * 420;

      ctx.save();
      ctx.translate(lx, ly);
      const sway = 0.15 * Math.sin(this.time * 1.8 + i) + (i % 2 === 0 ? 0.25 : -0.25);
      ctx.rotate(sway);

      // Lush foliage leaf
      const leafGrad = ctx.createLinearGradient(-120, 0, 120, 0);
      leafGrad.addColorStop(0, i % 2 === 0 ? '#15803d' : '#166534');
      leafGrad.addColorStop(0.5, i % 2 === 0 ? '#22c55e' : '#4ade80');
      leafGrad.addColorStop(1, '#14532d');

      ctx.fillStyle = leafGrad;
      ctx.beginPath();
      ctx.ellipse(0, 0, 150, 75, 0.35, 0, Math.PI * 2);
      ctx.fill();

      // Crisp leaf veins
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(-135, 0);
      ctx.lineTo(135, 0);
      ctx.stroke();

      // Side lateral veins
      ctx.lineWidth = 2.5;
      for (let v = -90; v <= 90; v += 35) {
        ctx.beginPath();
        ctx.moveTo(v, 0);
        ctx.lineTo(v + 35, 45);
        ctx.moveTo(v, 0);
        ctx.lineTo(v + 35, -45);
        ctx.stroke();
      }

      ctx.restore();
    }
    ctx.restore();
  }

  _renderCustom(ctx, w, h) {
    if (!this.customImage) return;

    ctx.fillStyle = '#05070a';
    ctx.fillRect(0, 0, w, h);

    const imgW = this.customImage.naturalWidth || this.customImage.width;
    const imgH = this.customImage.naturalHeight || this.customImage.height;

    const scale = Math.max(w / imgW, h / imgH);
    const renderW = imgW * scale;
    const renderH = imgH * scale;
    const offsetX = (w - renderW) / 2;
    const offsetY = (h - renderH) / 2;

    // High quality bicubic scaling without ANY scanlines
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(this.customImage, offsetX, offsetY, renderW, renderH);

    // Subtle edge vignette for photorealistic integration
    const vignette = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.45, w / 2, h / 2, Math.max(w, h) * 0.72);
    vignette.addColorStop(0, 'rgba(0, 0, 0, 0)');
    vignette.addColorStop(1, 'rgba(0, 0, 0, 0.32)');
    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, w, h);
  }

  getBase64Frame() {
    if (!this.retinaCanvas) {
      this.retinaCanvas = document.createElement('canvas');
      this.retinaCanvas.width = 90;
      this.retinaCanvas.height = 160;
      this.retinaCtx = this.retinaCanvas.getContext('2d', { willReadFrequently: true });
    }
    this.retinaCtx.drawImage(this.canvas, 0, 0, 90, 160);
    return this.retinaCanvas.toDataURL('image/jpeg', 0.85);
  }
}

// ============================================================================
// 3. THREE.JS PHOTOREALISTIC 3D ELECTROPHYSIOLOGY CHAMBER & RIG
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
    this.head = null;
    this.leftWing = null;
    this.rightWing = null;
    this.legs = [];
    this.connectomePointCloud = null;
    this.graphToSomaMap = null;
    this.glowingSomas = [];
    this.phoneScreenMesh = null;
    this.phoneLight = null;
    this.phoneTexture = null;

    this.neuropils = {};

    this.forwardDrive = 0.0;
    this.steeringDeflection = 0.0;
    this.jumpTriggered = false;
    this.jumpY = 0;
    this.jumpVy = 0;

    this.isSwiping = false;
    this.swipeProgress = 0.0;

    this.cpgTripodPhase = 0.0;
    this.vncLegs = null;

    this._initScene();
    this._buildEnvironment();
    this._buildPhotorealisticFly();
    this._buildNeuropilCompartments();
    this._buildVirtualSmartphone();
    this._loadRealSomaPointCloud();
    this._setupEventListeners();
    this._setCameraPreset('fly');
  }

  _initScene() {
    const w = this.container.clientWidth || 800;
    const h = this.container.clientHeight || 600;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x05070c);
    this.scene.fog = new THREE.FogExp2(0x05070c, 0.035);

    this.rigGroup = new THREE.Group();
    this.scene.add(this.rigGroup);

    this.camera = new THREE.PerspectiveCamera(42, w / h, 0.1, 100);
    this.camera.position.set(2.2, 1.55, 0.50);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setSize(w, h);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.35;
    this.container.appendChild(this.renderer.domElement);

    if (window.THREE && window.THREE.OrbitControls) {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.08;
      this.controls.minDistance = 0.8;
      this.controls.maxDistance = 10.0;
      this.controls.maxPolarAngle = Math.PI / 2 - 0.02;
      this.controls.target.set(0.0, 1.18, 0.80);
    }

    const ambientLight = new THREE.AmbientLight(0x162035, 1.4);
    this.scene.add(ambientLight);

    this.microscopeLight = new THREE.SpotLight(0xffffff, 3.2);
    this.microscopeLight.position.set(1.5, 5.0, 1.8);
    this.microscopeLight.angle = 0.45;
    this.microscopeLight.penumbra = 0.5;
    this.microscopeLight.castShadow = true;
    this.microscopeLight.shadow.mapSize.width = 2048;
    this.microscopeLight.shadow.mapSize.height = 2048;
    this.scene.add(this.microscopeLight);

    const fillLight = new THREE.DirectionalLight(0x00f0ff, 1.2);
    fillLight.position.set(-3.5, 3.0, 2.5);
    this.scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0xff0066, 1.0);
    rimLight.position.set(2.0, 2.5, -3.5);
    this.scene.add(rimLight);
  }

  _buildEnvironment() {
    const breadboardTex = generateBreadboardTexture();
    const tableGeo = new THREE.BoxGeometry(6.0, 0.4, 6.0);
    const tableMat = new THREE.MeshStandardMaterial({
      map: breadboardTex,
      roughness: 0.25,
      metalness: 0.88,
    });
    const table = new THREE.Mesh(tableGeo, tableMat);
    table.position.y = -0.2;
    table.receiveShadow = true;
    this.scene.add(table);

    const borderMat = new THREE.MeshStandardMaterial({ color: 0x3a4250, metalness: 0.95, roughness: 0.15 });
    const border = new THREE.Mesh(new THREE.BoxGeometry(6.05, 0.05, 6.05), borderMat);
    border.position.y = 0.01;
    this.scene.add(border);

    const nozzleGroup = new THREE.Group();
    nozzleGroup.position.set(0, 0, 0);

    const baseFlangeGeo = new THREE.CylinderGeometry(0.7, 0.85, 0.15, 32);
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x222834, metalness: 0.9, roughness: 0.2 });
    const baseFlange = new THREE.Mesh(baseFlangeGeo, metalMat);
    baseFlange.position.y = 0.075;
    nozzleGroup.add(baseFlange);

    const cupGeo = new THREE.CylinderGeometry(0.55, 0.45, 0.28, 32);
    const cup = new THREE.Mesh(cupGeo, metalMat);
    cup.position.y = 0.28;
    nozzleGroup.add(cup);

    const sensorGeo = new THREE.BoxGeometry(0.12, 0.12, 0.18);
    const sensorMat = new THREE.MeshStandardMaterial({ color: 0x0e1420, metalness: 0.5, roughness: 0.5 });

    const sensorL = new THREE.Mesh(sensorGeo, sensorMat);
    sensorL.position.set(-0.52, 0.38, 0.1);
    sensorL.rotation.y = 0.4;
    nozzleGroup.add(sensorL);

    const sensorR = new THREE.Mesh(sensorGeo, sensorMat);
    sensorR.position.set(0.52, 0.38, 0.1);
    sensorR.rotation.y = -0.4;
    nozzleGroup.add(sensorR);

    this.rigGroup.add(nozzleGroup);

    const ballGeo = new THREE.SphereGeometry(0.55, 48, 48);
    const ballMat = new THREE.MeshStandardMaterial({
      color: 0x222a38,
      roughness: 0.75,
      metalness: 0.1,
    });
    this.treadmillBall = new THREE.Mesh(ballGeo, ballMat);
    this.treadmillBall.position.set(0, 0.55, 0);
    this.treadmillBall.castShadow = true;
    this.treadmillBall.receiveShadow = true;
    this.rigGroup.add(this.treadmillBall);

    const manipGroup = new THREE.Group();
    manipGroup.position.set(-1.1, 0.6, 0.2);

    const manipBaseGeo = new THREE.BoxGeometry(0.35, 0.8, 0.35);
    const manipBase = new THREE.Mesh(manipBaseGeo, metalMat);
    manipGroup.add(manipBase);

    const armGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.75, 12);
    const arm = new THREE.Mesh(armGeo, metalMat);
    arm.position.set(0.32, 0.35, 0.15);
    arm.rotation.z = -0.85;
    arm.rotation.x = 0.2;
    manipGroup.add(arm);

    const pipetteGeo = new THREE.CylinderGeometry(0.004, 0.015, 0.6, 12);
    const glassMat = new THREE.MeshPhysicalMaterial({
      color: 0xe0f7ff,
      transmission: 0.95,
      opacity: 0.8,
      roughness: 0.05,
      ior: 1.5,
    });
    const pipette = new THREE.Mesh(pipetteGeo, glassMat);
    pipette.position.set(0.62, 0.58, 0.22);
    pipette.rotation.z = -0.95;
    manipGroup.add(pipette);

    this.rigGroup.add(manipGroup);

    const scopeGroup = new THREE.Group();
    scopeGroup.position.set(0, 3.2, 0.2);

    const barrelGeo = new THREE.CylinderGeometry(0.4, 0.5, 1.2, 32);
    const barrel = new THREE.Mesh(barrelGeo, metalMat);
    scopeGroup.add(barrel);

    const ringLightGeo = new THREE.TorusGeometry(0.42, 0.05, 16, 32);
    const ringLightMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const ringLightMesh = new THREE.Mesh(ringLightGeo, ringLightMat);
    ringLightMesh.position.y = -0.6;
    ringLightMesh.rotation.x = Math.PI / 2;
    scopeGroup.add(ringLightMesh);

    this.rigGroup.add(scopeGroup);

    const domeGeo = new THREE.SphereGeometry(3.6, 32, 24, 0, Math.PI * 2, 0, Math.PI / 2);
    const domeMat = new THREE.MeshPhysicalMaterial({
      color: 0x88bbff,
      transparent: true,
      opacity: 0.08,
      roughness: 0.05,
      metalness: 0.05,
      transmission: 0.92,
      ior: 1.48,
      side: THREE.BackSide,
    });
    const dome = new THREE.Mesh(domeGeo, domeMat);
    this.scene.add(dome);
  }

  _buildPhotorealisticFly() {
    this.flyGroup = new THREE.Group();
    this.flyGroup.position.set(0, 1.18, 0);

    const ommatidiaTex = generateOmmatidiaTexture();
    const wingTex = generateWingTexture();

    const chitinMat = new THREE.MeshPhysicalMaterial({
      color: 0x5a341a,
      roughness: 0.32,
      metalness: 0.22,
      clearcoat: 0.8,
      clearcoatRoughness: 0.2,
      reflectivity: 0.7,
    });

    const eyeMat = new THREE.MeshPhysicalMaterial({
      color: 0x8a0418,
      emissive: 0x220004,
      roughness: 0.18,
      metalness: 0.35,
      bumpMap: ommatidiaTex,
      bumpScale: 0.04,
      clearcoat: 0.9,
      clearcoatRoughness: 0.1,
    });

    const wingMat = new THREE.MeshPhysicalMaterial({
      map: wingTex,
      transparent: true,
      opacity: 0.9,
      roughness: 0.08,
      metalness: 0.15,
      transmission: 0.7,
      ior: 1.35,
      side: THREE.DoubleSide,
      depthWrite: false,
    });

    // 1. Thorax
    const thoraxGroup = new THREE.Group();

    const scutumGeo = new THREE.SphereGeometry(0.36, 24, 20);
    scutumGeo.scale(0.85, 1.05, 1.35);
    const scutum = new THREE.Mesh(scutumGeo, chitinMat);
    scutum.castShadow = true;
    thoraxGroup.add(scutum);

    const scutellumGeo = new THREE.ConeGeometry(0.16, 0.22, 16);
    scutellumGeo.scale(1.2, 0.6, 1.4);
    const scutellum = new THREE.Mesh(scutellumGeo, chitinMat);
    scutellum.position.set(0, 0.22, -0.42);
    scutellum.rotation.x = -0.4;
    scutellum.castShadow = true;
    thoraxGroup.add(scutellum);

    const bristleMat = new THREE.MeshBasicMaterial({ color: 0x150d06 });
    const bristleCoords = [
      [-0.12, 0.34, 0.15],
      [0.12, 0.34, 0.15],
      [-0.18, 0.32, -0.1],
      [0.18, 0.32, -0.1],
      [-0.14, 0.3, -0.3],
      [0.14, 0.3, -0.3],
      [-0.08, 0.25, -0.48],
      [0.08, 0.25, -0.48],
    ];

    for (const [bx, by, bz] of bristleCoords) {
      const bGeo = new THREE.CylinderGeometry(0.003, 0.008, 0.14, 6);
      bGeo.translate(0, 0.07, 0);
      const bMesh = new THREE.Mesh(bGeo, bristleMat);
      bMesh.position.set(bx, by, bz);
      bMesh.rotation.x = -0.35 + (Math.random() - 0.5) * 0.2;
      bMesh.rotation.z = (bx > 0 ? 0.3 : -0.3) + (Math.random() - 0.5) * 0.2;
      thoraxGroup.add(bMesh);
    }

    this.flyGroup.add(thoraxGroup);

    // 2. Segmented Abdomen
    const abdGroup = new THREE.Group();
    abdGroup.position.set(0, -0.06, -0.78);
    abdGroup.rotation.x = -0.24;

    const abdSegments = 6;
    this.abdomenMeshes = [];

    for (let s = 0; s < abdSegments; s++) {
      const progress = s / (abdSegments - 1);
      const rad = 0.36 * Math.sin((progress + 0.15) * Math.PI * 0.85);
      const segGeo = new THREE.CylinderGeometry(rad * 0.95, rad, 0.18, 20);
      segGeo.scale(0.85, 1.0, 1.25);

      const isStripe = s >= 2;
      const segMat = new THREE.MeshPhysicalMaterial({
        color: isStripe ? 0x221308 : 0x5a341a,
        roughness: 0.4,
        metalness: 0.18,
      });

      const segMesh = new THREE.Mesh(segGeo, segMat);
      segMesh.position.set(0, -s * 0.14, -s * 0.05);
      segMesh.castShadow = true;
      abdGroup.add(segMesh);
      this.abdomenMeshes.push(segMesh);
    }

    this.flyGroup.add(abdGroup);

    // 3. Head Capsule
    this.head = new THREE.Group();
    this.head.position.set(0, 0.12, 0.58);

    const headCuticleMat = new THREE.MeshPhysicalMaterial({
      color: 0x5a341a,
      transparent: true,
      opacity: 0.88,
      roughness: 0.28,
      metalness: 0.2,
      transmission: 0.35,
      ior: 1.4,
    });

    const headGeo = new THREE.SphereGeometry(0.26, 20, 16);
    headGeo.scale(1.25, 1.0, 0.9);
    const headMesh = new THREE.Mesh(headGeo, headCuticleMat);
    headMesh.castShadow = true;
    this.head.add(headMesh);

    // 4. Compound Eyes
    const eyeGeo = new THREE.SphereGeometry(0.16, 24, 20);
    eyeGeo.scale(0.85, 1.35, 1.15);

    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.21, 0.03, 0.08);
    leftEye.rotation.set(0.12, 0.38, -0.22);
    leftEye.castShadow = true;
    this.head.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.21, 0.03, 0.08);
    rightEye.rotation.set(0.12, -0.38, 0.22);
    rightEye.castShadow = true;
    this.head.add(rightEye);

    // 5. Antennae & Aristae
    for (const side of [-1, 1]) {
      const antGroup = new THREE.Group();
      antGroup.position.set(side * 0.08, 0.14, 0.22);

      const pedicelGeo = new THREE.SphereGeometry(0.03, 8, 8);
      const pedicel = new THREE.Mesh(pedicelGeo, chitinMat);
      antGroup.add(pedicel);

      const funGeo = new THREE.SphereGeometry(0.04, 10, 8);
      funGeo.scale(0.7, 1.2, 0.8);
      const funiculus = new THREE.Mesh(funGeo, chitinMat);
      funiculus.position.set(0, 0.04, 0.02);
      antGroup.add(funiculus);

      const aristaStemGeo = new THREE.CylinderGeometry(0.003, 0.005, 0.18, 6);
      aristaStemGeo.translate(0, 0.09, 0);
      const aristaStem = new THREE.Mesh(aristaStemGeo, bristleMat);
      aristaStem.rotation.x = 0.5;
      aristaStem.rotation.z = side * 0.4;
      antGroup.add(aristaStem);

      for (let f = 1; f <= 5; f++) {
        const branchGeo = new THREE.CylinderGeometry(0.001, 0.002, 0.05, 4);
        branchGeo.translate(0, 0.025, 0);
        const branch = new THREE.Mesh(branchGeo, bristleMat);
        branch.position.set(0, f * 0.028, 0);
        branch.rotation.z = side * 0.8;
        aristaStem.add(branch);
      }

      this.head.add(antGroup);
    }

    // 6. Proboscis
    const probGroup = new THREE.Group();
    probGroup.position.set(0, -0.24, 0.12);

    const rostrumGeo = new THREE.CylinderGeometry(0.04, 0.07, 0.22, 12);
    const rostrum = new THREE.Mesh(rostrumGeo, chitinMat);
    rostrum.rotation.x = 0.4;
    probGroup.add(rostrum);

    const labGeo = new THREE.SphereGeometry(0.06, 12, 10);
    labGeo.scale(1.3, 0.8, 1.0);
    const labellum = new THREE.Mesh(labGeo, chitinMat);
    labellum.position.set(0, -0.12, 0.06);
    probGroup.add(labellum);

    this.head.add(probGroup);

    this.flyGroup.add(this.head);

    // 8. Wings
    const wingGeo = new THREE.PlaneGeometry(0.55, 1.45);
    wingGeo.translate(0, 0.72, 0);

    this.leftWing = new THREE.Mesh(wingGeo, wingMat);
    this.leftWing.position.set(-0.18, 0.28, -0.16);
    this.leftWing.rotation.set(Math.PI / 2 - 0.08, -0.38, 0.28);
    this.leftWing.castShadow = true;
    this.flyGroup.add(this.leftWing);

    this.rightWing = new THREE.Mesh(wingGeo, wingMat);
    this.rightWing.position.set(0.18, 0.28, -0.16);
    this.rightWing.rotation.set(Math.PI / 2 - 0.08, 0.38, -0.28);
    this.rightWing.castShadow = true;
    this.flyGroup.add(this.rightWing);

    // 9. Articulated Legs
    this.legs = [];
    const legConfigs = [
      { side: -1, z: 0.24, name: 'pro_L' },
      { side: 1, z: 0.24, name: 'pro_R' },
      { side: -1, z: -0.02, name: 'meso_L' },
      { side: 1, z: -0.02, name: 'meso_R' },
      { side: -1, z: -0.32, name: 'meta_L' },
      { side: 1, z: -0.32, name: 'meta_R' },
    ];

    for (let i = 0; i < legConfigs.length; i++) {
      const cfg = legConfigs[i];
      const legRoot = new THREE.Group();
      legRoot.position.set(cfg.side * 0.28, -0.14, cfg.z);

      const coxaGeo = new THREE.CylinderGeometry(0.035, 0.028, 0.12, 8);
      const coxa = new THREE.Mesh(coxaGeo, chitinMat);
      coxa.rotation.z = cfg.side * 0.5;
      legRoot.add(coxa);

      const femurGeo = new THREE.CylinderGeometry(0.028, 0.022, 0.42, 8);
      femurGeo.translate(0, -0.21, 0);
      const femur = new THREE.Mesh(femurGeo, chitinMat);
      femur.position.set(cfg.side * 0.05, -0.05, 0);
      femur.rotation.z = cfg.side * 0.75;
      femur.rotation.x = cfg.z > 0 ? 0.32 : -0.32;
      coxa.add(femur);

      const tibiaGeo = new THREE.CylinderGeometry(0.02, 0.014, 0.48, 8);
      tibiaGeo.translate(0, -0.24, 0);
      const tibia = new THREE.Mesh(tibiaGeo, chitinMat);
      tibia.position.set(0, -0.4, 0);
      tibia.rotation.z = -cfg.side * 0.95;
      femur.add(tibia);

      const tarsusGeo = new THREE.CylinderGeometry(0.012, 0.008, 0.28, 6);
      tarsusGeo.translate(0, -0.14, 0);
      const tarsus = new THREE.Mesh(tarsusGeo, chitinMat);
      tarsus.position.set(0, -0.46, 0);
      tarsus.rotation.x = 0.2;
      tibia.add(tarsus);

      this.flyGroup.add(legRoot);

      this.legs.push({
        group: legRoot,
        coxa: coxa,
        femur: femur,
        tibia: tibia,
        tarsus: tarsus,
        side: cfg.side,
        phase: i * 1.05,
        name: cfg.name,
        tripodGroup: (cfg.name === 'pro_L' || cfg.name === 'meso_R' || cfg.name === 'meta_L') ? 'A' : 'B',
        defaultRotZ: femur.rotation.z,
        defaultFemurRotX: femur.rotation.x,
        defaultTibiaRotZ: tibia.rotation.z,
        defaultPosX: legRoot.position.x,
        defaultPosY: legRoot.position.y,
        defaultPosZ: legRoot.position.z,
      });
    }

    this.rigGroup.add(this.flyGroup);
  }

  _buildNeuropilCompartments() {
    const opticMat = new THREE.MeshStandardMaterial({
      color: 0x00f0ff,
      emissive: 0x00aacc,
      emissiveIntensity: 0.45,
      transparent: true,
      opacity: 0.65,
      roughness: 0.2,
    });

    const opticGeo = new THREE.SphereGeometry(0.08, 12, 10);
    opticGeo.scale(0.8, 1.4, 1.1);

    const leftOptic = new THREE.Mesh(opticGeo, opticMat);
    leftOptic.position.set(-0.16, 0.04, 0.06);
    this.head.add(leftOptic);

    const rightOptic = new THREE.Mesh(opticGeo, opticMat);
    rightOptic.position.set(0.16, 0.04, 0.06);
    this.head.add(rightOptic);

    const mbMat = new THREE.MeshStandardMaterial({
      color: 0x10b981,
      emissive: 0x059669,
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.75,
      roughness: 0.25,
    });

    const mbGroup = new THREE.Group();
    const calyxGeo = new THREE.SphereGeometry(0.045, 10, 8);
    const calyxL = new THREE.Mesh(calyxGeo, mbMat);
    calyxL.position.set(-0.05, 0.09, -0.03);
    const calyxR = new THREE.Mesh(calyxGeo, mbMat);
    calyxR.position.set(0.05, 0.09, -0.03);
    mbGroup.add(calyxL, calyxR);

    const lobeGeo = new THREE.CylinderGeometry(0.015, 0.02, 0.12, 8);
    const lobeL = new THREE.Mesh(lobeGeo, mbMat);
    lobeL.position.set(-0.03, 0.02, 0.02);
    lobeL.rotation.z = -0.3;
    const lobeR = new THREE.Mesh(lobeGeo, mbMat);
    lobeR.position.set(0.03, 0.02, 0.02);
    lobeR.rotation.z = 0.3;
    mbGroup.add(lobeL, lobeR);

    this.head.add(mbGroup);

    const ccMat = new THREE.MeshStandardMaterial({
      color: 0xffaa00,
      emissive: 0xff8800,
      emissiveIntensity: 0.6,
      transparent: true,
      opacity: 0.8,
      roughness: 0.2,
    });
    const ccGeo = new THREE.TorusGeometry(0.04, 0.012, 8, 24);
    const centralComplex = new THREE.Mesh(ccGeo, ccMat);
    centralComplex.position.set(0, 0.04, 0.03);
    centralComplex.rotation.x = Math.PI / 2 - 0.2;
    this.head.add(centralComplex);

    const gfMat = new THREE.MeshStandardMaterial({
      color: 0xef4444,
      emissive: 0xb91c1c,
      emissiveIntensity: 0.3,
      transparent: true,
      opacity: 0.7,
      roughness: 0.3,
    });
    const gfGeo = new THREE.CylinderGeometry(0.012, 0.018, 0.24, 8);
    const gfTract = new THREE.Mesh(gfGeo, gfMat);
    gfTract.position.set(0, -0.06, -0.08);
    gfTract.rotation.x = 0.45;
    this.head.add(gfTract);

    this.neuropils = {
      opticMat: opticMat,
      mbMat: mbMat,
      ccMat: ccMat,
      centralComplex: centralComplex,
      gfMat: gfMat,
    };
  }

  async _loadRealSomaPointCloud() {
    try {
      const [coordRes, metaRes] = await Promise.all([
        fetch('/api/connectome/soma-coordinates'),
        fetch('/api/connectome/soma-metadata'),
      ]);
      if (!coordRes.ok) {
        console.warn(`[Connectome 3D] Failed to fetch coordinates (HTTP ${coordRes.status})`);
        return;
      }
      const buffer = await coordRes.arrayBuffer();

      const headerView = new Uint32Array(buffer, 0, 2);
      const magic = headerView[0];
      const count = headerView[1];
      if (magic !== 0x464C5933) {
        console.warn('[Connectome 3D] Invalid binary magic header:', magic.toString(16));
        return;
      }

      let offset = 16;
      // Positions: count * 3 float32 (offset 16)
      const posBytes = count * 3 * 4;
      const positions = new Float32Array(buffer.slice(offset, offset + posBytes));
      offset += posBytes;

      // Graph node indices: count int32 (offset 1,701,388)
      const graphBytes = count * 4;
      const graphIndices = new Int32Array(buffer.slice(offset, offset + graphBytes));
      offset += graphBytes;

      // Circuit tags: count uint8
      const circuitTags = new Uint8Array(buffer.slice(offset, offset + count));
      this.somaCircuits = circuitTags;
      offset += count;

      // Polarities: count int8
      const polarities = new Int8Array(buffer.slice(offset, offset + count));
      offset += count;

      // Build reverse O(1) graphToSomaMap (166700 graph nodes -> soma index)
      this.graphToSomaMap = new Int32Array(166700);
      this.graphToSomaMap.fill(-1);
      for (let i = 0; i < count; i++) {
        const gIdx = graphIndices[i];
        if (gIdx >= 0 && gIdx < 166700) {
          this.graphToSomaMap[gIdx] = i;
        }
      }

      // Map Circuit tags to colors
      // 0: #38bdf8 (central_brain) -> [0.22, 0.74, 0.97]
      // 1: #00f0ff (optic_lobe) -> [0.0, 0.94, 1.0]
      // 2: #10b981 (mushroom_body) -> [0.06, 0.73, 0.51]
      // 3: #f59e0b (central_complex) -> [0.96, 0.62, 0.04]
      // 4: #ef4444 (descending_motor) -> [0.94, 0.27, 0.27]
      // 5: #a855f7 (vnc_motor_cord) -> [0.66, 0.33, 0.97]
      const palette = [
        [0.22, 0.74, 0.97],
        [0.0, 0.94, 1.0],
        [0.06, 0.73, 0.51],
        [0.96, 0.62, 0.04],
        [0.94, 0.27, 0.27],
        [0.66, 0.33, 0.97],
      ];

      const colors = new Float32Array(count * 3);
      const activity = new Float32Array(count);

      for (let i = 0; i < count; i++) {
        const tag = circuitTags[i] < palette.length ? circuitTags[i] : 0;
        const rgb = palette[tag];
        colors[i * 3 + 0] = rgb[0];
        colors[i * 3 + 1] = rgb[1];
        colors[i * 3 + 2] = rgb[2];
        activity[i] = 0.0;
      }

      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      geometry.setAttribute('activity', new THREE.BufferAttribute(activity, 1));

      const pointShaderMat = new THREE.ShaderMaterial({
        vertexColors: true,
        uniforms: {
          baseSize: { value: 0.010 },
        },
        vertexShader: `
          #ifndef USE_COLOR
          attribute vec3 color;
          #endif
          attribute float activity;
          varying vec3 vColor;
          varying float vActivity;
          uniform float baseSize;
          void main() {
            vColor = color.rgb;
            vActivity = activity;
            vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
            gl_PointSize = (baseSize + activity * 0.024) * (260.0 / -mvPosition.z);
            gl_Position = projectionMatrix * mvPosition;
          }
        `,
        fragmentShader: `
          varying vec3 vColor;
          varying float vActivity;
          void main() {
            float dist = length(gl_PointCoord - vec2(0.5));
            if (dist > 0.5) discard;
            float alpha = smoothstep(0.5, 0.12, dist) * (0.65 + vActivity * 0.35);
            vec3 finalColor = mix(vColor, vec3(1.0, 1.0, 1.0), vActivity * 0.85);
            gl_FragColor = vec4(finalColor, alpha);
          }
        `,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      });

      this.connectomePointCloud = new THREE.Points(geometry, pointShaderMat);
      if (this.head) {
        this.head.add(this.connectomePointCloud);
      }

      console.log(`[Connectome 3D] Successfully loaded ${count.toLocaleString()} real EM neuron somas into Three.js point cloud.`);
      this.somaData = {
        count,
        positions,
        circuitTags,
        graphToSomaMap: this.graphToSomaMap,
      };
      if (typeof this.onSomaDataLoaded === 'function') {
        this.onSomaDataLoaded(this.somaData);
      }
    } catch (err) {
      console.error('[Connectome 3D] Failed to load 141K soma point cloud:', err);
    }
  }

  _buildVirtualSmartphone() {
    const phoneGroup = new THREE.Group();
    phoneGroup.position.set(0.0, 1.24, 1.18);

    phoneGroup.rotation.y = Math.PI - 0.08;
    phoneGroup.rotation.x = -0.08;

    const bodyGeo = new THREE.BoxGeometry(0.86, 1.52, 0.045);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0x181e28,
      roughness: 0.2,
      metalness: 0.9,
    });
    const phoneBody = new THREE.Mesh(bodyGeo, bodyMat);
    phoneBody.castShadow = true;
    phoneGroup.add(phoneBody);

    const bezelGeo = new THREE.BoxGeometry(0.82, 1.48, 0.048);
    const bezelMat = new THREE.MeshBasicMaterial({ color: 0x080a10 });
    const bezel = new THREE.Mesh(bezelGeo, bezelMat);
    phoneGroup.add(bezel);

    this.phoneTexture = new THREE.CanvasTexture(this.stimulusCanvas);
    this.phoneTexture.minFilter = THREE.LinearFilter;
    this.phoneTexture.magFilter = THREE.LinearFilter;
    this.phoneTexture.generateMipmaps = false;
    if (this.renderer && this.renderer.capabilities) {
      this.phoneTexture.anisotropy = Math.min(this.renderer.capabilities.getMaxAnisotropy(), 16);
    }

    const screenGeo = new THREE.PlaneGeometry(0.78, 1.42);
    const screenMat = new THREE.MeshBasicMaterial({
      map: this.phoneTexture,
      toneMapped: false,
    });
    this.phoneScreenMesh = new THREE.Mesh(screenGeo, screenMat);
    this.phoneScreenMesh.position.z = 0.026;
    phoneGroup.add(this.phoneScreenMesh);

    this.phoneLight = new THREE.SpotLight(0xff3366, 3.5, 3.0, 0.85, 0.4);
    this.phoneLight.position.set(0, 0, 0.1);
    this.phoneLight.target = this.flyGroup;
    phoneGroup.add(this.phoneLight);

    const camIslandGeo = new THREE.BoxGeometry(0.28, 0.28, 0.02);
    const camIsland = new THREE.Mesh(camIslandGeo, bodyMat);
    camIsland.position.set(-0.24, 0.52, -0.03);
    phoneGroup.add(camIsland);

    const standMat = new THREE.MeshStandardMaterial({
      color: 0x222a38,
      metalness: 0.85,
      roughness: 0.3,
    });

    // Rear clamp and knuckle joint mounted securely to the back of the smartphone
    const rearClampGeo = new THREE.BoxGeometry(0.34, 0.16, 0.025);
    const rearClamp = new THREE.Mesh(rearClampGeo, standMat);
    rearClamp.position.set(0.0, -0.08, -0.032);
    phoneGroup.add(rearClamp);

    const knuckleJointGeo = new THREE.CylinderGeometry(0.025, 0.025, 0.07, 12);
    const knuckleJoint = new THREE.Mesh(knuckleJointGeo, standMat);
    knuckleJoint.rotation.x = Math.PI / 2;
    knuckleJoint.position.set(0.0, -0.08, -0.07);
    phoneGroup.add(knuckleJoint);

    // Stand base resting on optical table, positioned safely behind the phone
    const standBaseGeo = new THREE.CylinderGeometry(0.28, 0.32, 0.05, 24);
    const standBase = new THREE.Mesh(standBaseGeo, standMat);
    standBase.position.set(0.0, 0.025, 1.28);
    this.rigGroup.add(standBase);

    // Vertical stand post rising behind the phone casing
    const standStemGeo = new THREE.CylinderGeometry(0.035, 0.045, 1.18, 16);
    const standStem = new THREE.Mesh(standStemGeo, standMat);
    standStem.position.set(0.0, 0.60, 1.28);
    this.rigGroup.add(standStem);

    // Articulated bridge arm connecting vertical post to phone rear knuckle
    const bridgeArmGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.10, 12);
    const bridgeArm = new THREE.Mesh(bridgeArmGeo, standMat);
    bridgeArm.rotation.x = Math.PI / 2;
    bridgeArm.position.set(0.0, 1.16, 1.24);
    this.rigGroup.add(bridgeArm);

    this.phoneGroup = phoneGroup;
    this.rigGroup.add(phoneGroup);
  }

  _isMobileViewport() {
    const w = this.container ? this.container.clientWidth : window.innerWidth;
    const h = this.container ? this.container.clientHeight : window.innerHeight;
    return (w / (h || 1) < 1.0) || w <= 768;
  }

  _setupEventListeners() {
    window.addEventListener('resize', () => {
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      if (w && h && this.camera && this.renderer) {
        this.camera.aspect = w / h;
        this._setCameraPreset(this.currentPreset || 'fly');
        this.renderer.setSize(w, h);
      }
    });

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
    if (preset) this.currentPreset = preset;
    const activePreset = this.currentPreset || 'fly';
    const isMobile = this._isMobileViewport();

    // Scale the whole laboratory rig: shrink to 0.76 on mobile so both the fly and the screen fit completely
    if (this.rigGroup) {
      const scale = isMobile ? 0.76 : 1.0;
      this.rigGroup.scale.set(scale, scale, scale);
    }

    if (activePreset === 'fly') {
      if (isMobile) {
        this.camera.position.set(2.3, 1.50, 0.40);
        this.controls.target.set(0.0, 1.05, 0.80);
        this.camera.fov = 48;
      } else {
        this.camera.position.set(2.2, 1.55, 0.50);
        this.controls.target.set(0.0, 1.18, 0.80);
        this.camera.fov = 42;
      }
    } else if (activePreset === 'phone') {
      if (isMobile) {
        this.camera.position.set(0.0, 1.36, 0.05);
        this.controls.target.set(0.0, 1.18, 1.18);
        this.camera.fov = 48;
      } else {
        this.camera.position.set(0.0, 1.38, 0.08);
        this.controls.target.set(0.0, 1.24, 1.18);
        this.camera.fov = 44;
      }
    } else if (activePreset === 'brain') {
      if (isMobile) {
        this.camera.position.set(0.45, 1.28, 0.98);
        this.controls.target.set(0.0, 1.15, 0.58);
        this.camera.fov = 46;
      } else {
        this.camera.position.set(0.40, 1.35, 0.95);
        this.controls.target.set(0.0, 1.25, 0.58);
        this.camera.fov = 40;
      }
    }
    this.camera.updateProjectionMatrix();
    this.controls.update();
  }

  triggerLegSwipe() {
    if (!this.isSwiping) {
      this.isSwiping = true;
      this.swipeProgress = 0.0;
    }
  }

  updateFromTelemetry(telemetry) {
    if (!telemetry) return;

    const motor = telemetry.motor || {};
    this.forwardDrive = (motor.forward_drive_pct || 0) / 100;
    this.steeringDeflection = motor.steering_deflection || 0;
    this.vncLegs = telemetry.vnc_legs || null;

    if (motor.giant_fiber_jump && !this.jumpTriggered) {
      this.jumpTriggered = true;
      this.jumpVy = 0.18;
    }

    const h = telemetry.hormones || {};
    const da = h.dopamine_nm || 5.0;
    const oa = h.octopamine_nm || 2.0;
    const spikes = telemetry.spike_counts?.total_spikes || 0;

    if (this.neuropils.mbMat) {
      this.neuropils.mbMat.emissiveIntensity = 0.3 + Math.min(2.5, (da / 15) * 1.5);
    }
    if (this.neuropils.opticMat) {
      this.neuropils.opticMat.emissiveIntensity = 0.3 + Math.min(2.0, (spikes / 100) * 1.2);
    }
    if (this.neuropils.gfMat) {
      this.neuropils.gfMat.emissiveIntensity = oa > 10.0 || motor.giant_fiber_jump ? 2.8 : 0.25;
    }
    if (this.neuropils.centralComplex) {
      const headingRad = (motor.compass_heading_deg || 0) * (Math.PI / 180);
      this.neuropils.centralComplex.rotation.z = headingRad;
    }

    if (da > 22.0 && !this.isSwiping && (spikes % 7 === 0)) {
      this.triggerLegSwipe();
    }

    if (this.connectomePointCloud && this.connectomePointCloud.geometry.attributes.activity) {
      const actAttr = this.connectomePointCloud.geometry.attributes.activity;
      const actArr = actAttr.array;

      // 1. Exponential decay of previously active somas (O(k) where k is active count)
      if (this.glowingSomas && this.glowingSomas.length > 0) {
        const nextGlowing = [];
        for (let i = 0; i < this.glowingSomas.length; i++) {
          const sIdx = this.glowingSomas[i];
          actArr[sIdx] *= 0.78;
          if (actArr[sIdx] > 0.04) {
            nextGlowing.push(sIdx);
          } else {
            actArr[sIdx] = 0.0;
          }
        }
        this.glowingSomas = nextGlowing;
      } else {
        this.glowingSomas = [];
      }

      // 2. Cascade real biological wave propagation across anatomical circuits
      const activeNeurons = telemetry.active_neurons || [];
      if (this.graphToSomaMap && activeNeurons.length > 0) {
        // Group somas by biological synaptic latency:
        // Wave 0 (0ms): Optic Lobe (retinal input cartridges)
        // Wave 1 (18ms): Central Brain & Mushroom Body (associative/neuropil)
        // Wave 2 (36ms): Central Complex & Descending Motor (steering / giant fiber)
        // Wave 3 (54ms): Ventral Nerve Cord (thoracic motor cord)
        const wave0 = [];
        const wave1 = [];
        const wave2 = [];
        const wave3 = [];

        for (let i = 0; i < activeNeurons.length; i++) {
          const gIdx = activeNeurons[i];
          if (gIdx >= 0 && gIdx < this.graphToSomaMap.length) {
            const sIdx = this.graphToSomaMap[gIdx];
            if (sIdx >= 0 && sIdx < actArr.length) {
              const tag = this.somaCircuits ? this.somaCircuits[sIdx] : 0;
              if (tag === 1) {
                wave0.push(sIdx);
              } else if (tag === 0 || tag === 2) {
                wave1.push(sIdx);
              } else if (tag === 3 || tag === 4) {
                wave2.push(sIdx);
              } else {
                wave3.push(sIdx);
              }
            }
          }
        }

        // Layer 0: Immediate visual retinal wave (0ms)
        for (let i = 0; i < wave0.length; i++) {
          actArr[wave0[i]] = 1.0;
          this.glowingSomas.push(wave0[i]);
        }
        actAttr.needsUpdate = true;

        // Layer 1: Central Brain & Mushroom Body (~18ms)
        if (wave1.length > 0) {
          setTimeout(() => {
            if (this.connectomePointCloud && this.connectomePointCloud.geometry.attributes.activity) {
              const curAct = this.connectomePointCloud.geometry.attributes.activity.array;
              for (let i = 0; i < wave1.length; i++) {
                curAct[wave1[i]] = 1.0;
                this.glowingSomas.push(wave1[i]);
              }
              this.connectomePointCloud.geometry.attributes.activity.needsUpdate = true;
            }
          }, 18);
        }

        // Layer 2: Central Complex & Descending Motor (~36ms)
        if (wave2.length > 0) {
          setTimeout(() => {
            if (this.connectomePointCloud && this.connectomePointCloud.geometry.attributes.activity) {
              const curAct = this.connectomePointCloud.geometry.attributes.activity.array;
              for (let i = 0; i < wave2.length; i++) {
                curAct[wave2[i]] = 1.0;
                this.glowingSomas.push(wave2[i]);
              }
              this.connectomePointCloud.geometry.attributes.activity.needsUpdate = true;
            }
          }, 36);
        }

        // Layer 3: Ventral Nerve Cord (~54ms)
        if (wave3.length > 0) {
          setTimeout(() => {
            if (this.connectomePointCloud && this.connectomePointCloud.geometry.attributes.activity) {
              const curAct = this.connectomePointCloud.geometry.attributes.activity.array;
              for (let i = 0; i < wave3.length; i++) {
                curAct[wave3[i]] = 1.0;
                this.glowingSomas.push(wave3[i]);
              }
              this.connectomePointCloud.geometry.attributes.activity.needsUpdate = true;
            }
          }, 54);
        }
      }
    }

    if (this.phoneLight) {
      if (oa > 4.5) {
        this.phoneLight.color.setHex(0xff1122);
      } else if (da > 8.0) {
        this.phoneLight.color.setHex(0x00f0ff);
      } else {
        this.phoneLight.color.setHex(0x22cc88);
      }
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    const dt = this.clock.getDelta();
    const time = this.clock.getElapsedTime();

    if (this.phoneTexture) {
      this.phoneTexture.needsUpdate = true;
    }

    if (this.legs && this.legs.length) {
      // 1. Thoracic CPG Tripod Phase Sync / Integration
      if (this.vncLegs && this.vncLegs.tripod_phase !== undefined) {
        const targetPhase = this.vncLegs.tripod_phase;
        const diff = Math.atan2(Math.sin(targetPhase - this.cpgTripodPhase), Math.cos(targetPhase - this.cpgTripodPhase));
        this.cpgTripodPhase = (this.cpgTripodPhase + diff * Math.min(1.0, dt * 18.0) + Math.PI * 2) % (Math.PI * 2);
      } else {
        const stepFreq = 3.0 + this.forwardDrive * 8.0;
        this.cpgTripodPhase = (this.cpgTripodPhase + dt * 2.0 * Math.PI * stepFreq) % (Math.PI * 2);
      }

      // 2. Map 6 Legs to Biological VNC Motor Neuron Pool Firing Rates
      const vnc = this.vncLegs || {};
      const legHzMap = {
        pro_L: vnc.t1_left_hz !== undefined ? vnc.t1_left_hz : (this.forwardDrive * 24.0),
        pro_R: vnc.t1_right_hz !== undefined ? vnc.t1_right_hz : (this.forwardDrive * 24.0),
        meso_L: vnc.t2_left_hz !== undefined ? vnc.t2_left_hz : (this.forwardDrive * 24.0),
        meso_R: vnc.t2_right_hz !== undefined ? vnc.t2_right_hz : (this.forwardDrive * 24.0),
        meta_L: vnc.t3_left_hz !== undefined ? vnc.t3_left_hz : (this.forwardDrive * 24.0),
        meta_R: vnc.t3_right_hz !== undefined ? vnc.t3_right_hz : (this.forwardDrive * 24.0),
      };

      for (const leg of this.legs) {
        if (leg.name === 'pro_R' && this.isSwiping) {
          this.swipeProgress += dt * 2.2;
          const p = this.swipeProgress;

          if (p < 1.0) {
            const lift = Math.sin(p * Math.PI);
            leg.group.position.x = leg.defaultPosX + 0.16 * lift;
            leg.group.position.y = leg.defaultPosY + 0.32 * lift;
            leg.group.position.z = leg.defaultPosZ + 0.62 * lift;

            leg.femur.rotation.x = -1.1 * lift;
            leg.tibia.rotation.z = -0.5 * lift;
          } else {
            leg.group.position.set(leg.defaultPosX, leg.defaultPosY, leg.defaultPosZ);
            leg.femur.rotation.z = leg.defaultRotZ;
            leg.femur.rotation.x = leg.defaultFemurRotX;
            leg.tibia.rotation.z = leg.defaultTibiaRotZ;
            this.isSwiping = false;
            this.swipeProgress = 0;
          }
        } else {
          // Tripod A (pro_L, meso_R, meta_L) vs Tripod B (pro_R, meso_L, meta_R)
          const legPhase = (leg.tripodGroup === 'A') ? this.cpgTripodPhase : (this.cpgTripodPhase + Math.PI);
          const hz = legHzMap[leg.name] || 0;
          const normHz = Math.min(1.0, hz / 35.0);

          // Biological protraction/retraction amplitude scaled by leg motor pool rate
          const amp = 0.08 + normHz * 0.28;
          const swingLift = Math.max(0, Math.sin(legPhase));

          // Femur swing/stance cycle
          leg.femur.rotation.x = leg.defaultFemurRotX + Math.cos(legPhase) * amp + leg.side * this.steeringDeflection * 0.22;

          // Tibia flexion during swing phase to lift foot off ball
          leg.tibia.rotation.z = leg.defaultTibiaRotZ - leg.side * swingLift * (0.10 + normHz * 0.22);
        }
      }
    }

    if (this.treadmillBall) {
      const vnc = this.vncLegs;
      const avgHz = vnc ? (
        ((vnc.t1_left_hz || 0) + (vnc.t1_right_hz || 0) +
         (vnc.t2_left_hz || 0) + (vnc.t2_right_hz || 0) +
         (vnc.t3_left_hz || 0) + (vnc.t3_right_hz || 0)) / 6.0
      ) : (this.forwardDrive * 24.0);

      const ballPitch = (avgHz / 35.0) * 0.08;
      this.treadmillBall.rotation.x += ballPitch;
      this.treadmillBall.rotation.y += this.steeringDeflection * 0.04;
    }

    if (this.flyGroup && !this.jumpTriggered) {
      // Dynamic physical yaw and subtle banking when steering toward stimulus
      this.flyGroup.rotation.y = this.steeringDeflection * 0.22;
      this.flyGroup.rotation.z = -this.steeringDeflection * 0.08;
    }

    if (this.leftWing && this.rightWing) {
      if (this.jumpTriggered || this.forwardDrive > 0.6) {
        const flutter = Math.sin(time * 65) * 0.45;
        this.leftWing.rotation.z = 0.28 + flutter;
        this.rightWing.rotation.z = -0.28 - flutter;
      } else {
        const breath = Math.sin(time * 3) * 0.04;
        this.leftWing.rotation.z = 0.18 + breath;
        this.rightWing.rotation.z = -0.18 - breath;
      }
    }

    if (this.jumpTriggered) {
      this.jumpY += this.jumpVy;
      this.jumpVy -= 0.009;
      if (this.jumpY <= 0) {
        this.jumpY = 0;
        this.jumpVy = 0;
        this.jumpTriggered = false;
      }
      this.flyGroup.position.y = 1.18 + this.jumpY;
      this.flyGroup.position.z = -this.jumpY * 0.8;
    } else {
      this.flyGroup.position.y = 1.18;
      this.flyGroup.position.z = 0;
    }

    if (this.abdomenMeshes) {
      const abdPulse = 1.0 + Math.sin(time * 4.5) * 0.03;
      for (const seg of this.abdomenMeshes) {
        seg.scale.set(0.85 * abdPulse, 1.0 * abdPulse, 1.25);
      }
    }

    if (this.controls) {
      this.controls.update();
    }

    this.renderer.render(this.scene, this.camera);
  }
}

// ============================================================================
// 4. CENTRAL COMPLEX (EPG) COMPASS & NEUROCHEMICAL COCKPIT VISUALIZERS
// ============================================================================

// ============================================================================
// 4. CNS LIVE 3D NEURAL ACTIVITY & COCKPIT VISUALIZERS
// ============================================================================

class CNSBrainVisualizer3D {
  constructor(canvasId = 'cns-brain-canvas') {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.isWebGL = false;
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.brainGroup = null;
    this.pointCloud = null;
    this.somaCount = 0;
    this.graphToSomaMap = null;
    this.activityArray = null;
    this.activeSomaQueue = [];
    this._loaded = false;
    this._loading = false;

    // Interactive 3D controls & auto-rotation
    this.autoRotate = true;
    this.rotationSpeed = 0.0035;
    this.basePitch = 0.28; // Forward pitch so dorsal surface & optic lobes tilt toward viewer
    this.isDragging = false;
    this.prevPointerX = 0;
    this.prevPointerY = 0;
    this._rafId = null;

    this._initThree();
    this._initInteraction();
  }

  _initThree() {
    if (typeof THREE === 'undefined') {
      console.warn('[CNS Visualizer] THREE.js not available.');
      return;
    }
    try {
      const rect = this.canvas.parentElement
        ? this.canvas.parentElement.getBoundingClientRect()
        : this.canvas.getBoundingClientRect();
      const width = rect.width > 0 ? rect.width : 340;
      const height = rect.height > 0 ? rect.height : 220;

      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        alpha: true,
        antialias: true,
        powerPreference: 'high-performance',
      });
      this.renderer.setSize(width, height, false);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

      this.scene = new THREE.Scene();

      // Camera positioned closer to fill the viewport and showcase fine connectome anatomy
      this.camera = new THREE.PerspectiveCamera(36, width / height, 0.05, 50);
      this.camera.position.set(0, 0.36, 0.58);
      this.camera.lookAt(0, 0, -0.06);

      this.brainGroup = new THREE.Group();
      this.brainGroup.rotation.x = -0.34;
      this.brainGroup.rotation.z = -0.05;
      this.scene.add(this.brainGroup);

      this.isWebGL = true;
      this._startLoop();

      window.addEventListener('resize', () => this._onResize());
    } catch (err) {
      console.warn('[CNS Visualizer] WebGL init failed:', err);
      this.isWebGL = false;
    }
  }

  _onResize() {
    if (!this.canvas || !this.renderer || !this.camera) return;
    const rect = this.canvas.parentElement
      ? this.canvas.parentElement.getBoundingClientRect()
      : this.canvas.getBoundingClientRect();
    const w = rect.width > 0 ? rect.width : 340;
    const h = rect.height > 0 ? rect.height : 220;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  _initInteraction() {
    if (!this.canvas) return;

    this.canvas.addEventListener('pointerdown', (e) => {
      this.isDragging = true;
      this.prevPointerX = e.clientX;
      this.prevPointerY = e.clientY;
      try { this.canvas.setPointerCapture(e.pointerId); } catch (_) {}
    });

    window.addEventListener('pointermove', (e) => {
      if (!this.isDragging || !this.brainGroup) return;
      const dx = e.clientX - this.prevPointerX;
      const dy = e.clientY - this.prevPointerY;
      this.brainGroup.rotation.y += dx * 0.009;
      this.brainGroup.rotation.x = Math.max(-0.85, Math.min(0.85, this.brainGroup.rotation.x + dy * 0.009));
      this.prevPointerX = e.clientX;
      this.prevPointerY = e.clientY;
    });

    const stopDrag = (e) => {
      if (this.isDragging) {
        this.isDragging = false;
        try { this.canvas.releasePointerCapture(e.pointerId); } catch (_) {}
      }
    };
    window.addEventListener('pointerup', stopDrag);
    window.addEventListener('pointercancel', stopDrag);
  }

  loadSomas(somaData) {
    if (!this.isWebGL || !somaData) return;
    const { count, positions, circuitTags, graphToSomaMap } = somaData;
    this.somaCount = count;
    this.circuitTags = circuitTags;
    this.graphToSomaMap = graphToSomaMap;
    this._loaded = true;

    // Center somas around origin (dataset center is [0.0, -0.0368, -0.2180])
    const centeredPos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      centeredPos[i * 3 + 0] = positions[i * 3 + 0];
      centeredPos[i * 3 + 1] = positions[i * 3 + 1] - (-0.0368);
      centeredPos[i * 3 + 2] = positions[i * 3 + 2] - (-0.2180);
    }
    this.centeredPositions = centeredPos;

    // Rich bioluminescent palette matching Drosophila neuroanatomy:
    // 0: Central Brain -> deep electric blue       [0.15, 0.65, 0.95]
    // 1: Optic Lobe    -> crisp cyan               [0.00, 0.88, 1.00]
    // 2: Mushroom Body -> warm amber / honey gold  [1.00, 0.65, 0.15]
    // 3: Central Comp. -> mint / emerald green     [0.10, 0.95, 0.55]
    // 4: Motor / GF    -> fiery coral red          [1.00, 0.28, 0.22]
    // 5: VNC Thoracic  -> radiant violet           [0.68, 0.35, 1.00]
    const palette = [
      [0.15, 0.65, 0.95],
      [0.00, 0.88, 1.00],
      [1.00, 0.65, 0.15],
      [0.10, 0.95, 0.55],
      [1.00, 0.28, 0.22],
      [0.68, 0.35, 1.00],
    ];

    const colors = new Float32Array(count * 3);
    this.activityArray = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      const tag = circuitTags[i] < palette.length ? circuitTags[i] : 0;
      const rgb = palette[tag];
      colors[i * 3 + 0] = rgb[0];
      colors[i * 3 + 1] = rgb[1];
      colors[i * 3 + 2] = rgb[2];
      this.activityArray[i] = 0.0;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(centeredPos, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('activity', new THREE.BufferAttribute(this.activityArray, 1));

    const pointShaderMat = new THREE.ShaderMaterial({
      vertexColors: true,
      uniforms: {
        baseSize: { value: 0.0045 },
      },
      vertexShader: `
        #ifndef USE_COLOR
        attribute vec3 color;
        #endif
        attribute float activity;
        varying vec3 vColor;
        varying float vActivity;
        uniform float baseSize;
        void main() {
          vColor = color;
          vActivity = activity;
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          // Crisp resting points (~1.6px - 2.2px); active firing flares expand dynamically (~5.0px - 7.0px)
          float size = (baseSize + activity * 0.0090) * (260.0 / -mvPosition.z);
          gl_PointSize = clamp(size, 1.4, 7.5);
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        varying vec3 vColor;
        varying float vActivity;
        void main() {
          float dist = length(gl_PointCoord - vec2(0.5));
          if (dist > 0.5) discard;
          float radial = smoothstep(0.5, 0.06, dist);

          // Perfectly balanced resting silhouette: clearly visible, translucent holographic anatomy
          float restAlpha = radial * 0.065;
          vec3 restColor = vColor * 0.70;

          // Momentary firing flare: intense, brilliant bioluminescent sparks with glowing core
          float activeAlpha = radial * 0.92;
          vec3 activeColor = mix(vColor * 1.9, vec3(1.0, 1.0, 1.0), 0.45);

          vec3 finalColor = mix(restColor, activeColor, vActivity);
          float finalAlpha = mix(restAlpha, activeAlpha, vActivity);

          gl_FragColor = vec4(finalColor, finalAlpha);
        }
      `,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    if (this.pointCloud) {
      this.brainGroup.remove(this.pointCloud);
    }
    this.pointCloud = new THREE.Points(geometry, pointShaderMat);
    this.brainGroup.add(this.pointCloud);

    console.log(`[CNS 3D Visualizer] Loaded ${count.toLocaleString()} real EM somas into rotating brain.`);
  }

  async fetchSomasIfMissing() {
    if (this._loaded || this._loading) return;
    this._loading = true;
    try {
      const res = await fetch('/api/connectome/soma-coordinates');
      if (!res.ok) return;
      const buffer = await res.arrayBuffer();
      const headerView = new Uint32Array(buffer, 0, 2);
      const magic = headerView[0];
      const count = headerView[1];
      if (magic !== 0x464C5933) return;

      let offset = 16;
      const posBytes = count * 3 * 4;
      const positions = new Float32Array(buffer.slice(offset, offset + posBytes));
      offset += posBytes;

      const graphBytes = count * 4;
      const graphIndices = new Int32Array(buffer.slice(offset, offset + graphBytes));
      offset += graphBytes;

      const circuitTags = new Uint8Array(buffer.slice(offset, offset + count));
      offset += count;

      const graphToSomaMap = new Int32Array(166700);
      graphToSomaMap.fill(-1);
      for (let i = 0; i < count; i++) {
        const gIdx = graphIndices[i];
        if (gIdx >= 0 && gIdx < 166700) {
          graphToSomaMap[gIdx] = i;
        }
      }

      this.loadSomas({ count, positions, circuitTags, graphToSomaMap });
    } catch (e) {
      console.warn('[CNS 3D Visualizer] Direct fetch error:', e);
    } finally {
      this._loading = false;
    }
  }

  updateActivity(activeNeurons = []) {
    const countEl = document.getElementById('cns-active-count');
    if (countEl) {
      countEl.textContent = `${activeNeurons.length.toLocaleString()} active`;
    }

    if (!this.isWebGL || !this.pointCloud || !this.graphToSomaMap || !this.activityArray) return;

    // Subsample background telemetry spikes for a gentle biological shimmer
    const totalActive = activeNeurons.length;
    if (totalActive === 0) return;

    const maxSparksPerTick = 120;
    const stride = totalActive > maxSparksPerTick ? Math.ceil(totalActive / maxSparksPerTick) : 1;
    for (let i = 0; i < totalActive; i += stride) {
      const gIdx = activeNeurons[i];
      if (gIdx >= 0 && gIdx < this.graphToSomaMap.length) {
        const sIdx = this.graphToSomaMap[gIdx];
        if (sIdx >= 0 && sIdx < this.somaCount) {
          this.activityArray[sIdx] = 1.0;
          this.activeSomaQueue.push(sIdx);
        }
      }
    }
  }

  flashCircuit(circuitTag, filterFn = null, count = 220) {
    if (!this.isWebGL || !this.pointCloud || !this.circuitTags || !this.activityArray) return;

    const candidates = [];
    const n = this.somaCount;
    for (let i = 0; i < n; i++) {
      if (this.circuitTags[i] === circuitTag) {
        if (!filterFn || filterFn(this.centeredPositions, i)) {
          candidates.push(i);
        }
      }
    }

    if (candidates.length === 0) return;

    const sparks = Math.min(count, candidates.length);
    const step = Math.max(1, Math.floor(candidates.length / sparks));
    for (let j = 0; j < candidates.length; j += step) {
      const sIdx = candidates[j];
      this.activityArray[sIdx] = 1.0;
      this.activeSomaQueue.push(sIdx);
    }
    if (this.pointCloud.geometry.attributes.activity) {
      this.pointCloud.geometry.attributes.activity.needsUpdate = true;
    }
  }

  _startLoop() {
    const render = () => {
      // Smooth continuous 3D rotation
      if (this.brainGroup && this.autoRotate && !this.isDragging) {
        this.brainGroup.rotation.y += this.rotationSpeed;
      }

      // Smooth biological spike decay (~180ms transient)
      if (this.pointCloud && this.activeSomaQueue.length > 0) {
        const nextQueue = [];
        const actAttr = this.pointCloud.geometry.attributes.activity;
        for (let i = 0; i < this.activeSomaQueue.length; i++) {
          const sIdx = this.activeSomaQueue[i];
          this.activityArray[sIdx] *= 0.78;
          if (this.activityArray[sIdx] > 0.03) {
            nextQueue.push(sIdx);
          } else {
            this.activityArray[sIdx] = 0.0;
          }
        }
        this.activeSomaQueue = nextQueue;
        actAttr.needsUpdate = true;
      }

      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }

      this._rafId = requestAnimationFrame(render);
    };
    this._rafId = requestAnimationFrame(render);
  }
}

class CockpitVisualizers {
  constructor() {
    this.compassCanvas = document.getElementById('compass-canvas');
    this.compassCtx = this.compassCanvas ? this.compassCanvas.getContext('2d') : null;

    this.daCanvas = document.getElementById('da-waveform');
    this.daCtx = this.daCanvas ? this.daCanvas.getContext('2d') : null;

    this.oaCanvas = document.getElementById('oa-waveform');
    this.oaCtx = this.oaCanvas ? this.oaCanvas.getContext('2d') : null;

    this.stCanvas = document.getElementById('st-waveform');
    this.stCtx = this.stCanvas ? this.stCanvas.getContext('2d') : null;

    this.eiCanvas = document.getElementById('ei-waveform');
    this.eiCtx = this.eiCanvas ? this.eiCanvas.getContext('2d') : null;

    this.dopamineCanvas = document.getElementById('dopamine-chart');
    this.dopamineCtx = this.dopamineCanvas ? this.dopamineCanvas.getContext('2d') : null;

    this.rasterCanvas = document.getElementById('raster-canvas');
    this.rasterCtx = this.rasterCanvas ? this.rasterCanvas.getContext('2d') : null;

    this.cnsVisualizer = new CNSBrainVisualizer3D('cns-brain-canvas');
    this.headingDeg = 0;
    this.lastHistory = [];
  }

  updateCNSActivity(activeNeurons = []) {
    if (this.cnsVisualizer) {
      this.cnsVisualizer.updateActivity(activeNeurons);
    }
  }

  flashCircuit(circuitTag, filterFn = null, count = 160) {
    if (this.cnsVisualizer) {
      this.cnsVisualizer.flashCircuit(circuitTag, filterFn, count);
    }
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

    ctx.fillStyle = 'rgba(10, 15, 25, 0.85)';
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fill();

    const sectors = 16;
    for (let i = 0; i < sectors; i++) {
      const a1 = (i / sectors) * Math.PI * 2;
      const a2 = ((i + 1) / sectors) * Math.PI * 2;
      const sectorDeg = (i / sectors) * 360;

      const diff = Math.abs((((sectorDeg - headingDeg) + 180) % 360) - 180);
      const intensity = Math.max(0.1, 1.0 - diff / 60);

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, radius - 4, a1, a2);
      ctx.closePath();
      ctx.fillStyle = `rgba(0, 240, 255, ${intensity * 0.85})`;
      ctx.fill();

      ctx.strokeStyle = 'rgba(20, 30, 45, 0.9)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    ctx.strokeStyle = '#00f0ff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.stroke();

    const rad = (headingDeg - 90) * (Math.PI / 180);
    const nx = cx + Math.cos(rad) * (radius - 8);
    const ny = cy + Math.sin(rad) * (radius - 8);

    ctx.strokeStyle = '#ff9d00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(nx, ny);
    ctx.stroke();

    ctx.fillStyle = '#ff9d00';
    ctx.beginPath();
    ctx.arc(cx, cy, 3.5, 0, Math.PI * 2);
    ctx.fill();
  }

  _drawSparkline(ctx, canvas, history, getValue, color, bgGrad, isPercent = false) {
    if (!ctx || !canvas) return;
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    if (!history || history.length < 2) return;

    const vals = history.map(pt => getValue(pt));
    const rawMin = Math.min(...vals);
    const rawMax = Math.max(...vals);

    let minVal, maxVal;
    if (isPercent) {
      minVal = Math.max(0, Math.floor(rawMin - 3));
      maxVal = Math.min(100, Math.ceil(Math.max(minVal + 8, rawMax + 3)));
    } else {
      minVal = Math.max(0, Math.floor(rawMin - 3));
      maxVal = Math.ceil(Math.max(minVal + 10, rawMax + 3));
    }
    const range = Math.max(0.2, maxVal - minVal);
    const stepX = w / (history.length - 1);

    // Subtle mid reference line
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.07)';
    ctx.setLineDash([2, 3]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h * 0.5);
    ctx.lineTo(w, h * 0.5);
    ctx.stroke();
    ctx.restore();

    // Soft luminous gradient under trace
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, bgGrad);
    grad.addColorStop(1, 'rgba(0, 0, 0, 0.0)');

    ctx.beginPath();
    ctx.moveTo(0, h);
    for (let i = 0; i < history.length; i++) {
      const x = i * stepX;
      const val = getValue(history[i]);
      const normY = Math.max(0, Math.min(1, (val - minVal) / range));
      const y = h - 4 - normY * (h - 8);
      ctx.lineTo(x, y);
    }
    ctx.lineTo((history.length - 1) * stepX, h);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Vibrant line trace with neon glow
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.8;
    ctx.shadowColor = color;
    ctx.shadowBlur = 6;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    for (let i = 0; i < history.length; i++) {
      const x = i * stepX;
      const val = getValue(history[i]);
      const normY = Math.max(0, Math.min(1, (val - minVal) / range));
      const y = h - 4 - normY * (h - 8);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();

    // Glowing head cursor dot at current real-time point
    const lastIdx = history.length - 1;
    const lastX = lastIdx * stepX;
    const lastVal = getValue(history[lastIdx]);
    const lastNormY = Math.max(0, Math.min(1, (lastVal - minVal) / range));
    const lastY = h - 4 - lastNormY * (h - 8);

    ctx.save();
    ctx.shadowColor = color;
    ctx.shadowBlur = 10;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(lastX - 2, lastY, 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();
  }

  drawDopamineWaveform(history = []) {
    this.lastHistory = history;
    if (!history || history.length < 2) return;

    // 1. Dopamine (PAM11) - lime #a3e635
    this._drawSparkline(
      this.daCtx,
      this.daCanvas,
      history,
      pt => pt.dopamine_hz || 0,
      '#a3e635',
      'rgba(163, 230, 53, 0.25)',
      false
    );

    // 2. Octopamine (TDC2) - neon orange #fb923c
    this._drawSparkline(
      this.oaCtx,
      this.oaCanvas,
      history,
      pt => pt.octopamine_hz || 0,
      '#fb923c',
      'rgba(251, 146, 60, 0.25)',
      false
    );

    // 3. Serotonin (5-HT) - neon cyan #38bdf8
    this._drawSparkline(
      this.stCtx,
      this.stCanvas,
      history,
      pt => pt.serotonin_hz || 0,
      '#38bdf8',
      'rgba(56, 189, 248, 0.25)',
      false
    );

    // 4. E/I Balance (Dale's Law) - neon mint #34d399
    this._drawSparkline(
      this.eiCtx,
      this.eiCanvas,
      history,
      pt => ((pt.ei_balance !== undefined ? pt.ei_balance : (pt.ei_balance_ratio || 0.644)) * 100),
      '#34d399',
      'rgba(52, 211, 153, 0.25)',
      true
    );
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

      const activeUnits = Math.min(rows, Math.floor(spikes / 3));
      for (let r = 0; r < activeUnits; r++) {
        const neuronId = (r * 17 + c * 7) % rows;
        const y = neuronId * rowHeight;

        ctx.fillStyle = r % 3 === 0 ? '#00f0ff' : '#00ff88';
        ctx.fillRect(x, y, Math.max(1.5, colWidth - 0.5), rowHeight - 0.8);
      }
    }
  }
}

// ============================================================================
// 5. BIDIRECTIONAL TELEMETRY & ENGINE ORCHESTRATOR
// ============================================================================

class ConnectomeApp {
  constructor() {
    this.stimulus = new StimulusGenerator('virtual-phone-canvas');
    this.chamber = new ObservationChamber3D('three-container', this.stimulus.canvas);
    this.visualizers = new CockpitVisualizers();

    // Link real 141K somas to the 3D CNS visualizer
    if (this.chamber.somaData) {
      this.visualizers.cnsVisualizer.loadSomas(this.chamber.somaData);
    } else {
      this.chamber.onSomaDataLoaded = (somaData) => {
        if (this.visualizers && this.visualizers.cnsVisualizer) {
          this.visualizers.cnsVisualizer.loadSomas(somaData);
        }
      };
    }

    this.ws = null;
    this.isStreaming = false;

    this._initLanguageSwitcher();
    this._initDomBindings();
    this._initMobileNavigation();
    this._initCustomPhotoUpload();
    this._initWebSocket();
    this._startObservationLoop();
  }

  _initMobileNavigation() {
    const navBtns = document.querySelectorAll('.mobile-nav-btn');
    const grid = document.querySelector('.cockpit-grid');
    if (!navBtns.length || !grid) return;

    // Default mobile active tab is the 3D observation viewport
    grid.setAttribute('data-mobile-tab', 'viewport');

    navBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.getAttribute('data-tab');
        if (!tab) return;

        navBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        grid.setAttribute('data-mobile-tab', tab);

        // When switching back to 3D Viewport on mobile, trigger Three.js resize event
        if (tab === 'viewport') {
          setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
          }, 80);
        }
      });
    });
  }

  _initLanguageSwitcher() {
    window.currentLang = localStorage.getItem('flyconnectome_lang') || 'en';
    this._applyLanguage(window.currentLang);

    const btnEn = document.getElementById('lang-btn-en');
    const btnTr = document.getElementById('lang-btn-tr');

    if (btnEn && btnTr) {
      btnEn.addEventListener('click', () => {
        this._setLanguage('en');
      });
      btnTr.addEventListener('click', () => {
        this._setLanguage('tr');
      });
    }
  }

  _setLanguage(lang) {
    window.currentLang = lang;
    localStorage.setItem('flyconnectome_lang', lang);
    this._applyLanguage(lang);
  }

  _applyLanguage(lang) {
    const btnEn = document.getElementById('lang-btn-en');
    const btnTr = document.getElementById('lang-btn-tr');
    if (btnEn && btnTr) {
      if (lang === 'tr') {
        btnTr.classList.add('active');
        btnEn.classList.remove('active');
      } else {
        btnEn.classList.add('active');
        btnTr.classList.remove('active');
      }
    }

    const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    if (this.stimulus) {
      this.stimulus.updateCardInfo();
    }

    if (this.visualizers && typeof this.visualizers.refreshChannelTexts === 'function') {
      this.visualizers.refreshChannelTexts();
    }

    const heroTime = document.getElementById('hero-neural-time');
    if (heroTime && this.lastTelemetrySnapshot?.latest) {
      const stepMs = this.lastTelemetrySnapshot.latest.duration_ms || 50;
      heroTime.textContent = lang === 'tr' ? `${Math.round(stepMs)} ms nöral sürede` : `in ${Math.round(stepMs)} ms of neural time`;
    }

    const statusEl = document.getElementById('engine-status');
    if (statusEl) {
      statusEl.textContent = lang === 'tr' ? '60 FPS CANLI' : '60 FPS LIVE';
    }
  }

  sendWsCommand(payload) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload));
    }
  }

  _initDomBindings() {
    document.querySelectorAll('.stim-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.id === 'upload-btn') return;
        document.querySelectorAll('.stim-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const preset = btn.getAttribute('data-preset');
        if (preset) {
          this.stimulus.setPreset(preset);
          const info = this.stimulus.presetsInfo[preset];
          const name = info?.title?.en || preset;
          const valence = info?.tag?.en || 'NEUTRAL';
          this.sendWsCommand({
            command: 'stimulus_preset',
            preset,
            name,
            valence,
          });

          // Momentarily flash corresponding sensory/neuropil circuit
          if (this.visualizers) {
            if (preset === 'predator' || preset === 'looming') {
              this.visualizers.flashCircuit(4, null, 180); // Giant Fiber / Escape Motor
              this.visualizers.flashCircuit(1, null, 100); // Optic Lobe
            } else if (preset === 'sugar') {
              this.visualizers.flashCircuit(2, null, 160); // Mushroom Body / Dopamine
              this.visualizers.flashCircuit(1, null, 90);  // Optic Lobe
            } else if (preset === 'mate') {
              this.visualizers.flashCircuit(0, null, 140); // Central Brain Courtship (P1)
              this.visualizers.flashCircuit(1, null, 90);  // Optic Lobe
            } else {
              this.visualizers.flashCircuit(1, null, 140); // Optic Lobes
            }
          }
        }
      });
    });

    document.querySelectorAll('.pos-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.pos-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const pos = btn.getAttribute('data-pos');
        if (pos) {
          this.stimulus.setPosition(pos);
          this.sendWsCommand({
            command: 'target_position',
            position: pos,
          });

          // Momentarily trigger localized sensory hemisphere
          if (this.visualizers) {
            if (pos === 'left') {
              // Left Optic Lobe hemisphere (x < -0.02)
              this.visualizers.flashCircuit(1, (p, i) => p[i * 3 + 0] < -0.02, 180);
            } else if (pos === 'right') {
              // Right Optic Lobe hemisphere (x > 0.02)
              this.visualizers.flashCircuit(1, (p, i) => p[i * 3 + 0] > 0.02, 180);
            } else {
              // Center: Central Complex navigation compass + both lobes
              this.visualizers.flashCircuit(3, null, 180);
              this.visualizers.flashCircuit(1, null, 120);
            }
          }
        }
      });
    });

    const wireheadBtn = document.getElementById('wirehead-btn');
    if (wireheadBtn) {
      wireheadBtn.addEventListener('click', () => {
        this.triggerWirehead(20.0);
        if (this.visualizers) {
          // Momentarily ignite Mushroom Body (PAM11 Dopaminergic cluster) in honey gold
          this.visualizers.flashCircuit(2, null, 220);
        }
      });
    }

    const threatBtn = document.getElementById('threat-btn');
    if (threatBtn) {
      threatBtn.addEventListener('click', () => {
        this.stimulus.triggerLoomingPulse();
        this.sendWsCommand({
          command: 'threat_trigger',
        });
        if (this.visualizers) {
          // Momentarily ignite Giant Fiber & Descending Escape Motor circuit in fiery coral red
          this.visualizers.flashCircuit(4, null, 240);
        }
      });
    }

    const swipeBtn = document.getElementById('swipe-btn');
    if (swipeBtn) {
      swipeBtn.addEventListener('click', () => {
        this.chamber.triggerLegSwipe();
        this.sendWsCommand({
          command: 'leg_swipe',
        });
        if (this.visualizers) {
          // Momentarily ignite VNC Thoracic cord neuromeres in vibrant violet
          this.visualizers.flashCircuit(5, null, 220);
        }
      });
    }

    // ── Startup sync: fire the initially-active preset and position immediately
    // so the brain receives the correct first frame without waiting for a click.
    const initialPresetBtn = document.querySelector('.stim-btn.active[data-preset]');
    if (initialPresetBtn) {
      const preset = initialPresetBtn.getAttribute('data-preset');
      this.stimulus.setPreset(preset);
      const info = this.stimulus.presetsInfo[preset];
      const name = info?.title?.en || preset;
      const valence = info?.tag?.en || 'NEUTRAL';
      // Send after a brief delay to let WebSocket connect first
      setTimeout(() => {
        this.sendWsCommand({ command: 'stimulus_preset', preset, name, valence });
      }, 800);
    }

    const initialPosBtn = document.querySelector('.pos-btn.active[data-pos]');
    if (initialPosBtn) {
      const pos = initialPosBtn.getAttribute('data-pos');
      this.stimulus.setPosition(pos);
    }
  }

  _updateActiveHeroChannel() {
    if (!this.lastTelemetrySnapshot || !this.lastTelemetrySnapshot.latest) return;
    this._handleTelemetrySnapshot(this.lastTelemetrySnapshot);
  }

  _initCustomPhotoUpload() {
    const fileInput = document.getElementById('photo-upload-input');
    const uploadBtn = document.getElementById('upload-btn');
    const previewContainer = document.querySelector('.screen-preview-container');

    if (uploadBtn && fileInput) {
      uploadBtn.addEventListener('click', () => {
        fileInput.click();
      });

      fileInput.addEventListener('change', e => {
        const file = e.target.files && e.target.files[0];
        if (file) this._handleImageFile(file);
      });
    }

    if (previewContainer) {
      previewContainer.addEventListener('dragover', e => {
        e.preventDefault();
        previewContainer.classList.add('dragover');
      });

      previewContainer.addEventListener('dragleave', () => {
        previewContainer.classList.remove('dragover');
      });

      previewContainer.addEventListener('drop', e => {
        e.preventDefault();
        previewContainer.classList.remove('dragover');
        const file = e.dataTransfer.files && e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
          this._handleImageFile(file);
        }
      });
    }
  }

  _handleImageFile(file) {
    const reader = new FileReader();
    reader.onload = event => {
      const img = new Image();
      img.onload = () => {
        document.querySelectorAll('.stim-btn').forEach(b => b.classList.remove('active'));
        const uploadBtn = document.getElementById('upload-btn');
        if (uploadBtn) uploadBtn.classList.add('active');

        this.stimulus.loadCustomImage(img, file.name);
        const valence = this.stimulus.customImageValence?.tag?.en || 'CUSTOM';
        this.sendWsCommand({
          command: 'custom_photo',
          name: file.name,
          valence,
        });
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  }

  _initWebSocket() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    if (this._wsReconnectTimer) {
      clearTimeout(this._wsReconnectTimer);
      this._wsReconnectTimer = null;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || '127.0.0.1:8000';
    const wsUrl = `${protocol}//${host}/ws/telemetry`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        if (this._wsReconnectTimer) {
          clearTimeout(this._wsReconnectTimer);
          this._wsReconnectTimer = null;
        }
        this._isFrameInFlight = false;
        console.log('[Connectome WS] Connected to biophysical engine');
        const statusEl = document.getElementById('engine-status');
        if (statusEl) {
          statusEl.textContent = window.currentLang === 'tr' ? '60 FPS CANLI' : '60 FPS LIVE';
        }
      };

      this.ws.onmessage = event => {
        // Acknowledge in-flight frame
        this._isFrameInFlight = false;
        try {
          const snapshot = JSON.parse(event.data);
          // Respond to server keep-alive ping with pong to maintain connection
          if (snapshot && snapshot.ping) {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
              this.ws.send(JSON.stringify({ command: 'pong' }));
            }
            return;
          }
          this._handleTelemetrySnapshot(snapshot);
        } catch (err) {
          console.error('[Connectome WS] Parse error:', err);
        }
      };

      this.ws.onerror = err => {
        console.warn('[Connectome WS] WebSocket error:', err);
      };

      this.ws.onclose = event => {
        this._isFrameInFlight = false;
        console.log(`[Connectome WS] Disconnected (code: ${event.code}, reason: "${event.reason || 'clean'}"). Reconnecting in 2s...`);
        if (!this._wsReconnectTimer) {
          this._wsReconnectTimer = setTimeout(() => {
            this._wsReconnectTimer = null;
            this._initWebSocket();
          }, 2000);
        }
      };
    } catch (e) {
      console.warn('[Connectome WS] WebSocket init failed:', e);
    }

    // Immediate reconnection on tab restore / focus
    if (!this._hasVisibilityListener) {
      this._hasVisibilityListener = true;
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          if (!this.ws || this.ws.readyState === WebSocket.CLOSED || this.ws.readyState === WebSocket.CLOSING) {
            console.log('[Connectome WS] Tab returned to foreground, reconnecting WebSocket immediately...');
            this._initWebSocket();
          }
        }
      });
    }
  }

  _startObservationLoop() {
    this._isFrameInFlight = false;
    this._lastFrameTime = 0;

    setInterval(() => {
      // If browser tab is minimized or hidden, pause sensory capture to conserve CPU & avoid timeouts
      if (document.hidden) return;

      this.stimulus.render(0.05);

      // Backpressure flow control:
      // The biological connectome steps in ~130ms. If previous frame is still
      // in-flight, skip sending this tick to prevent TCP buffer overflow.
      const now = performance.now();
      if (this._isFrameInFlight) {
        if (now - this._lastFrameTime > 800) {
          this._isFrameInFlight = false; // Safety timeout recovery
        } else {
          return; // Engine still calculating, wait for response
        }
      }

      const frameB64 = this.stimulus.getBase64Frame();
      this._isFrameInFlight = true;
      this._lastFrameTime = now;

      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(
          JSON.stringify({
            command: 'observe',
            image_base64: frameB64,
            duration_ms: 50.0,
          })
        );
      } else {
        fetch('/api/observe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: frameB64,
            duration_ms: 50.0,
          }),
        })
          .then(res => res.json())
          .then(data => {
            this._isFrameInFlight = false;
            this._handleTelemetrySnapshot(data);
          })
          .catch(() => {
            this._isFrameInFlight = false;
          });
      }
    }, 50);
  }

  triggerWirehead(currentMv = 20.0) {
    console.log(`[Connectome] Injecting +${currentMv} mV dopamine wirehead`);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          command: 'wirehead',
          current_mv: currentMv,
        })
      );
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
    this.lastTelemetrySnapshot = snapshot;
    const t = snapshot.latest;

    this.chamber.updateFromTelemetry(t);

    const simMs = t.sim_time_ms || 0;
    document.getElementById('sim-time').textContent =
      simMs >= 100000
        ? `${(simMs / 1000).toFixed(1)}s`
        : `${simMs.toFixed(simMs >= 1000 ? 0 : 1)} ms`;
    document.getElementById('total-spikes').textContent = (t.spike_counts?.total_spikes || 0).toLocaleString();

    const h = t.hormones || {};
    const da = h.dopamine_nm || 5.0;
    const oa = h.octopamine_nm || 2.0;
    const st = h.serotonin_nm || 8.0;

    const daHz = t.spike_counts?.dopamine_hz || 0;
    const oaHz = t.spike_counts?.octopamine_hz || 0;
    const stHz = t.spike_counts?.serotonin_hz || 0;
    const totalSpk = t.spike_counts?.total_spikes || 0;

    // Dynamic E/I Balance (Dale's Law)
    const eiRatio = h.ei_balance !== undefined ? h.ei_balance : (t.ei_balance_ratio !== undefined ? t.ei_balance_ratio : 0.644);
    const excSpk = t.excitatory_spikes || t.spike_counts?.excitatory_spikes || 0;
    const inhSpk = t.inhibitory_spikes || t.spike_counts?.inhibitory_spikes || 0;
    const eiPercent = (eiRatio * 100).toFixed(1);

    // Active Channel Left Hero Metric (DA, OA, 5-HT, E/I)
    const activeCh = (this.visualizers && this.visualizers.activeChannel) || 'da';
    const heroValEl = document.getElementById('hero-channel-val');
    if (heroValEl) {
      if (activeCh === 'da') {
        heroValEl.textContent = daHz.toFixed(1);
      } else if (activeCh === 'oa') {
        heroValEl.textContent = oaHz.toFixed(1);
      } else if (activeCh === 'st') {
        heroValEl.textContent = stHz.toFixed(1);
      } else if (activeCh === 'ei') {
        heroValEl.textContent = eiPercent;
      }
    }

    // Right Hero Metric: Total Fly Spikes & Neural Duration
    const heroSpk = document.getElementById('hero-spikes-val');
    if (heroSpk) heroSpk.textContent = totalSpk.toLocaleString();

    const heroTime = document.getElementById('hero-neural-time');
    if (heroTime) {
      const stepMs = t.duration_ms || 50;
      const lang = window.currentLang || 'en';
      heroTime.textContent = lang === 'tr' ? `${Math.round(stepMs)} ms içinde` : `in ${Math.round(stepMs)} ms`;
    }

    // Legacy backwards-compatibility ID
    const heroDa = document.getElementById('hero-da-val');
    if (heroDa) heroDa.textContent = daHz.toFixed(1);

    // 4-Channel Modern Real-Time Telemetry Rows (All Channels Alt Alta)
    // 1. Dopamine (PAM11)
    const daHzEl = document.getElementById('da-hz');
    if (daHzEl) daHzEl.textContent = daHz.toFixed(1);
    const daNmEl = document.getElementById('da-nm');
    if (daNmEl) daNmEl.textContent = da.toFixed(2);

    // 2. Octopamine (TDC2)
    const oaHzEl = document.getElementById('oa-hz');
    if (oaHzEl) oaHzEl.textContent = oaHz.toFixed(1);
    const oaNmEl = document.getElementById('oa-nm');
    if (oaNmEl) oaNmEl.textContent = oa.toFixed(2);

    // 3. Serotonin (5-HT)
    const stHzEl = document.getElementById('st-hz');
    if (stHzEl) stHzEl.textContent = stHz.toFixed(1);
    const stNmEl = document.getElementById('st-nm');
    if (stNmEl) stNmEl.textContent = st.toFixed(2);

    // 4. E/I Balance (Dale's Law)
    const eiValEl = document.getElementById('ei-val');
    const excEl = document.getElementById('exc-spikes');
    const inhEl = document.getElementById('inh-spikes');

    if (eiValEl) eiValEl.textContent = `${eiPercent}%`;
    if (excEl) excEl.textContent = excSpk.toLocaleString();
    if (inhEl) inhEl.textContent = inhSpk.toLocaleString();

    if (eiFillEl) {
      eiFillEl.style.width = `${Math.min(100, Math.max(0, eiRatio * 100))}%`;
      if (eiRatio > 0.80) {
        eiFillEl.style.background = 'linear-gradient(90deg, #ff9100, #ff1744)';
      } else if (eiRatio < 0.50) {
        eiFillEl.style.background = 'linear-gradient(90deg, #2979ff, #00e5ff)';
      } else {
        eiFillEl.style.background = 'linear-gradient(90deg, #34d399, #00e5ff)';
      }
    }

    const m = t.motor || {};
    const steer = m.steering_deflection || 0;
    const drive = m.forward_drive_pct || 0;

    document.getElementById('steering-val').textContent = (steer >= 0 ? '+' : '') + steer.toFixed(2);
    const steerPercent = 50 + steer * 45;
    document.getElementById('steering-indicator').style.left = `${Math.max(5, Math.min(95, steerPercent))}%`;

    // Retinal Hemisphere Telemetry (Phototaxis / Light Asymmetry)
    const vis = t.visual || {};
    const lumL = vis.left_luminance !== undefined ? vis.left_luminance : (t.left_luminance || 0);
    const lumR = vis.right_luminance !== undefined ? vis.right_luminance : (t.right_luminance || 0);
    const asym = vis.hemispheric_asymmetry !== undefined ? vis.hemispheric_asymmetry : (t.hemispheric_asymmetry || 0);

    const lumLFill = document.getElementById('lum-left-fill');
    if (lumLFill) lumLFill.style.width = `${Math.min(100, Math.max(0, lumL * 100))}%`;

    const lumRFill = document.getElementById('lum-right-fill');
    if (lumRFill) lumRFill.style.width = `${Math.min(100, Math.max(0, lumR * 100))}%`;

    const asymValEl = document.getElementById('retinal-asym-val');
    if (asymValEl) {
      const lang = window.currentLang || 'en';
      if (asym < -0.06) {
        asymValEl.textContent = `${asym.toFixed(2)} (${lang === 'tr' ? 'Sol Baskın' : 'Left Dominant'})`;
        asymValEl.style.color = '#38bdf8';
      } else if (asym > 0.06) {
        asymValEl.textContent = `+${asym.toFixed(2)} (${lang === 'tr' ? 'Sağ Baskın' : 'Right Dominant'})`;
        asymValEl.style.color = '#38bdf8';
      } else {
        asymValEl.textContent = `0.00 (${lang === 'tr' ? 'Dengeli' : 'Balanced'})`;
        asymValEl.style.color = 'var(--text-muted)';
      }
    }

    document.getElementById('drive-val').textContent = `${drive.toFixed(0)}%`;
    document.getElementById('drive-fill').style.width = `${Math.max(0, Math.min(100, drive))}%`;

    const badgeRetreat = document.getElementById('badge-retreat');
    if (badgeRetreat) {
      if (m.moonwalker_retreat) {
        badgeRetreat.classList.add('active');
        if (this.visualizers) {
          this.visualizers.flashCircuit(4, null, 90);
          this.visualizers.flashCircuit(5, null, 110);
        }
      } else {
        badgeRetreat.classList.remove('active');
      }
    }

    const badgeJump = document.getElementById('badge-jump');
    if (badgeJump) {
      if (m.giant_fiber_jump) {
        badgeJump.classList.add('active');
        if (this.visualizers) {
          this.visualizers.flashCircuit(4, null, 160);
        }
      } else {
        badgeJump.classList.remove('active');
      }
    }

    const heading = m.compass_heading_deg || 0;
    document.getElementById('heading-deg').textContent = `${heading.toFixed(1)}°`;
    this.visualizers.drawEPGCompass(heading);

    const plast = h.plasticity_index || 0;
    document.getElementById('plasticity-val').textContent = (plast >= 0 ? '+' : '') + plast.toFixed(3);

    // VNC Thoracic Hexapod Motor Telemetry
    const vnc = t.vnc_legs || {};
    const t1l = vnc.t1_left_hz !== undefined ? vnc.t1_left_hz : 0;
    const t1r = vnc.t1_right_hz !== undefined ? vnc.t1_right_hz : 0;
    const t2l = vnc.t2_left_hz !== undefined ? vnc.t2_left_hz : 0;
    const t2r = vnc.t2_right_hz !== undefined ? vnc.t2_right_hz : 0;
    const t3l = vnc.t3_left_hz !== undefined ? vnc.t3_left_hz : 0;
    const t3r = vnc.t3_right_hz !== undefined ? vnc.t3_right_hz : 0;
    const tripodPhase = vnc.tripod_phase !== undefined ? vnc.tripod_phase : (this.chamber ? this.chamber.cpgTripodPhase : 0);

    const setLegHz = (id, hz) => {
      const el = document.getElementById(id);
      if (el) el.textContent = `${hz.toFixed(1)} Hz`;
    };
    setLegHz('vnc-t1l-hz', t1l);
    setLegHz('vnc-t1r-hz', t1r);
    setLegHz('vnc-t2l-hz', t2l);
    setLegHz('vnc-t2r-hz', t2r);
    setLegHz('vnc-t3l-hz', t3l);
    setLegHz('vnc-t3r-hz', t3r);

    const setLegBar = (id, hz) => {
      const el = document.getElementById(id);
      if (el) el.style.width = `${Math.min(100, Math.max(0, (hz / 35.0) * 100))}%`;
    };
    setLegBar('vnc-t1l-fill', t1l);
    setLegBar('vnc-t1r-fill', t1r);
    setLegBar('vnc-t2l-fill', t2l);
    setLegBar('vnc-t2r-fill', t2r);
    setLegBar('vnc-t3l-fill', t3l);
    setLegBar('vnc-t3r-fill', t3r);

    // Tripod A vs Tripod B Alternation
    // When sin(phase) > 0: Tripod A in Swing, Tripod B in Stance
    // When sin(phase) <= 0: Tripod A in Stance, Tripod B in Swing
    const isASwing = Math.sin(tripodPhase) > 0;
    const tripAEl = document.getElementById('tripod-a-badge');
    const tripBEl = document.getElementById('tripod-b-badge');
    if (tripAEl && tripBEl) {
      if (isASwing) {
        tripAEl.className = 'tripod-pill active-swing';
        tripBEl.className = 'tripod-pill active-stance';
      } else {
        tripAEl.className = 'tripod-pill active-stance';
        tripBEl.className = 'tripod-pill active-swing';
      }
    }

    const updateCard = (id, isSwing) => {
      const el = document.getElementById(id);
      if (el) {
        el.classList.toggle('swing-active', isSwing);
        el.classList.toggle('stance-active', !isSwing);
      }
    };
    // Tripod A: L1, R2, L3
    updateCard('leg-card-t1l', isASwing);
    updateCard('leg-card-t2r', isASwing);
    updateCard('leg-card-t3l', isASwing);

    // Tripod B: R1, L2, R3
    updateCard('leg-card-t1r', !isASwing);
    updateCard('leg-card-t2l', !isASwing);
    updateCard('leg-card-t3r', !isASwing);

    if (snapshot.history) {
      this.visualizers.drawDopamineWaveform(snapshot.history);
      this.visualizers.drawSpikeRaster(snapshot.history);
    }

    const activeNeurons = t.active_neurons || [];
    if (this.visualizers && typeof this.visualizers.updateCNSActivity === 'function') {
      this.visualizers.updateCNSActivity(activeNeurons);
    }
  }

  start() {
    this.chamber.animate();
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.app = new ConnectomeApp();
  window.app.start();
});
