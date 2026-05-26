import json
from pprint import pprint
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

results = []
def log(name, response):
    try:
        body = response.json()
    except Exception:
        body = response.text
    results.append({
        "endpoint": name,
        "status": response.status_code,
        "body": body,
        "cookies": dict(client.cookies),
    })
    print(f"{name}: {response.status_code}")
    pprint(body)
    print("cookies:", dict(client.cookies))
    print("---")

try:
    print("GET /health/")
    r = client.get("/health/")
    log("GET /health/", r)

    print("POST /auth/register")
    payload = {
        "username": "admin_test",
        "full_name": "Admin Test",
        "email": "admin_test@example.com",
        "password": "AdminTest123!"
    }
    r = client.post("/auth/register", json=payload)
    log("POST /auth/register", r)

    print("POST /auth/token")
    r = client.post("/auth/token", data={"username": "admin_test", "password": "AdminTest123!"})
    log("POST /auth/token", r)

    print("GET /auth/me")
    r = client.get("/auth/me")
    log("GET /auth/me", r)

    print("GET /auth/roles")
    r = client.get("/auth/roles")
    log("GET /auth/roles", r)

    print("GET /auth/admin/usuarios")
    r = client.get("/auth/admin/usuarios")
    log("GET /auth/admin/usuarios", r)

    print("POST /auth/admin/usuarios/1/roles")
    r = client.post("/auth/admin/usuarios/1/roles", json={"rol_codigo": "ADMIN"})
    log("POST /auth/admin/usuarios/1/roles", r)

    print("GET /productos")
    r = client.get("/productos")
    log("GET /productos", r)

    print("POST /productos")
    r = session.post(f"{BASE}/productos", json={"nombre": "Test Producto", "descripcion": "Prueba", "precio_base": 10.5, "stock_cantidad": 100, "disponible": True})
    log("POST /productos", r)

    print("PUT /productos/1")
    r = client.put("/productos/1", json={"descripcion": "Actualizado"})
    log("PUT /productos/1", r)

    print("DELETE /productos/1")
    r = client.delete("/productos/1")
    log("DELETE /productos/1", r)

    print("GET /categorias")
    r = client.get("/categorias")
    log("GET /categorias", r)

    print("POST /categorias")
    r = session.post(f"{BASE}/categorias", json={"nombre": "Test Cat", "descripcion": "Prueba"})
    log("POST /categorias", r)

    print("PUT /categorias/1")
    r = client.put("/categorias/1", json={"descripcion": "Actualizado"})
    log("PUT /categorias/1", r)

    print("DELETE /categorias/1")
    r = client.delete("/categorias/1")
    log("DELETE /categorias/1", r)

    print("GET /ingredientes")
    r = client.get("/ingredientes")
    log("GET /ingredientes", r)

    print("POST /ingredientes")
    r = session.post(f"{BASE}/ingredientes", json={"nombre": "Test Ing", "cantidad": 100, "precio_por_unidad": 5.25, "unidad_medida_id": 1})
    log("POST /ingredientes", r)

    print("PUT /ingredientes/1")
    r = client.put("/ingredientes/1", json={"precio_por_unidad": 6.00})
    log("PUT /ingredientes/1", r)

    print("DELETE /ingredientes/1")
    r = client.delete("/ingredientes/1")
    log("DELETE /ingredientes/1", r)

    print("GET /pedidos")
    r = client.get("/pedidos")
    log("GET /pedidos", r)

    print("POST /pedidos")
    r = client.post("/pedidos", json={"direccion_id": None, "forma_pago_codigo": "EFECTIVO", "items": []})
    log("POST /pedidos", r)

    print("PUT /pedidos/1")
    r = client.put("/pedidos/1", json={"notas": "Cambio"})
    log("PUT /pedidos/1", r)

    print("POST /auth/logout")
    r = client.post("/auth/logout")
    log("POST /auth/logout", r)

except Exception as exc:
    print("EXCEPTION", exc)
    raise
