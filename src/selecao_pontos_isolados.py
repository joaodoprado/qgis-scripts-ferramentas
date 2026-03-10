# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, 
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink,
                       QgsFeatureSink, QgsFeature, QgsField, QgsFields,
                       QgsSpatialIndex, QgsDistanceArea, QgsProject,
                       QgsCoordinateTransform, QgsCoordinateReferenceSystem,
                       QgsWkbTypes, QgsGeometry, QgsPointXY)

import math


class SelecaoPontosIsolados(QgsProcessingAlgorithm):
    """
    Algoritmo para selecionar pontos isolados utilizando Spatial Index
    e criar camada de saída padronizada (Progeo) em EPSG:4326.
    """

    # Parâmetros de entrada
    CAMADA_BUSCA = 'CAMADA_BUSCA'
    CAMADA_REFERENCIA = 'CAMADA_REFERENCIA'
    RAIO = 'RAIO'
    
    # Parâmetros de saída
    CRIAR_CAMADA = 'CRIAR_CAMADA'
    CAMADA_SAIDA = 'CAMADA_SAIDA'

    def name(self):
        return 'selecao_pontos_isolados'

    def displayName(self):
        return 'Seleção de Pontos Isolados (Métrico)'

    def shortHelpString(self):
        return """
        Seleciona pontos que não possuem vizinhos dentro do raio especificado.
        
        Opcionalmente cria uma nova camada padronizada (EPSG:4326) com os campos:
        município, mslink_pg, barramento, lat, long, Propriedade
        
        Diferenciais:
        • Usa Spatial Index (R-Tree) para alta performance
        • Cálculo geodésico preciso em metros (QgsDistanceArea)
        • Saída padronizada em WGS84 (EPSG:4326) - padrão Progeo
        • Case-insensitive para nomes de campos
        """

    def initAlgorithm(self, config=None):
        # Camada de busca (pontos a verificar)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.CAMADA_BUSCA,
                'Camada de busca (pontos)',
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Camada de referência (pontos de comparação)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.CAMADA_REFERENCIA,
                'Camada de referência (pontos)',
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Raio de busca em metros
        self.addParameter(
            QgsProcessingParameterNumber(
                self.RAIO,
                'Raio de busca (metros)',
                QgsProcessingParameterNumber.Double,
                defaultValue=1.0,
                minValue=0.1
            )
        )

        # Opção de criar camada de saída
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CRIAR_CAMADA,
                'Criar camada padronizada com pontos isolados (EPSG:4326)',
                defaultValue=True
            )
        )

        # Saída da camada (opcional, será memory se não especificado)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.CAMADA_SAIDA,
                'Camada de pontos isolados (padrão Progeo - WGS84)',
                optional=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Obter parâmetros
        camada_busca = self.parameterAsVectorLayer(parameters, self.CAMADA_BUSCA, context)
        camada_ref = self.parameterAsVectorLayer(parameters, self.CAMADA_REFERENCIA, context)
        raio = self.parameterAsDouble(parameters, self.RAIO, context)
        criar_camada = self.parameterAsBool(parameters, self.CRIAR_CAMADA, context)

        if feedback.isCanceled():
            return {}

        # Configurar cálculo de distância geodésica
        dist_area = QgsDistanceArea()
        dist_area.setSourceCrs(camada_busca.sourceCrs(), context.transformContext())
        dist_area.setEllipsoid(QgsProject.instance().ellipsoid())

        feedback.pushInfo(f"Usando elipsoide: {QgsProject.instance().ellipsoid()}")

        # CRS de saída padrão: EPSG:4326 (WGS 84)
        crs_wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')
        
        # Preparar transformação se necessário (para extrair lat/long corretos)
        transform_to_wgs84 = None
        if camada_busca.sourceCrs() != crs_wgs84:
            transform_to_wgs84 = QgsCoordinateTransform(
                camada_busca.sourceCrs(),
                crs_wgs84,
                context.transformContext()
            )
            feedback.pushInfo(f"Transformando coordenadas de {camada_busca.sourceCrs().authid()} para EPSG:4326")

        # Criar Spatial Index na camada de referência
        feedback.pushInfo("Criando índice espacial...")
        spatial_index = QgsSpatialIndex(camada_ref.getFeatures())

        if feedback.isCanceled():
            return {}

        # Preparar camada de saída se necessário
        sink = None
        camada_saida_id = None
        
        if criar_camada:
            # CORREÇÃO: Verificação de campos obrigatórios apenas se for criar camada
            # Converter tudo para minúsculo para comparação case-insensitive
            campos_obrigatorios = ['município', 'mslink_pg', 'barramento']
            campos_existentes = [f.name().lower() for f in camada_busca.fields()]
            
            campos_faltantes = [c for c in campos_obrigatorios if c not in campos_existentes]
            if campos_faltantes:
                raise Exception(
                    f"Campos obrigatórios não encontrados na camada de busca: {', '.join(campos_faltantes)}"
                )

            # Criar QgsFields em vez de lista
            fields_saida = QgsFields()
            fields_saida.append(QgsField('município', QVariant.String))
            fields_saida.append(QgsField('mslink_pg', QVariant.String))
            fields_saida.append(QgsField('barramento', QVariant.String))
            fields_saida.append(QgsField('lat', QVariant.Double))
            fields_saida.append(QgsField('long', QVariant.Double))
            fields_saida.append(QgsField('Propriedade', QVariant.String))

            # Criar sink SEMPRE em EPSG:4326
            (sink, camada_saida_id) = self.parameterAsSink(
                parameters,
                self.CAMADA_SAIDA,
                context,
                fields_saida,
                QgsWkbTypes.Point,
                crs_wgs84
            )

            if sink is None:
                raise Exception("Não foi possível criar a camada de saída")

        # Processar pontos
        total = camada_busca.featureCount()
        feedback.pushInfo(f"Processando {total} feições...")

        pontos_isolados = []
        pontos_saida = []

        # Deselecionar tudo inicialmente
        camada_busca.removeSelection()

        for current, feature in enumerate(camada_busca.getFeatures()):
            if feedback.isCanceled():
                return {}

            feedback.setProgress(int(current * 100 / total))

            geom = feature.geometry()
            if geom.isNull() or not geom.isGeosValid():
                continue

            ponto = geom.asPoint()
            
            # Busca rápida via BBOX no Spatial Index (buffer do raio)
            if camada_ref.sourceCrs().isGeographic():
                raio_graus = raio / 111000.0
            else:
                raio_graus = raio
            
            rect = geom.boundingBox()
            rect.grow(raio_graus)

            candidatos = spatial_index.intersects(rect)

            isolado = True
            
            for id_candidato in candidatos:
                feat_candidato = camada_ref.getFeature(id_candidato)
                
                if camada_busca.id() == camada_ref.id() and feature.id() == id_candidato:
                    continue

                geom_candidato = feat_candidato.geometry()
                if geom_candidato.isNull():
                    continue

                ponto_candidato = geom_candidato.asPoint()
                
                distancia = dist_area.measureLine(ponto, ponto_candidato)

                if distancia <= raio:
                    isolado = False
                    break

            if isolado:
                pontos_isolados.append(feature.id())
                
                if criar_camada and sink is not None:
                    feat_saida = QgsFeature()
                    
                    # CORREÇÃO: Buscar campos de forma case-insensitive
                    # Criar dicionário com nomes em minúsculo
                    atributos_lower = {k.lower(): v for k, v in feature.attributeMap().items()}
                    
                    município = atributos_lower.get('município')
                    mslink_pg = atributos_lower.get('mslink_pg')
                    barramento = atributos_lower.get('barramento')
                    
                    # Obter geometria em WGS84 para lat/long corretos
                    geom_wgs84 = QgsGeometry(geom)
                    if transform_to_wgs84:
                        geom_wgs84.transform(transform_to_wgs84)
                    
                    ponto_wgs84 = geom_wgs84.asPoint()
                    lat = ponto_wgs84.y()
                    long = ponto_wgs84.x()
                    
                    feat_saida.setGeometry(geom_wgs84)
                    
                    propriedade = None
                    
                    feat_saida.setAttributes([
                        município,
                        mslink_pg,
                        barramento,
                        lat,
                        long,
                        propriedade
                    ])
                    
                    pontos_saida.append(feat_saida)

        if pontos_isolados:
            camada_busca.selectByIds(pontos_isolados)
            feedback.pushInfo(f"Selecionados {len(pontos_isolados)} pontos isolados")
        else:
            feedback.pushInfo("Nenhum ponto isolado encontrado")

        if criar_camada and sink is not None and pontos_saida:
            sink.addFeatures(pontos_saida, QgsFeatureSink.FastInsert)
            feedback.pushInfo(f"Criada camada de saída com {len(pontos_saida)} pontos (EPSG:4326)")

        resultado = {
            'Pontos_Isolados': len(pontos_isolados)
        }
        
        if criar_camada and camada_saida_id:
            resultado[self.CAMADA_SAIDA] = camada_saida_id

        return resultado

    def createInstance(self):
        return SelecaoPontosIsolados()
