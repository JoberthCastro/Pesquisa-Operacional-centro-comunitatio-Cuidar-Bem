# Agendamento e Escalonamento Psicológico com Programação Linear

Este projeto utiliza programação linear para otimizar o agendamento de atendimentos psicológicos, considerando a disponibilidade de profissionais, salas e a demanda de pacientes. O projeto evoluiu através de dois modelos principais, cada um com foco em diferentes aspectos da otimização.

## Modelos Implementados

### 1. Modelo de Agendamento Básico (`agendamento_psicologico.py`)

Este modelo inicial foca na maximização do número total de atendimentos, balanceando a distribuição entre salas e horários. Ele considera as seguintes restrições:

*   **Disponibilidade de Psicólogos:** Cada psicólogo pode realizar apenas um atendimento por horário.
*   **Disponibilidade de Salas:** Cada sala pode ser utilizada por apenas um atendimento por horário.
*   **Disponibilidade de Pacientes:** Cada paciente pode ser agendado para apenas um horário.
*   **Balanceamento de Salas:** Limita o número de atendimentos por sala para garantir uma distribuição mais equitativa.

**Objetivo:** Maximizar o total de atendimentos agendados.

### 2. Modelo de Escalonamento Avançado (`modelo_escalonamento.py`)

Este modelo é mais abrangente e visa minimizar o custo total dos atendimentos, levando em conta a prioridade dos tipos de atendimento e a gestão de demandas não atendidas. As principais características e restrições incluem:

*   **Tipos de Atendimento e Prioridades:** Diferencia atendimentos por tipo (e.g., psicoterapia, avaliação) e permite atribuir custos ou prioridades a eles.
*   **Variável de Folga (`Folga`):** Representa as demandas de pacientes que não puderam ser atendidas, permitindo a quantificação da demanda reprimida.
*   **Balanceamento de Carga de Trabalho:** Permite distribuir a carga de trabalho entre os psicólogos de forma mais equilibrada.

**Objetivo:** Minimizar o custo total dos atendimentos, considerando prioridades e penalidades por demandas não atendidas. Um custo menor significa mais atendimentos agendados e menos demandas não atendidas.

## Dados

Os dados para os modelos são carregados a partir de arquivos CSV:

*   `profissionais.csv`: Contém informações sobre os psicólogos, incluindo sua disponibilidade.
*   `salas.csv`: Detalha as salas disponíveis para atendimento.
*   `demandas.csv`: Lista as demandas dos pacientes, incluindo o tipo de atendimento solicitado.

## Como Rodar os Modelos

1.  **Instalação de Dependências:** Certifique-se de ter o Python instalado. As dependências do projeto estão listadas no arquivo `requirements.txt`. Você pode instalá-las usando pip:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Executar o Modelo de Agendamento Básico:**
    Para rodar o modelo `agendamento_psicologico.py`:
    ```bash
    python agendamento_psicologico.py
    ```

3.  **Executar o Modelo de Escalonamento Avançado:**
    Para rodar o modelo `modelo_escalonamento.py`:
    ```bash
    python modelo_escalonamento.py
    ```
    Após a execução, os resultados (atendimentos agendados, folgas, etc.) serão impressos no console.

## Resultados Atuais e Análise Comparativa

Para uma compreensão aprofundada do desempenho de cada modelo, executamos os três modelos e coletamos os seguintes resultados:

### Modelo de Agendamento Psicológico (`agendamento_psicologico.py`)

Este modelo, após otimizações recentes, demonstra uma alocação eficiente com um excelente balanceamento de carga de trabalho.

*   **Status:** Ótimo
*   **Total de atendimentos ponderados:** 198.0
*   **Carga Horária por Profissional:** Todos os profissionais (Ana Souza, Carla Dias, Luana Silva) atingiram 20.0 horas, indicando uma distribuição de carga de trabalho perfeitamente equilibrada.
*   **Utilização de Salas:** A capacidade das salas foi bem utilizada na maioria dos turnos, embora alguns turnos (ex: 2024-06-11 tarde, 2024-06-14 tarde, 2024-06-15 tarde) tenham tido capacidade ociosa.

### Modelo de Escalonamento Avançado (`modelo_escalonamento.py`)

Este modelo continua a ser a solução mais robusta para a otimização geral, focando na minimização de custos e no atendimento prioritário das demandas.

*   **Status:** Ótimo
*   **Custo Total:** -440.1 (um valor menor indica melhor desempenho, maximizando atendimentos ponderados e minimizando penalidades)
*   **Atendimentos Alocados:** O modelo aloca eficientemente diversos tipos de atendimentos por profissional, demonstrando a capacidade de gerenciar uma variedade de demandas.
*   **Demandas Não Atendidas (Folga):** Existem algumas demandas não atendidas, o que é esperado em um cenário complexo, mas o modelo as penaliza de forma a priorizar as mais importantes.

### Solução Aleatória (`solucao_aleatoria.py`)

A versão atualizada da solução aleatória incorpora maior variabilidade, refletindo um cenário sem otimização.

*   **Atendimentos Ponderados Atendidos:** 176.71 (inferior ao modelo otimizado de agendamento psicológico)
*   **Total de Atendimentos Alocados:** 84 (significativamente menor que a capacidade dos modelos otimizados)
*   **Carga Máxima Individual (para equilíbrio):** 20 horas (no entanto, a distribuição geral da carga de trabalho é menos equilibrada, com profissionais variando de 8 a 20 horas)
*   **Custo Total:** -119.71 (consideravelmente mais alto que o modelo de escalonamento, indicando uma solução menos eficiente em termos de custo/benefício)
*   **Demandas Não Atendidas:** A solução aleatória apresenta um número maior e menos estruturado de demandas não atendidas.

### Conclusão Comparativa

A combinação do **Modelo de Escalonamento Avançado** e do **Modelo de Agendamento Psicológico** oferece uma solução robusta e eficiente. O **Modelo de Escalonamento** atua como uma estrutura abrangente que minimiza o custo total e gerencia prioridades. O **Modelo de Agendamento Psicológico**, por sua vez, complementa ao otimizar especificamente o agendamento de consultas psicológicas, garantindo um excelente balanceamento da carga de trabalho entre os profissionais.

A **Solução Aleatória** serve como uma linha de base crucial, evidenciando o valor da programação linear ao mostrar que uma alocação sem otimização resulta em menos atendimentos, distribuição de carga de trabalho desequilibrada e um custo muito menos favorável.

## 👥 Equipe
- **Joberth Emanoel da Conceição Mateo Castro** - [GitHub](https://github.com/JoberthCastro) | [LinkedIn](https://www.linkedin.com/in/joberth-castro-013840252)  
- **Maria Clara Cutrim Nunes Costa** - [LinkedIn](https://www.linkedin.com/in/maria-clara-cutrim-nunes-costa-55b7a8248/)  
- **Wesley Silva Gomes** - [GitHub](https://github.com/WesDevss) | [LinkedIn](https://www.linkedin.com/in/wesley-silva-gomes-9bb195259/)
- **Anderson Felipe Silva Aires** - [LinkedIn](https://www.linkedin.com/in/anderson-aires-b23720230/) 