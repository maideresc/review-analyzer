from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import openai
from openai import RateLimitError, APIError, AuthenticationError

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    reviews = request.form.get("reviews")

    if not reviews:
        return jsonify({"error": "No reviews provided"}), 400

    prompt = f"""
    Eres un asistente que analiza comentarios de clientes de un restaurante.
    Extrae los principales puntos a mejorar en formato de lista numerada a partir de estos comentarios:
    
    {reviews}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente que genera puntos a mejorar de comentarios de clientes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        result = response['choices'][0]['message']['content']
        return jsonify({"points_to_improve": result})

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

