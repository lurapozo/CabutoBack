$("#limpiarCampos-btn").click(function() {
	limpiarCampos()
})
$("#guardar-btn").click(function() {
	if (verificarCampos()) {
		$("#form").submit()
	}
})

function limpiarCampos() {
	var inputs = $(".input")
	//LIMPIANDO INPUTS
	inputs.each(function() {
		$(this).val("")
	})
}

function verificarCampos() {
	var verificacion = true
	var inputs = $(".input")
	//VERIFICANDO CADA CAMPO
	inputs.each(function() {if ($(this).val() == "") {verificacion = false}})

	//DISPARANDO ALERTA SI ES NECESARIA
	if (! verificacion) {alert("Por favor llene todos los campos.")}
	return verificacion
}

var $ = JQuery.noConflict();
function abrir_agregar_producto(url){
    $('#agregar').load(url, function(){
      $(this).modal('show');
    });
}