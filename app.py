import json
import html
import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)
PRODUCTS = [
    {"title":"Netflix Premium","category":"Netflix","description":"Entretenimiento en alta calidad.","type":"Perfil","duration":"1 mes","mode":"Alquiler","price":5,"stock":12,"color":"#ef4444"},
    {"title":"Disney+ Premium","category":"Disney+","description":"Películas, series y contenido familiar.","type":"Cuenta completa","duration":"1 mes","mode":"Alquiler","price":6,"stock":8,"color":"#3b82f6"},
    {"title":"Combo Streaming","category":"Combos","description":"Tus plataformas favoritas en un solo combo.","type":"Compartida","duration":"1 mes","mode":"Alquiler","price":10,"stock":0,"color":"#22d3ee"}
]
PAGE = """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Streaming Factory</title><style>
:root{--bg:#050b18;--panel:#0d192c;--line:#1d304b;--cyan:#16c7f3;--muted:#91a4be}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 80% 0,#123250,transparent 40%),var(--bg);color:#f8fafc;font-family:Inter,system-ui,Arial}.promo{text-align:center;padding:10px;background:linear-gradient(90deg,#087ca8,#16c7f3);color:#00131d;font-weight:800;font-size:13px}.wrap{max-width:1150px;margin:auto;padding:24px}.nav{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding:16px 0}.logo{width:240px;max-width:55vw;display:block}.brand{font-weight:900;letter-spacing:5px;font-size:22px}.brand i{color:var(--cyan);font-style:normal}.brand small{display:block;color:var(--cyan);font-size:10px;letter-spacing:8px;margin-top:5px}.nav a{color:#b8c9dd;text-decoration:none;margin-left:22px;font-size:14px}.hero{padding:72px 0 45px;max-width:720px}.eyebrow{color:var(--cyan);font-size:12px;font-weight:800;letter-spacing:3px}.hero h1{font-size:clamp(43px,7vw,78px);line-height:.98;margin:15px 0}.hero p{color:var(--muted);font-size:18px;line-height:1.7}.cta,.whats{display:inline-block;text-decoration:none;background:var(--cyan);color:#00131d;border-radius:8px;padding:12px 17px;font-weight:900}.head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:25px 0}.head h2{font-size:30px}.filters{display:flex;gap:8px;flex-wrap:wrap}.filter{background:transparent;color:#b8c9dd;border:1px solid var(--line);border-radius:99px;padding:9px 14px;cursor:pointer}.filter.active,.filter:hover{background:var(--cyan);color:#00131d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}.card{background:linear-gradient(145deg,#11223a,#091321);border:1px solid var(--line);border-radius:15px;overflow:hidden}.visual{height:145px;display:grid;place-items:center;background:radial-gradient(circle,var(--color),transparent 65%),#091321}.visual b{font-size:20px;letter-spacing:2px}.body{padding:18px}.body h3{margin:0 0 7px;font-size:20px}.body p{color:var(--muted);min-height:42px;line-height:1.45;font-size:14px}.badges{display:flex;gap:6px;flex-wrap:wrap;margin:15px 0}.badge{font-size:11px;border:1px solid var(--line);padding:5px 8px;border-radius:5px;color:#b8c9dd}.stock{color:#4ade80;font-size:12px;font-weight:800}.out{color:#fb7185}.buy{display:flex;justify-content:space-between;align-items:center;margin-top:16px}.price{font-size:24px;font-weight:900}.price small{font-size:12px;color:var(--muted)}.whats{background:#22c55e;font-size:13px}.disabled{background:#334155;pointer-events:none;color:#94a3b8}.reviews{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:60px 0}.review{border:1px solid var(--line);border-radius:12px;padding:18px;color:#c7d2e3}.stars{color:#facc15;letter-spacing:2px}.footer{border-top:1px solid var(--line);padding:28px 0;color:var(--muted);font-size:13px}.float{position:fixed;right:22px;bottom:22px;width:56px;height:56px;border-radius:50%;display:grid;place-items:center;background:#22c55e;color:#06230e;text-decoration:none;font-size:25px}@media(max-width:650px){.wrap{padding:18px}.nav a{display:none}.head{display:block}.filters{margin-top:15px}}
</style></head><body><div class='promo'>⚡ Entrega inmediata · Soporte por WhatsApp</div><main class='wrap'><nav class='nav'><div class='brand'><img class='logo' src='https://res.cloudinary.com/ounnwnlg/image/upload/v1787126292/streaming-factory-logo.png' alt='Streaming Factory'></div><div><a href='#catalogo'>Catálogo</a><a href='#reviews'>Reseñas</a></div></nav><section class='hero'><div class='eyebrow'>TU ENTRETENIMIENTO, A TU MANERA</div><h1>Todo el streaming en un solo lugar.</h1><p>Elige tu servicio favorito, recibe atención rápida y empieza a disfrutar hoy mismo.</p><a class='cta' href='#catalogo'>Ver catálogo ↓</a></section><section id='catalogo'><div class='head'><h2>Catálogo</h2><div class='filters'><button class='filter active' data-cat='Todos'>Todos</button><button class='filter' data-cat='Netflix'>Netflix</button><button class='filter' data-cat='Disney+'>Disney+</button><button class='filter' data-cat='Combos'>Combos</button></div></div><div id='products' class='grid'></div></section><section id='reviews'><div class='head'><h2>Reseñas de clientes</h2></div><div class='reviews'><div class='review'><div class='stars'>★★★★★</div><p>Entrega rápida y todo funcionando perfecto.</p><b>— Cliente verificado</b></div><div class='review'><div class='stars'>★★★★★</div><p>Excelente atención, respondieron al instante.</p><b>— Cliente verificado</b></div><div class='review'><div class='stars'>★★★★☆</div><p>Proceso sencillo y buena experiencia.</p><b>— Cliente verificado</b></div></div></section><footer class='footer'>© 2026 Streaming Factory · Atención por WhatsApp</footer></main><a class='float' href='https://wa.me/50259271314?text=Hola%20Streaming%20Factory,%20necesito%20informacion' target='_blank'>◔</a><script>const products=PRODUCTS_JSON;const root=document.querySelector('#products');function render(cat='Todos'){root.innerHTML=products.filter(p=>cat==='Todos'||p.category===cat).map(p=>{const out=!p.stock;const msg=encodeURIComponent('Hola qué tal Streaming Factory, quisiera comprar '+p.title+' '+p.duration+' por el valor de $'+p.price+'.');return '<article class="card"><div class="visual" style="--color:'+p.color+'"><b>'+p.category+'</b></div><div class="body"><h3>'+p.title+'</h3><p>'+p.description+'</p><div class="badges"><span class="badge">'+p.type+'</span><span class="badge">'+p.duration+'</span><span class="badge">'+p.mode+'</span></div><span class="stock '+(out?'out':'')+'">● '+(out?'Agotado':'En Stock')+'</span><div class="buy"><div class="price">$'+p.price+' <small>USD</small></div><a class="whats '+(out?'disabled':'')+'" href="https://wa.me/50259271314?text='+msg+'" target="_blank">WhatsApp</a></div></div></article>'}).join('')}document.querySelectorAll('.filter').forEach(b=>b.onclick=()=>{document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');render(b.dataset.cat)});render();</script></body></html>"""

def _supabase_get(path):
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    if not url or not key:
        return None
    try:
        response = requests.get(url.rstrip('/') + path, headers={'apikey': key, 'Authorization': 'Bearer ' + key}, timeout=8)
        return response.json() if response.ok else None
    except (requests.RequestException, ValueError):
        return None

def catalog_products():
    records = _supabase_get('/rest/v1/products?active=eq.true&order=created_at.asc') or PRODUCTS
    return [{
        'id': item.get('id'),
        'title': item['title'], 'category': item['category'],
        'description': item.get('description', ''),
        'type': item.get('account_type', item.get('type', 'Perfil')),
        'duration': item['duration'], 'mode': item['mode'],
        'price': float(item['price']), 'stock': item['stock'],
        'color': item.get('accent_color', item.get('color', '#16c7f3')),
        'image_url': item.get('image_url')
    } for item in records]

def site_settings():
    values = _supabase_get('/rest/v1/site_settings?id=eq.true&select=*')
    return values[0] if values else {'promo_enabled': True, 'promo_text': '⚡ Entrega inmediata · Soporte por WhatsApp'}

@app.get('/')
def home():
    settings = site_settings()
    promo = html.escape(settings.get('promo_text', '')) if settings.get('promo_enabled', True) else ''
    page = PAGE.replace('PRODUCTS_JSON', json.dumps(catalog_products(), ensure_ascii=False))
    return page.replace('⚡ Entrega inmediata · Soporte por WhatsApp', promo)

@app.get('/api/health')
def health():
    url, key = os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY')
    if url and key:
        try:
            r = requests.get(url.rstrip('/') + '/rest/v1/', headers={'apikey': key}, timeout=5)
            return jsonify({'status':'ok','supabase':r.status_code < 500}), 200
        except requests.RequestException:
            return jsonify({'status':'ok','supabase':False}), 200
    return jsonify({'status':'ok','supabase':'not_configured'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)))
