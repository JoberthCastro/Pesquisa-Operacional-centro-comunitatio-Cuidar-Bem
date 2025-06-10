import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df_prof = pd.read_csv('profissionais.csv')
df_salas = pd.read_csv('salas.csv')
df_demanda = pd.read_csv('demandas.csv')

dias = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab']
turnos = ['manhã', 'tarde']

# 1. Gráfico: Demanda prevista por tipo e turno ao longo da semana
plt.figure(figsize=(14,6))
for tipo in df_demanda['tipo_atendimento'].unique():
    dados = df_demanda[df_demanda['tipo_atendimento'] == tipo]
    plt.plot(dados['data'] + ' ' + dados['turno'], dados['quantidade_prevista'], marker='o', label=tipo)
plt.xticks(rotation=90)
plt.ylabel('Demanda Prevista')
plt.title('Demanda Prevista por Tipo de Atendimento e Turno')
plt.legend()
plt.tight_layout()
plt.savefig('apres_demanda_prevista.png')
plt.close()

# 2. Gráfico: Capacidade total das salas por turno
capacidade_turno = []
labels_turno = []
for dia in dias:
    for turno in turnos:
        cap = df_salas[df_salas['dias_funcionamento'].str.contains(dia) & df_salas['turnos_disponiveis'].str.contains(turno)]['capacidade'].sum()
        capacidade_turno.append(cap)
        labels_turno.append(f'{dia}\n{turno}')
plt.figure(figsize=(10,5))
plt.bar(labels_turno, capacidade_turno, color='mediumseagreen')
plt.ylabel('Capacidade Total das Salas')
plt.title('Capacidade Total das Salas por Dia e Turno')
plt.tight_layout()
plt.savefig('apres_capacidade_salas.png')
plt.close()

# 3. Gráfico: Carga horária máxima dos profissionais
plt.figure(figsize=(8,5))
plt.bar(df_prof['nome'], df_prof['carga_horaria_max'], color='cornflowerblue')
plt.ylabel('Carga Horária Máxima (h/semana)')
plt.title('Carga Horária Máxima dos Profissionais')
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('apres_carga_profissionais.png')
plt.close()

# 4. Gráfico: Disponibilidade dos profissionais por dia da semana
plt.figure(figsize=(12,6))
for idx, row in df_prof.iterrows():
    disponiveis = [len(str(row[f'disponibilidade_{dia}']).split(',')) if pd.notnull(row[f'disponibilidade_{dia}']) else 0 for dia in dias]
    plt.plot(dias, disponiveis, marker='o', label=row['nome'])
plt.ylabel('Turnos Disponíveis')
plt.title('Disponibilidade dos Profissionais por Dia da Semana')
plt.legend()
plt.tight_layout()
plt.savefig('apres_disponibilidade_profissionais.png')
plt.close()

print('Gráficos gerados:')
print('- apres_demanda_prevista.png')
print('- apres_capacidade_salas.png')
print('- apres_carga_profissionais.png')
print('- apres_disponibilidade_profissionais.png') 