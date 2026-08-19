import html
import json
import os
import secrets
import requests
from flask import Flask, jsonify, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
DEFAULT_PRODUCTS = [
    {'title':'Netflix Premium','category':'Netflix','description':'Entretenimiento en alta calidad.','type':'Perfil','duration':'1 mes','mode':'Alquiler','price':5,'stock':12,'color':'#ef4444'},
    {'title':'Disney+ Premium','category':'Disney+','description':'Películas, series y contenido familiar.','type':'Cuenta completa','duration':'1 mes','mode':'Alquiler','price':6,'stock':8,'color':'#3b82f6'},
    {'title':'Combo Streaming','category':'Combos','description':'Tus plataformas favoritas en un solo combo.','type':'Compartida','duration':'1 mes','mode':'Alquiler','price':10,'stock':0,'color':'#22d3ee'}
]

def supabase(method, path, data=None, admin=False):
    base = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') if admin else (os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY'))
    if not base or not key: return None
    headers = {'apikey': key, 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json', 'Prefer': 'return=representation'}
    try:
        r = requests.request(method, base.rstrip('/') + path, headers=headers, json=data, timeout=10)
        if r.status_code == 204: return []
        return r.json() if r.ok else None
    except (requests.RequestException, ValueError): return None

def products():
    result = supabase('GET', '/rest/v1/products?active=eq.true&order=created_at.asc')
    rows = result if isinstance(result, list) else DEFAULT_PRODUCTS
    return [{'id':x.get('id'),'title':x['title'],'category':x['category'],'description':x.get('description',''),'type':x.get('account_type',x.get('type','Perfil')),'duration':x['duration'],'mode':x['mode'],'price':float(x['price']),'stock':x['stock'],'color':x.get('accent_color',x.get('color','#16c7f3')),'image_url':x.get('image_url')} for x in rows]

def logged_in(): return bool(session.get('admin'))
def admin_ok(): return request.form.get('username') == os.getenv('ADMIN_USERNAME','streamingfactorygt') and request.form.get('password') == os.getenv('ADMIN_PASSWORD','')

PUBLIC = """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Streaming Factory</title><style>
:root{--ink:#071426;--navy:#0b1e39;--blue:#137caa;--cyan:#20c8ed;--ice:#edf8fc;--muted:#597087;--line:#cadce8}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 86% 8%,#c7f2fb 0,transparent 28%),linear-gradient(135deg,#f9fdff 0%,#eaf6fb 48%,#f6fbfe 100%);color:var(--ink);font-family:Inter,system-ui,Arial}.promo{text-align:center;padding:10px;background:var(--ink);color:#fff;font-weight:800;font-size:13px}.wrap{max-width:1150px;margin:auto;padding:24px}.nav{display:flex;justify-content:space-between;align-items:center;border:1px solid #d5e7f0;background:#ffffffd9;backdrop-filter:blur(12px);border-radius:18px;padding:14px 20px;margin-top:12px;box-shadow:0 10px 30px #0b1e3910}.wordmark{font-size:24px;font-weight:950;letter-spacing:3px;line-height:.78;color:#071426}.wordmark span{color:#10c7ee}.wordmark small{display:block;color:#137caa;font-size:8px;letter-spacing:8px;margin:7px 0 0 5px;font-weight:900}.nav a{color:var(--ink);text-decoration:none;margin-left:22px;font-size:14px;font-weight:700}.hero{padding:54px 42px;min-height:380px;display:flex;align-items:center;max-width:none;margin-top:22px;border-radius:24px;background:linear-gradient(90deg,rgba(7,20,38,.98) 0%,rgba(7,20,38,.86) 43%,rgba(7,20,38,.20) 100%),url('https://res.cloudinary.com/ounnwnlg/image/upload/v1787127061/cinematic-streaming-hero.jpg') center/cover;box-shadow:0 22px 50px #0b1e3926}.hero .eyebrow{color:#6ee7f9}.hero h1{color:#fff;max-width:680px}.hero p{color:#d1e5ee;max-width:600px}.eyebrow{color:var(--blue);font-size:12px;font-weight:900;letter-spacing:3px}.hero h1{font-size:clamp(43px,7vw,78px);line-height:.98;margin:15px 0}.hero p{color:var(--muted);font-size:18px;line-height:1.7}.cta,.whats{display:inline-block;text-decoration:none;background:var(--cyan);color:#021421;border-radius:10px;padding:12px 18px;font-weight:900;box-shadow:0 8px 18px #20c8ed3b}.head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:25px 0}.head h2{font-size:30px}.filters{display:flex;gap:8px;flex-wrap:wrap}.filter{background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:99px;padding:9px 14px;cursor:pointer}.filter.active,.filter:hover{background:var(--ink);color:#fff}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}.card{background:linear-gradient(160deg,#0b1e39,#071426);color:#fff;border:1px solid #1a5475;border-radius:18px;overflow:hidden;box-shadow:0 18px 34px #0b1e3924;transition:transform .2s,box-shadow .2s}.card:hover{transform:translateY(-5px);box-shadow:0 24px 42px #0b1e3935}.visual{height:145px;display:grid;place-items:center;background:radial-gradient(circle at 50% 25%,var(--color),transparent 58%),linear-gradient(145deg,#12385a,#08192e)}.visual img{width:100%;height:100%;object-fit:cover}.visual b{font-size:20px;letter-spacing:2px}.body{padding:18px}.body h3{margin:0 0 7px;font-size:20px}.body p{color:#b8c7d8;min-height:42px;line-height:1.45;font-size:14px}.badges{display:flex;gap:6px;flex-wrap:wrap;margin:15px 0}.badge{font-size:11px;border:1px solid #2d4965;padding:5px 8px;border-radius:5px;color:#cbd8e6}.stock{color:#4ade80;font-size:12px;font-weight:800}.out{color:#fb7185}.buy{display:flex;justify-content:space-between;align-items:center;margin-top:16px}.price{font-size:24px;font-weight:900}.price small{font-size:12px;color:#a9bbcd}.whats{background:#22c55e;font-size:13px}.disabled{background:#475569;pointer-events:none;color:#cbd5e1}.reviews{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:60px 0}.review{border:1px solid #d4e8f1;border-radius:16px;padding:20px;color:var(--muted);background:#ffffffd9;box-shadow:0 10px 25px #0b1e390c}.stars{color:#eab308;letter-spacing:2px}.footer{border-top:1px solid var(--line);padding:28px 0;color:var(--muted);font-size:13px}.float{position:fixed;right:22px;bottom:22px;width:56px;height:56px;border-radius:50%;display:grid;place-items:center;background:#22c55e;color:#06230e;text-decoration:none;font-size:25px}@media(max-width:650px){.wrap{padding:18px}.nav a{display:none}.head{display:block}.filters{margin-top:15px}}</style></head><body><div class='promo'>PROMO_TEXT</div><main class='wrap'><nav class='nav'><div class='wordmark'>STR<span>E</span>AMING<small>FACTORY</small></div><div><a href='#catalogo'>Catálogo</a><a href='#reviews'>Reseñas</a><a href='/admin'>Admin</a></div></nav><section class='hero'><div class='eyebrow'>TU ENTRETENIMIENTO, A TU MANERA</div><h1>Todo el streaming en un solo lugar.</h1><p>Elige tu servicio favorito, recibe atención rápida y empieza a disfrutar hoy mismo.</p><a class='cta' href='#catalogo'>Ver catálogo ↓</a></section><section id='catalogo'><div class='head'><h2>Catálogo</h2><div class='filters'><button class='filter active' data-cat='Todos'>Todos</button><button class='filter' data-cat='Netflix'>Netflix</button><button class='filter' data-cat='Disney+'>Disney+</button><button class='filter' data-cat='Combos'>Combos</button></div></div><div id='products' class='grid'></div></section><section id='reviews'><div class='head'><h2>Reseñas de clientes</h2></div><div class='reviews'><div class='review'><div class='stars'>★★★★★</div><p>Entrega rápida y todo funcionando perfecto.</p><b>— Cliente verificado</b></div><div class='review'><div class='stars'>★★★★★</div><p>Excelente atención, respondieron al instante.</p><b>— Cliente verificado</b></div><div class='review'><div class='stars'>★★★★☆</div><p>Proceso sencillo y buena experiencia.</p><b>— Cliente verificado</b></div></div></section><footer class='footer'>© 2026 Streaming Factory · Atención por WhatsApp</footer></main><a class='float' href='https://wa.me/50259271314?text=Hola%20Streaming%20Factory,%20necesito%20informacion' target='_blank'>◔</a><script>const products=PRODUCTS_JSON;const root=document.querySelector('#products');function render(cat='Todos'){root.innerHTML=products.filter(p=>cat==='Todos'||p.category===cat).map(p=>{const out=!p.stock;const msg=encodeURIComponent('Hola qué tal Streaming Factory, quisiera comprar '+p.title+' '+p.duration+' por el valor de $'+p.price+'.');const image=p.image_url?'<img src="'+p.image_url+'" alt="'+p.title+'">':'<b>'+p.category+'</b>';return '<article class="card"><div class="visual" style="--color:'+p.color+'">'+image+'</div><div class="body"><h3>'+p.title+'</h3><p>'+p.description+'</p><div class="badges"><span class="badge">'+p.type+'</span><span class="badge">'+p.duration+'</span><span class="badge">'+p.mode+'</span></div><span class="stock '+(out?'out':'')+'">● '+(out?'Agotado':'En Stock')+'</span><div class="buy"><div class="price">$'+p.price+' <small>USD</small></div><a class="whats '+(out?'disabled':'')+'" href="https://wa.me/50259271314?text='+msg+'" target="_blank">WhatsApp</a></div></div></article>'}).join('')}document.querySelectorAll('.filter').forEach(b=>b.onclick=()=>{document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');render(b.dataset.cat)});render();</script></body></html>"""

LOGIN = """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin · Streaming Factory</title><style>body{margin:0;background:#f7fafc;font-family:system-ui;color:#07111f;display:grid;place-items:center;min-height:100vh}.box{background:#07111f;color:#fff;padding:32px;border-radius:16px;width:min(420px,90vw);box-shadow:0 20px 50px #07111f33}input,button{width:100%;padding:13px;margin:8px 0;border-radius:8px;border:1px solid #38506b;box-sizing:border-box}input{background:#10243a;color:#fff}button{background:#09b9e8;border:0;font-weight:900;cursor:pointer}.error{color:#fb7185}.back{color:#9beafa}</style></head><body><form class='box' method='post'><h1>Panel privado</h1><p>Streaming Factory</p>{error}<input name='username' placeholder='Usuario' required><input name='password' type='password' placeholder='Contraseña' required><button>Acceder</button><a class='back' href='/'>← Volver al catálogo</a></form></body></html>"""

ADMIN = """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Panel · Streaming Factory</title><style>body{margin:0;background:#f7fafc;font-family:system-ui;color:#07111f}.top{background:#07111f;color:#fff;padding:20px 5%;display:flex;justify-content:space-between}.top a{color:#9beafa}.wrap{max-width:1100px;margin:auto;padding:28px}.panel{background:#fff;border:1px solid #d9e3ec;border-radius:14px;padding:22px;margin-bottom:22px}.form{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.form input,.form select,.form button{padding:12px;border:1px solid #cbd5e1;border-radius:7px;box-sizing:border-box}.form button{background:#09b9e8;border:0;font-weight:900;cursor:pointer}.full{grid-column:1/-1}.table{width:100%;border-collapse:collapse}.table td,.table th{padding:10px;text-align:left;border-bottom:1px solid #e2e8f0}.danger{background:#fee2e2;border:0;border-radius:6px;padding:7px;color:#991b1b;cursor:pointer}@media(max-width:650px){.form{grid-template-columns:1fr}.full{grid-column:auto}}</style></head><body><header class='top'><b>STREAMING FACTORY · ADMIN</b><span><a href='/'>Ver sitio</a> · <a href='/admin/logout'>Salir</a></span></header><main class='wrap'><h1>Gestión de productos</h1><section class='panel'><h2>Nuevo producto</h2><form class='form' method='post' action='/admin/products'><input name='title' placeholder='Título' required><input name='category' placeholder='Categoría' required><input name='description' placeholder='Descripción' required><input name='account_type' placeholder='Tipo de cuenta' required><input name='duration' placeholder='Duración' required><input name='mode' placeholder='Modalidad' required><input name='price' type='number' step='0.01' placeholder='Precio USD' required><input name='stock' type='number' placeholder='Stock' required><input class='full' name='image_url' placeholder='URL de imagen en Cloudinary (opcional)'><button class='full'>Guardar producto</button></form></section><section class='panel'><h2>Productos actuales</h2><table class='table'><tr><th>Producto</th><th>Categoría</th><th>Precio</th><th>Stock</th><th></th></tr>PRODUCT_ROWS</table></section></main></body></html>"""

@app.get('/')
def home():
    settings = supabase('GET','/rest/v1/site_settings?id=eq.true&select=*') or []
    promo = settings[0].get('promo_text','⚡ Entrega inmediata · Soporte por WhatsApp') if settings else '⚡ Entrega inmediata · Soporte por WhatsApp'
    return PUBLIC.replace('PRODUCTS_JSON',json.dumps(products(),ensure_ascii=False)).replace('PROMO_TEXT',html.escape(promo))

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if logged_in(): return redirect(url_for('admin_dashboard'))
    error = ''
    if request.method == 'POST':
        if admin_ok(): session['admin'] = True; return redirect(url_for('admin_dashboard'))
        error = '<p class="error">Credenciales incorrectas.</p>'
    return LOGIN.replace('{error}',error)

@app.get('/admin/dashboard')
def admin_dashboard():
    if not logged_in(): return redirect('/admin')
    rows = supabase('GET','/rest/v1/products?order=created_at.desc',admin=True) or []
    table = ''.join('<tr><td>'+html.escape(str(x.get('title','')))+' </td><td>'+html.escape(str(x.get('category','')))+' </td><td>$'+str(x.get('price',0))+'</td><td>'+str(x.get('stock',0))+'</td><td><form method="post" action="/admin/products/delete/'+str(x.get('id'))+'"><button class="danger">Eliminar</button></form></td></tr>' for x in rows)
    return ADMIN.replace('PRODUCT_ROWS',table or '<tr><td colspan="5">No hay productos.</td></tr>')

@app.post('/admin/products')
def create_product():
    if not logged_in(): return redirect('/admin')
    data = {k:request.form.get(k,'') for k in ['title','description','category','account_type','duration','mode','image_url']}
    data.update({'price':float(request.form.get('price',0)),'stock':int(request.form.get('stock',0))})
    supabase('POST','/rest/v1/products',data,admin=True)
    return redirect('/admin/dashboard')

@app.post('/admin/products/delete/<product_id>')
def delete_product(product_id):
    if not logged_in(): return redirect('/admin')
    supabase('DELETE','/rest/v1/products?id=eq.'+product_id,admin=True)
    return redirect('/admin/dashboard')

@app.get('/admin/logout')
def admin_logout():
    session.clear(); return redirect('/admin')

@app.get('/api/health')
def health():
    configured = bool(os.getenv('SUPABASE_URL') and (os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY')))
    return jsonify({'status':'ok','supabase':configured}),200

if __name__ == '__main__': app.run(host='0.0.0.0',port=int(os.getenv('PORT',5000)))
