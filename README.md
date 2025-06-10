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
## 👥 Equipe
- **Joberth Emanoel da Conceição Mateo Castro** - [GitHub](https://github.com/JoberthCastro) | [LinkedIn](https://www.linkedin.com/in/joberth-castro-013840252)  
- **Maria Clara Cutrim Nunes Costa** - [LinkedIn](https://www.linkedin.com/in/maria-clara-cutrim-nunes-costa-55b7a8248/)  
- **Wesley Silva Gomes** - [GitHub](https://github.com/WesDevss) | [LinkedIn](https://www.linkedin.com/in/wesley-silva-gomes-9bb195259/)
- **Anderson Felipe Silva Aires** - [LinkedIn](https://www.linkedin.com/in/anderson-aires-b23720230/)  
Após a execução, os resultados (atendimentos agendados, folgas, etc.) serão impressos no console. 