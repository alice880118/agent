# 像素點陣 3D Hero 特效（Pixel-Dot 3D Hero）

把一個即時 3D 模型轉成固定網格上的「圓點／方塊像素畫」，模型會跟著滑鼠轉向，滑鼠劃過時留下抹開的拖痕。
靈感來自 hemi.xyz/institutions 的 hero（保險箱），本 repo 的完整實作在 [`shell-hero/index.html`](../shell-hero/index.html)（粉色水中貝殼版）。

> 用法：之後要做類似效果時，把這份檔案（或它的路徑）連同需求一起給 Claude，並說「照 pixel-dot-3d-hero.md 的做法」。

---

## 1. 下指令範本

複製下面這段，把 `[ ]` 換成你要的內容：

```
照 docs/pixel-dot-3d-hero.md 的做法，做一個像素點陣 3D hero：

- 主體：[例如 水中貝殼 / 保險箱 / 我提供的 model.glb]
- 主體自己的動態：[例如 每 6 秒開闔一次 / 轉輪持續旋轉 / 無]
- 像素形狀：[圓點 / 方塊]，格子大小 [10] px
- 配色：[深色、主色、淡色、背景] 或 [粉色系 / 藍色系]
- 滑鼠跟隨：[明顯 ±50° / 輕微 ±20°]，要不要依移動速度傾斜：[要 / 不要]
- 滑鼠拖痕：[要 / 不要]
- 版面：主體放在 hero [右側 / 中間]，左側文案：[標題、副標]
- 交付：單一 HTML，可直接預覽
```

---

## 2. 架構（四層）

```
┌──────────────────────────────────────────────────────────────┐
│ ① 3D 場景（Three.js）                                          │
│    模型 + toon 材質：輸出灰階「亮度 tone」而不是真實顏色            │
│    → 渲染到離屏 RenderTarget（sceneRT，半解析度，透明背景）          │
├──────────────────────────────────────────────────────────────┤
│ ② 滑鼠軌跡貼圖（trail FBO，ping-pong）                            │
│    每格一個 texel：rg = 移動方向，b = 強度；每幀衰減               │
├──────────────────────────────────────────────────────────────┤
│ ③ 合成 shader（全螢幕 quad）                                      │
│    以 gl_FragCoord 切成固定網格 → 取每格中心的場景亮度               │
│    → 分成 4 階顏色 → 畫成圓點（或方塊）                             │
│    → 有拖痕的格子：沿移動方向往回取樣（抹開）、轉淡色、閃爍            │
├──────────────────────────────────────────────────────────────┤
│ ④ 互動與動畫（JS 每幀）                                           │
│    模型轉向滑鼠（lerp）+ 速度傾斜（阻尼彈簧）+ 自身動畫（開闔等）       │
└──────────────────────────────────────────────────────────────┘
```

關鍵觀念：**網格是固定在螢幕上的，模型在網格後面動**。所以轉動時看到的是「格子裡的顏色重新分配」，這正是原網站的質感。

---

## 3. 可調參數一覽

| 參數 | 位置 | 預設 | 效果 |
|---|---|---|---|
| `CELL_CSS` | JS 常數 | `10` | 格子大小（CSS px） |
| `disc(lp, 0.43)` | 合成 shader | `0.43` | 圓點半徑（0.5 = 相切）；改方塊見 §5.3 |
| 亮度門檻 `0.80` / `0.36` | `tierOf()` | — | 白 / 中 / 深 三階的分界 |
| `TRAIL_RADIUS` | JS 常數 | `2.6` | 拖痕筆刷半徑（格數） |
| `TRAIL_DECAY` | JS 常數 | `0.955` | 每幀衰減，約 1 秒淡出 |
| 抹開長度 `2.0 + 5.0 * hash` | 合成 shader | — | 拖痕把像素拉多長（格數） |
| `target.x * 0.88` | `frame()` | ≈ ±50° | 左右轉向幅度 |
| `target.y * (… 0.18 : 0.55)` | `frame()` | +10° / −32° | 上下仰俯幅度（往下刻意較小） |
| `0.0004`（ease） | `frame()` | — | 跟隨速度，越小越快 |
| `swingVel … 0.012`、`k=60, damp=9` | pointermove / `frame()` | — | 依滑鼠速度傾斜的力道與回彈 |
| `reach = min(W,H) * 0.42` | pointermove | — | 滑鼠離主體多遠算「轉到底」 |
| `setViewOffset(…, -W * 0.2, …)` | `resize()` | — | 主體在畫面中往右偏移 |

---

## 4. 核心程式碼

以下是可以直接套用的骨架（Three.js r160，ES module）。完整版本與貝殼模型見 `shell-hero/index.html`。

### 4.1 載入 Three.js

```html
<script type="importmap">
{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js" } }
</script>
<script type="module">
import * as THREE from 'three';
// ...
</script>
```

Hero 容器要設 `touch-action: pan-y pinch-zoom`：手機上可以用手指觸發效果，同時保留上下捲動。

### 4.2 Toon 材質（讓亮度分階可預測）

不要用 `MeshStandardMaterial` / `MeshLambertMaterial`：它們的亮度很難控制，常常整片變白。改用自訂 shader，輸出 `tone × 光照`：

```js
const LIGHT_DIR = new THREE.Vector3(-0.45, 0.55, 0.7).normalize();

// tag=true 時 r > g，合成時可辨識成「特殊物件」，給它專屬配色（例如珍珠）
function toonMaterial({ tone = 1, vertexTone = false, ambient = 0.45,
                        side = THREE.FrontSide, tag = false } = {}) {
  return new THREE.ShaderMaterial({
    side, vertexColors: vertexTone,
    uniforms: { tone: { value: tone }, ambient: { value: ambient },
                lightDir: { value: LIGHT_DIR }, tag: { value: tag ? 0.5 : 1 } },
    vertexShader: `
      varying vec3 vN; varying float vTone; uniform float tone;
      void main(){
        vN = normalize(mat3(modelMatrix) * normal);
        #ifdef USE_COLOR
          vTone = color.r * tone;
        #else
          vTone = tone;
        #endif
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }`,
    fragmentShader: `
      varying vec3 vN; varying float vTone;
      uniform float ambient, tag; uniform vec3 lightDir;
      void main(){
        vec3 n = normalize(vN) * (gl_FrontFacing ? 1.0 : -1.0);
        float l = ambient + (1.0 - ambient) * max(dot(n, lightDir), 0.0);
        float v = vTone * l;
        gl_FragColor = vec4(v, v * tag, v * tag, 1.0);
      }`,
  });
}
```

`tone` 的用法：
- **想要白色線條**（例如門框、殼緣）：把 tone 設成 `2.4`（頂點色可以 > 1），不管光照如何都會是白。
- **亮面**：約 `0.8`；**暗溝 / 內側**：約 `0.3`。
- 用 `vertexTone` 可以在同一個網格上畫出條紋（肋紋、溝槽）。

### 4.3 Render targets

```js
const sceneRT = new THREE.WebGLRenderTarget(2, 2, { depthBuffer: true });   // 半解析度即可
const trailOpts = { type: THREE.HalfFloatType, minFilter: THREE.NearestFilter,
                    magFilter: THREE.NearestFilter, depthBuffer: false };
let trailA = new THREE.WebGLRenderTarget(2, 2, trailOpts);   // 大小 = 網格欄數 × 列數
let trailB = new THREE.WebGLRenderTarget(2, 2, trailOpts);
renderer.setClearColor(0x000000, 0);   // 場景背景透明 → alpha 就是「有沒有東西」
```

### 4.4 拖痕 shader（ping-pong，每幀一次）

```glsl
varying vec2 vUv;
uniform sampler2D prev; uniform vec2 a, b, dir; uniform float power, decay, radius;
void main(){
  vec4 p = texture2D(prev, vUv);
  p.b *= decay;                                   // 強度衰減
  vec2 c = gl_FragCoord.xy;                       // 目前格子（格座標）
  vec2 pa = c - a, ba = b - a;                    // 到「上一幀→這一幀」線段的距離
  float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-4), 0.0, 1.0);
  float d = length(pa - ba * h);
  float s = exp(-d * d / (radius * radius)) * power;
  p.rg = mix(p.rg, dir, clamp(s * 1.5, 0.0, 1.0)); // 記錄移動方向
  p.b = min(1.0, max(p.b, s));
  gl_FragColor = p;
}
```

JS 端：`a`、`b` 是上一幀和這一幀的滑鼠位置換算成格座標（y 要翻轉：`(H - y) * DPR / CELL`）；`power = min(1, 移動格數 / 0.9)`；`decay = pow(TRAIL_DECAY, dt * 60)`。

### 4.5 合成 shader（像素化 + 拖痕）

```glsl
uniform sampler2D tScene, tTrail;
uniform vec2 res, grid; uniform float cell, px, time;
uniform vec3 cBg, cLine, cDeep, cMid, cEdge, cPale, cWhite, cDot;

float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec4 sceneAt(vec2 cid){ return texture2D(tScene, (cid + 0.5) * cell / res); }
float disc(vec2 lp, float r){ float aa = 1.2 / cell; return 1.0 - smoothstep(r - aa, r + aa, length(lp)); }

// 0 空, 1 邊緣, 2 深, 3 中, 4 白, 5 淡（拖痕 / 特殊物件）, 6 閃爍
int tierOf(vec4 s){
  if (s.a < 0.12) return 0;
  if (s.a < 0.55) return 1;
  if (s.r - s.g > 0.12 * s.a) {               // tag 過的物件：自己的配色
    float v = s.r / s.a;
    return v > 0.93 ? 4 : (v > 0.55 ? 5 : 3);
  }
  float lum = dot(s.rgb, vec3(0.299, 0.587, 0.114)) / s.a;
  if (lum > 0.80) return 4;
  if (lum > 0.36) return 3;
  return 2;
}
vec3 colorOf(int t){ return t == 1 ? cEdge : t == 2 ? cDeep : t == 3 ? cMid : cWhite; }

void main(){
  vec2 fc = gl_FragCoord.xy;
  vec2 cid = floor(fc / cell);              // 第幾格
  vec2 lp = fract(fc / cell) - 0.5;         // 格內座標 -0.5..0.5

  vec3 col = cBg;
  if (fc.x - cid.x * cell < px) col = cLine;   // 背景直線

  vec4 tr = texture2D(tTrail, (cid + 0.5) / grid);
  float s = clamp(tr.b, 0.0, 1.0);
  vec2 dir = tr.rg;

  int tier = tierOf(sceneAt(cid));

  if (s > 0.06) {
    // 抹開：沿移動方向「往回」取樣，每列長度隨機 → 條紋感
    float len = s * (2.0 + 5.0 * hash(vec2(cid.y + cid.x * 0.02, floor(time * 8.0))));
    int upTier = tierOf(sceneAt(floor(cid - dir * len + 0.5)));
    if (tier > 0 || upTier > 0) {
      tier = upTier == 0 ? 5 : upTier;
      if (tier != 4 && hash(cid * 1.73 + floor(time * 14.0)) < smoothstep(0.1, 0.55, s) * 0.9) tier = 5;
      if (hash(cid + floor(time * 9.0) * 1.31) < 0.06 * s) tier = 6;
    } else if (hash(cid + floor(time * 10.0) * 0.77) < s * 0.85) {
      col = mix(col, cDot, disc(lp, 0.17));   // 背景上的小點拖痕
    }
  }

  if (tier == 2 && hash(cid + floor(time * 0.6) * 3.7) < 0.012) tier = 4;  // 暗面白色雜點

  if (tier == 5)      col = mix(col, cPale, disc(lp, 0.43));
  else if (tier == 6) { col = mix(col, cPale, disc(lp, 0.43));
                        col = mix(col, cDeep, disc(lp, 0.22));
                        col = mix(col, cWhite, disc(lp, 0.08)); }
  else if (tier > 0)  col = mix(col, colorOf(tier), disc(lp, 0.43));

  gl_FragColor = vec4(col, 1.0);
}
```

顏色用 `new THREE.Color().setStyle('#E0457F', THREE.NoColorSpace)` 傳入，ShaderMaterial 不做色彩空間轉換，所以寫什麼 hex 就輸出什麼。

### 4.6 滑鼠跟隨（明顯的 3D 視角變化）

```js
obj.rotation.order = 'YXZ';          // ★ 一定要：左右轉繞世界垂直軸

// pointermove：以「主體在螢幕上的位置」為中心，不是 hero 中心
const reach = Math.min(rect.width, rect.height) * 0.42;
target.x = clamp((x - objScreen.x) / reach, -1, 1);
target.y = clamp((y - objScreen.y) / reach, -1, 1);
swingVel.x += clamp((x - pointer.x) * 0.012, -0.5, 0.5);   // 速度 → 傾斜衝量
swingVel.y += clamp((y - pointer.y) * 0.012, -0.5, 0.5);

// frame()
const k = 60, damp = 9;                                    // 阻尼彈簧，傾斜後彈回
swingVel.x += (-k * swing.x - damp * swingVel.x) * dt;
swing.x = clamp(swing.x + swingVel.x * dt * 6, -0.45, 0.45);   // y 同理

const ease = 1 - Math.pow(0.0004, dt);                     // 與幀率無關的 lerp
obj.rotation.y += (BASE_YAW   + target.x * 0.88 + swing.x - obj.rotation.y) * ease;
obj.rotation.x += (BASE_PITCH + target.y * (target.y > 0 ? 0.18 : 0.55) + swing.y * 0.6 - obj.rotation.x) * ease;
obj.rotation.z += (-swing.x * 0.35 - obj.rotation.z) * ease;   // 往移動方向側傾
obj.position.x += (target.x * 0.18 - obj.position.x) * ease;   // 輕微位移

// 每幀更新主體的螢幕位置，給 pointermove 用
_v.set(0, 0.2, 0).project(camera);
objScreen.x = (_v.x * 0.5 + 0.5) * W;
objScreen.y = (-_v.y * 0.5 + 0.5) * H;
```

### 4.7 每幀順序

```js
renderer.setRenderTarget(sceneRT); renderer.clear(); renderer.render(scene, camera);  // ①
updateTrail(dt);                                     // ② 畫到 trailB，然後交換 A/B
compMat.uniforms.tTrail.value = trailA.texture;      // ③
quad.material = compMat;
renderer.setRenderTarget(null); renderer.render(quadScene, quadCam);
```

### 4.8 尺寸與版面

```js
DPR = Math.min(devicePixelRatio, 2);
CELL = Math.round(CELL_CSS * DPR);                  // shader 裡的格子用裝置像素
sceneRT.setSize(ceil(pw / 2), ceil(ph / 2));
grid.set(ceil(pw / CELL), ceil(ph / CELL));          // trail RT 大小 = 網格
// 桌機：主體放右邊；手機：放下面，鏡頭依寬度拉遠
if (W >= 860) camera.setViewOffset(W, H, -W * 0.2, 0, W, H);
else          camera.setViewOffset(W, H, 0, -H * 0.2, W, H);
```

另外要做：`ResizeObserver` 監聽 hero、`IntersectionObserver` 在畫面外時暫停、`prefers-reduced-motion` 時停止自動動畫。

---

## 5. 換成別的主體

### 5.1 用 .glb 模型

```js
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
new GLTFLoader().load('model.glb', (gltf) => {
  gltf.scene.traverse((m) => {
    if (!m.isMesh) return;
    // 依部位指定 tone：亮面 0.8、暗部 0.3、要變白的線 2.4
    m.material = toonMaterial({ tone: m.name.includes('frame') ? 2.4 : 0.8 });
  });
  body.add(gltf.scene);
});
```

在 artifact 中，模型檔要用 `files` 一起發布，或轉成 data URI 內嵌。

### 5.2 程式建模（不需要模型檔）

貝殼就是用參數曲面建出來的（見 `shellPoint()` / `makeValve()`）：扇形角度 θ × 半徑 r 組成網格，高度用 `sin(πr)^0.7` 做成圓頂，再疊 `cos(Nθ)` 做出肋紋。頂點色寫入 tone，讓肋紋和溝槽各自落在不同色階。

### 5.3 方塊取代圓點

把 `disc()` 換成：

```glsl
float box(vec2 lp, float r){ vec2 q = abs(lp); return step(max(q.x, q.y), r); }
```

`r = 0.45` 時，格子之間會留下約 1px 的縫，跟 hemi 原版一樣。

### 5.4 配色

需要 6～8 個顏色：

| 名稱 | 用途 |
|---|---|
| `cBg` | 背景 |
| `cLine` | 背景直線 |
| `cDeep` | 暗面 |
| `cMid` | 亮面 |
| `cEdge` | 輪廓過渡 |
| `cPale` | 拖痕和淡色物件 |
| `cWhite` | 高光、白線 |
| `cDot` | 背景小點 |

兩組參考配色：

- **粉**：`#FFF8FB` / `#F7E6EE` / `#E0457F` / `#F5A3C3` / `#F0C2D6` / `#FCE1EC` / `#FFFFFF` / `#F2A9C6`
- **藍（hemi 原版）**：`#FFFFFF` / `#EEF0F4` / `#0057E7` / `#7FA8F0` / `#C9D2F0` / `#E3E8F8` / `#FFFFFF` / `#9DB8F2`

---

## 6. 踩過的坑（一定要看）

1. **旋轉順序要用 `YXZ`**：預設的 `XYZ` 會先做 Y 軸旋轉，等於繞著物體自己傾斜後的軸轉。結果左右轉看起來像原地自轉，幾乎看不出在轉向滑鼠。
2. **方向要以主體為中心算**：如果用 hero 中心，主體在右側時，滑鼠在主體附近移動，角度幾乎不會變。
3. **純白會被看成「洞」**：白色圓點和背景太接近。需要白色的實心物件（例如珍珠）要用 `tag` 給它專屬配色（淡色本體加白色高光），只有線條和高光才用純白。
4. **閉合的物件邊緣要真的碰在一起**：例如貝殼的圓頂函數在 r=1 時必須等於 0，不然會一直留著一道縫。
5. **不要用 PBR / Lambert 材質**：亮度不好控制，容易整片變白或整片變深。用 toon shader，搭配 tone 數值直接決定色階。
6. **看起來不像那個東西時，先關掉像素化看原始 3D**：把合成 shader 最後一行暫時換成 `gl_FragColor = texture2D(tScene, fc / res);` 就能看到原始渲染，比較容易判斷是模型的問題，還是分階門檻的問題。
7. **角度不能轉到側面**：鏡頭在略高的位置時，物體往下轉太多會變成扁扁的側面，所以往下的角度要比往上小（+10° / −32°）。
8. **開闔類動畫要讓鏡頭看得到開口**：物體正面直對鏡頭時，開闔動作會被擋住。讓預設姿勢稍微往後仰（貝殼 pitch 從 −1.2 改成 −0.8）。
9. **縮成網格後細節會消失**：形狀要靠大面積的明暗和一兩條白線來辨識，細小的花紋縮成格子後看不出來。

---

## 7. 本機驗證方式

在雲端或無頭瀏覽器裡用 SwiftShader 跑 WebGL：

```js
chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
// 如果 CDN 連不到，把 three.module.js 用 page.route 換成本機的 node_modules/three 檔案
```

要截的圖：
- 預設姿勢
- 滑鼠分別在主體的上、下、左、右（各等約 1.5 秒讓它穩定）
- 快速劃過主體（拖痕）
- 動畫循環中的幾個時間點
- 手機寬度 390px
