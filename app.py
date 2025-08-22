from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import openai
from openai import RateLimitError, APIError, AuthenticationError

# Cargamos las variables de entorno desde el archivo .env
load_dotenv()

# Configuramos la clave de API de OpenAI desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# Ruta para analizar los comentarios
@app.route("/analyze", methods=["POST"])
def analyze():
    reviews = request.form.get("reviews")

    if not reviews:
        return jsonify({"error": "No reviews provided"}), 400

    # Prompt para enviar a la API de OpenAI
    prompt = f"""
    Eres un asistente que analiza textos o comentarios de usuarios.
    Extrae los principales puntos a mejorar o aspectos importantes en formato de lista numerada a partir de este texto:
    
    {reviews}
    """

    try:
        # Llamamos a la API de OpenAI
        response = openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente que genera puntos a mejorar de comentarios de clientes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300 # Límite de tokens en la respuesta
        )
        # Extraemos el contenido de la respuesta
        result = response['choices'][0]['message']['content']

        # Devolvemos los puntos o aspectos importantes en formato JSON
        return jsonify({"points_to_improve": result})
        
    # Posibles errores de la API
    except RateLimitError:
        return jsonify({"error": "Has superado tu cuota de OpenAI."}), 429
    except AuthenticationError:
        return jsonify({"error": "API key inválida."}), 401
    except APIError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
