import base64
import io
import json
import textwrap
from datetime import date
import requests
import streamlit as st
from zipfile import ZipFile, ZIP_DEFLATED

st.set_page_config(page_title="Tu primer repo en GitHub", page_icon="🧰")

st.title("🧰 Crea tu primer repositorio en GitHub (vía Streamlit)")
st.caption("Modo A: genera un ZIP para subir por la Web UI.  ·  Modo B (opcional): usa la API de GitHub con tu token.")

with st.form("repo_form"):
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Nombre del proyecto (slug/readme)", value="mi-primer-repo")
        visibility = st.selectbox("Visibilidad del repo", ["private", "public"])
        license_choice = st.selectbox("Licencia", ["MIT", "Apache-2.0", "GPL-3.0", "Sin licencia"])
    with col2:
        gitignore_choice = st.selectbox(".gitignore", ["Python", "Node", "General", "Ninguno"])
        author_name = st.text_input("Autor/a", value="Nombre Apellido")
        project_desc = st.text_area("Descripción breve (README)", value="Repo inicial creado en clase con Streamlit.")
    token = st.text_input("Token personal de GitHub (opcional, dejar vacío para Modo A)", type="password")
    github_user = st.text_input("Tu usuario de GitHub (requerido si usas API)", value="")
    submit = st.form_submit_button("Generar plantilla")

def mit_license(author, year):
    return textwrap.dedent(f"""        MIT License

    Copyright (c) {year} {author}

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """)

def apache2_license(author, year):
    # Short pointer to official text to keep this file compact for class use
    return textwrap.dedent(f"""        Apache License 2.0 (resumen pedagógico)
    © {year} {author}
    Nota: para uso real, reemplaza por el texto oficial de Apache-2.0:
    https://www.apache.org/licenses/LICENSE-2.0.txt
    """)

def gpl3_license(author, year):
    # Short pointer to official text to keep this file compact for class use
    return textwrap.dedent(f"""        GNU GPL v3 (resumen pedagógico)
    © {year} {author}
    Nota: para uso real, reemplaza por el texto oficial de GPL-3.0:
    https://www.gnu.org/licenses/gpl-3.0.txt
    """)

def make_gitignore(choice):
    templates = {
        "Python": """    __pycache__/
*.pyc
.env
.venv/
.ipynb_checkpoints/
        """,
        "Node": """    node_modules/
dist/
.env
npm-debug.log*
.yarn/*
        """,
        "General": """    .DS_Store
Thumbs.db
.env
.vscode/
.idea/
        """,
        "Ninguno": ""
    }
    return textwrap.dedent(templates[choice]).strip() + "\n"

def readme_md(name, desc, author):
    return textwrap.dedent(f"""        # {name}

    {desc}

    ## Estructura
    - `streamlit_app.py`: app base en Streamlit
    - `requirements.txt`: dependencias mínimas
    - `.gitignore`: según tu selección
    - `LICENSE`: si seleccionaste una

    ## Ejecutar en local
    ```bash
    pip install -r requirements.txt
    streamlit run streamlit_app.py
    ```

    ## Autor
    {author}
    """)

def streamlit_stub():
    return textwrap.dedent("""        import streamlit as st

    st.set_page_config(page_title="Hola GitHub", page_icon="👋")
    st.title("👋 Mi primer repo")
    st.write("Este proyecto nació en clase, con una plantilla generada desde Streamlit.")
    st.info("Edita este archivo y haz tu primer commit.")

    st.subheader("Checklist")
    st.markdown("- [ ] He creado el repo en GitHub\n- [ ] He subido o visto estos archivos\n- [ ] He ejecutado la app en local")
    """)

def requirements_txt():
    return "streamlit\nrequests\n"

def license_text(choice, author):
    y = date.today().year
    if choice == "MIT":
        return mit_license(author, y)
    if choice == "Apache-2.0":
        return apache2_license(author, y)
    if choice == "GPL-3.0":
        return gpl3_license(author, y)
    return ""

def build_zip(files: dict) -> bytes:
    mem = io.BytesIO()
    with ZipFile(mem, "w", ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content)
    mem.seek(0)
    return mem.read()

def to_b64(content: bytes) -> str:
    return base64.b64encode(content).decode("utf-8")

def create_repo_via_api(user, token, repo_name, private=True, description=""):
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json"}
    payload = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": False
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    return r.status_code, r.json()

def put_file_via_api(user, token, repo, path, content_bytes, message="add file"):
    url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json"}
    payload = {"message": message, "content": to_b64(content_bytes)}
    r = requests.put(url, headers=headers, data=json.dumps(payload), timeout=30)
    return r.status_code, r.json()

if submit:
    if not project_name.strip():
        st.error("El nombre del proyecto es obligatorio.")
        st.stop()

    files = {
        "README.md": readme_md(project_name, project_desc, author_name),
        "streamlit_app.py": streamlit_stub(),
        "requirements.txt": requirements_txt(),
    }

    gi = make_gitignore(gitignore_choice)
    if gi.strip():
        files[".gitignore"] = gi

    lic = license_text(license_choice, author_name)
    if license_choice != "Sin licencia":
        files["LICENSE"] = lic

    # --- Modo A: generar ZIP descargable ---
    zip_bytes = build_zip({k: v.encode("utf-8") for k, v in files.items()})
    st.success("Plantilla generada. Descarga el ZIP o usa la API con tu token (opcional).")
    st.download_button(
        "⬇️ Descargar ZIP del repo",
        data=zip_bytes,
        file_name=f"{project_name}.zip",
        mime="application/zip"
    )

    # --- Modo B (opcional): crear repo vía API ---
    if token and github_user:
        with st.spinner("Creando repositorio en GitHub…"):
            is_private = (visibility == "private")
            code, resp = create_repo_via_api(github_user, token, project_name, private=is_private, description=project_desc)
            if code not in (200, 201):
                st.error(f"Error al crear repo ({code}): {resp.get('message')}")
            else:
                repo_url = resp.get("html_url", f"https://github.com/{github_user}/{project_name}")
                st.success(f"Repositorio creado: {repo_url}")

                # Subir archivos uno a uno
                ok = True
                for path, content in files.items():
                    code2, resp2 = put_file_via_api(github_user, token, project_name, path, content.encode("utf-8"), message=f"Add {path}")
                    if code2 not in (200, 201):
                        ok = False
                        st.error(f"Error subiendo {path}: {resp2.get('message')}")
                if ok:
                    st.balloons()
                    st.info("Listo. Revisa tu repo en GitHub y abre README.md.")
    else:
        st.info("Modo A listo: crea el repo manualmente en GitHub y sube el ZIP (Add file → Upload files).")
