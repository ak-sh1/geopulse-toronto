'use client'

import dynamic from 'next/dynamic'
import { useState } from 'react'

const Map = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading map...</p>
      </div>
    </div>
  ),
})

export type LayerType = 'attention' | 'crime' | 'transit' | 'housing' | '311'

export default function Home() {
  const [selectedLayer, setSelectedLayer] = useState<LayerType>('attention')

  return (
    <main className="relative w-full h-screen">
      <Map selectedLayer={selectedLayer} />
      
      <div className="absolute top-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4 max-w-sm">
        <h1 className="text-2xl font-bold mb-2 text-gray-800">
          GeoPulse Toronto
        </h1>
        <p className="text-sm text-gray-600 mb-4">
          Neighbourhood analysis: transit, housing, crime, and 311 demand
        </p>
        
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Layer View
          </label>
          <select
            value={selectedLayer}
            onChange={(e) => setSelectedLayer(e.target.value as LayerType)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
          >
            <option value="attention">🎯 Attention Score (Composite)</option>
            <option value="crime">🚨 Crime Rate</option>
            <option value="transit">🚇 Transit Access</option>
            <option value="housing">🏠 Housing Pressure</option>
            <option value="311">📞 311 Request Rate</option>
          </select>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Data: City of Toronto Open Data via CKAN
          </p>
        </div>
      </div>
    </main>
  )
}
