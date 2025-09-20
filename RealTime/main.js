const { app, BrowserWindow, ipcMain, screen } = require('electron');
const path = require('path');
const screenshot = require('screenshot-desktop');
const sharp = require('sharp');
const fs = require('fs');

// Renamed for clarity, as this window now controls both states
let controlWindow;

// ## This is the correct function to call on startup ##
function createStarterWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth } = primaryDisplay.bounds;

  const starterWidth = 160;
  const starterHeight = 50;

  controlWindow = new BrowserWindow({
    // Position the window at the top-middle of the screen
    x: Math.round((screenWidth - starterWidth) / 2),
    y: 20,
    width: starterWidth,
    height: starterHeight,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
     backgroundColor: '#00000000',
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  

  // Load the starter.html file first
  controlWindow.loadFile(path.join(__dirname, 'starter.html'));
}

// ✨ FIX: Call the correct function when the app is ready
app.whenReady().then(createStarterWindow);


// ## Listener: Switches from 'Start' button to full overlay ##
ipcMain.on('start-capture', () => {
  if (!controlWindow) return;




  const { width, height } = screen.getPrimaryDisplay().bounds;
  
  // 2. Do all the resizing and loading while the window is hidden
  controlWindow.setIgnoreMouseEvents(false);
  controlWindow.setBounds({ x: 0, y: 0, width, height });
  controlWindow.loadFile(path.join(__dirname, 'overlay.html'));

});


// ## Listener: Switches from full overlay back to 'Start' button ##
ipcMain.on('return-to-starter', () => {
  if (!controlWindow) return;
  const { width: screenWidth } = screen.getPrimaryDisplay().bounds;
  const starterWidth = 200;
  const starterHeight = 60;

  controlWindow.setBounds({
    x: Math.round((screenWidth - starterWidth) / 2),
    y: 20,
    width: starterWidth,
    height: starterHeight,
  });
  controlWindow.loadFile(path.join(__dirname, 'starter.html'));
});


// ## The screenshot logic (no changes needed here) ##
ipcMain.on('region-selected', async (event, { region, id }) => {
  if (!controlWindow) return;

  const inputDir = path.join(__dirname, 'input');
  if (!fs.existsSync(inputDir)) fs.mkdirSync(inputDir);
  const capturePath = path.join(inputDir, `capture_${id}.png`);

  try {
    const fullScreenBuffer = await screenshot({ format: 'png' });
    const pointDisplay = screen.getDisplayNearestPoint({ x: region.x, y: region.y });
    const scaleFactor = pointDisplay.scaleFactor || 1;
    
    await sharp(fullScreenBuffer)
      .extract({
        left: Math.round(region.x * scaleFactor),
        top: Math.round(region.y * scaleFactor),
        width: Math.round(region.width * scaleFactor),
        height: Math.round(region.height * scaleFactor),
      })
      .toFile(capturePath);
    
    console.log('Saved snippet to:', capturePath);

    const outputDir = path.join(__dirname, 'output');
    const translatedImagePath = path.join(outputDir, 'Page.png');
    
    await new Promise(resolve => setTimeout(resolve, 500));

    if (fs.existsSync(translatedImagePath)) {
      controlWindow.webContents.send('translation-complete', {
        id: id,
        originalRegion: region,
        translatedImagePath: translatedImagePath,
      });
    } else {
      console.error(`Mock translation not found at: ${translatedImagePath}`);
    }

  } catch (err) {
    console.error('Error in region-selected process:', err);
  }
});