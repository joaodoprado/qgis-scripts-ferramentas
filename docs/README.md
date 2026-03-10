# 🗺️ Progeo Spatial Analyzer

[![QGIS](https://img.shields.io/badge/QGIS-3.22+-green.svg)](https://qgis.org)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

&gt; Algoritmo de processamento customizado para QGIS que automatiza a identificação 
&gt; de feições pontuais isoladas utilizando Spatial Index (R-Tree) e cálculos 
&gt; geodésicos precisos.

![Interface](docs/IMAGENS/interface_tool.png)

## 🚀 Diferenciais Técnicos

| Recurso | Benefício |
|---------|-----------|
| **Spatial Index (R-Tree)** | Complexidade O(n log n) vs O(n²) tradicional |
| **QgsDistanceArea** | Precisão geodésica em metros (elipsoidal) |
| **Case-insensitive** | Robustez em dados heterogêneos |
| **Saída EPSG:4326** | Padronização corporativa Progeo |

## ⚡ Performance

Testado com 50.000+ pontos:
- **Tempo de execução:** &lt; 10 segundos
- **Consumo de memória:** Otimizado via streaming

## 🛠️ Stack Tecnológico

- **PyQGIS** - API Python do QGIS
- **Spatial Index** - R-Tree para consultas espaciais
- **QgsDistanceArea** - Cálculos geodésicos elipsoidais
- **Qt5** - Interface nativa do QGIS

## 📸 Demonstração

[Adicionar GIF ou link para vídeo]

## 🏢 Contexto Profissional

Desenvolvido para **[Progeo Engenharia]** como solução de automação para 
análise de ativos de infraestrutura (postes, transformadores, etc.).
