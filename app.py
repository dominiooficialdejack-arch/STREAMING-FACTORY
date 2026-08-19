import hashlib
import html
import json
import os
import secrets
import time
import threading
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
def admin_ok():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()
    expected_user = os.getenv('ADMIN_USERNAME', 'streamingfactorygt').strip().lower()
    expected_password = os.getenv('ADMIN_PASSWORD', '').strip()
    return username == expected_user and password == expected_password

PUBLIC = """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Streaming Factory</title><style>
:root{--ink:#071426;--navy:#0b1e39;--blue:#137caa;--cyan:#20c8ed;--ice:#edf8fc;--muted:#597087;--line:#cadce8}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 86% 8%,#c7f2fb 0,transparent 28%),linear-gradient(135deg,#f9fdff 0%,#eaf6fb 48%,#f6fbfe 100%);color:var(--ink);font-family:Inter,system-ui,Arial}.promo{text-align:center;padding:10px;background:var(--ink);color:#fff;font-weight:800;font-size:13px}.wrap{max-width:1150px;margin:auto;padding:24px}.nav{display:flex;justify-content:space-between;align-items:center;border:1px solid #d5e7f0;background:#ffffffd9;backdrop-filter:blur(12px);border-radius:18px;padding:14px 20px;margin-top:12px;box-shadow:0 10px 30px #0b1e3910}.wordmark{font-size:24px;font-weight:950;letter-spacing:3px;line-height:.78;color:#071426}.wordmark span{color:#10c7ee}.wordmark small{display:block;color:#137caa;font-size:8px;letter-spacing:8px;margin:7px 0 0 5px;font-weight:900}.nav a{color:var(--ink);text-decoration:none;margin-left:22px;font-size:14px;font-weight:700}.hero{padding:54px 42px;min-height:380px;display:flex;align-items:center;max-width:none;margin-top:22px;border-radius:24px;background:linear-gradient(90deg,rgba(7,20,38,.98) 0%,rgba(7,20,38,.86) 43%,rgba(7,20,38,.20) 100%),url('https://res.cloudinary.com/ounnwnlg/image/upload/v1787127061/cinematic-streaming-hero.jpg') center/cover;box-shadow:0 22px 50px #0b1e3926}.hero .eyebrow{color:#6ee7f9}.hero h1{color:#fff;max-width:680px}.hero p{color:#d1e5ee;max-width:600px}.eyebrow{color:var(--blue);font-size:12px;font-weight:900;letter-spacing:3px}.hero h1{font-size:clamp(43px,7vw,78px);line-height:.98;margin:15px 0}.hero p{color:var(--muted);font-size:18px;line-height:1.7}.cta,.whats{display:inline-block;text-decoration:none;background:var(--cyan);color:#021421;border-radius:10px;padding:12px 18px;font-weight:900;box-shadow:0 8px 18px #20c8ed3b}.head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:25px 0}.head h2{font-size:30px}.filters{display:flex;gap:8px;flex-wrap:wrap}.filter{background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:99px;padding:9px 14px;cursor:pointer}.filter.active,.filter:hover{background:var(--ink);color:#fff}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:18px}.card{background:linear-gradient(160deg,#0b1e39,#071426);color:#fff;border:1px solid #1a5475;border-radius:18px;overflow:hidden;box-shadow:0 18px 34px #0b1e3924;transition:transform .2s,box-shadow .2s}.card:hover{transform:translateY(-5px);box-shadow:0 24px 42px #0b1e3935}.visual{height:145px;display:grid;place-items:center;background:radial-gradient(circle at 50% 25%,var(--color),transparent 58%),linear-gradient(145deg,#12385a,#08192e)}.visual img{width:100%;height:100%;object-fit:cover}.visual b{font-size:20px;letter-spacing:2px}.body{padding:18px}.body h3{margin:0 0 7px;font-size:20px}.body p{color:#b8c7d8;min-height:42px;line-height:1.45;font-size:14px}.badges{display:flex;gap:6px;flex-wrap:wrap;margin:15px 0}.badge{font-size:11px;border:1px solid #2d4965;padding:5px 8px;border-radius:5px;color:#cbd8e6}.stock{color:#4ade80;font-size:12px;font-weight:800}.out{color:#fb7185}.buy{display:flex;justify-content:space-between;align-items:center;margin-top:16px}.price{font-size:24px;font-weight:900}.price small{font-size:12px;color:#a9bbcd}.whats{background:#22c55e;font-size:13px}.disabled{background:#475569;pointer-events:none;color:#cbd5e1}.reviews{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:60px 0}.review{border:1px solid #d4e8f1;border-radius:16px;padding:20px;color:var(--muted);background:#ffffffd9;box-shadow:0 10px 25px #0b1e390c}.stars{color:#eab308;letter-spacing:2px}.footer{border-top:1px solid var(--line);padding:28px 0;color:var(--muted);font-size:13px}.float{position:fixed;right:22px;bottom:22px;width:56px;height:56px;border-radius:50%;display:grid;place-items:center;background:#22c55e;color:#06230e;text-decoration:none;font-size:25px}@media(max-width:650px){.wrap{padding:18px}.nav a{display:none}.head{display:block}.filters{margin-top:15px}}@media(max-width:700px){.wrap{padding:12px}.nav{padding:12px 14px;flex-wrap:wrap;gap:12px}.wordmark{font-size:19px}.wordmark small{font-size:7px;letter-spacing:5px}.nav a{margin-left:8px;font-size:12px}.hero{padding:34px 22px;min-height:430px;border-radius:18px;background-position:center}.hero h1{font-size:clamp(36px,12vw,56px);line-height:1}.hero p{font-size:15px;line-height:1.5}.head{display:block;margin:22px 0 16px}.head h2{font-size:25px;margin:0 0 14px}.filters{flex-wrap:nowrap;overflow-x:auto;padding-bottom:5px}.filter{white-space:nowrap}.grid{grid-template-columns:1fr;gap:14px}.visual{height:170px}.body{padding:16px}.body p{min-height:0}.buy{gap:10px}.whats{padding:10px 12px;font-size:12px}.reviews{grid-template-columns:1fr;gap:12px;margin:40px 0}}.search{background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:99px;padding:9px 14px;min-width:220px;outline:none}.search:focus{border-color:var(--blue);box-shadow:0 0 0 3px #20c8ed22}@media(max-width:700px){.search{min-width:190px;width:100%}}.hero{flex-direction:column;align-items:flex-start;justify-content:center;width:100%;overflow:hidden}.hero h1,.hero p,.hero .eyebrow{width:100%;max-width:680px}@media(max-width:700px){.hero{min-height:360px;padding:30px 20px;gap:0;background-position:center;border-radius:18px}.hero .eyebrow{font-size:10px;letter-spacing:1.7px;line-height:1.4}.hero h1{font-size:clamp(34px,11vw,48px);line-height:1.02;margin:12px 0;overflow-wrap:break-word}.hero p{font-size:15px;line-height:1.5;margin:0 0 20px}.hero .cta{max-width:100%;white-space:nowrap;padding:11px 15px}}</style></head><body><div class='promo'>PROMO_TEXT</div><main class='wrap'><nav class='nav'><div class='wordmark'>STR<span>E</span>AMING<small>FACTORY</small></div><div><a href='#catalogo'>Catálogo</a><a href='#reviews'>Reseñas</a><a href='/admin'>Admin</a></div></nav><section class='hero'><div class='eyebrow'>TU ENTRETENIMIENTO, A TU MANERA</div><h1>Todo el streaming en un solo lugar.</h1><p>Elige tu servicio favorito, recibe atención rápida y empieza a disfrutar hoy mismo.</p><a class='cta' href='#catalogo'>Ver catálogo ↓</a></section><section id='catalogo'><div class='head'><h2>Catálogo</h2><div class='filters'><button class='filter active' data-cat='Todos'>Todos</button><input id='search' class='search' type='search' placeholder='🔍 Buscar productos...'></div></div><div id='products' class='grid'></div></section><section id='reviews'><div class='head'><h2>Reseñas de clientes</h2></div><div class='reviews'><div class='review'><div class='stars'>★★★★★</div><p>Entrega rápida y todo funcionando perfecto.</p><b>— Cliente verificado</b></div><div class='review'><div class='stars'>★★★★★</div><p>Excelente atención, respondieron al instante.</p><b>— Cliente verificado</b></div><div class='review'><div class='stars'>★★★★☆</div><p>Proceso sencillo y buena experiencia.</p><b>— Cliente verificado</b></div></div></section><footer class='footer'>© 2026 Streaming Factory · Atención por WhatsApp</footer></main><a class='float' href='https://wa.me/50259271314?text=Hola%20Streaming%20Factory,%20necesito%20informacion' target='_blank'>◔</a><script>const products=PRODUCTS_JSON;const root=document.querySelector('#products');let query='';function render(cat='Todos'){root.innerHTML=products.filter(p=>(cat==='Todos'||p.category===cat)&&(!query||[p.title,p.category,p.description].join(' ').toLowerCase().includes(query))).map(p=>{const out=!p.stock;const msg=encodeURIComponent('Hola qué tal Streaming Factory, quisiera comprar '+p.title+' '+p.duration+' por el valor de $'+p.price+'.');const image=p.image_url?'<img src="'+p.image_url+'" alt="'+p.title+'">':'<b>'+p.category+'</b>';return '<article class="card"><div class="visual" style="--color:'+p.color+'">'+image+'</div><div class="body"><h3>'+p.title+'</h3><p>'+p.description+'</p><div class="badges"><span class="badge">'+p.type+'</span><span class="badge">'+p.duration+'</span><span class="badge">'+p.mode+'</span></div><span class="stock '+(out?'out':'')+'">● '+(out?'Agotado':'En Stock')+'</span><div class="buy"><div class="price">$'+p.price+' <small>USD</small></div><a class="whats '+(out?'disabled':'')+'" href="https://wa.me/50259271314?text='+msg+'" target="_blank">WhatsApp</a></div></div></article>'}).join('')}document.querySelectorAll('.filter').forEach(b=>b.onclick=()=>{document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');render(b.dataset.cat)});document.querySelector('#search').addEventListener('input',e=>{query=e.target.value.toLowerCase().trim();render()});render();</script></body></html>"""

LOGIN = """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='google' content='notranslate'><title>Admin · Streaming Factory</title><style>body{margin:0;background:#f7fafc;font-family:system-ui;color:#07111f;display:grid;place-items:center;min-height:100vh}.box{background:#07111f;color:#fff;padding:32px;border-radius:16px;width:min(420px,90vw);box-shadow:0 20px 50px #07111f33}input,button{width:100%;padding:13px;margin:8px 0;border-radius:8px;border:1px solid #38506b;box-sizing:border-box}input{background:#10243a;color:#fff}button{background:#09b9e8;border:0;font-weight:900;cursor:pointer}.error{color:#fb7185}.show{display:flex;align-items:center;gap:8px;font-size:13px;color:#c7e8f1;margin:5px 0}.show input{width:auto;margin:0}.back{color:#9beafa}</style></head><body><form class='box notranslate' translate='no' method='post'><h1>Panel privado</h1><p>Streaming Factory</p>{error}<input name='username' placeholder='Usuario' autocomplete='username' autocapitalize='none' spellcheck='false' translate='no' required><input id='password' name='password' type='password' placeholder='Contraseña' autocomplete='current-password' autocapitalize='none' spellcheck='false' translate='no' required><label class='show'><input type='checkbox' onclick="document.getElementById('password').type=this.checked?'text':'password'"> Mostrar contraseña</label><button>Acceder</button><a class='back' href='/'>← Volver al catálogo</a></form></body></html>"""

ADMIN = """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Panel · Streaming Factory</title><style>body{margin:0;background:#f7fafc;font-family:system-ui;color:#07111f}.top{background:#07111f;color:#fff;padding:20px 5%;display:flex;justify-content:space-between}.top a{color:#9beafa}.wrap{max-width:1100px;margin:auto;padding:28px}.panel{background:#fff;border:1px solid #d9e3ec;border-radius:14px;padding:22px;margin-bottom:22px}.form{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.form input,.form select,.form button{padding:12px;border:1px solid #cbd5e1;border-radius:7px;box-sizing:border-box}.form button{background:#09b9e8;border:0;font-weight:900;cursor:pointer}.full{grid-column:1/-1}.table{width:100%;border-collapse:collapse}.table td,.table th{padding:10px;text-align:left;border-bottom:1px solid #e2e8f0}.danger{background:#fee2e2;border:0;border-radius:6px;padding:7px;color:#991b1b;cursor:pointer}@media(max-width:650px){.form{grid-template-columns:1fr}.full{grid-column:auto}}@media(max-width:650px){.top{padding:16px;flex-wrap:wrap;gap:10px}.top b{font-size:13px}.top span{font-size:13px}.wrap{padding:14px}.panel{padding:14px;overflow:hidden}.table{display:block;max-width:100%;overflow-x:auto;white-space:nowrap}.table td,.table th{padding:8px}.edit-form{display:grid;gap:7px;min-width:250px;margin:10px 0;white-space:normal}.edit-form input,.edit-form button{width:100%;box-sizing:border-box;padding:9px}.form{grid-template-columns:1fr}.full{grid-column:auto}}</style></head><body><header class='top'><b>STREAMING FACTORY · ADMIN</b><span><a href='/'>Ver sitio</a> · <a href='/admin/logout'>Salir</a></span></header><main class='wrap'><h1>Gestión de productos</h1><section class='panel'><h2>Nuevo producto</h2><form class='form' method='post' action='/admin/products' enctype='multipart/form-data'><input name='title' placeholder='Título' required><input name='category' placeholder='Categoría' required><input name='description' placeholder='Descripción' required><input name='account_type' placeholder='Tipo de cuenta' required><input name='duration' placeholder='Duración' required><input name='mode' placeholder='Modalidad' required><input name='price' type='number' step='0.01' placeholder='Precio USD' required><input name='stock' type='number' placeholder='Stock' required><label class='full'>Imagen del producto<input name='image' type='file' accept='image/png,image/jpeg,image/webp'></label><button class='full'>Guardar producto</button></form></section><section class='panel'><h2>Productos actuales</h2><table class='table'><tr><th>Producto</th><th>Categoría</th><th>Precio</th><th>Stock</th><th>Acciones</th></tr>PRODUCT_ROWS</table></section></main></body></html>"""

def cloudinary_upload(file):
    cloud = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    if not cloud or not api_key or not api_secret or not file:
        return None
    timestamp = int(time.time())
    folder = 'streaming-factory/products'
    signature_base = 'folder=' + folder + '&timestamp=' + str(timestamp) + api_secret
    signature = hashlib.sha1(signature_base.encode()).hexdigest()
    try:
        response = requests.post('https://api.cloudinary.com/v1_1/' + cloud + '/image/upload', data={'api_key':api_key,'timestamp':timestamp,'folder':folder,'signature':signature}, files={'file':(file.filename,file.stream,file.mimetype)}, timeout=45)
        return response.json().get('secure_url') if response.ok else None
    except (requests.RequestException, ValueError):
        return None

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
    rows = supabase('GET', '/rest/v1/products?order=created_at.desc') or []
    def field(item, name): return html.escape(str(item.get(name, '')), quote=True)
    def row(item):
        product_id = str(item.get('id', ''))
        edit = '<details><summary>Editar</summary><form class="edit-form" method="post" enctype="multipart/form-data" action="/admin/products/edit/' + product_id + '"><input name="title" value="' + field(item, 'title') + '" required><input name="category" value="' + field(item, 'category') + '" required><input name="description" value="' + field(item, 'description') + '" required><input name="account_type" value="' + field(item, 'account_type') + '" required><input name="duration" value="' + field(item, 'duration') + '" required><input name="mode" value="' + field(item, 'mode') + '" required><input name="price" type="number" step="0.01" value="' + field(item, 'price') + '" required><input name="stock" type="number" value="' + field(item, 'stock') + '" required><input name="image" type="file" accept="image/png,image/jpeg,image/webp"><button>Guardar cambios</button></form></details>'
        remove = '<form method="post" action="/admin/products/delete/' + product_id + '"><button class="danger">Eliminar</button></form>'
        return '<tr><td>' + field(item, 'title') + '</td><td>' + field(item, 'category') + '</td><td>USD ' + field(item, 'price') + '</td><td>' + field(item, 'stock') + '</td><td>' + edit + remove + '</td></tr>'
    table = ''.join(row(item) for item in rows)
    notice = session.pop('notice', '')
    page = ADMIN.replace('PRODUCT_ROWS', table or '<tr><td colspan="5">No hay productos en Supabase.</td></tr>')
    return page.replace('<h1>Gestión de productos</h1>', '<h1>Gestión de productos</h1><p>' + html.escape(notice) + '</p>')

def product_data():
    data = {k: request.form.get(k, '') for k in ['title', 'description', 'category', 'account_type', 'duration', 'mode']}
    data.update({'price': float(request.form.get('price', 0)), 'stock': int(request.form.get('stock', 0))})
    image_url = cloudinary_upload(request.files.get('image'))
    if image_url: data['image_url'] = image_url
    return data

@app.post('/admin/products')
def create_product():
    if not logged_in(): return redirect('/admin')
    saved = supabase('POST', '/rest/v1/products', product_data(), admin=True)
    session['notice'] = 'Producto guardado correctamente.' if saved is not None else 'No se pudo guardar. Revisa las claves de Supabase y Cloudinary.'
    return redirect('/admin/dashboard')

@app.post('/admin/products/edit/<product_id>')
def edit_product(product_id):
    if not logged_in(): return redirect('/admin')
    saved = supabase('PATCH', '/rest/v1/products?id=eq.' + product_id, product_data(), admin=True)
    session['notice'] = 'Producto actualizado.' if saved is not None else 'No se pudo actualizar el producto.'
    return redirect('/admin/dashboard')

@app.post('/admin/products/delete/<product_id>')
def delete_product(product_id):
    if not logged_in(): return redirect('/admin')
    removed = supabase('DELETE', '/rest/v1/products?id=eq.' + product_id, admin=True)
    session['notice'] = 'Producto eliminado.' if removed is not None else 'No se pudo eliminar el producto.'
    return redirect('/admin/dashboard')

@app.get('/admin/logout')
def admin_logout():
    session.clear(); return redirect('/admin')

@app.get('/api/health')
def health():
    configured = bool(os.getenv('SUPABASE_URL') and (os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY')))
    result = supabase('GET','/rest/v1/site_settings?select=id&limit=1') if configured else None
    return jsonify({'status':'ok','supabase':result is not None}),200

def keepalive_loop():
    url = os.getenv('PUBLIC_APP_URL', 'https://streaming-factory.onrender.com').rstrip('/') + '/api/health'
    while True:
        try:
            requests.get(url, timeout=45)
        except requests.RequestException:
            pass
        time.sleep(840)

if os.getenv('ENABLE_KEEPALIVE', 'true').lower() == 'true':
    threading.Thread(target=keepalive_loop, daemon=True).start()

if __name__ == '__main__': app.run(host='0.0.0.0',port=int(os.getenv('PORT',5000)))
