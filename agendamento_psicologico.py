import pandas as pd
from pulp import *

# Carregar os dados de profissionais, salas e demandas a partir de arquivos CSV.
# Estes dados são a base para a formulação do problema de otimização.
profissionais = pd.read_csv('profissionais.csv')
salas = pd.read_csv('salas.csv')
demandas = pd.read_csv('demandas.csv')

# Definir os dias da semana e turnos de operação que são considerados no agendamento.
dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab']
turnos = ['manhã', 'tarde']

# Definir a duração padrão de cada atendimento em horas. Este valor é crucial para
# o cálculo da carga horária e utilização das salas.
duracao_atendimento = 1  # 1 hora por atendimento

# Definir pesos para diferentes tipos de atendimento. Estes pesos são utilizados
# na função objetivo para priorizar atendimentos mais urgentes ou importantes.
pesos = {'urgência': 5, 'triagem': 3, 'rotina': 1}

# Pré-processamento das disponibilidades dos profissionais.
# A coluna de disponibilidade em cada dia é convertida de uma string para uma lista
# de turnos, facilitando o acesso e a validação no modelo.
for dia in dias:
    col = f'disponibilidade_{dia}'
    profissionais[col] = profissionais[col].fillna('').apply(lambda x: [t.strip() for t in str(x).split(',') if t.strip()])

# Criar o problema de Programação Linear. Definido como um problema de maximização
# (`LpMaximize`), pois o objetivo principal é maximizar o valor total dos atendimentos.
prob = LpProblem("Agendamento_Psicologico", LpMaximize)

# =============================================================================
# Variáveis de Decisão
# =============================================================================

# Variável binária `x[(p, d, t, s, tipo_atendimento)]`:
# Representa se um profissional `p` está agendado para um atendimento do tipo
# `tipo_atendimento` em uma data `d`, turno `t`, na sala `s`.
# Valor 1: o agendamento ocorre; Valor 0: não ocorre.
x = LpVariable.dicts("x", 
                      [(p, d, t, s, tipo_atendimento) 
                       for p in profissionais['id_profissional'] 
                       for d in demandas['data'] 
                       for t in turnos 
                       for s in salas['id_sala'] 
                       for tipo_atendimento in demandas['tipo_atendimento'].unique()], 
                      0, 1, LpBinary)

# Variável contínua `folga[(data, turno, tipo_atendimento)]`:
# Indica a quantidade de demandas de um `tipo_atendimento` específico em uma
# `data` e `turno` que não puderam ser atendidas. Essencial para quantificar
# a demanda reprimida e aplicar penalidades na função objetivo.
folga = LpVariable.dicts("folga", 
                           [(d, t, tipo) 
                            for d in demandas['data'] 
                            for t in turnos 
                            for tipo in demandas['tipo_atendimento'].unique()], 
                           0, None, LpContinuous)

# Variável contínua `desbalanceamento[p]`:
# Mede o desvio absoluto da carga horária de um profissional `p` em relação à
# carga horária média esperada de todos os profissionais. Utilizada para penalizar
# desequilíbrios na distribuição de trabalho na função objetivo.
desbalanceamento = LpVariable.dicts("desbalanceamento", 
                                      [p for p in profissionais['id_profissional']], 
                                      0, None, LpContinuous)

# =============================================================================
# Função Objetivo
# =============================================================================

# A função objetivo busca MAXIMIZAR o benefício total dos atendimentos agendados
# e MINIMIZAR as penalidades associadas às demandas não atendidas (folga) e ao
# desequilíbrio da carga de trabalho dos profissionais.
# Componente 1: Soma ponderada dos atendimentos alocados (benefício).
# Componente 2: Penalidade por demandas não atendidas (folga), ponderada pelos `pesos`.
# Componente 3: Penalidade pelo desbalanceamento da carga de trabalho dos profissionais.
prob += lpSum(pesos[tipo_atendimento] * x[(p, d, t, s, tipo_atendimento)] * duracao_atendimento
              for p, d, t, s, tipo_atendimento in x) \
        - lpSum(pesos[tipo] * folga[(d, t, tipo)] for d, t, tipo in folga) \
        - 0.1 * lpSum(desbalanceamento[p] for p in profissionais['id_profissional']),
        "Total_de_Atendimentos_Ponderados_e_Balanceamento"

# =============================================================================
# Restrições
# =============================================================================

# Restrição 1: Um profissional só pode realizar um atendimento por turno específico.
# Garante que cada psicólogo esteja agendado para, no máximo, um atendimento
# por cada combinação de dia e turno, respeitando sua disponibilidade.
for p in profissionais['id_profissional']:
    for d in demandas['data']:
        dia_semana = demandas[demandas['data'] == d]['dia_semana'].iloc[0]
        for t in turnos:
            if t in profissionais[profissionais['id_profissional'] == p][f'disponibilidade_{dia_semana}'].iloc[0]:
                prob += lpSum(x[(p, d, t, s, tipo)] 
                              for s in salas['id_sala'] 
                              for tipo in demandas['tipo_atendimento'].unique()) <= 1, \
                          f"R1_Profissional_Um_Atendimento_Por_Turno_{p}_{d}_{t}"

# Restrição 2: Uma sala só pode ser usada por um profissional por turno.
# Assegura que cada sala seja utilizada por, no máximo, um profissional em cada
# combinação de dia e turno, conforme a disponibilidade da sala.
for s in salas['id_sala']:
    for d in demandas['data']:
        dia_semana_sala = salas[salas['id_sala'] == s]['dias_funcionamento'].iloc[0]
        for t in turnos:
            # Verifica se a sala está disponível para o dia da semana e turno.
            if pd.isna(dia_semana_sala) or (dia_semana in dia_semana_sala.split(',') and \
                                            t in salas[salas['id_sala'] == s]['turnos_disponiveis'].iloc[0].split(',')):
                prob += lpSum(x[(p, d, t, s, tipo)] 
                              for p in profissionais['id_profissional'] 
                              for tipo in demandas['tipo_atendimento'].unique()) <= 1, \
                          f"R2_Sala_Exclusiva_Por_Turno_{s}_{d}_{t}"

# Restrição 3: Atender a demanda prevista ou registrar folga.
# Para cada combinação de data, turno e tipo de atendimento, a soma dos atendimentos
# alocados (x) mais a quantidade de folga deve ser igual à demanda prevista.
for index, row in demandas.iterrows():
    data = row['data']
    turno = row['turno']
    tipo = row['tipo_atendimento']
    quantidade_prevista = row['quantidade_prevista']
    prob += lpSum(x[(p, data, turno, s, tipo)] 
                  for p in profissionais['id_profissional'] 
                  for s in salas['id_sala']) + folga[(data, turno, tipo)] == quantidade_prevista, \
              f"R3_Atender_Demanda_ou_Folga_{data}_{turno}_{tipo}"

# Restrição 4: Capacidade máxima da sala por turno.
# Garante que o número total de atendimentos agendados em uma sala não exceda
# sua capacidade máxima para aquele turno específico. Cada atendimento ocupa `duracao_atendimento`.
for s in salas['id_sala']:
    capacidade_sala = salas[salas['id_sala'] == s]['capacidade'].iloc[0]
    for d in demandas['data']:
        dia_semana_sala = salas[salas['id_sala'] == s]['dias_funcionamento'].iloc[0]
        for t in turnos:
            # Verifica se a sala está disponível para o dia da semana e turno.
            if pd.isna(dia_semana_sala) or (dia_semana in dia_semana_sala.split(',') and \
                                            t in salas[salas['id_sala'] == s]['turnos_disponiveis'].iloc[0].split(',')):
                prob += lpSum(x[(p, d, t, s, tipo)] * duracao_atendimento
                              for p in profissionais['id_profissional'] 
                              for tipo in demandas['tipo_atendimento'].unique()) <= capacidade_sala, \
                          f"R4_Capacidade_Sala_Por_Turno_{s}_{d}_{t}"

# Restrição 5: Carga horária máxima dos profissionais e balanceamento.
# Assegura que a carga horária total de cada profissional não exceda seu limite máximo.
# Além disso, define o `desbalanceamento[p_id]` como a diferença absoluta entre
# a carga horária do profissional `p_id` e a média esperada.
for p_id in profissionais['id_profissional']:
    carga_horaria_max = profissionais[profissionais['id_profissional'] == p_id]['carga_horaria_max'].iloc[0]
    # Calcula o total de horas agendadas para o profissional p_id.
    total_horas_p = lpSum(x[(p_id, d, t, s, tipo)] * duracao_atendimento 
                          for d in demandas['data'] 
                          for t in turnos 
                          for s in salas['id_sala'] 
                          for tipo in demandas['tipo_atendimento'].unique()
                          if (p_id, d, t, s, tipo) in x) # Garante que a chave existe no dicionário x
    prob += total_horas_p <= carga_horaria_max, f"R5_Carga_Horaria_Max_{p_id}"
    
    # Calculamos a média aproximada da carga horária esperada para todos os profissionais.
    # Esta média serve como um alvo para o balanceamento da carga de trabalho.
    media_carga_esperada = (sum(profissionais['carga_horaria_max']) * duracao_atendimento) / len(profissionais['id_profissional'])
    
    # Restrições para o desbalanceamento: modelam o valor absoluto.
    # `desbalanceamento[p_id]` deve ser maior ou igual à diferença positiva
    # e à diferença negativa entre `total_horas_p` e `media_carga_esperada`.
    prob += total_horas_p - media_carga_esperada <= desbalanceamento[p_id], f"R5_Desbalanceamento_Positivo_{p_id}"
    prob += media_carga_esperada - total_horas_p <= desbalanceamento[p_id], f"R5_Desbalanceamento_Negativo_{p_id}"

# =============================================================================
# Resolução do Problema
# =============================================================================

# Escreve o problema de Programação Linear em um arquivo no formato .lp.
# Isso é útil para depuração e para visualizar a estrutura do modelo.
prob.writeLP("agendamento_psicologico.lp")

# Resolve o problema usando o solver padrão (geralmente CBC, se disponível).
# O solver encontra os valores ótimos para as variáveis de decisão que satisfazem
# todas as restrições e otimizam a função objetivo.
prob.solve()

# Exibe o status da solução encontrada pelo solver (Optimal, Infeasible, Unbounded, etc.).
print("Status:", LpStatus[prob.status])

# =============================================================================
# Apresentação dos Resultados
# =============================================================================

print("\n--- Resultados do Agendamento Psicológico ---")

# Calcula e imprime o total de atendimentos ponderados atendidos.
# Percorre todas as variáveis de decisão `x` e soma os valores dos atendimentos
# que foram agendados, multiplicando-os pelos seus respectivos pesos.
total_atendimentos_ponderados = 0
for p, d, t, s, tipo_atendimento in x:
    if x[(p, d, t, s, tipo_atendimento)].varValue is not None and x[(p, d, t, s, tipo_atendimento)].varValue > 0:
        total_atendimentos_ponderados += pesos[tipo_atendimento] * duracao_atendimento

print(f"Total de atendimentos ponderados: {total_atendimentos_ponderados}")

# Detalha a carga de trabalho de cada profissional.
# Soma as horas de atendimento alocadas para cada profissional.
carga_trabalho_profissionais = {p_id: 0 for p_id in profissionais['id_profissional']}
for p, d, t, s, tipo_atendimento in x:
    if x[(p, d, t, s, tipo_atendimento)].varValue is not None and x[(p, d, t, s, tipo_atendimento)].varValue > 0:
        carga_trabalho_profissionais[p] += duracao_atendimento

print("\nCarga horária dos profissionais:")
for p_id, carga in carga_trabalho_profissionais.items():
    print(f"  Profissional {p_id}: {carga} horas")

# Detalha a utilização da capacidade das salas por data, turno e sala.
# Calcula a ocupação de cada sala e compara com sua capacidade máxima.
capacidade_salas_ocupada = {}
for d in demandas['data']:
    for t in turnos:
        for s in salas['id_sala']:
            # Soma os valores de x para calcular a ocupação de uma sala em um dado turno.
            ocupacao = sum(x[(p, d, t, s, tipo)].varValue for p in profissionais['id_profissional'] for tipo in demandas['tipo_atendimento'].unique() if (p, d, t, s, tipo) in x and x[(p, d, t, s, tipo)].varValue is not None)
            if ocupacao is not None and ocupacao > 0:
                capacidade_salas_ocupada[(d, t, s)] = ocupacao

print("\nUtilização da capacidade das salas:")
for (data, turno, sala), ocupacao in capacidade_salas_ocupada.items():
    capacidade_max = salas[salas['id_sala'] == sala]['capacidade'].iloc[0]
    print(f"  Data: {data}, Turno: {turno}, Sala: {sala}, Ocupação: {ocupacao:.0f}/{capacidade_max:.0f}")

# Detalha as demandas não atendidas (folga).
# Exibe a quantidade de cada tipo de demanda que não pôde ser agendada.
print("\nDemandas não atendidas (folga):")
folga_total = 0
for d, t, tipo in folga:
    if folga[(d, t, tipo)].varValue is not None and folga[(d, t, tipo)].varValue > 0:
        print(f"  Data: {d}, Turno: {t}, Tipo: {tipo}, Quantidade: {folga[(d, t, tipo)].varValue:.0f}")
        folga_total += folga[(d, t, tipo)].varValue

if folga_total == 0:
    print("  Todas as demandas foram atendidas.")

# Imprime o valor final da função objetivo. Este valor reflete o custo total
# minimizado, considerando os atendimentos agendados, as penalidades por folga
# e as penalidades por desbalanceamento de carga.
print(f"\nCusto Total do Objetivo (com penalidade de desbalanceamento): {prob.objective.value():.2f}") 