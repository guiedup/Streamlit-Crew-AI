# app_crewai_custom.py
import streamlit as st
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
import os

# Configuração inicial
st.set_page_config(page_title="Crew AI Builder Pro", page_icon="🤖")
st.title("🚀 Advanced Crew AI Constructor")
st.caption("Create custom agents and use templates!")

# ========== CONFIGURAÇÕES ==========
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key Groq
    groq_api_key = st.text_input(
        "🔑 Input your Groq API Key:",
        type="password",
        help="GET in https://console.groq.com/keys"
    )
    os.environ["GROQ_API_KEY"] = groq_api_key
    
    # Configuração do Modelo
    model_config = {
        "model": st.selectbox(
            "LLM Model",
            ["mixtral-8x7b-32768", "llama2-70b-4096", "gemma-7b-it"],
            index=0
        ),
        "temperature": st.slider("Temperature", 0.0, 1.0, 0.7),
        "max_tokens": st.number_input("Máx Tokens", 512, 32768, 4096)
    }

# ========== GERENCIAMENTO DE AGENTS ==========
if 'custom_agents' not in st.session_state: # Estado para selecionar agentes
    st.session_state.custom_agents = {}

if 'workflow' not in st.session_state:
    st.session_state.workflow = []

# Agents pré-definidos
premade_agents = {
    "🔍 Pesquisador": {
        "role": "Pesquisador Sênior",
        "goal": "Realizar pesquisas detalhadas em bases técnicas",
        "backstory": "Expert com 10+ anos em pesquisa acadêmica"
    },
    "📊 Analista": {
        "role": "Analista de Dados", 
        "goal": "Analisar e interpretar dados complexos",
        "backstory": "Especialista em análise quantitativa"
    }
}

# Interface de criação de agents
with st.expander("🛠️ New Agent", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        new_emoji = st.selectbox("Emoji", ["🧠", "🤖", "🎨", "💡", "🔧", "📈"])
        new_role = st.text_input("Função (Role)")
    with col2:
        new_goal = st.text_area("Objetivo (Goal)")
        new_backstory = st.text_area("Histórico (Backstory)")
    
    if st.button("➕ Save Agent"):
        if new_role and new_goal:
            agent_id = f"{new_emoji} {new_role}"
            st.session_state.custom_agents[agent_id] = {
                "role": new_role,
                "goal": new_goal,
                "backstory": new_backstory,
                "emoji": new_emoji
            }
            st.success("Agent saved!")
        else:
            st.error("Fill the form to finish!")

# ========== TEMPLATES PRONTOS ==========
team_templates = {
    "Content Team": {
        "agents": ["✍️ Redator Conteúdo", "🔍 Especialista SEO"],
        "tasks": [
            "Pesquisar tópicos relevantes para SEO",
            "Escrever artigo otimizado"
        ]
    },
    "Data Team": {
        "agents": ["📊 Analista Dados", "📈 Cientista Dados"],
        "tasks": [
            "Coletar e limpar dados",
            "Criar modelo preditivo"
        ]
    }
}

# Seletor de templates
with st.sidebar:
    st.divider()
    selected_template = st.selectbox
    (
        "🏆 Crew Templates",
        ["Nenhum"]+ list(team_templates.keys()))
    
    if selected_template != "Nenhum":
        if st.button("🔄 Load Template"):
            template = team_templates[selected_template]
            st.session_state.workflow = template["agents"]
            st.session_state.tasks_config = {
                f"task_{idx}": {
                    "description": task,
                    "agent_type": template["agents"][idx % len(template["agents"])]
                } for idx, task in enumerate(template["tasks"])
            }
            st.rerun()

# ========== INTERFACE PRINCIPAL ==========
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🧩 Available Agents")
    
    # Mostrar agents pré-definidos
    with st.expander("📦 Premade Agents"):
        for agent in premade_agents:
            if st.button(f"{agent} {premade_agents[agent]['role']}"):
                st.session_state.workflow.append(agent)
    
    # Mostrar agents customizados
    if st.session_state.custom_agents:
        with st.expander("💼 My Agents"):
            for agent_id in st.session_state.custom_agents:
                if st.button(f"{agent_id}"):
                    st.session_state.workflow.append(agent_id)

with col2:
    st.subheader("📋 Workflow")
    
    if not st.session_state.workflow:
        st.info("Add agents using the left painel ←")
    
    # Configuração das tasks
    if 'tasks_config' not in st.session_state:
        st.session_state.tasks_config = {}
    
    for idx, agent_id in enumerate(st.session_state.workflow):
        agent_config = premade_agents.get(agent_id) or st.session_state.custom_agents.get(agent_id)
        
        with st.expander(f"{agent_id}", expanded=True):
            task_key = f"task_{idx}"
            
            # Configuração da Task
            task_desc = st.text_area(
                "Task Description",
                value=st.session_state.tasks_config.get(task_key, {}).get("description", ""),
                key=f"desc_{idx}"
            )
            
            expected_output = st.text_area(
                "Waited Result",
                value=st.session_state.tasks_config.get(task_key, {}).get("output", ""),
                key=f"out_{idx}"
            )
            
            # Salvar configuração
            st.session_state.tasks_config[task_key] = {
                "description": task_desc,
                "output": expected_output,
                "agent_type": agent_id
            }

# ========== FUNÇÕES DE EXECUÇÃO ==========
def create_agent(agent_id):
    config = premade_agents.get(agent_id) or st.session_state.custom_agents.get(agent_id)
    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config.get("backstory", ""),
        llm=ChatGroq(**model_config),
        verbose=True
    )

# ========== GERENCIAMENTO DE EXECUÇÃO ==========
tab_code, tab_run = st.tabs(["📄 Generate the Code", "⚡ Execute"])

with tab_code:
    if st.button("🔄 Generate Python Code"):
        if not groq_api_key:
            st.error("🔑 API Key Needed!")
        else:
            code = [
                "from crewai import Agent, Task, Crew\n",
                "from langchain_groq import ChatGroq\n\n",
                "# Configuração Inicial\n",
                f"llm_config = {model_config}\n\n",
                "os.environ['GROQ_API_KEY'] = 'SUA_CHAVE_AQUI'\n\n"
            ]
            
            # Agents
            unique_agents = list(set(st.session_state.workflow))
            for agent_id in unique_agents:
                config = premade_agents.get(agent_id) or st.session_state.custom_agents.get(agent_id)
                code.append(
                    f"{config['role'].replace(' ', '_')} = Agent(\n"
                    f"    role='{config['role']}',\n"
                    f"    goal='{config['goal']}',\n"
                    f"    backstory='{config.get('backstory', '')}',\n"
                    f"    llm=ChatGroq(**llm_config),\n"
                    f"    verbose=True\n)\n\n"
                )
            
            # Tasks
            code.append("# Tasks\n")
            for idx, task_key in enumerate(st.session_state.tasks_config):
                task = st.session_state.tasks_config[task_key]
                agent_config = premade_agents.get(task['agent_type']) or st.session_state.custom_agents.get(task['agent_type'])
                code.append(
                    f"task_{idx} = Task(\n"
                    f"    description='{task['description']}',\n"
                    f"    agent={agent_config['role'].replace(' ', '_')},\n"
                    f"    expected_output='{task['output']}'\n)\n\n"
                )
            
            # Crew
            code.append("crew = Crew(\n")
            code.append(f"    agents=[{', '.join([a['role'].replace(' ', '_') for a in [premade_agents.get(id) or st.session_state.custom_agents.get(id) for id in unique_agents]])}],\n")
            code.append(f"    tasks=[{', '.join([f'task_{i}' for i in range(len(st.session_state.tasks_config))])}],\n")
            code.append("    verbose=2\n)\n\n")
            code.append("result = crew.kickoff()\n")
            code.append("print(result)")
            
            st.code("".join(code), language="python")

with tab_run:
    if st.button("🚀 Execute Pipeline"):
        if not groq_api_key:
            st.error("🔑 Input the API Key Groq!")
        else:
            try:
                # Criar agents
                agents = {
                    agent_id: create_agent(agent_id)
                    for agent_id in set(st.session_state.workflow)
                }
                
                # Criar tasks
                tasks = []
                for task_key in st.session_state.tasks_config:
                    task_data = st.session_state.tasks_config[task_key]
                    tasks.append(Task(
                        description=task_data["description"],
                        agent=agents[task_data["agent_type"]],
                        expected_output=task_data["output"]
                    ))
                
                # Executar
                crew = Crew(
                    agents=list(agents.values()),
                    tasks=tasks,
                    verbose=2
                )
                
                with st.spinner("🧠 Processing..."):
                    result = crew.kickoff()
                    st.success("✅ Completed!")
                    st.markdown(f"```\n{result}\n```")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Gerenciamento do workflow
st.sidebar.divider()
if st.sidebar.button("🧹 Clear"):
    st.session_state.workflow = []
    st.session_state.tasks_config = {}
    st.session_state.custom_agents = {}
    st.rerun()