import streamlit as st
import requests

# Link da API hospedada no Render
API_URL = "https://novo-instala-o-4.onrender.com"

st.set_page_config(page_title="Biblioteca Digital", layout="wide")

# Marca pra confirmar que o Streamlit atualizou
st.caption("VERSÃO NOVA DO APP - DEBUG ATIVO")

# Guarda o token do login
if "token" not in st.session_state:
    st.session_state.token = None


# =========================
# LOGIN
# =========================
with st.sidebar:
    if not st.session_state.token:
        st.header("Login")

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            try:
                resposta = requests.post(
                    f"{API_URL}/auth/login",
                    json={
                        "username": usuario,
                        "password": senha
                    },
                    timeout=30
                )

                if resposta.status_code == 200:
                    dados = resposta.json()
                    st.session_state.token = dados.get("token")
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao logar")
                    st.write("Status code:", resposta.status_code)
                    st.write("Resposta da API:", resposta.text)
                    st.write("URL chamada:", f"{API_URL}/auth/login")

            except requests.exceptions.RequestException as erro:
                st.error("Erro ao conectar com a API.")
                st.write(erro)

    else:
        st.success("Logado")

        if st.button("Sair"):
            st.session_state.token = None
            st.rerun()


# =========================
# INTERFACE PRINCIPAL
# =========================
st.title("Gestão de Acervo")

if st.session_state.token:
    st.success("Acesso liberado.")

    # FORMULÁRIO PARA CRIAR LIVRO
    with st.expander("Novo Registro"):
        col1, col2 = st.columns(2)

        titulo = col1.text_input("Título do Livro")
        autor = col2.text_input("Autor")

        if st.button("Salvar Livro"):
            if titulo.strip() == "" or autor.strip() == "":
                st.warning("Preencha o título e o autor.")
            else:
                try:
                    resposta = requests.post(
                        f"{API_URL}/livros",
                        json={
                            "titulo": titulo,
                            "autor": autor
                        },
                        timeout=30
                    )

                    if resposta.status_code == 200:
                        st.success("Livro adicionado!")
                        st.rerun()
                    else:
                        st.error("Erro ao salvar livro")
                        st.write("Status code:", resposta.status_code)
                        st.write("Resposta da API:", resposta.text)

                except requests.exceptions.RequestException as erro:
                    st.error("Erro ao conectar com a API.")
                    st.write(erro)

    # LISTAGEM DOS LIVROS
    st.subheader("Livros cadastrados")

    try:
        resposta = requests.get(f"{API_URL}/livros", timeout=30)

        if resposta.status_code == 200:
            livros = resposta.json()

            if len(livros) == 0:
                st.info("Nenhum livro cadastrado ainda.")
            else:
                for livro in livros:
                    with st.container(border=True):
                        col_info, col_del = st.columns([4, 1])

                        col_info.write(f"**{livro['titulo']}**")
                        col_info.write(f"Autor: {livro['autor']}")

                        if col_del.button("Excluir", key=f"del_{livro['id']}"):
                            resposta_delete = requests.delete(
                                f"{API_URL}/livros/{livro['id']}",
                                timeout=30
                            )

                            if resposta_delete.status_code == 200:
                                st.success("Livro excluído!")
                                st.rerun()
                            else:
                                st.error("Erro ao excluir livro")
                                st.write("Status code:", resposta_delete.status_code)
                                st.write("Resposta da API:", resposta_delete.text)
        else:
            st.error("Erro ao listar livros")
            st.write("Status code:", resposta.status_code)
            st.write("Resposta da API:", resposta.text)

    except requests.exceptions.RequestException as erro:
        st.error("Erro ao conectar com a API.")
        st.write(erro)

else:
    st.info("Acesse com seu usuário para gerenciar os livros.")