from pulp import *
import pandas as pd

# Carregar dados dos arquivos CSV
profissionais_df = pd.read_csv('profissionais.csv')
salas_df = pd.read_csv('salas.csv')
demandas_df = pd.read_csv('demandas.csv')

# Criar o problema
prob = LpProblem("Agendamento_Psicologico", LpMaximize)

# Dados do problema
psicologos = profissionais_df[profissionais_df['especialidade'] == 'Psicólogo']['id_profissional'].tolist()
salas = salas_df['id_sala'].tolist()
dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab']
turnos = ['manhã', 'tarde']

# Variáveis de decisão
# x[profissional, sala, dia, turno] = 1 se o profissional atende na sala no dia e turno
x = LpVariable.dicts("atendimento",
                     ((p, s, d, t) for p in psicologos 
                      for s in salas 
                      for d in dias 
                      for t in turnos),
                     cat='Binary')

# Função objetivo: Maximizar o número total de atendimentos
prob += lpSum(x[p, s, d, t] for p in psicologos for s in salas for d in dias for t in turnos)

# Restrição 1: Cada profissional só pode atender em uma sala por turno
for p in psicologos:
    for d in dias:
        for t in turnos:
            # Verificar disponibilidade do profissional
            disponibilidade = profissionais_df[profissionais_df['id_profissional'] == p][f'disponibilidade_{d}'].iloc[0]
            if pd.notna(disponibilidade) and t in disponibilidade.split(','):
                prob += lpSum(x[p, s, d, t] for s in salas) <= 1

# Restrição 2: Cada sala só pode ser utilizada por um profissional por turno
for s in salas:
    for d in dias:
        for t in turnos:
            # Verificar disponibilidade da sala
            dias_func = salas_df[salas_df['id_sala'] == s]['dias_funcionamento'].iloc[0].split(',')
            turnos_disp = salas_df[salas_df['id_sala'] == s]['turnos_disponiveis'].iloc[0].split(',')
            if d in dias_func and t in turnos_disp:
                prob += lpSum(x[p, s, d, t] for p in psicologos) <= 1

# Restrição 3: Respeitar a demanda prevista
for d in dias:
    for t in turnos:
        demanda = demandas_df[(demandas_df['dia_semana'] == d) & 
                            (demandas_df['turno'] == t)]['quantidade_prevista'].sum()
        if demanda > 0:
            prob += lpSum(x[p, s, d, t] for p in psicologos for s in salas) <= demanda

# Restrição 4: Balancear a distribuição de atendimentos entre as salas
# Calcula o número total de atendimentos possíveis
total_atendimentos = len(dias) * len(turnos) * len(psicologos)
# Define o limite máximo de atendimentos por sala (média + 20%)
limite_por_sala = int((total_atendimentos / len(salas)) * 1.2)

for s in salas:
    prob += lpSum(x[p, s, d, t] for p in psicologos for d in dias for t in turnos) <= limite_por_sala

# Resolver o problema
prob.solve()

# Imprimir resultados
print(f"Status: {LpStatus[prob.status]}")
print(f"Total de atendimentos: {value(prob.objective)}")

# Imprimir agendamento
print("\nAgendamento:")
for p in psicologos:
    for s in salas:
        for d in dias:
            for t in turnos:
                if value(x[p, s, d, t]) == 1:
                    nome_prof = profissionais_df[profissionais_df['id_profissional'] == p]['nome'].iloc[0]
                    print(f"Profissional {nome_prof} (ID: {p}) atenderá na Sala {s} no {d} à {t}")

# Imprimir estatísticas por sala
print("\nEstatísticas por Sala:")
for s in salas:
    total_sala = sum(value(x[p, s, d, t]) for p in psicologos for d in dias for t in turnos)
    print(f"Sala {s}: {total_sala} atendimentos") 