import streamlit as st
import requests

API_URL = "https://novo-instala-o-4.onrender.com"

st.set_page_config(page_title="Agenda de Tarefas", layout="wide")
st.caption("APP ATUALIZADO")

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
                    st.error("Usuário ou senha inválidos.")

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
st.title("Agenda de Tarefas")

if st.session_state.token:
    st.success("Acesso liberado. Gerencie suas tarefas abaixo.")

    with st.expander("Nova Tarefa"):
        titulo = st.text_input("Título da tarefa")
        descricao = st.text_area("Descrição")

        col_data, col_hora = st.columns(2)
        data = col_data.date_input("Data")
        hora = col_hora.time_input("Horário")

        if st.button("Salvar Tarefa"):
            if titulo.strip() == "":
                st.warning("Digite o título da tarefa.")
            else:
                try:
                    resposta = requests.post(
                        f"{API_URL}/tarefas",
                        json={
                            "titulo": titulo,
                            "descricao": descricao,
                            "data": str(data),
                            "hora": str(hora)
                        },
                        timeout=30
                    )

                    if resposta.status_code == 200:
                        st.success("Tarefa agendada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao salvar tarefa.")
                        st.write(resposta.text)

                except requests.exceptions.RequestException as erro:
                    st.error("Erro ao conectar com a API.")
                    st.write(erro)

    st.subheader("Tarefas agendadas")

    try:
        resposta = requests.get(f"{API_URL}/tarefas", timeout=30)

        if resposta.status_code == 200:
            tarefas = resposta.json()

            if len(tarefas) == 0:
                st.info("Nenhuma tarefa cadastrada ainda.")
            else:
                for tarefa in tarefas:
                    with st.container(border=True):
                        col_info, col_status, col_del = st.columns([4, 2, 1])

                        col_info.write(f"**{tarefa['titulo']}**")
                        col_info.write(f"Descrição: {tarefa['descricao']}")
                        col_info.write(f"Data: {tarefa['data']}")
                        col_info.write(f"Hora: {tarefa['hora']}")

                        status_atual = tarefa.get("status", "pendente")

                        novo_status = col_status.selectbox(
                            "Status",
                            ["pendente", "concluída"],
                            index=0 if status_atual == "pendente" else 1,
                            key=f"status_{tarefa['id']}"
                        )

                        if novo_status != status_atual:
                            requests.put(
                                f"{API_URL}/tarefas/{tarefa['id']}",
                                json={
                                    "status": novo_status
                                },
                                timeout=30
                            )
                            st.rerun()

                        if col_del.button("Excluir", key=f"del_{tarefa['id']}"):
                            resposta_delete = requests.delete(
                                f"{API_URL}/tarefas/{tarefa['id']}",
                                timeout=30
                            )

                            if resposta_delete.status_code == 200:
                                st.success("Tarefa excluída!")
                                st.rerun()
                            else:
                                st.error("Erro ao excluir tarefa.")
                                st.write(resposta_delete.text)
        else:
            st.error("Erro ao carregar tarefas.")
            st.write(resposta.text)

    except requests.exceptions.RequestException as erro:
        st.error("Erro ao conectar com a API.")
        st.write(erro)

else:
    st.info("Acesse com seu usuário para gerenciar suas tarefas.")