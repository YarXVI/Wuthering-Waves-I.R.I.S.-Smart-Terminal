/**
 * Electron Main Process
 * - Creates main window
 * - Launches Python backend service (packaged mode)
 * - Manages subprocess lifecycle
 */

const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')

const isDev = !app.isPackaged
const API_PORT = 8000

let apiProcess = null
let mainWindow = null

function log(msg) {
  const ts = new Date().toLocaleTimeString()
  console.log(`[${ts}][ELECTRON] ${msg}`)
}

function createWindow() {
  log('Creating main window...')
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'I.R.I.S.',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  const startUrl = isDev
    ? 'http://localhost:5173'
    : `file://${path.join(__dirname, '../dist/index.html')}`

  log(`Loading: ${startUrl}`)
  mainWindow.loadURL(startUrl)

  if (isDev) {
    mainWindow.webContents.openDevTools()
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function startBackend() {
  if (isDev) {
    log('Dev mode: backend should be started separately')
    return
  }

  const backendScript = path.join(__dirname, '../../server/main.py')
  if (!fs.existsSync(backendScript)) {
    log('ERROR: backend script not found at ' + backendScript)
    return
  }

  log(`Starting backend: ${process.execPath} ${backendScript}`)
  apiProcess = spawn(process.execPath, [backendScript], {
    cwd: path.dirname(backendScript),
    detached: true,
    stdio: 'ignore',
  })

  apiProcess.unref()

  setTimeout(() => {
    log('Backend process started')
  }, 2000)
}

app.whenReady().then(() => {
  log('App ready')
  startBackend()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  log('All windows closed')
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('will-quit', () => {
  log('App will quit')
  if (apiProcess) {
    try {
      process.kill(apiProcess.pid, 'SIGTERM')
    } catch (e) {
      log(`Error killing backend: ${e.message}`)
    }
  }
})
