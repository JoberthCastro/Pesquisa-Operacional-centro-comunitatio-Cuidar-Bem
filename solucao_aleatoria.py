import pandas as pd
import random

# Carregar os dados
profissionais = pd.read_csv('profissionais.csv')
salas = pd.read_csv('salas.csv')
demandas = pd.read_csv('demandas.csv')

dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab']
turnos = ['manhã', 'tarde']

duracao_atendimento = 1  # em horas

# Pesos de prioridade para tipos de atendimento (agora aleatórios)
pesos_base = {'urgência': 3, 'triagem': 2, 'rotina': 1}
pesos = {k: v * random.uniform(0.8, 1.2) for k, v in pesos_base.items()}

# Pré-processamento das disponibilidades
for dia in dias:
    col = f'disponibilidade_{dia}'
    profissionais[col] = profissionais[col].fillna('').apply(lambda x: [t.strip() for t in str(x).split(',') if t.strip()])

# Inicializar estruturas para a alocação aleatória
alocacao_aleatoria = []
folga_aleatoria = {}
carga_trabalho_profissionais = {p_id: 0 for p_id in profissionais['id_profissional']}

# Função para inicializar a capacidade das salas por dia/turno
def inicializar_capacidade_salas():
    cap_salas = {}
    for data in demandas['data'].unique():
        for turno in turnos:
            dia_semana = demandas[demandas['data'] == data]['dia_semana'].iloc[0]
            capacidade_total = salas[salas['dias_funcionamento'].str.contains(dia_semana) & 
                                   salas['turnos_disponiveis'].str.contains(turno)]['capacidade'].sum()
            # Adiciona aleatoriedade na capacidade
            capacidade_total = int(capacidade_total * random.uniform(0.9, 1.1))
            cap_salas[(data, turno)] = {'total': capacidade_total, 'ocupada': 0}
    return cap_salas

capacidade_salas_info = inicializar_capacidade_salas()

# Converter demandas para lista e embaralhar completamente
demandas_lista = demandas.to_dict('records')
random.shuffle(demandas_lista)

# Implementação da alocação verdadeiramente aleatória
for demanda_row in demandas_lista:
    data_demanda = demanda_row['data']
    turno_demanda = demanda_row['turno']
    tipo_atendimento_demanda = demanda_row['tipo_atendimento']
    quantidade_prevista = demanda_row['quantidade_prevista']
    dia_semana_demanda = demanda_row['dia_semana']

    # Adiciona aleatoriedade na quantidade prevista
    quantidade_prevista = int(quantidade_prevista * random.uniform(0.9, 1.1))
    quantidade_prevista = max(1, quantidade_prevista)  # Garante pelo menos 1 atendimento

    atendimentos_alocados_para_demanda = 0
    
    # Lista de profissionais elegíveis para esta demanda
    profissionais_elegiveis = []
    for _, prof in profissionais.iterrows():
        prof_id = prof['id_profissional']
        if turno_demanda in prof[f'disponibilidade_{dia_semana_demanda}'] and \
           carga_trabalho_profissionais[prof_id] + duracao_atendimento <= prof['carga_horaria_max']:
            profissionais_elegiveis.append(prof_id)
    
    # Embaralhar a lista de profissionais elegíveis
    random.shuffle(profissionais_elegiveis)

    # Tentar alocar o máximo possível da demanda
    for _ in range(quantidade_prevista):
        alocado_nesta_iteracao = False
        # Embaralhar novamente os profissionais a cada tentativa
        random.shuffle(profissionais_elegiveis)
        
        for prof_id in profissionais_elegiveis:
            # Verificar capacidade da sala com aleatoriedade
            capacidade_atual = capacidade_salas_info[(data_demanda, turno_demanda)]['ocupada']
            capacidade_maxima = capacidade_salas_info[(data_demanda, turno_demanda)]['total']
            
            # Adiciona chance aleatória de rejeitar mesmo com capacidade disponível
            if random.random() < 0.1:  # 10% de chance de rejeitar
                continue
                
            if capacidade_atual < capacidade_maxima:
                if carga_trabalho_profissionais[prof_id] + duracao_atendimento <= profissionais[profissionais['id_profissional'] == prof_id]['carga_horaria_max'].iloc[0]:
                    # Alocar atendimento
                    alocacao_aleatoria.append({
                        'profissional': prof_id,
                        'data': data_demanda,
                        'turno': turno_demanda,
                        'tipo_atendimento': tipo_atendimento_demanda
                    })
                    carga_trabalho_profissionais[prof_id] += duracao_atendimento
                    capacidade_salas_info[(data_demanda, turno_demanda)]['ocupada'] += 1
                    atendimentos_alocados_para_demanda += 1
                    alocado_nesta_iteracao = True
                    break
        
        if not alocado_nesta_iteracao:
            break
    
    # Calcular folga para esta demanda
    folga_para_demanda = quantidade_prevista - atendimentos_alocados_para_demanda
    if folga_para_demanda > 0:
        folga_aleatoria[(data_demanda, turno_demanda, tipo_atendimento_demanda)] = folga_para_demanda

# Calcular métricas de desempenho com pesos aleatórios
total_demanda_atendida_aleatoria = sum(pesos[item['tipo_atendimento']] for item in alocacao_aleatoria)
total_folga_aleatoria = sum(folga_aleatoria.values())

# Calcular o custo com pesos aleatórios
max_carga_aleatoria = max(carga_trabalho_profissionais.values()) if carga_trabalho_profissionais else 0
penalidade_folga = random.uniform(1.8, 2.2)  # Penalidade aleatória para folga
penalidade_carga = random.uniform(0.08, 0.12)  # Penalidade aleatória para carga

custo_aleatorio = -total_demanda_atendida_aleatoria + \
                 (penalidade_folga * sum(pesos[key[2]] * value for key, value in folga_aleatoria.items())) + \
                 (penalidade_carga * max_carga_aleatoria)

print(f"Weighted Total Demand Attended (Aleatória): {total_demanda_atendida_aleatoria}")
print(f"Max Load (Aleatória): {max_carga_aleatoria}")

print("\n--- Resultados da Solução Aleatória ---")
print("Total de atendimentos alocados:", len(alocacao_aleatoria))
print("Demandas não atendidas (folga):")
for (data, turno, tipo), quantidade in folga_aleatoria.items():
    print(f"  Data: {data}, Turno: {turno}, Tipo: {tipo}, Quantidade: {quantidade}")
print("Carga de trabalho dos profissionais:")
for prof_id, carga in carga_trabalho_profissionais.items():
    print(f"  Profissional {prof_id}: {carga} horas")
print("Carga máxima individual (para equilíbrio):", max_carga_aleatoria)
print(f"Custo total (comparável ao objetivo do modelo otimizado): {custo_aleatorio}") 