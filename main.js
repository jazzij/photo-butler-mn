const electron = require('electron')
const app = electron.app
const BrowserWindow = electron.BrowserWindow
const path = require('path')
const dialog = electron.dialog
const fs = require('fs')
const ipc = require('electron').ipcMain
const remote = electron.remote
//exports.openFile = openFile

let mainWindow = null

app.on('ready', () => {
  console.log('The application is ready.')

  mainWindow = new BrowserWindow()
  
  mainWindow.loadURL('file://' + path.join(__dirname, 'index.html'))
  mainWindow.on('closed', () => {
    mainWindow = null
  })
})

/*function openFile () {
  dialog.showOpenDialog(mainWindow, {
	  properties: ['openDirectory','multiSelections']
  }, (folderPaths) => {
	  if(folderPaths === undefined){
		  console.log("no folder selected");
		  return;
	  }else{
		  mainWindow.webContents.send('selected-file', folderPaths)
		  console.log(folderPaths);
	  }
  });	
}*/

