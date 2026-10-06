export async function notify(title,body){
  if('Notification' in window){if(Notification.permission==='default') await Notification.requestPermission(); if(Notification.permission==='granted') new Notification(title,{body});}
}
export async function registerOffline(){if('serviceWorker' in navigator) try{await navigator.serviceWorker.register('/sw.js')}catch{} }
