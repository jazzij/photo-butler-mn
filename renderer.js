// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.

/*jshint esversion: 6 */
var remote = require('electron').remote;
var dialog = remote.dialog;
var fs = require('fs');
var demoColorPicker = new iro.ColorPicker("#color-picker-container", {
  // Set the size of the color picker UI
  width: 320,
  height: 320,
  // Set the initial color to red
  color: "#f00"
});

document.getElementById("select-file").addEventListener("click",() => {
  dialog.showOpenDialog({
	  properties: ['openFile','openDirectory', 'multiSelections'],
	  filters:  [
		  {name: 'Image Files', extensions:[ 'jpg', 'jpeg', 'png' ]}
	  ]
    },function (fileNames){
	  if(fileNames === undefined){
      console.log("No file selected");
	  return;
    }else{
	  alert("Files uploaded successfully", fileNames);
	  alert(fileNames)
    }
  });
},false);


function readFile(filepath) {
  fs.readFile(filepath, 'utf-8', function (err, data) {
    if(err){
      alert("An error ocurred reading the file :" + err.message);
      return;
    }
    document.getElementById("content-editor").value = data;
  });
}
var {ipcRenderer, remote} = require('electron');  
var main = remote.require("./main.js");

// Send async message to main process
ipcRenderer.send('async', 1);

// Listen for async-reply message from main process
ipcRenderer.on('async-reply', (event, arg) => {  
    // Print 2
    console.log(arg);
    // Send sync message to main process
    let mainValue = ipcRenderer.sendSync('sync', 3);
    // Print 4
    console.log(mainValue);
});

// Listen for main message
ipcRenderer.on('ping', (event, arg) => {  
    // Print 5
    console.log(arg);
    // Invoke method directly on main process
    main.pong(6);
});
