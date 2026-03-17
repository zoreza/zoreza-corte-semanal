#!/usr/bin/env python3
"""
Script para ver exactamente qué responde Turso
"""
import os
import requests
import json

# Credenciales
turso_url = "libsql://zoreza-corte-zoreza.aws-us-east-1.turso.io"
turso_token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzM0NjI3MTYsImlkIjoiMDE5Y2U5YjEtMzEwMS03ZDk2LTkwMWYtZTY2Mzk2NTk1ZTZjIiwicmlkIjoiOTk2ODZhYjItMTc0ZS00OThkLTliNzEtMGU5NjY4ZTg4NDQ0In0.IwiFkSEa5_KI7zqTt2w2tf2itZF2d2WQScZDgDtj-E09M-TvO7mVIxTol-gutzeGVHBPshsRp6l2mymfCs5lCg"

# Convertir URL
http_url = turso_url.replace("libsql://", "https://")

print("=" * 70)
print("🔍 DEBUG DE RESPUESTA DE TURSO")
print("=" * 70)
print()
print(f"URL: {http_url}")
print()

# Preparar request
headers = {
    "Authorization": f"Bearer {turso_token}",
    "Content-Type": "application/json"
}

request_data = {
    "requests": [
        {
            "type": "execute",
            "stmt": {
                "sql": "SELECT username, nombre, rol, activo FROM usuarios"
            }
        },
        {"type": "close"}
    ]
}

print("📤 Enviando request...")
print(json.dumps(request_data, indent=2))
print()

# Ejecutar
response = requests.post(
    f"{http_url}/v2/pipeline",
    headers=headers,
    json=request_data,
    timeout=10
)

print(f"📥 Status Code: {response.status_code}")
print()

if response.status_code == 200:
    result = response.json()
    print("📋 Respuesta completa:")
    print(json.dumps(result, indent=2))
    print()
    
    # Analizar estructura
    if "results" in result:
        print(f"✅ Tiene 'results': {len(result['results'])} elementos")
        
        if len(result["results"]) > 0:
            first_result = result["results"][0]
            print(f"   Tipo: {first_result.get('type')}")
            
            if "response" in first_result:
                response_data = first_result["response"]
                print(f"   Tiene 'response'")
                
                if "result" in response_data:
                    result_data = response_data["result"]
                    print(f"   Tiene 'result'")
                    
                    if "columns" in result_data:
                        print(f"   Columnas: {result_data['columns']}")
                    
                    if "rows" in result_data:
                        rows = result_data["rows"]
                        print(f"   Filas: {len(rows)}")
                        
                        if rows:
                            print()
                            print("   Contenido de filas:")
                            for i, row in enumerate(rows):
                                print(f"   Fila {i}: {row}")
                                print(f"   Tipo: {type(row)}")
                                if isinstance(row, list):
                                    for j, val in enumerate(row):
                                        print(f"      [{j}] = {val} (tipo: {type(val)})")
                        else:
                            print("   ⚠️  Array de filas está vacío")
else:
    print(f"❌ Error: {response.text}")

print()
print("=" * 70)

# Made with Bob
