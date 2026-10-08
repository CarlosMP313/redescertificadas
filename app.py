from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
import sqlite3, os
BASE=Path(__file__).resolve().parent; DB=BASE/'instance'/'redcer.db'; UP=BASE/'static/images/uploads'; UP.mkdir(parents=True,exist_ok=True)
app=Flask(__name__); app.secret_key=os.environ.get('REDCER_SECRET_KEY','REDCER-V2-CHANGE-ME'); app.config['MAX_CONTENT_LENGTH']=30*1024*1024
IMG={'jpg','jpeg','png','webp','gif'}; VIDEO={'mp4','webm','mov'}

SERVICE_NAMES = [
    'Detección de incendio', 'Control de acceso', 'Seguridad Física', 'Seguridad Lógica',
    'Enfriamiento', 'Confort', 'Precisión', 'Paneles fotovoltaicos', 'Plantas de emergencia',
    'Sistemas de alimentación ininterrumpida (UPS)', 'Redes Eléctricas', 'Iluminación',
    'Tierras físicas y pararrayos', 'Video vigilancia', 'Domótica', 'Networking', 'Cableado estructurado'
]
SCHEMA='''
CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1),company_name TEXT,phone TEXT,email TEXT,address TEXT,schedule TEXT,hero_title TEXT,hero_highlight TEXT,hero_description TEXT,home_media TEXT,home_media_type TEXT DEFAULT 'image',home_media_enabled INTEGER DEFAULT 1,about_title TEXT,about_text TEXT,mission TEXT,vision TEXT,history TEXT,experience TEXT,about_media TEXT,about_media_type TEXT DEFAULT 'image',about_media_enabled INTEGER DEFAULT 1,team_enabled INTEGER DEFAULT 1,team_text TEXT,cert_title TEXT,cert_text TEXT,cert_media TEXT,cert_media_type TEXT DEFAULT 'image',cert_media_enabled INTEGER DEFAULT 1,contact_title TEXT,contact_text TEXT,contact_media TEXT,contact_media_type TEXT DEFAULT 'image',contact_media_enabled INTEGER DEFAULT 1,footer_text TEXT,social_enabled INTEGER DEFAULT 1,social_facebook TEXT,social_instagram TEXT,social_linkedin TEXT,social_youtube TEXT,social_tiktok TEXT,reviews_enabled INTEGER DEFAULT 1,site_logo TEXT,logo_header_width INTEGER DEFAULT 340,logo_header_height INTEGER DEFAULT 100,logo_footer_width INTEGER DEFAULT 220,logo_fit TEXT DEFAULT 'contain');
CREATE TABLE IF NOT EXISTS services(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,description TEXT,icon TEXT,image TEXT,media_type TEXT DEFAULT 'image',active INTEGER DEFAULT 1,sort_order INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,description TEXT,logo TEXT,photo TEXT,active INTEGER DEFAULT 1,sort_order INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS certifications(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,media TEXT,media_type TEXT DEFAULT 'image',active INTEGER DEFAULT 1,sort_order INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS team(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,position TEXT,bio TEXT,photo TEXT,active INTEGER DEFAULT 1,sort_order INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,company TEXT,comment TEXT,rating INTEGER DEFAULT 5,active INTEGER DEFAULT 1,created_at TEXT);
CREATE TABLE IF NOT EXISTS quotes(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,email TEXT,phone TEXT,service TEXT,message TEXT,status TEXT DEFAULT 'Nueva',created_at TEXT);
CREATE TABLE IF NOT EXISTS admins(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,password_hash TEXT);
CREATE TABLE IF NOT EXISTS site_stats(id INTEGER PRIMARY KEY CHECK(id=1),visit_count INTEGER DEFAULT 0);
'''
def db():
 c=sqlite3.connect(DB,timeout=10); c.row_factory=sqlite3.Row; return c
def init_db():
 DB.parent.mkdir(exist_ok=True); c=db(); c.executescript(SCHEMA)
 # Migration: add any fields introduced in V2.2 to an existing V2 database.
 cols={r[1] for r in c.execute('pragma table_info(settings)').fetchall()}
 newcols={
  'home_media':'TEXT','home_media_type':"TEXT DEFAULT 'image'",'home_media_enabled':'INTEGER DEFAULT 1',
  'about_title':'TEXT','about_text':'TEXT','mission':'TEXT','vision':'TEXT','history':'TEXT','experience':'TEXT','team_text':'TEXT','about_media':'TEXT','about_media_type':"TEXT DEFAULT 'image'",'about_media_enabled':'INTEGER DEFAULT 1','team_enabled':'INTEGER DEFAULT 1',
  'cert_title':'TEXT','cert_text':'TEXT','cert_media':'TEXT','cert_media_type':"TEXT DEFAULT 'image'",'cert_media_enabled':'INTEGER DEFAULT 1',
  'contact_title':'TEXT','contact_text':'TEXT','contact_media':'TEXT','contact_media_type':"TEXT DEFAULT 'image'",'contact_media_enabled':'INTEGER DEFAULT 1','footer_text':'TEXT','social_enabled':'INTEGER DEFAULT 1','social_facebook':'TEXT','social_instagram':'TEXT','social_linkedin':'TEXT','social_youtube':'TEXT','social_tiktok':'TEXT','reviews_enabled':'INTEGER DEFAULT 1','site_logo':'TEXT','logo_header_width':'INTEGER DEFAULT 340','logo_header_height':'INTEGER DEFAULT 100','logo_footer_width':'INTEGER DEFAULT 220','logo_fit':"TEXT DEFAULT 'contain'"}
 for name,typ in newcols.items():
  if name not in cols: c.execute(f'ALTER TABLE settings ADD COLUMN {name} {typ}')
 scols={r[1] for r in c.execute('pragma table_info(services)').fetchall()}
 for name,typ in {'image':'TEXT','media_type':"TEXT DEFAULT 'image'"}.items():
  if name not in scols: c.execute(f'ALTER TABLE services ADD COLUMN {name} {typ}')
 c.execute("UPDATE settings SET about_title=COALESCE(about_title,'Conectamos infraestructura con confianza.'), about_text=COALESCE(about_text,'Somos una empresa especializada en soluciones integrales para infraestructura tecnológica, eléctrica y de seguridad.'), mission=COALESCE(mission,'Proporcionar soluciones confiables e innovadoras que ayuden a nuestros clientes a operar de forma segura, eficiente y continua.'), vision=COALESCE(vision,'Ser un referente nacional en integración de infraestructura, tecnología y servicios especializados.'), history=COALESCE(history,'Nuestros comienzos se construyeron con proyectos de telecomunicaciones e infraestructura. Con el tiempo ampliamos nuestras capacidades para atender proyectos empresariales e industriales.'), experience=COALESCE(experience,'15+ años de experiencia'), team_text=COALESCE(team_text,'Nuestro equipo reúne especialistas técnicos y profesionales comprometidos con la calidad de cada proyecto.'), cert_title=COALESCE(cert_title,'Capacitación, estándares y compromiso'), cert_text=COALESCE(cert_text,'Promovemos la capacitación continua de nuestro personal y el cumplimiento de estándares, lineamientos de seguridad y buenas prácticas aplicables a cada especialidad.'), contact_title=COALESCE(contact_title,'Hablemos de tu proyecto'), contact_text=COALESCE(contact_text,'Cuéntanos tus requerimientos y prepararemos una propuesta a la medida. Solicita que un asesor se contacte contigo en un clic.'), footer_text=COALESCE(footer_text,'Soluciones profesionales en infraestructura tecnológica, eléctrica y de seguridad. Calidad, seguridad y continuidad para nuestros clientes.') WHERE id=1")
 defaults={'company_name':'REDES CERTIFICADAS S.A. DE C.V.','phone':'+52 443 123 4567','email':'ventas@redcer.mx','address':'Morelia, Michoacán, México','schedule':'Lunes a Viernes 8:00 am - 6:00 pm | Sábado 9:00 am - 1:00 pm','hero_title':'INFRAESTRUCTURA QUE','hero_highlight':'CONECTA TU FUTURO','hero_description':'Diseñamos e implementamos soluciones de infraestructura tecnológica, eléctrica y de seguridad con calidad, continuidad y alto desempeño.','about_title':'Conectamos infraestructura con confianza.','about_text':'Somos una empresa especializada en soluciones integrales para infraestructura tecnológica, eléctrica, seguridad y continuidad operativa.','mission':'Proporcionar soluciones confiables e innovadoras que ayuden a nuestros clientes a operar de forma segura, eficiente y continua.','vision':'Ser un referente nacional en integración de infraestructura, tecnología y servicios especializados.','history':'Nuestros comienzos se construyeron con proyectos de telecomunicaciones e infraestructura. Con el tiempo ampliamos nuestras capacidades para atender proyectos empresariales e industriales.','experience':'15+ años de experiencia','team_text':'Nuestro equipo reúne especialistas técnicos y profesionales comprometidos con la calidad de cada proyecto.','cert_title':'Capacitación, estándares y compromiso','cert_text':'Promovemos la capacitación continua de nuestro personal y el cumplimiento de estándares, lineamientos de seguridad y buenas prácticas aplicables a cada especialidad.','contact_title':'Hablemos de tu proyecto','contact_text':'Cuéntanos tus requerimientos y prepararemos una propuesta a la medida. Solicita que un asesor se contacte contigo en un clic.','footer_text':'Soluciones profesionales en infraestructura tecnológica, eléctrica y de seguridad. Calidad, seguridad y continuidad para nuestros clientes.'}
 if c.execute('select count(*) from settings').fetchone()[0]==0:
  cols=['company_name','phone','email','address','schedule','hero_title','hero_highlight','hero_description','about_title','about_text','mission','vision','history','experience','team_text','cert_title','cert_text','contact_title','contact_text','footer_text']; c.execute('insert into settings(id,'+','.join(cols)+') values(1,'+','.join('?'*len(cols))+')',[defaults[x] for x in cols])
 if c.execute('select count(*) from services').fetchone()[0]==0:
  c.executemany('insert into services(title,description,icon,sort_order) values(?,?,?,?)',[(n,'Soluciones profesionales diseñadas para las necesidades de cada proyecto.','◈',i) for i,n in enumerate(SERVICE_NAMES,1)])
 # Ensure the requested REDCER service catalog exists in existing installations too.
 desired=SERVICE_NAMES
 existing={r[0] for r in c.execute('select title from services').fetchall()}
 for i,n in enumerate(desired,1):
  if n not in existing:
   c.execute('insert into services(title,description,icon,sort_order,active) values(?,?,?,?,1)',(n,'Soluciones profesionales diseñadas para las necesidades de cada proyecto.','◈',i))
 if c.execute('select count(*) from admins').fetchone()[0]==0: c.execute('insert into admins(username,password_hash) values(?,?)',('admin',generate_password_hash('REDCER2026!')))
 if c.execute('select count(*) from site_stats').fetchone()[0]==0: c.execute('insert into site_stats(id,visit_count) values(1,0)')
 c.commit(); c.close()
def guard(): return None if session.get('admin_id') else redirect(url_for('login',next=request.path))
def upload(f, kinds=IMG):
 if not f or not f.filename:return ''
 ext=Path(f.filename).suffix.lower().lstrip('.');
 if ext not in kinds: raise ValueError('Formato no permitido.')
 name=secure_filename(Path(f.filename).stem) or 'archivo'; fn=f'{name}_{datetime.now().strftime("%Y%m%d%H%M%S%f")}.{ext}'; f.save(UP/fn); return 'uploads/'+fn
@app.context_processor
def common():
 c=db(); s=c.execute('select * from settings where id=1').fetchone(); stats=c.execute('select visit_count from site_stats where id=1').fetchone(); c.close(); return {'settings':s,'visit_count':(stats['visit_count'] if stats else 0)}

@app.before_request
def count_public_visit():
 # Cuenta una entrada por sesión del visitante y evita contar rutas administrativas o archivos estáticos.
 if request.endpoint in {'home','nosotros','servicios','certificaciones','clientes','contacto'} and not session.get('visitor_counted'):
  c=db(); c.execute('update site_stats set visit_count=visit_count+1 where id=1'); c.commit(); c.close(); session['visitor_counted']=True
# public
@app.get('/')
def home():
 c=db(); services=c.execute('select * from services where active=1 order by sort_order,id').fetchall(); clients=c.execute('select * from clients where active=1 order by sort_order,id').fetchall(); c.close(); return render_template('index.html',services=services,clients=clients)
@app.get('/nosotros')
def nosotros():
 c=db(); team=c.execute('select * from team where active=1 order by sort_order,id').fetchall(); c.close(); return render_template('nosotros.html',team=team)
@app.get('/servicios')
def servicios():
 c=db(); rows=c.execute('select * from services where active=1 order by sort_order,id').fetchall(); c.close(); return render_template('servicios.html',services=rows)
@app.get('/certificaciones')
def certificaciones():
 c=db(); rows=c.execute('select * from certifications where active=1 order by sort_order,id').fetchall(); c.close(); return render_template('certificaciones.html',certifications=rows)
@app.get('/clientes')
def clientes():
 c=db(); rows=c.execute('select * from clients where active=1 order by sort_order,id').fetchall(); c.close(); return render_template('clientes.html',clients=rows)
@app.route('/contacto',methods=['GET','POST'])
def contacto():
 if request.method=='POST':
  f=request.form
  if not f.get('nombre') or not f.get('correo') or not f.get('mensaje'): flash('Completa nombre, correo y mensaje.','error'); return redirect(url_for('contacto'))
  c=db(); c.execute('insert into quotes(name,email,phone,service,message,created_at) values(?,?,?,?,?,?)',(f.get('nombre','').strip(),f.get('correo','').strip(),f.get('telefono','').strip(),f.get('servicio','').strip(),f.get('mensaje','').strip(),datetime.now().strftime('%Y-%m-%d %H:%M:%S'))); c.commit(); c.close(); flash('Solicitud enviada correctamente.','success'); return redirect(url_for('contacto'))
 c=db(); services=c.execute('select * from services where active=1 order by sort_order,id').fetchall(); reviews=c.execute('select * from reviews where active=1 order by id desc').fetchall(); c.close(); return render_template('contacto.html',services=services,reviews=reviews)
# admin auth
@app.route('/admin/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  c=db(); a=c.execute('select * from admins where username=?',(request.form.get('username','').strip(),)).fetchone(); c.close()
  if a and check_password_hash(a['password_hash'],request.form.get('password','')): session.clear(); session['admin_id']=a['id']; session['admin_user']=a['username']; return redirect(url_for('dashboard'))
  flash('Usuario o contraseña incorrectos.','error')
 return render_template('admin/login.html')
@app.get('/admin/logout')
def logout(): session.clear(); return redirect(url_for('login'))
@app.post('/contacto/recomendacion')
def submit_review():
 c=db()
 try:
  setting=c.execute('select reviews_enabled from settings where id=1').fetchone()
  if not setting or not setting['reviews_enabled']:
   flash('La sección de recomendaciones no está disponible en este momento.','error')
   return redirect(url_for('contacto')+'#recomendaciones')
  name=request.form.get('name','').strip()
  company=request.form.get('company','').strip()
  comment=request.form.get('comment','').strip()
  try: rating=max(1,min(5,int(request.form.get('rating',5))))
  except (TypeError,ValueError): rating=5
  if not name or not comment:
   flash('Escribe tu nombre y tu comentario para enviar la recomendación.','error')
  else:
   c.execute('insert into reviews(name,company,comment,rating,active,created_at) values(?,?,?,?,1,?)',(name,company,comment,rating,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
   c.commit()
   flash('Gracias por compartir tu experiencia con REDCER. Tu recomendación fue enviada correctamente.','success')
 finally:
  c.close()
 return redirect(url_for('contacto')+'#recomendaciones')

@app.get('/admin')
def dashboard():
 g=guard();
 if g:return g
 c=db(); counts={x:c.execute('select count(*) from '+x).fetchone()[0] for x in ['services','clients','certifications','team','reviews','quotes']}; counts['visitas']=c.execute('select visit_count from site_stats where id=1').fetchone()[0]; recent=c.execute('select * from quotes order by id desc limit 10').fetchall(); c.close(); return render_template('admin/dashboard.html',counts=counts,recent=recent)
@app.route('/admin/settings',methods=['GET','POST'])
def settings_admin():
 g=guard();
 if g:return g
 c=db()
 if request.method=='POST':
  try:
   data={k:request.form.get(k,'').strip() for k in ['company_name','phone','email','address','schedule','hero_title','hero_highlight','hero_description','about_title','about_text','mission','vision','history','experience','team_text','cert_title','cert_text','contact_title','contact_text','footer_text','social_facebook','social_instagram','social_linkedin','social_youtube','social_tiktok']}
   checks=['home_media_enabled','about_media_enabled','team_enabled','cert_media_enabled','contact_media_enabled','social_enabled','reviews_enabled']; data.update({k:1 if request.form.get(k)=='1' else 0 for k in checks})
   for prefix in ['home','about','cert','contact']:
    f=request.files.get(prefix+'_media'); current=c.execute('select '+prefix+'_media,'+prefix+'_media_type from settings where id=1').fetchone(); val=upload(f,IMG|VIDEO) if f and f.filename else current[0]; typ=('video' if val and Path(val).suffix.lower().lstrip('.') in VIDEO else 'image') if val else current[1]; data[prefix+'_media']=val; data[prefix+'_media_type']=typ
   fields=list(data); c.execute('update settings set '+','.join(f'{x}=?' for x in fields)+' where id=1',[data[x] for x in fields]); c.commit(); flash('Configuración guardada correctamente.','success')
  except Exception as e: c.rollback(); flash('No se pudo guardar: '+str(e),'error')
 s=c.execute('select * from settings where id=1').fetchone(); c.close(); return render_template('admin/settings.html',s=s)
# Administración de identidad visual y logos
@app.route('/admin/logos',methods=['GET','POST'])
def logos_admin():
 g=guard()
 if g:return g
 c=db()
 if request.method=='POST':
  try:
   current=c.execute('select * from settings where id=1').fetchone()
   f=request.files.get('site_logo')
   logo=upload(f,IMG) if f and f.filename else current['site_logo']
   if request.form.get('reset_logo')=='1': logo=None
   def limit(name,default,low,high):
    try:return max(low,min(high,int(request.form.get(name,default))))
    except:return default
   hw=limit('logo_header_width',340,120,900)
   hh=limit('logo_header_height',100,40,300)
   fw=limit('logo_footer_width',220,100,900)
   fit=request.form.get('logo_fit','contain')
   if fit not in ('contain','cover'): fit='contain'
   c.execute('update settings set site_logo=?,logo_header_width=?,logo_header_height=?,logo_footer_width=?,logo_fit=? where id=1',(logo,hw,hh,fw,fit))
   c.commit(); flash('Configuración de logos guardada correctamente.','success')
  except Exception as e:
   c.rollback(); flash('No se pudo guardar el logo: '+str(e),'error')
  return redirect(url_for('logos_admin'))
 srow=c.execute('select * from settings where id=1').fetchone(); c.close()
 return render_template('admin/logos.html',s=srow)

# generic CRUD
@app.route('/admin/services',methods=['GET','POST'])
def services_admin():
 g=guard();
 if g:return g
 c=db()
 if request.method=='POST': c.execute('insert into services(title,description,icon,image,media_type,sort_order) values(?,?,?,?,?,?)',(request.form['title'].strip(),request.form['description'].strip(),request.form.get('icon','◈'),upload(request.files.get('image'),IMG|VIDEO),('video' if request.files.get('image') and Path(request.files['image'].filename).suffix.lower().lstrip('.') in VIDEO else 'image'),int(request.form.get('sort_order',0)))); c.commit(); flash('Servicio guardado.','success'); return redirect(url_for('services_admin'))
 rows=c.execute('select * from services order by sort_order,id').fetchall(); c.close(); return render_template('admin/services.html',rows=rows)
@app.post('/admin/services/<int:id>/edit')
def service_edit(id):
 g=guard();
 if g:return g
 c=db(); old=c.execute('select image from services where id=?',(id,)).fetchone(); f=request.files.get('image'); img=upload(f,IMG|VIDEO) if f and f.filename else old['image']; typ='video' if img and Path(img).suffix.lower().lstrip('.') in VIDEO else 'image'; c.execute('update services set title=?,description=?,icon=?,image=?,media_type=?,active=?,sort_order=? where id=?',(request.form['title'],request.form['description'],request.form.get('icon','◈'),img,typ,int(request.form.get('active',1)),int(request.form.get('sort_order',0)),id)); c.commit(); c.close(); flash('Servicio actualizado.','success'); return redirect(url_for('services_admin'))
@app.post('/admin/services/<int:id>/delete')
def service_delete(id):
 g=guard();
 if g:return g
 c=db(); c.execute('delete from services where id=?',(id,)); c.commit(); c.close(); return redirect(url_for('services_admin'))
@app.route('/admin/clients',methods=['GET','POST'])
def clients_admin():
 g=guard();
 if g:return g
 c=db()
 if request.method=='POST': c.execute('insert into clients(name,description,logo,photo,sort_order) values(?,?,?,?,?)',(request.form['name'],request.form.get('description',''),upload(request.files.get('logo'),IMG),upload(request.files.get('photo'),IMG),int(request.form.get('sort_order',0)))); c.commit(); flash('Cliente guardado.','success'); return redirect(url_for('clients_admin'))
 rows=c.execute('select * from clients order by sort_order,id').fetchall(); c.close(); return render_template('admin/clients.html',rows=rows)
@app.post('/admin/clients/<int:id>/edit')
def client_edit(id):
 g=guard();
 if g:return g
 c=db(); old=c.execute('select * from clients where id=?',(id,)).fetchone(); logo=upload(request.files.get('logo'),IMG) or old['logo']; photo=upload(request.files.get('photo'),IMG) or old['photo']; c.execute('update clients set name=?,description=?,logo=?,photo=?,active=?,sort_order=? where id=?',(request.form['name'],request.form.get('description',''),logo,photo,int(request.form.get('active',1)),int(request.form.get('sort_order',0)),id)); c.commit(); c.close(); flash('Cliente actualizado.','success'); return redirect(url_for('clients_admin'))
@app.post('/admin/clients/<int:id>/delete')
def client_delete(id):
 g=guard();
 if g:return g
 c=db(); c.execute('delete from clients where id=?',(id,)); c.commit(); c.close(); return redirect(url_for('clients_admin'))
@app.route('/admin/certificaciones',methods=['GET','POST'])
def cert_admin():
 g=guard();
 if g:return g
 c=db()
 if request.method=='POST':
  f=request.files.get('media'); val=upload(f,IMG|VIDEO); typ='video' if f and Path(f.filename).suffix.lower().lstrip('.') in VIDEO else 'image'; c.execute('insert into certifications(name,media,media_type,sort_order) values(?,?,?,?)',(request.form['name'],val,typ,int(request.form.get('sort_order',0)))); c.commit(); flash('Certificación guardada.','success'); return redirect(url_for('cert_admin'))
 rows=c.execute('select * from certifications order by sort_order,id').fetchall(); c.close(); return render_template('admin/certificaciones.html',rows=rows)
@app.post('/admin/certificaciones/<int:id>/delete')
def cert_delete(id):
 g=guard();
 if g:return g
 c=db(); c.execute('delete from certifications where id=?',(id,)); c.commit(); c.close(); return redirect(url_for('cert_admin'))
@app.route('/admin/team',methods=['GET','POST'])
def team_admin():
 g=guard();
 if g:return g
 c=db()
 if request.method=='POST': c.execute('insert into team(name,position,bio,photo,sort_order) values(?,?,?,?,?)',(request.form['name'],request.form.get('position',''),request.form.get('bio',''),upload(request.files.get('photo'),IMG),int(request.form.get('sort_order',0)))); c.commit(); flash('Personal guardado.','success'); return redirect(url_for('team_admin'))
 rows=c.execute('select * from team order by sort_order,id').fetchall(); c.close(); return render_template('admin/team.html',rows=rows)
@app.post('/admin/team/<int:id>/delete')
def team_delete(id):
 g=guard();
 if g:return g
 c=db(); c.execute('delete from team where id=?',(id,)); c.commit(); c.close(); return redirect(url_for('team_admin'))
@app.route('/admin/reviews',methods=['GET','POST'])
def reviews_admin():
 g=guard();
 if g:return g
 c=db()
 if request.method=='POST': c.execute('insert into reviews(name,company,comment,rating,created_at) values(?,?,?,?,?)',(request.form['name'],request.form.get('company',''),request.form['comment'],int(request.form.get('rating',5)),datetime.now().strftime('%Y-%m-%d'))); c.commit(); flash('Recomendación guardada.','success'); return redirect(url_for('reviews_admin'))
 rows=c.execute('select * from reviews order by id desc').fetchall(); c.close(); return render_template('admin/reviews.html',rows=rows)
@app.post('/admin/reviews/<int:id>/edit')
def review_edit(id):
 g=guard();
 if g:return g
 c=db(); c.execute('update reviews set name=?,company=?,comment=?,rating=?,active=? where id=?',(request.form['name'].strip(),request.form.get('company','').strip(),request.form['comment'].strip(),max(1,min(5,int(request.form.get('rating',5)))),int(request.form.get('active',1)),id)); c.commit(); c.close(); flash('Recomendación actualizada.','success'); return redirect(url_for('reviews_admin'))
@app.post('/admin/reviews/<int:id>/delete')
def review_delete(id):
 g=guard();
 if g:return g
 c=db(); c.execute('delete from reviews where id=?',(id,)); c.commit(); c.close(); return redirect(url_for('reviews_admin'))
@app.get('/admin/quotes')
def quotes_admin():
 g=guard();
 if g:return g
 c=db(); rows=c.execute('select * from quotes order by id desc').fetchall(); c.close(); return render_template('admin/quotes.html',rows=rows)
@app.post('/admin/quotes/<int:id>/status')
def quote_status(id):
 g=guard();
 if g:return g
 c=db(); c.execute('update quotes set status=? where id=?',(request.form.get('status','Nueva'),id)); c.commit(); c.close(); return redirect(url_for('quotes_admin'))
@app.route('/admin/password',methods=['GET','POST'])
def password_admin():
 g=guard();
 if g:return g
 if request.method=='POST':
  p=request.form.get('password','');
  if len(p)<8: flash('Mínimo 8 caracteres.','error')
  else:
   c=db(); c.execute('update admins set password_hash=? where id=?',(generate_password_hash(p),session['admin_id'])); c.commit(); c.close(); flash('Contraseña actualizada.','success')
 return render_template('admin/password.html')
if __name__=='__main__': init_db(); app.run(host='127.0.0.1',port=5000,debug=False)
