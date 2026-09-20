'use client'

import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import type { Feature, FeatureCollection, GeoJsonObject } from 'geojson'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

type LayerType = 'attention' | 'crime' | 'transit' | 'housing' | '311'

interface NeighbourhoodProperties {
  neighbourhood: string
  attention_score_normalized?: number
  crime_rate?: number
  stop_density?: number
  median_stop_dist?: number
  housing_pressure?: number
  request_rate?: number
  population?: number
  [key: string]: any
}

interface MapProps {
  selectedLayer: LayerType
}

function getColor(value: number, layer: LayerType): string {
  const normalizedValue = value / 100
  
  if (layer === 'attention') {
    if (value > 80) return '#d73027'
    if (value > 60) return '#fc8d59'
    if (value > 40) return '#fee08b'
    if (value > 20) return '#d9ef8b'
    return '#91cf60'
  }
  
  if (layer === 'crime') {
    if (value > 20) return '#d73027'
    if (value > 15) return '#fc8d59'
    if (value > 10) return '#fee08b'
    if (value > 5) return '#d9ef8b'
    return '#91cf60'
  }
  
  if (layer === 'transit') {
    if (value > 10) return '#1a9850'
    if (value > 7) return '#91cf60'
    if (value > 4) return '#fee08b'
    if (value > 2) return '#fc8d59'
    return '#d73027'
  }
  
  if (layer === 'housing') {
    const pressure = value * 100
    if (pressure > 90) return '#d73027'
    if (pressure > 80) return '#fc8d59'
    if (pressure > 70) return '#fee08b'
    if (pressure > 60) return '#d9ef8b'
    return '#91cf60'
  }
  
  if (layer === '311') {
    if (value > 100) return '#d73027'
    if (value > 75) return '#fc8d59'
    if (value > 50) return '#fee08b'
    if (value > 25) return '#d9ef8b'
    return '#91cf60'
  }
  
  return '#cccccc'
}

function getLayerValue(properties: NeighbourhoodProperties, layer: LayerType): number {
  switch (layer) {
    case 'attention':
      return properties.attention_score_normalized || 0
    case 'crime':
      return properties.crime_rate || 0
    case 'transit':
      return properties.stop_density || 0
    case 'housing':
      return properties.housing_pressure || 0
    case '311':
      return properties.request_rate || 0
    default:
      return 0
  }
}

function Legend({ layer }: { layer: LayerType }) {
  const legendData = {
    attention: {
      title: 'Attention Score',
      grades: [0, 20, 40, 60, 80],
      labels: ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
    },
    crime: {
      title: 'Crime Rate (per 1k)',
      grades: [0, 5, 10, 15, 20],
      labels: ['<5', '5-10', '10-15', '15-20', '>20'],
    },
    transit: {
      title: 'Stop Density (per km²)',
      grades: [0, 2, 4, 7, 10],
      labels: ['<2', '2-4', '4-7', '7-10', '>10'],
    },
    housing: {
      title: 'Housing Pressure',
      grades: [0, 60, 70, 80, 90],
      labels: ['<60%', '60-70%', '70-80%', '80-90%', '>90%'],
    },
    '311': {
      title: '311 Requests (per 1k)',
      grades: [0, 25, 50, 75, 100],
      labels: ['<25', '25-50', '50-75', '75-100', '>100'],
    },
  }

  const data = legendData[layer]

  return (
    <div className="absolute bottom-8 right-4 z-[1000] bg-white rounded-lg shadow-lg p-4">
      <h4 className="font-semibold mb-2 text-gray-800">{data.title}</h4>
      <div className="space-y-1">
        {data.grades.map((grade, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className="w-6 h-4 rounded"
              style={{
                backgroundColor: getColor(grade, layer),
              }}
            />
            <span className="text-xs text-gray-700">{data.labels[i]}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function RankingTable({ 
  data, 
  layer 
}: { 
  data: FeatureCollection | null
  layer: LayerType 
}) {
  if (!data) return null

  const features = data.features as Feature<any, NeighbourhoodProperties>[]
  
  const sorted = [...features].sort((a, b) => {
    const valueA = getLayerValue(a.properties, layer)
    const valueB = getLayerValue(b.properties, layer)
    return layer === 'transit' ? valueA - valueB : valueB - valueA
  })

  const top10 = sorted.slice(0, 10)

  const getLabel = (layer: LayerType) => {
    const labels = {
      attention: 'Attention Score',
      crime: 'Crime Rate',
      transit: 'Transit Access',
      housing: 'Housing Pressure',
      '311': '311 Rate',
    }
    return labels[layer]
  }

  return (
    <div className="absolute bottom-8 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4 max-w-md max-h-96 overflow-auto">
      <h4 className="font-semibold mb-3 text-gray-800">
        Top 10 by {getLabel(layer)}
      </h4>
      <div className="space-y-2">
        {top10.map((feature, idx) => {
          const value = getLayerValue(feature.properties, layer)
          return (
            <div
              key={idx}
              className="flex justify-between items-center text-sm py-2 border-b border-gray-100"
            >
              <div>
                <span className="font-medium text-gray-700">{idx + 1}.</span>{' '}
                <span className="text-gray-800">
                  {feature.properties.neighbourhood}
                </span>
              </div>
              <span className="font-semibold text-gray-900">
                {value.toFixed(1)}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function MapContent({ 
  data, 
  selectedLayer 
}: { 
  data: FeatureCollection | null
  selectedLayer: LayerType 
}) {
  const map = useMap()

  useEffect(() => {
    if (data) {
      const bounds = L.geoJSON(data as GeoJsonObject).getBounds()
      map.fitBounds(bounds)
    }
  }, [data, map])

  if (!data) return null

  const style = (feature: Feature<any, NeighbourhoodProperties> | undefined) => {
    if (!feature) return {}
    
    const value = getLayerValue(feature.properties, selectedLayer)
    const fillColor = getColor(value, selectedLayer)

    return {
      fillColor,
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7,
    }
  }

  const onEachFeature = (
    feature: Feature<any, NeighbourhoodProperties>,
    layer: L.Layer
  ) => {
    const props = feature.properties
    const value = getLayerValue(props, selectedLayer)
    
    let label = ''
    switch (selectedLayer) {
      case 'attention':
        label = `Attention Score: ${value.toFixed(1)}`
        break
      case 'crime':
        label = `Crime Rate: ${value.toFixed(1)} per 1k`
        break
      case 'transit':
        label = `Stop Density: ${value.toFixed(1)} per km²`
        break
      case 'housing':
        label = `Housing Pressure: ${(value * 100).toFixed(0)}%`
        break
      case '311':
        label = `311 Rate: ${value.toFixed(1)} per 1k`
        break
    }

    const popupContent = `
      <div class="p-2">
        <h3 class="font-bold text-lg mb-2">${props.neighbourhood}</h3>
        <p class="text-sm mb-1"><strong>${label}</strong></p>
        <hr class="my-2" />
        <p class="text-xs text-gray-600">Population: ${props.population?.toLocaleString() || 'N/A'}</p>
        <p class="text-xs text-gray-600">Crime: ${props.crime_rate?.toFixed(1) || 'N/A'} per 1k</p>
        <p class="text-xs text-gray-600">Transit: ${props.stop_density?.toFixed(1) || 'N/A'} stops/km²</p>
        <p class="text-xs text-gray-600">Housing: ${props.housing_pressure ? (props.housing_pressure * 100).toFixed(0) + '%' : 'N/A'}</p>
        <p class="text-xs text-gray-600">311 Rate: ${props.request_rate?.toFixed(1) || 'N/A'} per 1k</p>
      </div>
    `

    layer.bindPopup(popupContent)
    
    if (layer instanceof L.Path) {
      layer.on({
        mouseover: (e) => {
          e.target.setStyle({
            weight: 3,
            color: '#666',
            fillOpacity: 0.9,
          })
        },
        mouseout: (e) => {
          e.target.setStyle({
            weight: 1,
            color: 'white',
            fillOpacity: 0.7,
          })
        },
      })
    }
  }

  return (
    <GeoJSON
      key={`${selectedLayer}-${Date.now()}`}
      data={data as GeoJsonObject}
      style={style}
      onEachFeature={onEachFeature}
    />
  )
}

export default function Map({ selectedLayer }: MapProps) {
  const [geoData, setGeoData] = useState<FeatureCollection | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/data/neighbourhoods_analysis.geojson')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load data')
        return res.json()
      })
      .then((data) => {
        setGeoData(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Error loading GeoJSON:', err)
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading neighbourhood data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center text-red-600">
          <p className="text-xl font-semibold mb-2">Error loading data</p>
          <p className="text-sm">{error}</p>
          <p className="text-xs mt-4 text-gray-500">
            Make sure to run the data processing pipeline first
          </p>
        </div>
      </div>
    )
  }

  return (
    <>
      <MapContainer
        center={[43.7, -79.4]}
        zoom={11}
        className="w-full h-screen"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapContent data={geoData} selectedLayer={selectedLayer} />
      </MapContainer>
      
      <Legend layer={selectedLayer} />
      <RankingTable data={geoData} layer={selectedLayer} />
    </>
  )
}
