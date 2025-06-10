import pandas as pd
from pulp import *

# Carregar os dados
profissionais = pd.read_csv('profissionais.csv')
salas = pd.read_csv('salas.csv')
demandas = pd.read_csv('demandas.csv')

dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab']
turnos = ['manhã', 'tarde']

duracao_atendimento = 1  # em horas. Ajuste para 0.5 se cada atendimento durar 30 minutos

# Pesos de prioridade para tipos de atendimento
pesos = {'urgência': 3, 'triagem': 2, 'rotina': 1}

# Pré-processamento das disponibilidades
for dia in dias:
    col = f'disponibilidade_{dia}'
    profissionais[col] = profissionais[col].fillna('').apply(lambda x: [t.strip() for t in str(x).split(',') if t.strip()])

# Variáveis de decisão: x[(profissional, data, turno, tipo_atendimento)]
x = LpVariable.dicts(
    "Atendimento",
    ((p, row['data'], row['turno'], row['tipo_atendimento'])
     for p in profissionais['id_profissional']
     for _, row in demandas.iterrows()),
    cat='Binary'
)

# Variáveis de folga: demanda não atendida por atendimento
folga = LpVariable.dicts(
    "Folga",
    ((row['data'], row['turno'], row['tipo_atendimento'])
     for _, row in demandas.iterrows()),
    lowBound=0, cat='Integer'
)

# Variável auxiliar para o máximo de carga de trabalho
max_carga = LpVariable('max_carga', lowBound=0)

# Modelo
model = LpProblem("Escalonamento_Cuidar_Bem", LpMinimize)

# Função objetivo: minimizar tempo de espera ponderado, folgas e equilibrar carga de trabalho
model += (
    -lpSum(x[(p, row['data'], row['turno'], row['tipo_atendimento'])] * pesos[row['tipo_atendimento']]
           for p in profissionais['id_profissional']
           for _, row in demandas.iterrows()) # Agora este termo é um 'benefício' (negativo na minimização)
    + 10 * lpSum(folga[(row['data'], row['turno'], row['tipo_atendimento'])] * pesos[row['tipo_atendimento']]
          for _, row in demandas.iterrows())  # penalidade alta para demanda não atendida
    + 0.1 * max_carga  # Peso para equilíbrio de carga
)

# 1. Atender toda a demanda prevista (permitindo folga)
for _, row in demandas.iterrows():
    model += (
        lpSum(x[(p, row['data'], row['turno'], row['tipo_atendimento'])]
              for p in profissionais['id_profissional']) + folga[(row['data'], row['turno'], row['tipo_atendimento'])] >= row['quantidade_prevista'],
        f"Demanda_{row['data']}_{row['turno']}_{row['tipo_atendimento']}"
    )

# 2. Respeitar disponibilidade dos profissionais
for _, prof in profissionais.iterrows():
    for _, row in demandas.iterrows():
        dia_semana = row['dia_semana']
        turno = row['turno']
        if turno not in prof[f'disponibilidade_{dia_semana}']:
            model += (
                x[(prof['id_profissional'], row['data'], turno, row['tipo_atendimento'])] == 0,
                f"Disponibilidade_{prof['id_profissional']}_{row['data']}_{turno}_{row['tipo_atendimento']}"
            )

# 3. Respeitar carga horária máxima semanal (ajustável pela duração do atendimento)
for _, prof in profissionais.iterrows():
    carga_prof = lpSum(x[(prof['id_profissional'], row['data'], row['turno'], row['tipo_atendimento'])] * duracao_atendimento
                      for _, row in demandas.iterrows())
    model += (carga_prof <= prof['carga_horaria_max'], f"CargaHoraria_{prof['id_profissional']}")
    # Equilíbrio de carga: cada carga <= max_carga
    model += (carga_prof <= max_carga, f"EquilibrioCarga_{prof['id_profissional']}")

# 4. Capacidade das salas por turno (somando todos os tipos de atendimento)
for data in demandas['data'].unique():
    for turno in turnos:
        dia = demandas[demandas['data'] == data]['dia_semana'].iloc[0]
        capacidade_total = salas[salas['dias_funcionamento'].str.contains(dia) & salas['turnos_disponiveis'].str.contains(turno)]['capacidade'].sum()
        model += (
            lpSum(x[(p, data, turno, tipo)]
                  for p in profissionais['id_profissional']
                  for tipo in demandas[(demandas['data'] == data) & (demandas['turno'] == turno)]['tipo_atendimento'].unique()) <= capacidade_total,
            f"CapacidadeSalas_{data}_{turno}"
        )

# Diagnóstico rápido de capacidade e carga horária
for _, row in demandas.iterrows():
    dia = row['dia_semana']
    turno = row['turno']
    capacidade_total = salas[salas['dias_funcionamento'].str.contains(dia) & salas['turnos_disponiveis'].str.contains(turno)]['capacidade'].sum()
    print(f"{row['data']} {turno}: Demanda={row['quantidade_prevista']} Capacidade={capacidade_total}")

total_carga = profissionais['carga_horaria_max'].sum()
total_demanda = demandas['quantidade_prevista'].sum()
print(f"Carga horária total disponível: {total_carga}")
print(f"Demanda total prevista: {total_demanda}")

# Resolver
model.solve()

# Resultados
print("\nAlocação de atendimentos por profissional:")
for v in model.variables():
    if v.name.startswith('Atendimento') and v.varValue > 0:
        print(v.name, '=', v.varValue)

print("\nDemandas não atendidas (folga):")
for v in model.variables():
    if v.name.startswith('Folga') and v.varValue > 0:
        print(v.name, '=', v.varValue)

print("\nStatus:", LpStatus[model.status])
print("Custo total:", value(model.objective)) 