
## Componentes Principais

### 1. Spatial Index (R-Tree)
- **Classe:** `QgsSpatialIndex`
- **Complexidade:** O(n log n) para construção, O(log n) para consulta
- **Função:** Elimina comparações desnecessárias entre pontos distantes

### 2. Cálculo de Distância
- **Classe:** `QgsDistanceArea`
- **Método:** `measureLine()` com elipsoide WGS84
- **Precisão:** Milimétrica, independente do CRS de entrada

### 3. Transformação de Coordenadas
- **Classe:** `QgsCoordinateTransform`
- **Condição:** Executa apenas se CRS de entrada ≠ EPSG:4326
- **Saída:** Sempre padronizada em WGS84

## Estrutura de Dados

### Campos de Saída
| Campo | Tipo | Origem |
|-------|------|--------|
| municipio | String | Camada de entrada |
| mslink_pg | String | Camada de entrada |
| barramento | String | Camada de entrada |
| lat | Double | Geometria (Y) |
| long | Double | Geometria (X) |
| Propriedade | String | NULL (preenchimento manual) |

## Decisões de Design

### Case-Insensitive
Nomes de campos convertidos para minúsculo antes da comparação, garantindo 
compatibilidade com diferentes convenções de nomenclatura.

### Validação Condicional
Verificação de campos obrigatórios executada apenas quando o usuário opta 
por criar a camada de saída, evitando bloqueios desnecessários.

### Streaming de Dados
Processamento iterativo via `getFeatures()` sem carregar toda a camada em 
memória, permitindo escalabilidade para grandes datasets.

## Performance

| Métrica | Valor |
|---------|-------|
| Complexidade algorítmica | O(n log n) |
| Tempo estimado (10k pontos) | < 5 segundos |
| Consumo de memória | O(n) para indexação |

## Dependências

- QGIS >= 3.22
- PyQt5 (interface)
- GDAL/OGR (via QGIS)
