import requests
import datetime

# Configura aquí tu API Key
API_KEY = "TU_API_KEY_AQUI"

# Configura el modelo que usas normalmente
MODELO = "gpt-4o-mini"  # Cambia por el tuyo

#  Precios por millón de tokens (USD)
PRECIOS = {
    "gpt-4o-mini": {"entrada": 0.15, "salida": 0.60},
    "gpt-4o": {"entrada": 2.50, "salida": 10.00},
    "gpt-3.5-turbo": {"entrada": 0.50, "salida": 1.50}
}

# Fechas para el cálculo (primer día del mes a hoy)
hoy = datetime.date.today()
inicio_mes = hoy.replace(day=1)

url = (
    f"https://api.openai.com/v1/dashboard/billing/usage"
    f"?start_date={inicio_mes}&end_date={hoy}"
)

headers = {"Authorization": f"Bearer {API_KEY}"}

response = requests.get(url, headers=headers)
data = response.json()

if "total_usage" in data:
    gasto_usd = data["total_usage"] / 100  # viene en centavos
    precios = PRECIOS.get(MODELO, None)

    print(f"Desde {inicio_mes} hasta {hoy}")
    print(f"Gasto total: ${gasto_usd:.4f} USD")

    if precios:
        # Aproximación: mitad tokens entrada, mitad salida
        gasto_entrada = gasto_usd / 2
        gasto_salida = gasto_usd / 2
        tokens_entrada = (gasto_entrada / precios["entrada"]) * 1_000_000
        tokens_salida = (gasto_salida / precios["salida"]) * 1_000_000

        print(f"Tokens de entrada aprox: {tokens_entrada:,.0f}")
        print(f"Tokens de salida aprox: {tokens_salida:,.0f}")
        print(f"Total tokens aprox: {tokens_entrada + tokens_salida:,.0f}")
    else:
        print("Modelo no encontrado en la tabla de precios.")
else:
    print(" No se pudo obtener el uso. Revisa tu API Key.")
