# 📍 Automação PyQGIS: Identificação de Pontos Isolados (Métrico)

## 📖 Descrição
Este projeto apresenta um script de processamento customizado para o **QGIS** (Python 3) que automatiza a identificação de feições de pontos "isoladas". O algoritmo percorre uma camada e seleciona todos os pontos que não possuem nenhuma feição de referência dentro de um raio de busca específico.

Ideal para limpeza de dados topológicos, conferência de ativos (ex: postes sem fiação) ou análise de cobertura de serviços.

## 🚀 Diferenciais Técnicos
Para sair do "básico", este script foi construído com foco em dois pilares:

1. **Performance (Spatial Index):** Em vez de comparar cada ponto com todos os outros (complexidade $O(n^2)$), utilizei o `QgsSpatialIndex` (R-Tree). Isso permite que a busca seja feita apenas entre vizinhos próximos, tornando o script extremamente rápido mesmo em camadas com milhares de feições.
2. **Precisão Geodésica:** Utilizei a classe `QgsDistanceArea` configurada com o elipsoide do projeto. Isso garante que a distância seja calculada em **metros**, considerando a curvatura da Terra, e não em graus decimais (que sofrem distorção dependendo da latitude).

## 🛠️ Como Utilizar
1. Baixe o arquivo `selecao_espacial.py`.
2. No QGIS, abra a **Caixa de Ferramentas de Processamento** (`Ctrl+Alt+T`).
3. Clique no ícone do Python -> **Adicionar Script ao Painel...** e selecione o arquivo baixado.
4. A ferramenta aparecerá no grupo "Meus Scripts de Automação".

## 📸 Interface da Ferramenta
<img width="773" height="549" alt="image" src="https://github.com/user-attachments/assets/11567129-8154-4092-9c33-17e01581c330" />



## 🧠 Lógica Implementada
O algoritmo segue o fluxo:
- **Entrada:** Camada de busca, camada de referência e raio (m).
- **Processamento:** - Criação de Índice Espacial na camada de referência.
    - Loop por cada feição da camada de busca.
    - Filtro rápido via Bounding Box (BBOX).
    - Cálculo preciso de distância geodésica.
- **Saída:** Seleção direta na camada de origem.
