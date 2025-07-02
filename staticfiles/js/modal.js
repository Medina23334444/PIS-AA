document.addEventListener('DOMContentLoaded', function() {
    const abrirModal = document.querySelector("#btnModal");
    const modal = document.querySelector("#modal");
    const cerrarModal = document.querySelector("#cerrarModal");
    const aplicarSeleccion = document.querySelector("#aplicar");

    abrirModal.addEventListener("click", () => {
        modal.showModal();
    });

    cerrarModal.addEventListener("click", () => {
        modal.close();
    });

});