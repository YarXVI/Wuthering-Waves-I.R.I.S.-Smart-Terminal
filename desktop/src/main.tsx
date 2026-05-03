import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import App from './App'
import { initApiFallback } from './utils/apiFallback'

initApiFallback()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <HashRouter>
    <App />
  </HashRouter>
)
