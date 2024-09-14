if (!firebase.apps.length) {
    firebase.initializeApp({
        apiKey: "AIzaSyBHNQjXsH7nxkpzOMTJ1w8L0nFW1mR6noY",
        authDomain: "cabutos.firebaseapp.com",
        databaseURL: "https://cabutos.firebaseio.com",
        projectId: "cabutos",
        storageBucket: "cabutos.appspot.com",
        messagingSenderId: "535520824503",
        appId: "1:535520824503:web:97c4525d2cca993337d132"
    });
} else {
    firebase.app();
}

const database = firebase.database();

function enviarSonido() {
    const audioPedido = document.getElementById('audioPedido');
    const audioNotificacionPedido = document.getElementById('audioNotificacionPedido');
    
    if (audioPedido) {
        location.reload();
    }
    if (!audioNotificacionPedido) {
        const nuevoAudio = document.createElement('audio');
        nuevoAudio.id = 'audioNotificacionPedido';
        nuevoAudio.src = 'https://www.bensound.com/bensound-music/bensound-theelevatorbossanova.mp3';
        document.body.appendChild(nuevoAudio);
        nuevoAudio.play();
    } else {
        audioNotificacionPedido.currentTime = 0;
        audioNotificacionPedido.play();
    }
}

function actualizarPedidosEspera() {
    const ultimoPedidoRef = database.ref('pedidos/ultimoPedido');    
    ultimoPedidoRef.on('child_changed', (snapshot) => {
            enviarSonido();
        });
}

document.addEventListener('DOMContentLoaded', function() {
    actualizarPedidosEspera();
});
