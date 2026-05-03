/**
 * Electron 主进�?- 完整�? * - 创建桌面窗口
 * - 启动 Python 后端服务（打包模式）
 * - 管理子进程生命周�? */

const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')

const isDev = !app.isPackaged
const API_PORT = 8765

let apiProcess = null
let mainWindow = null

function log(msg) {
  const ts = new Date().toLocaleTimeString()
  console.log(`[${ts}][ELECTRON] ${msg}`)
}

function findPythonExecutable() {
  if (isDev) {
    return 'python'
  }
  // 打包模式：尝试找到嵌入的 Python 或使用系�?Python
  const possiblePaths = [
    path.join(process.resourcesPath, 'server', 'iris-server.exe'),
    path.join(process.resourcesPath, 'iris-server.exe'),
  ]
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p
    }
  }
  return 'python'
}

function startApiServer() {
  if (isDev) {
    log('Dev mode: API server should be started manually')
    return
  }

  const pythonExe = findPythonExecutable()
  log(`Starting API server with: ${pythonExe}`)

  let args = []
  let cwd = process.cwd()

  if (pythonExe.endsWith('.exe') && fs.existsSync(pythonExe)) {
    args = []
    cwd = path.dirname(pythonExe)
  } else {
    const serverScript = path.join(process.resourcesPath, 'server', 'main.py')
    if (fs.existsSync(serverScript)) {
      args = ['-m', 'server.main']
      cwd = process.resourcesPath
    }
  }

  apiProcess = spawn(pythonExe, args, {
    cwd,
    env: { ...process.env },
    stdio: 'pipe',
  })

  apiProcess.stdout?.on('data', (data) => {
    console.log(`[API] ${data.toString().trim()}`)
  })

  apiProcess.stderr?.on('data', (data) => {
    console.error(`[API] ${data.toString().trim()}`)
  })

  apiProcess.on('close', (code) => {
    log(`API server exited with code ${code}`)
    apiProcess = null
  })

  apiProcess.on('error', (err) => {
    log(`Failed to start API server: ${err}`)
  })
}

function stopApiServer() {
  if (apiProcess) {
    log('Stopping API server...')
    apiProcess.kill()
    apiProcess = null
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: '爱弥�?�?虚拟办公�?,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  return mainWindow
}

app.whenReady().then(() => {
  log('App ready, starting services...')

  startApiServer()
  const win = createWindow()

  // 全局快捷�? Alt+Space 呼出/隐藏
  globalShortcut.register('Alt+Space', () => {
    if (win.isVisible()) {
      win.hide()
    } else {
      win.show()
      win.focus()
    }
  })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  globalShortcut.unregisterAll()
  stopApiServer()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  stopApiServer()
})
