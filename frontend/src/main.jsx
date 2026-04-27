import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes, Link } from "react-router-dom";
import { BrowserMultiFormatReader } from "@zxing/browser";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import * as XLSX from "xlsx";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://3.88.51.188:8000/api/v1";
const tok = () => localStorage.getItem("token") || "";
const usr = () => {
  try {
    return JSON.parse(localStorage.getItem("user") || "null");
  } catch {
    return null;
  }
};
const roleUsers = () => {
  try {
    return JSON.parse(localStorage.getItem("role_users") || "[]");
  } catch {
    return [];
  }
};

const ROLE_PERMISSIONS = {
  admin: ["dashboard", "leer", "crear", "editar", "eliminar", "importar", "exportar", "firma", "etiquetas", "backups", "roles"],
  supervisor: ["dashboard", "leer", "crear", "editar", "importar", "exportar", "firma", "etiquetas"],
  operator: ["leer", "crear", "exportar", "etiquetas"],
};

const AREAS = {
  sonido: ["Consola", "Micrófonos", "Monitores", "Cableado"],
  iluminacion: ["Cabeza móvil", "Par LED", "Control DMX", "Strobo"],
  pantalla: ["LED Wall", "Proyector", "Switcher", "Procesador"],
  layher: ["Truss", "Torre", "Plataforma", "Accesorios"],
};

async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(tok() ? { Authorization: `Bearer ${tok()}` } : {}),
    },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function can(permission) {
  const user = usr();
  const ids = [user?.name, user?.full_name, user?.username, user?.email, user?.id]
    .filter(Boolean)
    .map((v) => String(v).trim().toLowerCase());
  const localOverride = roleUsers().find((entry) => ids.includes(String(entry?.name || "").trim().toLowerCase()));
  const effectiveRole = localOverride?.role || user?.role;
  const base = ROLE_PERMISSIONS[effectiveRole] || [];
  const custom = [...(user?.permissions || []), ...(localOverride?.permissions || [])];
  return [...new Set([...base, ...custom])].includes(permission);
}

function DescriptionCard({ title, description }) {
  return (
    <div className="card description-card">
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function ThemeToggle() {
  const [theme, setTheme] = React.useState(localStorage.getItem("theme") || "oscuro");
  React.useEffect(() => {
    document.body.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);
  return (
    <button type="button" onClick={() => setTheme(theme === "oscuro" ? "claro" : "oscuro")}>Modo {theme === "oscuro" ? "claro" : "oscuro"}</button>
  );
}

function Shell({ title, children }) {
  const u = usr();
  return (
    <div className="app">
      <aside>
        <h2>Stock Pro PGR</h2>
        <p>{u?.full_name} · rol: {u?.role}</p>
        <nav>
          {can("dashboard") && <Link to={u?.role === "admin" ? "/admin" : "/operator"}>Dashboard</Link>}
          <Link to={u?.role === "admin" ? "/admin/scanner" : "/operator/scanner"}>Escáner QR</Link>
          <Link to={u?.role === "admin" ? "/admin/items" : "/operator/items"}>Equipos</Link>
          <Link to={u?.role === "admin" ? "/admin/events" : "/operator/events"}>Eventos</Link>
          <Link to={u?.role === "admin" ? "/admin/checklists" : "/operator/checklists"}>Checklists</Link>
          {u?.role === "admin" && <Link to="/admin/clients">Clientes</Link>}
          {u?.role === "admin" && can("firma") && <Link to="/admin/contracts">Contratos con firma</Link>}
          {u?.role === "admin" && can("roles") && <Link to="/admin/roles">Roles y permisos</Link>}
          {u?.role === "admin" && can("backups") && <Link to="/admin/backups">Backups</Link>}
          <ThemeToggle />
          <a onClick={() => { localStorage.clear(); location.href = "/login"; }}>Salir</a>
        </nav>
      </aside>
      <main><h1>{title}</h1>{children}</main>
      <div className="bottom">
        <Link to={u?.role === "admin" ? "/admin" : "/operator"}>Inicio</Link>
        <Link to={u?.role === "admin" ? "/admin/scanner" : "/operator/scanner"}>QR</Link>
        <Link to={u?.role === "admin" ? "/admin/items" : "/operator/items"}>Equipos</Link>
        <Link to={u?.role === "admin" ? "/admin/events" : "/operator/events"}>Eventos</Link>
      </div>
    </div>
  );
}

function Login() {
  async function sub(e) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const t = await api("/auth/login", { method: "POST", body: JSON.stringify({ username: f.get("username"), password: f.get("password") }) });
    localStorage.setItem("token", t.access_token);
    const me = await api("/auth/me");
    localStorage.setItem("user", JSON.stringify(me));
    location.href = me.role === "admin" ? "/admin" : "/operator";
  }
  return <div className="login"><form className="card" onSubmit={sub}><h1>Stock Control Pro</h1><input name="username" defaultValue="admin" /><input name="password" type="password" defaultValue="admin1234" /><button>Entrar</button></form></div>;
}

function P({ admin = false, permission, children }) {
  const u = usr();
  if (!tok() || !u) return <Navigate to="/login" />;
  if (admin && u.role !== "admin") return <Navigate to="/operator" />;
  if (permission && !can(permission)) return <div className="card"><h3>Sin permiso</h3><p>Tu rol actual no tiene permisos para esta función.</p></div>;
  return children;
}

function Innovations() {
  const quick = [
    { t: "Modo oscuro/claro", d: "Cambia la apariencia completa para trabajo de día o noche." },
    { t: "Importación masiva", d: "Carga datos desde Excel/CSV para acelerar operaciones." },
    { t: "Firma digital", d: "Firma contratos desde pantalla y guarda evidencia." },
    { t: "Permisos granulares", d: "Controla exactamente qué puede hacer cada rol." },
    { t: "Etiquetas QR/Barras", d: "Genera e imprime identificación para cada equipo nuevo." },
  ];
  return <div className="card innovation"><h3>Innovaciones activas</h3><div className="innovation-grid">{quick.map((q) => <div key={q.t} className="innovation-item"><b>{q.t}</b><span>{q.d}</span></div>)}</div></div>;
}

function AdminDash() {
  const [s, setS] = React.useState(null);
  React.useEffect(() => { api("/dashboard/admin").then(setS); }, []);
  const data = s ? [{ n: "Disponibles", v: s.available_items }, { n: "En uso", v: s.in_use_items }, { n: "Mantenimiento", v: s.maintenance_items }, { n: "Eventos", v: s.active_events }] : [];
  return <P admin permission="dashboard"><Shell title="Dashboard administrativo"><DescriptionCard title="Descripción de esta función" description="Aquí visualizas métricas clave para tomar decisiones rápidas de operación y mantenimiento." />{!s ? <div className="card">Cargando...</div> : <><div className="stats">{["clients", "items", "active_events", "checklists_pending", "contracts", "backups"].map((k) => <div className="stat" key={k}><b>{s[k]}</b><span>{k}</span></div>)}</div><div className="card"><ResponsiveContainer width="100%" height={250}><BarChart data={data}><XAxis dataKey="n" /><YAxis /><Tooltip /><Bar dataKey="v" /></BarChart></ResponsiveContainer></div></>}</Shell></P>;
}

function Scanner({ admin = false }) {
  const [item, setItem] = React.useState(null);
  const [err, setErr] = React.useState("");
  const v = React.useRef(null);
  async function lookup(code) {
    try { setItem(await api("/items/scan/" + encodeURIComponent(code))); setErr(""); }
    catch { setErr("No encontrado: " + code); setItem(null); }
  }
  async function start() {
    try {
      const r = new BrowserMultiFormatReader();
      await r.decodeFromVideoDevice(undefined, v.current, (res, e, ctrl) => {
        if (res) lookup(res.getText());
        if (res && ctrl) ctrl.stop();
      });
    } catch {
      setErr("No se pudo abrir cámara. Requiere HTTPS o app móvil.");
    }
  }
  return <P admin={admin}><Shell title="Escáner QR"><DescriptionCard title="Descripción de esta función" description="Escanea un código QR o escribe el código manual para encontrar el equipo en segundos." /><div className="grid"><div className="card"><video ref={v} /><button onClick={start}>Abrir cámara</button><input placeholder="Código manual + Enter" onKeyDown={(e) => e.key === "Enter" && lookup(e.currentTarget.value)} />{err && <p className="err">{err}</p>}</div><div className="card"><pre>{item ? JSON.stringify(item, null, 2) : "Sin lectura"}</pre></div></div></Shell></P>;
}

function RolesManager() {
  const [users, setUsers] = React.useState(() => {
    try { return JSON.parse(localStorage.getItem("role_users") || "[]"); } catch { return []; }
  });
  const [name, setName] = React.useState("");
  const [role, setRole] = React.useState("operator");
  const [perms, setPerms] = React.useState([]);
  const all = [...new Set(Object.values(ROLE_PERMISSIONS).flat())];
  function save() {
    const next = [{ name, role, permissions: perms }, ...users];
    setUsers(next);
    localStorage.setItem("role_users", JSON.stringify(next));
    setName(""); setRole("operator"); setPerms([]);
  }
  function togglePerm(p) { setPerms((prev) => prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]); }
  return <P admin permission="roles"><Shell title="Roles y permisos granulares"><DescriptionCard title="Descripción de esta función" description="Define permisos detallados por usuario para controlar lectura, creación, importación, firma y más." /><div className="grid"><div className="card"><input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nombre del usuario" /><select value={role} onChange={(e) => setRole(e.target.value)}><option value="operator">Operador</option><option value="supervisor">Supervisor</option><option value="admin">Administrador</option></select><p>Permisos adicionales:</p><div className="checks">{all.map((p) => <label key={p}><input type="checkbox" checked={perms.includes(p)} onChange={() => togglePerm(p)} />{p}</label>)}</div><button type="button" onClick={save}>Guardar permisos</button></div><div className="card">{users.map((u, i) => <pre key={i}>{JSON.stringify(u, null, 2)}</pre>)}</div></div></Shell></P>;
}

function generateLabelSVG(item) {
  const code = item.code || "SIN-CODIGO";
  const qrPayload = `${code}|${item.name || "equipo"}|${item.category || "general"}`;
  const bars = Array.from(code).map((ch, i) => `<rect x='${20 + i * 6}' y='130' width='${(ch.charCodeAt(0) % 3) + 2}' height='80' fill='black'/>`).join("");
  const hash = Array.from(qrPayload).reduce((a, c) => a + c.charCodeAt(0), 0);
  let squares = "";
  for (let y = 0; y < 10; y++) {
    for (let x = 0; x < 10; x++) {
      if (((x * y + hash + x + y) % 3) === 0) squares += `<rect x='${340 + x * 10}' y='${80 + y * 10}' width='9' height='9' fill='black'/>`;
    }
  }
  return `data:image/svg+xml;utf8,${encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' width='500' height='250'><rect width='100%' height='100%' fill='white'/><text x='20' y='40' font-size='22' font-family='Arial'>PGR - ${item.name || "Equipo"}</text><text x='20' y='70' font-size='15' font-family='Arial'>Código: ${code}</text><text x='20' y='95' font-size='15' font-family='Arial'>Categoría: ${item.category || "general"}</text>${bars}<rect x='330' y='70' width='120' height='120' fill='none' stroke='black'/>${squares}<text x='330' y='210' font-size='12'>QR interno</text></svg>`)}`;
}

function SignaturePad({ onSave }) {
  const canvasRef = React.useRef(null);
  const drawing = React.useRef(false);
  function pos(e) {
    const r = canvasRef.current.getBoundingClientRect();
    const p = e.touches?.[0] || e;
    return { x: p.clientX - r.left, y: p.clientY - r.top };
  }
  function start(e) { drawing.current = true; const ctx = canvasRef.current.getContext("2d"); const p = pos(e); ctx.moveTo(p.x, p.y); }
  function move(e) { if (!drawing.current) return; const ctx = canvasRef.current.getContext("2d"); const p = pos(e); ctx.lineTo(p.x, p.y); ctx.stroke(); }
  function end() { drawing.current = false; const ctx = canvasRef.current.getContext("2d"); ctx.beginPath(); }
  function clear() { const ctx = canvasRef.current.getContext("2d"); ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height); }
  return <div className="signature"><canvas width="420" height="150" ref={canvasRef} onMouseDown={start} onMouseMove={move} onMouseUp={end} onMouseLeave={end} onTouchStart={start} onTouchMove={move} onTouchEnd={end} /><div className="signature-actions"><button type="button" onClick={clear}>Limpiar firma</button><button type="button" onClick={() => onSave(canvasRef.current.toDataURL("image/png"))}>Guardar firma</button></div></div>;
}

function Crud({ title, ep, fields, admin = false, permission = "leer", itemMode = false, contractMode = false }) {
  const [rows, setRows] = React.useState([]);
  const [q, setQ] = React.useState("");
  const [lastItem, setLastItem] = React.useState(null);
  const [signature, setSignature] = React.useState("");
  const [massStatus, setMassStatus] = React.useState("");
  const [area, setArea] = React.useState("sonido");
  const [subcat, setSubcat] = React.useState(AREAS.sonido[0]);

  React.useEffect(() => { api(ep).then(setRows); }, [ep]);
  React.useEffect(() => { setSubcat(AREAS[area][0]); }, [area]);

  async function sub(e) {
    e.preventDefault();
    if (!can("crear")) return alert("No tienes permiso para crear registros.");
    const f = Object.fromEntries(new FormData(e.currentTarget).entries());
    Object.keys(f).forEach((k) => f[k] === "" && delete f[k]);
    if (itemMode) {
      f.category = `${area} / ${subcat}`;
      f.qr_code = f.qr_code || `PGR-QR-${f.code}`;
      f.barcode = f.barcode || `PGR-BAR-${f.code}`;
    }
    if (f.replacement_value) f.replacement_value = Number(f.replacement_value);
    if (contractMode && signature) f.terms = `${f.terms || ""}\n\n[FIRMA_DIGITAL_BASE64]\n${signature}`;
    const r = await api(ep, { method: "POST", body: JSON.stringify(f) });
    setRows([r, ...rows]);
    if (itemMode) setLastItem(r);
    e.currentTarget.reset();
  }

  const filtered = rows.filter((r) => JSON.stringify(r).toLowerCase().includes(q.toLowerCase()));

  function exp() {
    if (!can("exportar")) return alert("No tienes permiso para exportar.");
    const b = new Blob([JSON.stringify(filtered, null, 2)], { type: "application/json" });
    const u = URL.createObjectURL(b);
    const a = document.createElement("a");
    a.href = u;
    a.download = `${title.toLowerCase().replaceAll(" ", "-")}.json`;
    a.click();
    URL.revokeObjectURL(u);
  }

  async function importMassive(file) {
    if (!can("importar")) return alert("No tienes permiso para importar.");
    if (!file) return;
    try {
      const data = await file.arrayBuffer();
      const wb = XLSX.read(data, { type: "array" });
      const ws = wb.Sheets[wb.SheetNames[0]];
      const parsed = XLSX.utils.sheet_to_json(ws, { defval: "" });
      let ok = 0;
      for (const row of parsed) {
        const payload = Object.fromEntries(Object.entries(row).map(([k, v]) => [String(k).trim(), v]));
        try { await api(ep, { method: "POST", body: JSON.stringify(payload) }); ok += 1; } catch {}
      }
      setMassStatus(`Importación finalizada: ${ok} de ${parsed.length} registros creados.`);
      const newest = await api(ep);
      setRows(newest);
    } catch {
      setMassStatus("No se pudo importar el archivo. Verifica columnas y formato.");
    }
  }

  function printLabel() {
    if (!lastItem) return;
    const src = generateLabelSVG(lastItem);
    const w = window.open("", "_blank", "width=700,height=500");
    if (!w) return;
    w.document.write(`<html><body style='margin:0;display:grid;place-items:center'><img src='${src}' style='max-width:95%'/><script>window.onload=()=>window.print()<\/script></body></html>`);
    w.document.close();
  }

  return (
    <P admin={admin} permission={permission}>
      <Shell title={title}>
        <DescriptionCard title="Descripción de esta función" description={`En ${title} puedes crear, buscar, importar y exportar información en español para un flujo operativo completo.`} />
        <Innovations />
        <div className="grid">
          <form className="card" onSubmit={sub}>
            {fields}
            {itemMode && <><h4>Categorías y subcategorías por área</h4><select value={area} onChange={(e) => setArea(e.target.value)}>{Object.keys(AREAS).map((k) => <option value={k} key={k}>{k}</option>)}</select><select value={subcat} onChange={(e) => setSubcat(e.target.value)}>{AREAS[area].map((x) => <option key={x} value={x}>{x}</option>)}</select></>}
            {contractMode && can("firma") && <><h4>Firma digital del contrato</h4><SignaturePad onSave={setSignature} />{signature && <p className="ok">Firma guardada para este contrato.</p>}</>}
            <button>Guardar registro</button>
            {itemMode && lastItem && can("etiquetas") && <><div className="label-preview"><img alt="Etiqueta equipo" src={generateLabelSVG(lastItem)} /></div><button type="button" onClick={printLabel}>Generar e imprimir QR/Barras</button></>}
          </form>
          <div className="card">
            <div className="tools"><input placeholder="Buscar..." value={q} onChange={(e) => setQ(e.target.value)} /><button type="button" onClick={exp}>Exportar JSON</button></div>
            {can("importar") && <div className="importer"><label>Importación masiva Excel/CSV</label><input type="file" accept=".xlsx,.xls,.csv" onChange={(e) => importMassive(e.target.files?.[0])} />{massStatus && <p>{massStatus}</p>}</div>}
            {filtered.map((r) => <pre key={r.id}>{JSON.stringify(r, null, 2)}</pre>)}
            {!filtered.length && <p>Sin resultados para tu búsqueda.</p>}
          </div>
        </div>
      </Shell>
    </P>
  );
}

function Backups() {
  async function run() { await api("/backups/run", { method: "POST" }); alert("Backup creado exitosamente"); }
  return <P admin permission="backups"><Shell title="Backups"><DescriptionCard title="Descripción de esta función" description="Crea respaldos de seguridad del sistema para prevenir pérdida de información." /><div className="card"><button onClick={run}>Crear backup ahora</button></div></Shell></P>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/admin" element={<AdminDash />} />
        <Route path="/operator" element={<P><Shell title="Panel operador"><DescriptionCard title="Descripción de esta función" description="Panel principal del operador: acceso directo a escaneo, inventario, eventos y checklists." /><Innovations /><div className="grid"><Link className="card action" to="/operator/scanner">Escanear QR</Link><Link className="card action" to="/operator/items">Gestionar equipos</Link></div></Shell></P>} />
        <Route path="/admin/scanner" element={<Scanner admin />} />
        <Route path="/operator/scanner" element={<Scanner />} />
        <Route path="/admin/roles" element={<RolesManager />} />

        <Route path="/admin/clients" element={<Crud admin title="Clientes" ep="/clients" fields={<><input name="name" placeholder="Nombre" required /><input name="company_name" placeholder="Empresa" /><input name="phone" placeholder="Teléfono" /><input name="email" placeholder="Email" /></>} />} />
        <Route path="/admin/items" element={<Crud admin title="Equipos" ep="/items" itemMode permission="etiquetas" fields={<><input name="code" placeholder="Código" required /><input name="qr_code" placeholder="QR (opcional, autogenerado)" /><input name="barcode" placeholder="Barcode (opcional, autogenerado)" /><input name="name" placeholder="Nombre" required /><input name="location" placeholder="Ubicación" /><input name="replacement_value" type="number" placeholder="Valor reposición" /><textarea name="notes" placeholder="Descripción de la función del equipo" /></>} />} />
        <Route path="/operator/items" element={<Crud title="Equipos" ep="/items" itemMode permission="leer" fields={<><input name="code" placeholder="Código" required /><input name="name" placeholder="Nombre" required /><input name="location" placeholder="Ubicación" /><textarea name="notes" placeholder="Descripción de uso" /></>} />} />

        <Route path="/admin/events" element={<Crud admin title="Eventos" ep="/events" fields={<><input name="name" required placeholder="Evento" /><input name="location" placeholder="Lugar" /><input name="start_date" type="date" required /><input name="end_date" type="date" required /><input name="operator_name" placeholder="Operador" /><textarea name="notes" placeholder="Descripción del evento" /></>} />} />
        <Route path="/operator/events" element={<Crud title="Eventos" ep="/events" fields={<><input name="name" required placeholder="Evento" /><input name="location" placeholder="Lugar" /><input name="start_date" type="date" required /><input name="end_date" type="date" required /><textarea name="notes" placeholder="Descripción operativa" /></>} />} />

        <Route path="/admin/checklists" element={<Crud admin title="Checklists" ep="/checklists" fields={<><input name="title" required placeholder="Título" /><input name="item_id" placeholder="ID equipo" /><input name="performed_by" placeholder="Realizado por" /><textarea name="notes" placeholder="Descripción del checklist" /></>} />} />
        <Route path="/operator/checklists" element={<Crud title="Checklists" ep="/checklists" fields={<><input name="title" required placeholder="Título" /><input name="item_id" placeholder="ID equipo" /><textarea name="notes" placeholder="Descripción de revisión" /></>} />} />

        <Route path="/admin/contracts" element={<Crud admin title="Contratos" ep="/contracts" contractMode permission="firma" fields={<><input name="title" required placeholder="Título" /><input name="client_id" placeholder="ID cliente" /><input name="event_id" placeholder="ID evento" /><textarea name="terms" placeholder="Términos y condiciones (se adjuntará firma digital)" /></>} />} />
        <Route path="/admin/backups" element={<Backups />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
