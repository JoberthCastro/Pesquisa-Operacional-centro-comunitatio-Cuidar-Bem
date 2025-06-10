from pulp import *
import pandas as pd

# Carregar dados dos arquivos CSV
profissionais_df = pd.read_csv('profissionais.csv')
salas_df = pd.read_csv('salas.csv')
demandas_df = pd.read_csv('demandas.csv')

# Duração padrão de um atendimento em horas
duracao_atendimento = 1

# Número máximo de atendimentos que um profissional pode realizar em um único turno
MAX_ATENDIMENTOS_POR_TURNO_PROF = 4

# Pesos de prioridade para tipos de atendimento (ajustados para dar mais ênfase às prioridades)
pesos = {'urgência': 5, 'triagem': 3, 'rotina': 1}

# Criar o problema
prob = LpProblem("Agendamento_Psicologico", LpMaximize)

# Dados do problema
psicologos = profissionais_df[profissionais_df['especialidade'] == 'Psicólogo']['id_profissional'].tolist()
datas_unicas = demandas_df['data'].unique().tolist()
turnos = ['manhã', 'tarde']
salas = salas_df['id_sala'].tolist()

# Variáveis de decisão
x = LpVariable.dicts("atendimento",
                     ((p, data, t, ta) for p in psicologos 
                      for data in datas_unicas
                      for t in turnos
                      for ta in demandas_df['tipo_atendimento'].unique()),
                     lowBound=0, cat='Integer')

# Variável de decisão para atendimentos realizados
atendimento_realizado = LpVariable.dicts(
    "AtendimentoRealizado",
    ((row['data'], row['turno'], row['tipo_atendimento'])
     for _, row in demandas_df.iterrows()),
    lowBound=0, cat='Integer'
)

# Nova variável para controlar o desbalanceamento da carga horária
desbalanceamento = LpVariable("Desbalanceamento", lowBound=0)

# Função objetivo: Maximizar a soma ponderada dos atendimentos realizados e minimizar o desbalanceamento
prob += lpSum(atendimento_realizado[(row['data'], row['turno'], row['tipo_atendimento'])] * pesos[row['tipo_atendimento']]
              for _, row in demandas_df.iterrows()) - 10 * desbalanceamento

# Restrição 1: Cada profissional só pode atender em no máximo um tipo de atendimento por turno
for p in psicologos:
    for data in datas_unicas:
        for t in turnos:
            dia_semana_atual = demandas_df[demandas_df['data'] == data]['dia_semana'].iloc[0]
            disponibilidade_prof = profissionais_df[profissionais_df['id_profissional'] == p][f'disponibilidade_{dia_semana_atual}'].iloc[0]
            if pd.isna(disponibilidade_prof) or t not in disponibilidade_prof.split(','):
                for ta_inner in demandas_df['tipo_atendimento'].unique():
                    prob += x[p, data, t, ta_inner] == 0, f"IndisponibilidadeProf_{p}_{data}_{t}_{ta_inner}"
            else:
                prob += lpSum(x[p, data, t, ta_inner] for ta_inner in demandas_df['tipo_atendimento'].unique()) <= MAX_ATENDIMENTOS_POR_TURNO_PROF, f"MaxAtendimentosTurno_{p}_{data}_{t}"

# Restrição 2: Capacidade total das salas por turno
for data in datas_unicas:
    for t in turnos:
        dia_semana_atual = demandas_df[demandas_df['data'] == data]['dia_semana'].iloc[0]
        capacidade_total_salas = salas_df[salas_df['dias_funcionamento'].apply(lambda x: dia_semana_atual in x.split(',')) & 
                                          salas_df['turnos_disponiveis'].apply(lambda x: t in x.split(','))]['capacidade'].sum()
        
        prob += lpSum(x[p, data, t, ta] 
                      for p in psicologos 
                      for ta in demandas_df['tipo_atendimento'].unique()) <= capacidade_total_salas, f"CapacidadeTotalSalas_{data}_{t}"

# Restrição 3: Respeitar a carga horária máxima de cada profissional
for p in psicologos:
    total_horas_prof = lpSum(x[p, data_inner_carga, t_inner_carga, ta_inner_carga] * duracao_atendimento
                             for data_inner_carga in datas_unicas
                             for t_inner_carga in turnos
                             for ta_inner_carga in demandas_df['tipo_atendimento'].unique())
    max_carga = profissionais_df[profissionais_df['id_profissional'] == p]['carga_horaria_max'].iloc[0]
    prob += total_horas_prof <= max_carga, f"CargaHorariaMax_{p}"

# Nova restrição: Controlar o desbalanceamento da carga horária
carga_media = lpSum(x[p, data, t, ta] * duracao_atendimento
                    for p in psicologos
                    for data in datas_unicas
                    for t in turnos
                    for ta in demandas_df['tipo_atendimento'].unique()) / len(psicologos)

for p in psicologos:
    total_horas_prof = lpSum(x[p, data, t, ta] * duracao_atendimento
                            for data in datas_unicas
                            for t in turnos
                            for ta in demandas_df['tipo_atendimento'].unique())
    prob += total_horas_prof - carga_media <= desbalanceamento, f"DesbalanceamentoPos_{p}"
    prob += carga_media - total_horas_prof <= desbalanceamento, f"DesbalanceamentoNeg_{p}"

# Restrição 4: atendimento_realizado não pode exceder a quantidade prevista da demanda
for _, demanda_row in demandas_df.iterrows():
    data_demanda = demanda_row['data']
    turno_demanda = demanda_row['turno']
    tipo_atendimento_demanda = demanda_row['tipo_atendimento']
    quantidade_prevista_demanda = demanda_row['quantidade_prevista']

    prob += atendimento_realizado[(data_demanda, turno_demanda, tipo_atendimento_demanda)] <= quantidade_prevista_demanda

    prob += lpSum(x[(p, data_demanda, turno_demanda, tipo_atendimento_demanda)]
                  for p in psicologos) == atendimento_realizado[(data_demanda, turno_demanda, tipo_atendimento_demanda)]

# Resolver o problema
prob.solve()

# Imprimir resultados
print(f"Status: {LpStatus[prob.status]}")
print(f"Total de atendimentos ponderados: {value(prob.objective)}")

# Imprimir agendamento
print("\nAgendamento:")
for p in psicologos:
    for data in datas_unicas:
        for t in turnos:
            for ta in demandas_df['tipo_atendimento'].unique():
                if value(x[p, data, t, ta]) == 1:
                    nome_prof = profissionais_df[profissionais_df['id_profissional'] == p]['nome'].iloc[0]
                    print(f"Profissional {nome_prof} (ID: {p}) atenderá no {data} à {t} - Tipo: {ta}")

# Imprimir estatísticas de atendimentos por tipo de atendimento
print("\nEstatísticas por Tipo de Atendimento (Demanda Atendida):")
for (data, turno, tipo), quantidade in atendimento_realizado.items():
    if value(quantidade) > 0:
        print(f"  Data: {data}, Turno: {turno}, Tipo: {tipo}, Atendimentos: {value(quantidade)}")

# Imprimir estatísticas por profissional (carga horária)
print("\nCarga horária por Profissional:")
for p in psicologos:
    total_horas_prof = sum(value(x[p, data, t, ta]) * duracao_atendimento
                           for data in datas_unicas
                           for t in turnos
                           for ta in demandas_df['tipo_atendimento'].unique())
    nome_prof = profissionais_df[profissionais_df['id_profissional'] == p]['nome'].iloc[0]
    print(f"  Profissional {nome_prof} (ID: {p}): {total_horas_prof} horas")

# Imprimir estatísticas por sala
print("\nCapacidade de Salas Utilizada (por Data e Turno):")
for data in datas_unicas:
    for t in turnos:
        dia_semana_atual = demandas_df[demandas_df['data'] == data]['dia_semana'].iloc[0]
        capacidade_total_salas = salas_df[salas_df['dias_funcionamento'].apply(lambda x: dia_semana_atual in x.split(',')) & 
                                          salas_df['turnos_disponiveis'].apply(lambda x: t in x.split(','))]['capacidade'].sum()
        
        atendimentos_neste_slot = sum(value(x[p, data, t, ta]) 
                                     for p in psicologos 
                                     for ta in demandas_df['tipo_atendimento'].unique())
        print(f"  {data} {t}: Capacidade Total de Salas = {capacidade_total_salas}, Atendimentos Alocados = {atendimentos_neste_slot}") 