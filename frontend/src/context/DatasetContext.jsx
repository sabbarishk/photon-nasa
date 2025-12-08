import { createContext, useContext, useState } from 'react'

const DatasetContext = createContext()

export function DatasetProvider({ children }) {
  const [selectedDataset, setSelectedDataset] = useState(null)

  const selectDataset = (dataset) => {
    setSelectedDataset(dataset)
  }

  const clearDataset = () => {
    setSelectedDataset(null)
  }

  return (
    <DatasetContext.Provider value={{ selectedDataset, selectDataset, clearDataset }}>
      {children}
    </DatasetContext.Provider>
  )
}

export function useDataset() {
  const context = useContext(DatasetContext)
  if (context === undefined) {
    throw new Error('useDataset must be used within a DatasetProvider')
  }
  return context}
