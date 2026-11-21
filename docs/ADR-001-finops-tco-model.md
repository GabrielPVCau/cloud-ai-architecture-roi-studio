# ADR-001: Modelagem FinOps (TCO 12 Meses) & Critério Build vs. Managed

- **Status:** Aceito
- **Data:** 2026-11-21
- **Contexto:** Propostas de GenAI frequentemente subestimam custos recorrentes de infraestrutura, egress e inferência, ou recomendam GPUs dedicadas prematuramente em volumes baixos.

## Decisão
Separar explicitamente no cálculo de TCO (`app/calculator.py`):
1. **Custo Fixo de Implantação (`implementation_cost_brl`)**;
2. **Custo Mensal de Infraestrutura Cloud** escalando com fator de volume e multiplicador de egress por provedor (`AWS`, `Azure`, `GCP`);
3. **Custo Mensal de Inferência IA:** variável por milhão de tokens (input/output) em modelos gerenciados vs. custo fixo de GPU dedicada em *self-hosted*.

## Consequências
- Permite demonstrar objetivamente em reuniões executivas que **modelos gerenciados vencem em TCO** para PoCs e operações abaixo de ~150k requisições/mês, reservando *self-hosted* para alto volume constante ou requisitos estritos de *air-gap*.
