import html
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs


def formato_cop(valor):
    return f"${valor:,.0f}".replace(",", ".")


def calcular_soldaduras(precio_pega, cantidad_pegas):
    if precio_pega < 0:
        raise ValueError("El precio por pega no puede ser negativo.")

    if cantidad_pegas < 1:
        raise ValueError("La cantidad de soldaduras debe ser al menos 1.")

    subtotal = precio_pega * cantidad_pegas

    if cantidad_pegas >= 3:
        descuento = subtotal * 0.10
    else:
        descuento = 0

    total = subtotal - descuento

    return {
        "precio_pega": precio_pega,
        "cantidad_pegas": cantidad_pegas,
        "subtotal": subtotal,
        "descuento": descuento,
        "total": total,
    }


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.enviar_pagina(
            "<h1>Calculadora de M&amp;G Joyería</h1>"
            "<p>Para realizar el cálculo, regresa al sitio y envía el formulario.</p>"
            '<a href="/">Volver al inicio</a>'
        )

    def do_POST(self):
        try:
            longitud = int(self.headers.get("Content-Length", 0))
            datos = self.rfile.read(longitud).decode("utf-8")
            formulario = parse_qs(datos)

            precio_texto = formulario.get("precio_pega", [""])[0].strip()
            cantidad_texto = formulario.get("cantidad_pegas", [""])[0].strip()

            if not precio_texto or not cantidad_texto:
                raise ValueError("Debes ingresar el precio y la cantidad de soldaduras.")

            precio_texto = precio_texto.replace(",", ".")

            precio = float(precio_texto)
            cantidad = int(cantidad_texto)

            if not precio.is_integer():
                raise ValueError("El precio debe ingresarse en pesos enteros, sin decimales.")

            resultado = calcular_soldaduras(int(precio), cantidad)

            precio_formateado = formato_cop(resultado["precio_pega"])
            subtotal_formateado = formato_cop(resultado["subtotal"])
            descuento_formateado = formato_cop(resultado["descuento"])
            total_formateado = formato_cop(resultado["total"])

            if cantidad >= 3:
                mensaje = (
                    "¡Tu compra cumple con la promoción! "
                    "Se aplicó el 10% de descuento."
                )
            else:
                mensaje = (
                    "Para obtener el 10% de descuento necesitas "
                    "realizar 3 o más soldaduras con fuego."
                )

            contenido = f"""
            <h1>Resultado de tu cotización</h1>

            <p>{html.escape(mensaje)}</p>

            <div class="resumen">
                <p><strong>Precio por pega:</strong> {precio_formateado}</p>
                <p><strong>Cantidad de soldaduras:</strong> {cantidad}</p>
                <p><strong>Subtotal:</strong> {subtotal_formateado}</p>
                <p><strong>Descuento del 10%:</strong> - {descuento_formateado}</p>
                <hr>
                <h2>Total a pagar: {total_formateado}</h2>
            </div>

            <p>
                Este cálculo es una referencia del valor de las soldaduras
                con fuego solicitadas.
            </p>

            <a class="boton" href="/#calculadora">
                Volver a la calculadora
            </a>

            <a class="enlace" href="/">
                Volver al inicio
            </a>
            """

            self.enviar_pagina(contenido)

        except ValueError as error:
            mensaje_error = html.escape(str(error))

            contenido = f"""
            <h1>No fue posible realizar el cálculo</h1>
            <p>{mensaje_error}</p>
            <a class="boton" href="/#calculadora">
                Volver a intentarlo
            </a>
            """

            self.enviar_pagina(contenido)

    def enviar_pagina(self, contenido):
        pagina = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="theme-color" content="#263E2C">
            <title>Resultado | M&G Taller de Joyería</title>

            <style>
                * {{
                    box-sizing: border-box;
                }}

                body {{
                    margin: 0;
                    padding: 30px 15px;
                    font-family: Arial, sans-serif;
                    background: #f4f1e9;
                    color: #263E2C;
                }}

                .contenedor {{
                    max-width: 600px;
                    margin: 40px auto;
                    padding: 30px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
                }}

                h1 {{
                    margin-top: 0;
                    color: #263E2C;
                }}

                .resumen {{
                    margin: 25px 0;
                    padding: 20px;
                    background: #f4f1e9;
                    border-radius: 8px;
                }}

                .resumen p {{
                    margin: 12px 0;
                }}

                .resumen h2 {{
                    margin-bottom: 0;
                    color: #263E2C;
                }}

                .boton {{
                    display: inline-block;
                    margin-top: 15px;
                    padding: 13px 20px;
                    background: #263E2C;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                }}

                .enlace {{
                    display: block;
                    margin-top: 20px;
                    color: #263E2C;
                }}
            </style>
        </head>

        <body>
            <main class="contenedor">
                {contenido}
            </main>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(pagina.encode("utf-8"))
        