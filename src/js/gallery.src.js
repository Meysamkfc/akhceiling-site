/* Projects gallery: a small, restrained WebGL ripple on hover (Curtains.js), replacing nothing — the
   plain <img> stays in the DOM and is the only thing that exists if WebGL/hover isn't available.
   Desktop/hover-capable + motion-ok only; never runs on touch devices (there's no hover to trigger it). */
import { Curtains, Plane } from 'curtainsjs';

const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
const hoverCapable = matchMedia('(hover: hover) and (pointer: fine)').matches;
const items = [...document.querySelectorAll('[data-lb] a.gi')];

if (!calm && hoverCapable && items.length) {
  const vertex = `
    precision highp float;
    attribute vec3 aVertexPosition;
    attribute vec2 aTextureCoord;
    uniform mat4 uMVMatrix;
    uniform mat4 uPMatrix;
    uniform float uTime;
    uniform float uStrength;
    uniform vec2 uMouse;
    varying vec2 vTextureCoord;
    void main() {
      vec3 pos = aVertexPosition;
      float dist = distance(aTextureCoord, uMouse);
      float ripple = sin(dist * 18.0 - uTime * 0.08) * 0.018 * uStrength * smoothstep(0.55, 0.0, dist);
      pos.z += ripple;
      gl_Position = uPMatrix * uMVMatrix * vec4(pos, 1.0);
      vTextureCoord = aTextureCoord;
    }
  `;
  const fragment = `
    precision highp float;
    varying vec2 vTextureCoord;
    uniform sampler2D uSampler0;
    uniform float uStrength;
    uniform vec2 uMouse;
    void main() {
      float dist = distance(vTextureCoord, uMouse);
      vec2 off = (vTextureCoord - uMouse) * 0.012 * uStrength * smoothstep(0.55, 0.0, dist);
      gl_FragColor = texture2D(uSampler0, vTextureCoord - off);
    }
  `;
  try {
    const curtains = new Curtains({ container: document.body, watchScroll: true, pixelRatio: Math.min(1.5, devicePixelRatio || 1), antialias: true });
    curtains.onError(() => curtains.dispose());
    items.forEach(el => {
      const img = el.querySelector('img'); if (!img) return;
      const plane = new Plane(curtains, el, {
        vertexShader: vertex, fragmentShader: fragment, widthSegments: 24, heightSegments: 24,
        uniforms: { time: { name: 'uTime', type: '1f', value: 0 }, strength: { name: 'uStrength', type: '1f', value: 0 }, mouse: { name: 'uMouse', type: '2f', value: [0.5, 0.5] } },
      });
      let target = 0;
      plane.onRender(() => {
        plane.uniforms.time.value++;
        plane.uniforms.strength.value += (target - plane.uniforms.strength.value) * 0.08;
      }).onReady(() => { plane.setPerspective(); });
      const setMouse = e => {
        const r = el.getBoundingClientRect();
        plane.uniforms.mouse.value = [(e.clientX - r.left) / r.width, 1 - (e.clientY - r.top) / r.height];
      };
      el.addEventListener('pointerenter', e => { target = 1; setMouse(e); });
      el.addEventListener('pointermove', setMouse);
      el.addEventListener('pointerleave', () => { target = 0; });
    });
  } catch (e) { /* no WebGL / init failure: the plain <img> already in the DOM is the whole experience */ }
}
