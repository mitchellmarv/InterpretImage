import base64

import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Análisis de imagen",
    page_icon="🔷",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# Estilos: azul profundo + cian eléctrico, rejilla tenue y brillo neón
# ------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Exo+2:wght@300;400;600&display=swap');

:root {
    --bg: #040B1E;
    --panel: #0A1633;
    --panel-2: #0E1E45;
    --blue: #1E6BFF;
    --cyan: #22D3EE;
    --ice: #E6F1FF;
    --muted: #8FA8D6;
    --line: rgba(34, 211, 238, 0.28);
}

.stApp {
    background:
        radial-gradient(1000px 500px at 85% -10%, rgba(30,107,255,0.30), transparent 60%),
        radial-gradient(800px 500px at -10% 110%, rgba(34,211,238,0.14), transparent 60%),
        linear-gradient(rgba(34,211,238,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34,211,238,0.04) 1px, transparent 1px),
        var(--bg);
    background-size: auto, auto, 44px 44px, 44px 44px, auto;
    color: var(--ice);
    font-family: 'Exo 2', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.5rem; max-width: 780px; }

h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em;
    line-height: 1.2 !important;
    background: linear-gradient(90deg, #FFFFFF 0%, var(--cyan) 55%, var(--blue) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 14px rgba(34,211,238,0.45));
}

h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    color: var(--ice) !important;
    letter-spacing: 0.03em;
}

p, label, li, span, .stMarkdown { font-family: 'Exo 2', sans-serif; }

/* Campos de texto */
.stTextInput input, .stTextArea textarea {
    background: var(--panel) !important;
    color: var(--ice) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    font-family: 'Exo 2', sans-serif;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 1px var(--cyan), 0 0 18px rgba(34,211,238,0.35) !important;
}
.stTextArea textarea::placeholder, .stTextInput input::placeholder { color: var(--muted); }

/* Cargador de archivos */
[data-testid="stFileUploader"] section {
    background: var(--panel);
    border: 1.5px dashed var(--cyan);
    border-radius: 14px;
    transition: box-shadow .2s ease, background .2s ease;
}
[data-testid="stFileUploader"] section:hover {
    background: var(--panel-2);
    box-shadow: 0 0 22px rgba(34,211,238,0.28);
}
[data-testid="stFileUploader"] button {
    background: linear-gradient(90deg, var(--blue), var(--cyan));
    color: #031026;
    border: none;
    font-weight: 600;
}

/* Botón principal */
.stButton button {
    background: linear-gradient(90deg, var(--blue), var(--cyan));
    color: #031026;
    border: none;
    border-radius: 10px;
    font-family: 'Orbitron', sans-serif;
    font-weight: 600;
    letter-spacing: 0.04em;
    padding: 0.6rem 1.4rem;
    box-shadow: 0 0 18px rgba(30,107,255,0.45);
    transition: box-shadow .2s ease, transform .2s ease;
}
.stButton button:hover {
    color: #031026;
    box-shadow: 0 0 26px rgba(34,211,238,0.65);
    transform: translateY(-1px);
}

/* Expander con la imagen */
[data-testid="stExpander"] {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 14px;
    box-shadow: 0 0 24px rgba(30,107,255,0.25);
}
[data-testid="stExpander"] summary { color: var(--cyan); }
[data-testid="stImage"] img { border-radius: 10px; }

/* Alertas */
[data-testid="stAlert"] {
    background: rgba(14,30,69,0.85);
    border: 1px solid var(--line);
    border-radius: 12px;
    color: var(--ice);
}

/* Panel de la respuesta */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(135deg, rgba(14,30,69,0.95), rgba(10,22,51,0.95));
    border: 1px solid var(--line) !important;
    border-left: 4px solid var(--cyan) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 26px rgba(30,107,255,0.28);
    line-height: 1.65;
}

::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--blue); border-radius: 8px; }

@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; animation: none !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def encode_image(image_file):
    """Convierte la imagen subida a base64."""
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


# ------------------------------------------------------------------
# Interfaz
# ------------------------------------------------------------------
st.title("Análisis de Imagen 🤖🏞️")

api_key = st.text_input("Ingresa tu Clave de OpenAI", type="password")

uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

show_details = st.toggle("Pregunta algo específico sobre la imagen", value=False)

additional_details = ""
if show_details:
    additional_details = st.text_area("Adiciona contexto de la imagen aquí:")

analyze_button = st.button("Analiza la imagen", type="secondary")

# ------------------------------------------------------------------
# Análisis
# ------------------------------------------------------------------
if analyze_button:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
    elif not uploaded_file:
        st.warning("Por favor sube una imagen.")
    else:
        # El cliente se crea solo cuando ya hay clave (evita el OpenAIError al iniciar)
        client = OpenAI(api_key=api_key)

        with st.spinner("Analizando ..."):
            base64_image = encode_image(uploaded_file)
            mime_type = uploaded_file.type or "image/jpeg"

            prompt_text = "Describe lo que ves en la imagen, en español."
            if show_details and additional_details:
                prompt_text += (
                    f"\n\nContexto adicional del usuario:\n{additional_details}"
                )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            },
                        },
                    ],
                }
            ]

            try:
                st.markdown("### Resultado")
                with st.container(border=True):
                    message_placeholder = st.empty()
                    full_response = ""
                    for completion in client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=1200,
                        stream=True,
                    ):
                        if completion.choices and completion.choices[0].delta.content:
                            full_response += completion.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
elif not api_key:
    st.info("Ingresa tu API key para comenzar.")
