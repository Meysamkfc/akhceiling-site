/* Procedural 3D hero: a suspended ceiling seen from below — T-bar grid, 60x60 tiles, luminous panels and a gypsum
   "hidden light" coffer. Nothing is downloaded: the geometry is generated here. Pauses when off-screen / hidden. */
import {
  WebGLRenderer, Scene, PerspectiveCamera, Color, Fog, InstancedMesh, BoxGeometry, PlaneGeometry, MeshStandardMaterial,
  MeshBasicMaterial, Object3D, HemisphereLight, DirectionalLight, PointLight, PCFSoftShadowMap, Group, Points, BufferGeometry,
  Float32BufferAttribute, PointsMaterial, MathUtils, TextureLoader, SRGBColorSpace
} from 'three';
import { getProject, types } from '@theatre/core';

// a one-shot, precisely-keyframed entrance (Theatre.js): the camera dollies in from further back/higher
// and settles into the exact same resting pose the idle loop below already computes, as an additive
// offset that eases to zero — so once it finishes, the hand-off to the idle drift is seamless and the
// scene itself (grid, lights, coffer) is untouched. Skipped entirely under prefers-reduced-motion.
const INTRO_LEN = 2.4;
const bez = [0.42, 1, 0.42, 0];
const kf = (id, position, value) => ({ id, position, value, handles: bez, connectedRight: position === 0, type: 'bezier' });
const THEATRE_STATE = {
  sheetsById: {
    Intro: {
      staticOverrides: { byObject: {} },
      sequence: {
        type: 'PositionalSequence', length: INTRO_LEN, subUnitsPerUnit: 30,
        tracksByObject: {
          camera: {
            trackIdByPropPath: { '["zOff"]': 'trZ', '["rotOff"]': 'trR', '["yOff"]': 'trY' },
            trackData: {
              trZ: { type: 'BasicKeyframedTrack', keyframes: [kf('z0', 0, -17), kf('z1', INTRO_LEN, 0)] },
              trR: { type: 'BasicKeyframedTrack', keyframes: [kf('r0', 0, -0.42), kf('r1', INTRO_LEN, 0)] },
              trY: { type: 'BasicKeyframedTrack', keyframes: [kf('y0', 0, 1.1), kf('y1', INTRO_LEN, 0)] },
            },
          },
        },
      },
    },
  },
};

const host = document.getElementById('hero');
const canvas = document.getElementById('hero3d');
if (host && canvas) {
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const small = matchMedia('(max-width: 760px)').matches;
  let renderer;
  try { renderer = new WebGLRenderer({ canvas, antialias: !small, alpha: true, powerPreference: 'high-performance' }); } catch (e) { renderer = null; }
  if (renderer) {
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, small ? 1.5 : 1.75));
    if (!small) { renderer.shadowMap.enabled = true; renderer.shadowMap.type = PCFSoftShadowMap; }
    const NIGHT = new Color(0x15173f);
    renderer.setClearColor(NIGHT, 0);
    const scene = new Scene();
    scene.fog = new Fog(NIGHT, 9, small ? 34 : 52);
    const cam = new PerspectiveCamera(62, 1, 0.1, 80);
    scene.add(new HemisphereLight(0xeef0ff, 0x1f2152, 1.4));

    const T = 0.6, COLS = 22, ROWS = small ? 70 : 110, Y = 3.0;           // 60 cm tiles, ceiling height 3 m
    const x0 = -(COLS * T) / 2, z0 = 2;
    const dummy = new Object3D();

    // a soft key light for real form-shading across the grid, plus a warm point light standing in for the
    // hidden-light cove around the gypsum coffer — it casts real (soft) shadows for depth, not flat fill light
    const key = new DirectionalLight(0xeef0ff, 0.55);
    key.position.set(-6, Y + 4, -10);
    scene.add(key);
    const cove = new PointLight(0xffc27a, small ? 1.6 : 2.6, 13, 2);
    cove.position.set(0, Y - 0.2, -21);
    if (!small) { cove.castShadow = true; cove.shadow.mapSize.set(512, 512); cove.shadow.bias = -0.0015; cove.shadow.radius = 3; cove.shadow.camera.near = 0.3; cove.shadow.camera.far = 13; }
    scene.add(cove);

    // --- tiles (instanced) ---
    const tileGeo = new PlaneGeometry(T - 0.028, T - 0.028); tileGeo.rotateX(Math.PI / 2);
    const tileMat = new MeshStandardMaterial({ color: 0xf0f1fa, roughness: .95, metalness: 0, transparent: true, opacity: .62 });
    const tiles = new InstancedMesh(tileGeo, tileMat, COLS * ROWS);
    const lightGeo = tileGeo.clone();
    const lights = [];
    let n = 0;
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
      const x = x0 + c * T + T / 2, z = z0 - r * T - T / 2;
      const lit = (r % 5 === 2) && (c % 4 === 1);
      if (lit) { lights.push([x, z]); dummy.position.set(x, Y - 0.001, z); dummy.updateMatrix(); tiles.setMatrixAt(n++, dummy.matrix); dummy.position.set(x, -999, z); }
      else { dummy.position.set(x, Y, z); dummy.updateMatrix(); tiles.setMatrixAt(n++, dummy.matrix); }
      const v = 0.94 + (Math.sin(c * 12.9898 + r * 78.233) * 43758.5453 % 1) * 0.06;
      tiles.setColorAt(n - 1, new Color(v, v * 0.995, v * 0.97));
    }
    tiles.count = n;
    tiles.receiveShadow = true;
    scene.add(tiles);

    // luminous panels
    const panelMat = new MeshBasicMaterial({ color: 0xfff0d2 });
    const panels = new InstancedMesh(lightGeo, panelMat, lights.length);
    lights.forEach(([x, z], i) => { dummy.position.set(x, Y - 0.004, z); dummy.updateMatrix(); panels.setMatrixAt(i, dummy.matrix); });
    scene.add(panels);

    // --- T-bars (main tees along Z every tile, cross tees along X) ---
    const barMat = new MeshStandardMaterial({ color: 0x2e3192, roughness: .5, metalness: .35 });
    const accentMat = new MeshBasicMaterial({ color: 0xf6821f });
    const lenZ = ROWS * T, lenX = COLS * T;
    const mains = new InstancedMesh(new BoxGeometry(0.03, 0.04, lenZ), barMat, COLS + 1);
    const accents = new InstancedMesh(new BoxGeometry(0.034, 0.012, lenZ), accentMat, 5);
    let ai = 0;
    for (let c = 0; c <= COLS; c++) {
      const x = x0 + c * T;
      dummy.position.set(x, Y - 0.02, z0 - lenZ / 2); dummy.updateMatrix(); mains.setMatrixAt(c, dummy.matrix);
      if (c % 9 === 4 && ai < 5) { dummy.position.set(x, Y - 0.046, z0 - lenZ / 2); dummy.updateMatrix(); accents.setMatrixAt(ai++, dummy.matrix); }
    }
    accents.count = ai;
    const cross = new InstancedMesh(new BoxGeometry(lenX, 0.04, 0.03), barMat, ROWS + 1);
    for (let r = 0; r <= ROWS; r++) { dummy.position.set(0, Y - 0.02, z0 - r * T); dummy.updateMatrix(); cross.setMatrixAt(r, dummy.matrix); }
    mains.castShadow = cross.castShadow = mains.receiveShadow = cross.receiveShadow = true;
    scene.add(mains, accents, cross);

    // --- gypsum coffer with hidden light, ahead of the camera ---
    const coffer = new Group();
    const gypsum = new MeshStandardMaterial({ color: 0xf0f1fa, roughness: .95 });
    const glow = new MeshBasicMaterial({ color: 0xffc27a });
    const frame = (w, d, h, y, mat) => {
      const g = new Group(), t = 0.16;
      [[0, d / 2 - t / 2, w, t], [0, -d / 2 + t / 2, w, t], [w / 2 - t / 2, 0, t, d], [-w / 2 + t / 2, 0, t, d]].forEach(([x, z, sx, sz]) => {
        const m = new (InstancedMesh)(new BoxGeometry(sx, h, sz), mat, 1); dummy.position.set(x, y, z); dummy.updateMatrix(); m.setMatrixAt(0, dummy.matrix);
        m.castShadow = m.receiveShadow = mat === gypsum; g.add(m);
      });
      return g;
    };
    coffer.add(frame(8, 6.4, 0.16, Y - 0.1, gypsum), frame(6.6, 5.2, 0.16, Y - 0.26, gypsum), frame(6.2, 4.8, 0.03, Y - 0.17, glow), frame(5.2, 3.9, 0.16, Y - 0.42, gypsum));
    // the hidden-light centerpiece — dead ahead, top-middle of the frame — shows the real project photo,
    // pre-rectified (perspective/keystone removed) so its own tile grid sits flat and square, matching the
    // 3D grid's rhythm instead of reading as a tilted picture glued onto the ceiling
    const coreMat = new MeshBasicMaterial({ color: 0xeef0fa });
    const PW = 4.6, PD = 3.33;
    const core = new InstancedMesh(new PlaneGeometry(PW, PD).rotateX(Math.PI / 2), coreMat, 1);
    dummy.position.set(0, Y - 0.5, 0); dummy.updateMatrix(); core.setMatrixAt(0, dummy.matrix); coffer.add(core);
    new TextureLoader().load('/assets/r/projects-p02-flat-960.webp', tex => {
      tex.colorSpace = SRGBColorSpace;
      coreMat.map = tex; coreMat.color.set(0xffffff); coreMat.needsUpdate = true;
    });
    // T-bar seams laid directly over the photo, at the same 60x60 rhythm as the main grid — so this reads
    // as the acoustic ceiling actually built/installed in that spot, not a picture pinned to the ceiling
    const PT = 0.6, vCols = Math.round(PW / PT), hRows = Math.round(PD / PT), seamY = Y - 0.505;
    const vSeams = new InstancedMesh(new BoxGeometry(0.03, 0.025, PD), barMat, vCols + 1);
    for (let i = 0; i <= vCols; i++) { dummy.position.set(-PW / 2 + i * (PW / vCols), seamY, 0); dummy.updateMatrix(); vSeams.setMatrixAt(i, dummy.matrix); }
    const hSeams = new InstancedMesh(new BoxGeometry(PW, 0.025, 0.03), barMat, hRows + 1);
    for (let i = 0; i <= hRows; i++) { dummy.position.set(0, seamY, -PD / 2 + i * (PD / hRows)); dummy.updateMatrix(); hSeams.setMatrixAt(i, dummy.matrix); }
    coffer.add(vSeams, hSeams);
    coffer.position.set(0, 0, -21);
    scene.add(coffer);

    // --- floating dust ---
    const P = small ? 120 : 280, pos = new Float32Array(P * 3);
    for (let i = 0; i < P; i++) { pos[i * 3] = (Math.random() - .5) * 18; pos[i * 3 + 1] = Math.random() * 3; pos[i * 3 + 2] = -Math.random() * 32; }
    const dustGeo = new BufferGeometry(); dustGeo.setAttribute('position', new Float32BufferAttribute(pos, 3));
    const dust = new Points(dustGeo, new PointsMaterial({ color: 0xffe2b8, size: .035, transparent: true, opacity: .55, depthWrite: false }));
    scene.add(dust);

    // --- walls (so the ceiling reads as a room) ---
    const wallMat = new MeshStandardMaterial({ color: 0x181a4a, roughness: 1 });
    [-1, 1].forEach(s => { const w = new InstancedMesh(new BoxGeometry(.2, 5, lenZ), wallMat, 1); dummy.position.set(s * (lenX / 2 + .6) * 0 + s * 6.6, Y - 2.5, z0 - lenZ / 2); dummy.updateMatrix(); w.setMatrixAt(0, dummy.matrix); scene.add(w); });

    // --- intro sequence (Theatre.js) ---
    let introZ = calm ? 0 : -17, introR = calm ? 0 : -0.42, introY = calm ? 0 : 1.1;
    if (!calm) {
      try {
        const proj = getProject('AKH Hero', { state: THEATRE_STATE });
        const introSheet = proj.sheet('Intro');
        const introObj = introSheet.object('camera', { zOff: types.number(-17, { range: [-17, 0] }), rotOff: types.number(-0.42, { range: [-0.42, 0] }), yOff: types.number(1.1, { range: [0, 1.1] }) });
        introObj.onValuesChange(v => { introZ = v.zOff; introR = v.rotOff; introY = v.yOff; });
        proj.ready.then(() => introSheet.sequence.play());
      } catch (e) { introZ = introR = introY = 0; }
    }

    // --- loop ---
    let mx = 0, my = 0, tx = 0, ty = 0, scrollP = 0, running = false, raf = 0, t0 = performance.now(), last = t0, ready = false;
    const resize = () => { const w = host.clientWidth, h = host.clientHeight; renderer.setSize(w, h, false); cam.aspect = w / h; cam.fov = w / h < .8 ? 78 : 62; cam.updateProjectionMatrix(); };
    new ResizeObserver(resize).observe(host); resize();
    addEventListener('pointermove', e => { tx = (e.clientX / innerWidth - .5) * 2; ty = (e.clientY / innerHeight - .5) * 2; }, { passive: true });
    addEventListener('scroll', () => { scrollP = MathUtils.clamp(scrollY / Math.max(1, host.clientHeight), 0, 1); }, { passive: true });
    const frameFn = (now) => {
      raf = 0; if (!running) return;
      const dt = Math.min(.05, (now - last) / 1000); last = now;
      const t = (now - t0) / 1000;
      mx += (tx - mx) * Math.min(1, dt * 3); my += (ty - my) * Math.min(1, dt * 3);
      const z = (calm ? -4 : -(8 + 7.5 * Math.sin(t * 0.055)) - scrollP * 10) + introZ;
      cam.position.set(mx * .35, 0.15 - my * .08 + introY, z);
      cam.rotation.set(0.5 + scrollP * .55 + my * -.05 + introR, -mx * .12, 0, 'YXZ');
      dust.position.z = (t * .12) % 3;
      renderer.render(scene, cam);
      if (!ready) { ready = true; host.classList.add('gl-ready'); }
      if (!calm) raf = requestAnimationFrame(frameFn);
    };
    const start = () => { if (running) return; running = true; last = performance.now(); raf = requestAnimationFrame(frameFn); };
    const stop = () => { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; };
    new IntersectionObserver(es => es.forEach(e => e.isIntersecting && !document.hidden ? start() : stop()), { threshold: .02 }).observe(host);
    document.addEventListener('visibilitychange', () => document.hidden ? stop() : start());
    canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); stop(); host.classList.remove('gl-ready'); });
    start();
  }
}
