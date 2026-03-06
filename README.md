# Seleção Espacial para QGIS

[![QGIS](https://img.shields.io/badge/QGIS-3.x-green)](https://qgis.org)
[![Python](https://img.shields.io/badge/Python-3.7+-blue)](https://python.org)
[![Licence](https://img.shields.io/badge/Licence-MIT-yellow)](LICENSE)

Script PyQGIS para seleção espacial de feições com controle de distância em centímetros.

## 🎯 Problema Resolvido

Em análises espaciais, frequentemente precisamos identificar pontos **isolados** — aqueles que não possuem nenhuma infraestrutura ou elemento de referência próximo. Este script automatiza essa tarefa no QGIS com precisão métrica.

## 🚀 Funcionalidades

- Interface simples via caixas de diálogo
- Busca por raio configurável em **centímetros**
- Otimizado com **índice espacial** para grandes volumes de dados
- Compatível com sistemas de coordenadas geográficas (graus)
- Validação automática de camadas

## 📊 Performance

Testado com:
- **23.443 pontos** vs **22.305 polígonos**
- Tempo de execução: **&lt; 30 segundos**
- Sem índice espacial: estimado **&gt; 30 minutos**

## 🖥️ Como Usar

1. Abra o QGIS e carregue suas camadas vetoriais
2. Vá em **Plugins → Console Python**
3. Cole o código do arquivo `selecao_espacial.py`
4. Informe:
   - Nome da camada de seleção (pontos)
   - Nome da camada de referência (polígonos/linhas)
   - Raio de busca em centímetros (ex: 11)

## 📁 Estrutura do Projeto
