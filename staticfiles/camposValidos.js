function validarCedula(cedula) {
    if (cedula.length !== 10) {
        return false;
    }

    let digitosCedula;
    try {
        digitosCedula = cedula.split('').map(Number);
    } catch (e) {
        return false;
    }

    const codProvincia = parseInt(cedula.slice(0, 2), 10);
    if (codProvincia < 1 || codProvincia > 24) {
        return false;
    }

    const digito3 = digitosCedula[2];
    if (digito3 < 0 || digito3 > 6) {
        return false;
    }

    let total = 0;
    for (let i = 0; i < 9; i++) {
        let x = digitosCedula[i];
        if (i % 2 === 0) {
            x *= 2;
            if (x > 9) {
                x -= 9;
            }
        }
        total += x;
    }

    let digitoVerificador = 10 - (total % 10);
    if (digitoVerificador === 10) {
        digitoVerificador = 0;
    }

    return digitoVerificador === digitosCedula[9];
}

(function () {
    'use strict';

    function validateInput(event) {
        const input = event.target;
        const pattern = new RegExp(input.pattern);
        let isValid = pattern.test(input.value);

        // Validar el campo DNI
        if (input.id === 'dni') {
            isValid = isValid && validarCedula(input.value);
        }

        if (!isValid) {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
        } else {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        }
    }

    function handleFormSubmission(event) {
        const form = event.target;
        let isFormValid = true;

        // Recorre todos los campos con el atributo pattern
        const inputs = form.querySelectorAll('input[pattern]');
        inputs.forEach(function (input) {
            const pattern = new RegExp(input.pattern);
            let isValid = pattern.test(input.value);

            // Validar el campo DNI
            if (input.id === 'dni') {
                isValid = isValid && validarCedula(input.value);
            }

            if (!isValid) {
                input.classList.add('is-invalid');
                input.classList.remove('is-valid');
                isFormValid = false;
            } else {
                input.classList.add('is-valid');
                input.classList.remove('is-invalid');
            }
        });

        // Añade la clase was-validated para mostrar los estilos de validación
        form.classList.add('was-validated');

        // Evita el envío del formulario si hay campos inválidos
        if (!isFormValid) {
            event.preventDefault();
            event.stopPropagation();
        }
    }

    window.addEventListener('load', function () {
        const forms = document.getElementsByClassName('needs-validation');
        Array.prototype.forEach.call(forms, function (form) {
            form.addEventListener('submit', handleFormSubmission, false);

            // Añade eventos de validación en tiempo real a los campos de entrada
            const inputs = form.querySelectorAll('input[pattern]');
            inputs.forEach(function (input) {
                input.addEventListener('input', validateInput);
            });
        });
    }, false);
})();
