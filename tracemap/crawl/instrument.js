/*
 * TraceMap in-page instrumentation. Injected before any page script, in every frame.
 *
 * Wraps privacy-relevant JS APIs and records, per (api, calling script), how often
 * they were used plus a few sample arguments. The calling script is the first
 * http(s) URL on the JS stack at call time.
 *
 * The API list is adapted from DuckDuckGo tracker-radar-collector
 * (collectors/APICalls/breakpoints.js, Apache-2.0, commit 3aec03f), see NOTICE.
 * TraceMap adds hooks TRC lacks: input value reads, keyboard/input listeners,
 * Storage.setItem/getItem, navigator.sendBeacon and per-cookie setter attribution.
 *
 * Limitation (documented in the methods): wrappers are detectable by page scripts,
 * unlike CDP debugger breakpoints. Hot APIs (Date.getTime, Event.timeStamp) are
 * deliberately not wrapped because they slow pages down.
 */
(() => {
  if (window.__tm) return;
  const calls = new Map();
  const jsCookies = new Map(); // cookie name -> script that set it (first writer)
  const URL_RE = /(https?:\/\/[^\s()'"]+?):\d+:\d+/;
  const MAX_ARGS = 6;

  function callerScript() {
    const stack = (new Error()).stack || '';
    const lines = stack.split('\n');
    for (let i = 1; i < lines.length; i++) {
      const m = lines[i].match(URL_RE);
      if (m) return m[1];
    }
    return '';
  }

  function record(api, arg) {
    try {
      const script = callerScript();
      const key = api + '\u0001' + script;
      let e = calls.get(key);
      if (!e) {
        e = { api: api, script_url: script, count: 0, sample_args: [] };
        calls.set(key, e);
      }
      e.count++;
      if (arg !== undefined && e.sample_args.length < MAX_ARGS) {
        let s;
        try { s = typeof arg === 'string' ? arg : JSON.stringify(arg); } catch (_) { s = String(arg); }
        e.sample_args.push(String(s).slice(0, 200));
      }
      return script;
    } catch (_) { return ''; }
  }

  function resolve(path) {
    try { return path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), window); } catch (_) { return undefined; }
  }

  function wrapMethod(target, name, api, argPick) {
    if (!target) return;
    const d = Object.getOwnPropertyDescriptor(target, name);
    if (!d || typeof d.value !== 'function') return;
    const orig = d.value;
    const wrapped = function (...args) {
      record(api, argPick ? argPick(args, this) : undefined);
      return orig.apply(this, args);
    };
    try { Object.defineProperty(wrapped, 'name', { value: orig.name }); } catch (_) {}
    try { Object.defineProperty(wrapped, 'length', { value: orig.length }); } catch (_) {}
    Object.defineProperty(target, name, Object.assign({}, d, { value: wrapped }));
  }

  function wrapGetter(target, name, api) {
    if (!target) return;
    const d = Object.getOwnPropertyDescriptor(target, name);
    if (!d || typeof d.get !== 'function') return;
    const get = d.get;
    Object.defineProperty(target, name, Object.assign({}, d, {
      get: function () { record(api); return get.call(this); },
    }));
  }

  function wrapConstructor(globalName, api) {
    const Orig = window[globalName];
    if (typeof Orig !== 'function') return;
    const P = new Proxy(Orig, {
      construct(t, args, nt) { record(api); return Reflect.construct(t, args, nt); },
    });
    try { window[globalName] = P; } catch (_) {}
  }

  const proto = (n) => { const c = resolve(n); return c && c.prototype; };

  // ---------------------------------------------------------------- navigator / screen / window
  const navProps = ['userAgent', 'appVersion', 'platform', 'language', 'languages', 'plugins', 'mimeTypes',
    'hardwareConcurrency', 'deviceMemory', 'maxTouchPoints', 'webdriver', 'doNotTrack', 'cookieEnabled',
    'connection', 'vendor', 'product', 'productSub', 'mediaDevices', 'keyboard', 'permissions', 'storage',
    'userAgentData'];
  navProps.forEach((p) => wrapGetter(proto('Navigator'), p, 'Navigator.' + p));
  ['getBattery', 'getGamepads', 'javaEnabled', 'requestMediaKeySystemAccess'].forEach(
    (m) => wrapMethod(proto('Navigator'), m, 'Navigator.' + m));
  wrapMethod(proto('NavigatorUAData'), 'getHighEntropyValues', 'NavigatorUAData.getHighEntropyValues', (a) => a[0]);
  wrapMethod(proto('MediaDevices'), 'enumerateDevices', 'MediaDevices.enumerateDevices');
  ['width', 'height', 'availWidth', 'availHeight', 'colorDepth', 'pixelDepth', 'orientation'].forEach(
    (p) => wrapGetter(proto('Screen'), p, 'Screen.' + p));
  wrapGetter(window, 'devicePixelRatio', 'window.devicePixelRatio');
  wrapMethod(window, 'matchMedia', 'window.matchMedia', (a) => a[0]);
  wrapMethod(proto('Intl.DateTimeFormat'), 'resolvedOptions', 'Intl.DateTimeFormat.resolvedOptions');
  wrapMethod(proto('Date'), 'getTimezoneOffset', 'Date.getTimezoneOffset');
  wrapMethod(Reflect.getPrototypeOf(document.fonts || {}), 'check', 'FontFaceSet.check', (a) => a[0]);
  wrapMethod(proto('Element'), 'getClientRects', 'Element.getClientRects');
  wrapMethod(proto('HTMLMediaElement'), 'canPlayType', 'HTMLMediaElement.canPlayType', (a) => a[0]);
  wrapMethod(resolve('speechSynthesis') && Reflect.getPrototypeOf(window.speechSynthesis), 'getVoices',
    'SpeechSynthesis.getVoices');

  // ---------------------------------------------------------------- canvas / webgl / audio / webrtc
  wrapMethod(proto('HTMLCanvasElement'), 'toDataURL', 'HTMLCanvasElement.toDataURL', (a, c) => c.width + 'x' + c.height);
  wrapMethod(proto('HTMLCanvasElement'), 'toBlob', 'HTMLCanvasElement.toBlob', (a, c) => c.width + 'x' + c.height);
  wrapMethod(proto('HTMLCanvasElement'), 'getContext', 'HTMLCanvasElement.getContext', (a) => a[0]);
  wrapMethod(proto('CanvasRenderingContext2D'), 'getImageData', 'CanvasRenderingContext2D.getImageData');
  wrapMethod(proto('CanvasRenderingContext2D'), 'fillText', 'CanvasRenderingContext2D.fillText', (a) => a[0]);
  wrapMethod(proto('CanvasRenderingContext2D'), 'strokeText', 'CanvasRenderingContext2D.strokeText', (a) => a[0]);
  wrapMethod(proto('CanvasRenderingContext2D'), 'measureText', 'CanvasRenderingContext2D.measureText');
  wrapMethod(proto('CanvasRenderingContext2D'), 'isPointInPath', 'CanvasRenderingContext2D.isPointInPath');
  ['WebGLRenderingContext', 'WebGL2RenderingContext'].forEach((g) => {
    ['getParameter', 'getExtension', 'getSupportedExtensions', 'getShaderPrecisionFormat', 'readPixels',
      'getContextAttributes'].forEach((m) => wrapMethod(proto(g), m, g + '.' + m, m === 'getParameter' || m === 'getExtension' ? (a) => a[0] : undefined));
  });
  wrapConstructor('OfflineAudioContext', 'OfflineAudioContext.constructor');
  ['createOscillator', 'createDynamicsCompressor', 'createAnalyser'].forEach(
    (m) => wrapMethod(proto('BaseAudioContext'), m, 'BaseAudioContext.' + m));
  wrapMethod(proto('AudioBuffer'), 'getChannelData', 'AudioBuffer.getChannelData');
  wrapMethod(proto('AnalyserNode'), 'getFloatFrequencyData', 'AnalyserNode.getFloatFrequencyData');
  wrapConstructor('RTCPeerConnection', 'RTCPeerConnection.constructor');
  wrapMethod(proto('RTCPeerConnection'), 'createDataChannel', 'RTCPeerConnection.createDataChannel');
  wrapMethod(proto('RTCPeerConnection'), 'createOffer', 'RTCPeerConnection.createOffer');

  // ---------------------------------------------------------------- storage and cookies
  const cookieDesc = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie');
  if (cookieDesc && cookieDesc.get && cookieDesc.set) {
    Object.defineProperty(Document.prototype, 'cookie', {
      configurable: true, enumerable: cookieDesc.enumerable,
      get: function () { record('Document.cookie.get'); return cookieDesc.get.call(this); },
      set: function (v) {
        const script = record('Document.cookie.set', v);
        try {
          const name = String(v).split(';')[0].split('=')[0].trim();
          if (name && !jsCookies.has(name)) jsCookies.set(name, script);
        } catch (_) {}
        return cookieDesc.set.call(this, v);
      },
    });
  }
  wrapMethod(proto('Storage'), 'setItem', 'Storage.setItem', (a) => a[0]);
  wrapMethod(proto('Storage'), 'getItem', 'Storage.getItem', (a) => a[0]);
  wrapMethod(proto('CookieStore'), 'set', 'CookieStore.set', (a) => a[0]);
  wrapMethod(window.indexedDB && Reflect.getPrototypeOf(window.indexedDB), 'open', 'IDBFactory.open', (a) => a[0]);

  // ---------------------------------------------------------------- forms, keystrokes, exfil
  const valueDesc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
  if (valueDesc && valueDesc.get) {
    Object.defineProperty(HTMLInputElement.prototype, 'value', Object.assign({}, valueDesc, {
      get: function () {
        const t = (this.type || 'text').toLowerCase();
        if (t !== 'hidden' && t !== 'submit' && t !== 'button') record('HTMLInputElement.value.get', t + ':' + (this.name || this.id || ''));
        return valueDesc.get.call(this);
      },
    }));
  }
  const WATCHED = { keydown: 1, keyup: 1, keypress: 1, input: 1, change: 1, paste: 1, blur: 1, focusout: 1 };
  const origAdd = EventTarget.prototype.addEventListener;
  const addWrapped = function (type, listener, opts) {
    if (WATCHED[type]) {
      const self = this;
      const tag = self === document ? 'document' : self === window ? 'window' : (self && self.tagName) || '?';
      record('EventTarget.addEventListener', type + '@' + tag);
    }
    return origAdd.call(this, type, listener, opts);
  };
  try { Object.defineProperty(addWrapped, 'name', { value: 'addEventListener' }); } catch (_) {}
  EventTarget.prototype.addEventListener = addWrapped;
  wrapMethod(proto('Navigator'), 'sendBeacon', 'Navigator.sendBeacon', (a) => a[0]);

  Object.defineProperty(window, '__tm', {
    value: {
      collect() {
        const out = Array.from(calls.values());
        calls.clear();
        const cookies = Array.from(jsCookies.entries()).map(([name, script]) => ({ name, script }));
        return { calls: out, cookies: cookies };
      },
    },
    enumerable: false,
  });
})();
