"""Testbed server. One process serves many fake hostnames (Chrome resolves *.localhost
to loopback), dispatching on the Host header. Everything planted here is listed in
ground_truth.json so detectors can be scored for precision/recall.

Sites:
  shop.localhost     "IndiShop": trackers, cookie sync, fingerprinting, leaky form scripts
  clean.localhost    no third parties at all (negative control: expect zero findings)
  blocked.localhost  bot-wall page (expect status=blocked)
Third parties:
  adnet-a      ad network: user ID in first-party storage, pixel, sync redirect -> broker-b
  broker-b     data broker receiving adnet-a's user ID via redirect
  analytics-c  analytics: canvas + audio fingerprinting, client ID cookie
  leaky-d      "form helper": sends sha256(email) on blur, base64(+91 phone) in POST body
  replay-f     session replay: records input values, posts them URL-encoded
  widget-g     chat widget iframe: sends base64url(email) typed inside the iframe
"""

from __future__ import annotations

import argparse
import base64
import secrets
import threading

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response

DEFAULT_PORT = 8765
GIF = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


def make_app(port: int) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    base = lambda host: f"http://{host}.localhost:{port}"  # noqa: E731

    # ------------------------------------------------------------------ page templates

    def shop_page(title: str, body: str) -> str:
        nav = "".join(
            f'<a href="{p}">{n}</a> '
            for p, n in [("/", "Home"), ("/products", "Products"), ("/offers", "Offers"),
                         ("/about", "About"), ("/contact", "Contact us"), ("/login", "Login")]
        )
        return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>IndiShop - {title}</title>
<script src="{base('adnet-a')}/tag.js"></script>
<script src="{base('analytics-c')}/a.js" async></script>
<script src="{base('leaky-d')}/form.js"></script>
<script src="{base('replay-f')}/rec.js"></script>
<script src="/static/app.js"></script>
</head><body><nav>{nav}</nav><main><h1>{title}</h1>{body}</main>
<footer><a href="/terms.pdf">Terms (PDF)</a> <a href="https://example.org/">Partner</a></footer></body></html>"""

    contact_form = f"""
<p>Subscribe for offers on WhatsApp and email.</p>
<form id="newsletter" action="/subscribe" method="post">
  <label>Email <input type="email" name="email" placeholder="you@example.com" required></label>
  <label>Mobile number <input type="tel" name="mobile" placeholder="10-digit mobile" required></label>
  <button type="submit">Subscribe</button>
</form>
<iframe src="{base('widget-g')}/chat" width="320" height="140" title="Chat"></iframe>"""

    login_form = """
<form id="login" action="/session" method="post">
  <label>Email ID <input type="text" name="user_email" autocomplete="email"></label>
  <label>Password <input type="password" name="password"></label>
  <button type="submit">Sign in</button>
</form>"""

    shop_pages = {
        "/": ("Home", "<p>Big Diwali sale. Free delivery across India.</p>"),
        "/products": ("Products", "<ul><li>Kurta</li><li>Saree</li><li>Phone</li></ul>"),
        "/offers": ("Offers", "<p>10% off with UPI.</p>"),
        "/about": ("About", "<p>IndiShop is a fictional testbed shop.</p>"),
        "/contact": ("Contact us", contact_form),
        "/login": ("Login", login_form),
    }

    clean_pages = {
        "/": "<h1>Clean site</h1><a href='/contact'>Contact</a><a href='/about'>About</a>",
        "/about": "<h1>About</h1><a href='/'>Home</a>",
        "/contact": "<h1>Contact</h1><form><input type='email' name='email'>"
                    "<input type='tel' name='phone'><button>Send</button></form>",
    }

    # ------------------------------------------------------------------ scripts

    adnet_js = f"""(function(){{
  var k='_adn_uid', uid=localStorage.getItem(k);
  if(!uid){{uid='';var a=new Uint8Array(12);crypto.getRandomValues(a);a.forEach(function(b){{uid+=('0'+b.toString(16)).slice(-2)}});localStorage.setItem(k,uid);}}
  document.cookie='_adn='+uid+'; path=/; max-age=31536000';
  new Image().src='{base('adnet-a')}/px?uid='+uid+'&p='+encodeURIComponent(location.pathname)+'&t='+Date.now();
  new Image().src='{base('adnet-a')}/sync?uid='+uid;
}})();"""

    analytics_js = f"""(function(){{
  function rnd(){{return Math.random().toString(36).slice(2)+Math.random().toString(36).slice(2)}}
  var m=document.cookie.match(/(?:^|; )_ac_cid=([^;]+)/), cid=m?m[1]:rnd();
  document.cookie='_ac_cid='+cid+'; path=/; max-age=63072000';
  var c=document.createElement('canvas');c.width=220;c.height=30;var x=c.getContext('2d');
  x.textBaseline='top';x.font='14px Arial';x.fillStyle='#f60';x.fillRect(125,1,62,20);
  x.fillStyle='#069';x.fillText('IndiShop fp \\ud83d\\ude03',2,15);var fp=c.toDataURL().length;
  try{{var o=new OfflineAudioContext(1,44100,44100),osc=o.createOscillator(),cmp=o.createDynamicsCompressor();
      osc.connect(cmp);cmp.connect(o.destination);osc.start(0);o.startRendering();}}catch(e){{}}
  var nav=[navigator.userAgent,navigator.language,navigator.hardwareConcurrency,navigator.platform,screen.width,screen.colorDepth].join('|');
  fetch('{base('analytics-c')}/collect',{{method:'POST',mode:'no-cors',headers:{{'Content-Type':'text/plain'}},
    body:JSON.stringify({{cid:cid,fp:fp,nav:nav.length,page:location.pathname}})}});
}})();"""

    leaky_js = f"""(function(){{
  async function sha256(s){{var b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));
    return Array.from(new Uint8Array(b)).map(function(x){{return('0'+x.toString(16)).slice(-2)}}).join('');}}
  document.addEventListener('blur',async function(e){{
    var el=e.target; if(!el||el.tagName!=='INPUT')return;
    var v=el.value; if(!v)return;
    if(el.type==='email'||/mail/i.test(el.name)){{
      new Image().src='{base('leaky-d')}/c?em='+(await sha256(v.trim().toLowerCase()));
    }} else if(el.type==='tel'||/mobile|phone/i.test(el.name)){{
      fetch('{base('leaky-d')}/c',{{method:'POST',mode:'no-cors',headers:{{'Content-Type':'text/plain'}},
        body:JSON.stringify({{ph:btoa('+91'+v.replace(/\\D/g,'').slice(-10))}})}});
    }}
  }},true);
}})();"""

    replay_js = f"""(function(){{
  var buf=[];
  document.addEventListener('input',function(e){{
    var el=e.target; if(!el||el.type==='password')return;
    buf.push({{n:el.name,v:el.value,t:Date.now()}});
  }},true);
  setInterval(function(){{ if(!buf.length)return;
    var body='d='+encodeURIComponent(JSON.stringify(buf.splice(0)));
    fetch('{base('replay-f')}/rec',{{method:'POST',mode:'no-cors',
      headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body:body}});
  }},1500);
}})();"""

    first_party_js = """(function(){
  document.addEventListener('change',function(e){
    var el=e.target; if(el&&el.type==='email'&&el.value){
      fetch('/api/track',{method:'POST',headers:{'Content-Type':'text/plain'},body:JSON.stringify({email:el.value})});
    }
  },true);
})();"""

    widget_html = f"""<!doctype html><html><body><p>Chat with us</p>
<input type="email" name="chat_email" placeholder="Your email">
<script>
document.querySelector('input').addEventListener('change',function(e){{
  var b=btoa(e.target.value).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,'');
  new Image().src='{base('widget-g')}/w?e='+b;
}});
</script></body></html>"""

    blocked_html = """<!doctype html><html><head><title>Just a moment...</title></head>
<body><div id="challenge-running">Checking if the site connection is secure. Verify you are human.</div>
<script>/* cf-chl */</script></body></html>"""

    js = lambda s: Response(s, media_type="application/javascript")  # noqa: E731

    @app.api_route("/{path:path}", methods=["GET", "POST"])
    async def dispatch(request: Request, path: str):
        host = (request.headers.get("host") or "").split(":")[0]
        name = host.removesuffix(".localhost")
        p = "/" + path
        if request.method == "POST":
            await request.body()

        if name == "shop":
            if p in shop_pages:
                return HTMLResponse(shop_page(*shop_pages[p]))
            if p == "/static/app.js":
                return js(first_party_js)
            if p == "/api/track":
                return PlainTextResponse("ok")
            if p == "/terms.pdf":
                return Response(b"%PDF-1.4", media_type="application/pdf")
        elif name == "clean":
            if p in clean_pages:
                return HTMLResponse(f"<!doctype html><title>Clean</title>{clean_pages[p]}")
        elif name == "blocked":
            return HTMLResponse(blocked_html, status_code=403)
        elif name == "adnet-a":
            if p == "/tag.js":
                return js(adnet_js)
            if p == "/px":
                return Response(GIF, media_type="image/gif")
            if p == "/sync":
                uid = request.query_params.get("uid", "")
                return RedirectResponse(f"{base('broker-b')}/match?partner=adnet&puid={uid}", status_code=302)
        elif name == "broker-b":
            if p == "/match":
                r = Response(GIF, media_type="image/gif")
                r.set_cookie("bk", secrets.token_hex(10), max_age=31536000)
                return r
        elif name == "analytics-c":
            if p == "/a.js":
                return js(analytics_js)
            if p == "/collect":
                return PlainTextResponse("ok", headers={"Access-Control-Allow-Origin": "*"})
        elif name == "leaky-d":
            if p == "/form.js":
                return js(leaky_js)
            if p == "/c":
                return Response(GIF, media_type="image/gif", headers={"Access-Control-Allow-Origin": "*"})
        elif name == "replay-f":
            if p == "/rec.js":
                return js(replay_js)
            if p == "/rec":
                return PlainTextResponse("ok", headers={"Access-Control-Allow-Origin": "*"})
        elif name == "widget-g":
            if p == "/chat":
                return HTMLResponse(widget_html)
            if p == "/w":
                return Response(GIF, media_type="image/gif")
        return PlainTextResponse("not found", status_code=404)

    return app


class TestbedServer:
    """Run the testbed in a background thread (used by tests and demos)."""

    __test__ = False  # not a pytest test class

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self._server = uvicorn.Server(uvicorn.Config(make_app(port), host="127.0.0.1", port=port, log_level="warning"))
        self._thread = threading.Thread(target=self._server.run, daemon=True)

    def url(self, site: str, path: str = "/") -> str:
        return f"http://{site}.localhost:{self.port}{path}"

    def __enter__(self) -> "TestbedServer":
        self._thread.start()
        import time
        for _ in range(100):
            if self._server.started:
                break
            time.sleep(0.05)
        return self

    def __exit__(self, *exc) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5)


def main() -> None:
    ap = argparse.ArgumentParser(description="TraceMap local testbed")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    print(f"Testbed on http://shop.localhost:{args.port}/  (also clean.localhost, blocked.localhost)")
    uvicorn.run(make_app(args.port), host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
