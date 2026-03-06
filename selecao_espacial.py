#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seletor Espacial para QGIS
==========================

Autor: João Vitor Prado
Data: 2025-03
Local: São Luís - MA, Brasil

Descrição:
    Script PyQGIS que seleciona pontos de uma camada vetorial (A) 
    que não possuem nenhuma feição de outra camada (B) dentro de 
    uma distância especificada em centímetros.
    
    Otimizado com índice espacial (R-tree) para performance em 
    grandes volumes de dados.

Aplicações:
    - Validação de dados cartográficos
    - Análise de cobertura de infraestrutura
    - Controle de qualidade de dados espaciais

Requisitos:
    - QGIS 3.x
    - Camadas vetoriais em sistema de coordenadas geográficas (graus)
    - Preferencialmente camada A como pontos, camada B como polígonos ou linhas

Limitações:
    - Para sistemas de coordenadas projetados (metros), a conversão 
      automática ainda não está implementada
    - Cálculo de distância usa aproximação euclidiana em graus (adequado 
      para pequenas distâncias < 1km)

Uso:
    1. Carregar duas camadas vetoriais no QGIS
    2. Executar script no Console Python do QGIS
    3. Informar nomes das camadas e raio de busca em cm
    4. Script seleciona automaticamente os pontos isolados
"""

from qgis.PyQt.QtWidgets import QInputDialog
from qgis.core import QgsProject, QgsSpatialIndex


def executar_selecao():
    """
    Executa a seleção espacial de pontos isolados.
    
    Solicita camadas e raio ao usuário, valida dados, cria índice espacial
    e seleciona pontos da camada A sem nenhuma feição da camada B no raio especificado.
    """
    # Diálogo 1: camada de seleção
    camada_para_selecao, ok1 = QInputDialog.getText(
        None, 
        'Camada p/ Seleção', 
        'Informe o nome da camada de onde serão selecionados os pontos'
    )
    if not ok1:
        print('Operação cancelada pelo usuário.')
        return
        
    # Diálogo 2: camada de referência
    camada_referencia, ok2 = QInputDialog.getText(
        None, 
        'Camada de referência', 
        'Informe o nome da camada de referência'
    )
    if not ok2:
        print('Operação cancelada pelo usuário.')
        return
    
    # Diálogo 3: raio de busca
    tamanho_cm, ok3 = QInputDialog.getText(
        None, 
        'Tamanho da busca', 
        'Informe o raio de busca em centímetros: ex(11)'
    )
    if not ok3:
        print('Operação Cancelada.')
        return
    
    # Validação e conversão do raio
    try:
        raio_cm = float(tamanho_cm)
        raio_metros = raio_cm / 100.0
    except ValueError:
        print('Erro: Digite um número válido.')
        return 
    
    # Conversão aproximada para graus
    # 1° de latitude ≈ 111km no equador
    # Adequado para distâncias pequenas (< 1km) e latitudes médias
    RAIO_GRAUS = raio_metros / 111000.0
    
    print(f'Camada de seleção: {camada_para_selecao}')
    print(f'Camada de referência: {camada_referencia}')
    print(f'Raio: {raio_cm}cm = {raio_metros}m = {RAIO_GRAUS:.10f}°')
    
    # Acesso ao projeto QGIS
    projeto = QgsProject.instance()
    camada_a = projeto.mapLayersByName(camada_para_selecao)
    camada_b = projeto.mapLayersByName(camada_referencia)
    
    # Validação de existência das camadas
    if not camada_a or not camada_b:
        print(f'Erro: Camadas não encontradas.')
        print('===CAMADAS DISPONÍVEIS===')
        for c in projeto.layerTreeRoot().findLayers():
            if c.layer():
                print(f' - {c.layer().name()}')
        return
        
    layer_a = camada_a[0]
    layer_b = camada_b[0]
    
    # Aviso sobre sistemas de coordenadas
    if not layer_a.crs().isGeographic():
        print(f'⚠️  Aviso: {layer_a.name()} não está em graus (CRS: {layer_a.crs().authid()})')
    if not layer_b.crs().isGeographic():
        print(f'⚠️  Aviso: {layer_b.name()} não está em graus (CRS: {layer_b.crs().authid()})')
        
    print(f'\nCamada A: {layer_a.name()} ({layer_a.featureCount()} pts)')
    print(f'Camada B: {layer_b.name()} ({layer_b.featureCount()} pts)')
    
    # CRIAÇÃO DO ÍNDICE ESPACIAL
    print('\nCriando índice espacial...')
    indice = QgsSpatialIndex()
    for feicao_b in layer_b.getFeatures():
        indice.insertFeature(feicao_b)
    print('Índice criado.')
    
    # PROCESSO DE SELEÇÃO
    layer_a.removeSelection()
    ids_para_selecionar = []
    
    # Margem de segurança para bounding box (10x o raio)
    TOLERANCIA_BBOX = RAIO_GRAUS * 10
    
    for i, feicao_a in enumerate(layer_a.getFeatures()):
        geom_a = feicao_a.geometry()
        ponto_a = geom_a.asPoint()
        
        # Expande bounding box para garantir captura de candidatos
        bbox = geom_a.boundingBox()
        bbox.grow(TOLERANCIA_BBOX)
        
        # Busca no índice espacial
        ids_candidatos = indice.intersects(bbox)
        
        # Sem candidatos = ponto isolado
        if not ids_candidatos:
            ids_para_selecionar.append(feicao_a.id())
            continue
            
        # Verificação precisa de distância
        ponto_isolado = True
        
        for id_b in ids_candidatos:
            geom_b = layer_b.getFeature(id_b).geometry()
            ponto_b = geom_b.asPoint()
            
            # Distância euclidiana em graus (adequada para pequenas distâncias)
            dist_graus = ((ponto_a.x() - ponto_b.x())**2 + (ponto_a.y() - ponto_b.y())**2) ** 0.5
            
            if dist_graus <= RAIO_GRAUS:
                ponto_isolado = False
                break
        
        if ponto_isolado:
            ids_para_selecionar.append(feicao_a.id())
            
    # Aplica seleção no QGIS
    layer_a.selectByIds(ids_para_selecionar)
    
    print(f'\n✅ Selecionados {len(ids_para_selecionar)} pontos ISOLADOS')


def main():
    """Função principal de execução com tratamento de erros."""
    try:
        executar_selecao()
        print(f"\n{'='*50}")
        print("PROCESSO CONCLUÍDO COM SUCESSO")
        print(f"{'='*50}")
    except Exception as erro:
        print(f"\n❌ ERRO INESPERADO: {str(erro)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
