const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    const isMac = process.platform === 'darwin';
    const isWindows = process.platform === 'win32';

    const windowConfig = {
        width: 1250,
        height: 700,
        minWidth: 1250,
        minHeight: 700,
        frame: false,
        transparent: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webviewTag: true,
            preload: path.join(__dirname, 'preload.js')
        },
        show: false
    };

    // Configuración específica para macOS
    if (isMac) {
        windowConfig.vibrancy = 'under-window';
        windowConfig.visualEffectState = 'active';
        windowConfig.titleBarStyle = 'hidden';
        windowConfig.trafficLightPosition = { x: 15, y: 11 };
    }

    // Configuración específica para Windows
    if (isWindows) {
        windowConfig.backgroundMaterial = 'acrylic';
    }

    mainWindow = new BrowserWindow(windowConfig);

    // Cargar la aplicación
    mainWindow.loadFile(path.join(__dirname, '../index.html'));

    // Mostrar ventana cuando esté lista
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    return mainWindow;
}

app.whenReady().then(() => {
    createWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});