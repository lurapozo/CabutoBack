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
const pedidosRef = database.ref('pedidos/');

function actualizarPedidosEspera() {
    let lastProcessedTimestamp = localStorage.getItem('lastProcessedTimestamp') || 0;

    const ultimoPedidoRef = database.ref('pedidos/ultimoPedido');
    
    ultimoPedidoRef.on('value', (snapshot) => {
        const nuevoPedido = snapshot.val();
        const pedidoTimestamp = snapshot.child("timestamp").val();

        if (nuevoPedido && pedidoTimestamp > lastProcessedTimestamp) {
            console.log("Nuevo pedido detectado:", nuevoPedido);
            localStorage.setItem('lastProcessedTimestamp', pedidoTimestamp);
            location.reload();
        }
    });
}

