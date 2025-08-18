// main.js
const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const screenshot = require('screenshot-desktop');
const sharp = require('sharp');
// const axios = require('axios');
// const FormData = require('form-data');
const fs = require('fs');

let overlayWindow;

function createOverlayWindow() {
  const displays = screen.getAllDisplays();
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  displays.forEach(d => {
    minX = Math.min(minX, d.bounds.x);
    minY = Math.min(minY, d.bounds.y);
    maxX = Math.max(maxX, d.bounds.x + d.bounds.width);
    maxY = Math.max(maxY, d.bounds.y + d.bounds.height);
  });
  const width = maxX - minX;
  const height = maxY - minY;

  overlayWindow = new BrowserWindow({
    x: minX,
    y: minY,
    width,
    height,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    focusable: true,
    resizable: false,
    movable: false,
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  overlayWindow.setIgnoreMouseEvents(false);
  overlayWindow.loadFile(path.join(__dirname, 'overlay.html'));
}

app.whenReady().then(() => {
  createOverlayWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createOverlayWindow();
  });
});

app.on('window-all-closed', () => {
  app.quit();
});

ipcMain.on('region-selected', async (event, region) => {
  try {
    if (!overlayWindow) return;

    const overlayBounds = overlayWindow.getBounds();
    const absX = overlayBounds.x + region.x;
    const absY = overlayBounds.y + region.y;

    const pointDisplay = screen.getDisplayNearestPoint({ x: absX, y: absY });
    const scaleFactor = pointDisplay.scaleFactor || 1;

    overlayWindow.hide();
    await new Promise(r => setTimeout(r, 140));

    const imgBuffer = await screenshot({ format: 'png' });

    const leftPx = Math.round(absX * scaleFactor);
    const topPx = Math.round(absY * scaleFactor);
    const widthPx = Math.round(region.width * scaleFactor);
    const heightPx = Math.round(region.height * scaleFactor);

    const meta = await sharp(imgBuffer).metadata();
    const imgW = meta.width;
    const imgH = meta.height;

    const L = Math.max(0, Math.min(leftPx, imgW - 1));
    const T = Math.max(0, Math.min(topPx, imgH - 1));
    const W = Math.max(1, Math.min(widthPx, imgW - L));
    const H = Math.max(1, Math.min(heightPx, imgH - T));

    const croppedBuffer = await sharp(imgBuffer)
      .extract({ left: L, top: T, width: W, height: H })
      .jpeg({ quality: 85 })
      .toBuffer();

    // Save locally instead of uploading
    const saveDir = path.join(__dirname, 'captures');
    if (!fs.existsSync(saveDir)) {
      fs.mkdirSync(saveDir);
    }
    const filePath = path.join(saveDir, `capture_${Date.now()}.jpg`);
    await fs.promises.writeFile(filePath, croppedBuffer);
    console.log('Saved capture to:', filePath);

    /*
    // Backend upload 
    const form = new FormData();
    form.append('file', croppedBuffer, {
      filename: 'capture.jpg',
      contentType: 'image/jpeg'
    });

    const uploadUrl = 'https://your-backend.com/upload';
    const response = await axios.post(uploadUrl, form, {
      headers: form.getHeaders(),
      maxBodyLength: Infinity
    });
    console.log('Upload response status:', response.status);
    */

    overlayWindow.close();
  } catch (err) {
    console.error('Error capturing/saving region:', err);
    try { overlayWindow.show(); } catch(e) {}
  }
});

ipcMain.on('selection-cancelled', () => {
  console.log("No screenshot was taken");
  try { overlayWindow.close(); } catch (e) {}
});
