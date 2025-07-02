document.addEventListener('DOMContentLoaded', () => {
    const cycleInputs = document.querySelectorAll('.cycle');
    const totalInputs = document.querySelectorAll('.total');

    const selectPeriodo = document.getElementById('selectPeriodo');
    const btnSeleccionarPeriodo = document.getElementById('btnSeleccionarPeriodo');
    const btnGuardarCambios = document.getElementById('btnGuardarCambios');
    const alertContainer = document.getElementById('alert-container');

    // Función para cargar los datos del periodo seleccionado
    btnSeleccionarPeriodo.addEventListener('click', async () => {
        const periodoId = selectPeriodo.value;

        // Primero verifica si se ha seleccionado un periodo
        if (!periodoId) {
            mostrarMensaje('Por favor, selecciona un periodo.', 'alert-danger');
            return; // Termina la ejecución para evitar errores adicionales
        }

        // Si hay un periodo seleccionado, intenta cargar los datos
        try {
            const response = await fetch(`/cargarDatos/${periodoId}/`);
            if (response.ok) {
                const data = await response.json();
                populateTable(data);
            } else {
                console.error('Error status:', response.status);
                mostrarMensaje('Por favor, selecciona un periodo.', 'alert-danger');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            mostrarMensaje('Por favor, selecciona un periodo.', 'alert-danger');
        }
    });

    // Función para llenar la tabla con los datos recibidos del servidor
    function populateTable(data) {
        const dataFields = ['matriculados', 'aprobados', 'reprobados', 'desertores', 'foraneos'];

        // Llenar los totales del periodo
        dataFields.forEach(field => {
            document.getElementById(`total_${field}`).textContent = data[`total_${field}`];
        });

        // Llenar los datos de cada ciclo
        Object.keys(data).forEach(key => {
            if (key.startsWith('ciclo_')) {
                const cicloData = data[key];
                const cicloNumero = key.split('_')[1];

                dataFields.forEach(field => {
                    const input = document.querySelector(`input[data-field="${field}_${cicloNumero}"]`);
                    if (input) {
                        input.value = cicloData[field] || 0;
                    }
                });
            }
        });
    }







    btnGuardarCambios.addEventListener('click', async (event) => {
        event.preventDefault(); // Previene la recarga de la página

        const periodoId = selectPeriodo.value;
        if (!periodoId) {
            mostrarMensaje('Por favor, selecciona un periodo.', 'alert-danger');
            return;
        }

        const data = {
            total_matriculados: parseInt(document.getElementById('total_matriculados').textContent) || 0,
            total_aprobados: parseInt(document.getElementById('total_aprobados').textContent) || 0,
            total_reprobados: parseInt(document.getElementById('total_reprobados').textContent) || 0,
            total_desertores: parseInt(document.getElementById('total_desertores').textContent) || 0,
            total_foraneos: parseInt(document.getElementById('total_foraneos').textContent) || 0,
            ciclos: []
        };

        for (let i = 1; i <= 9; i++) {
            data.ciclos.push({
                numero: i,
                matriculados: parseInt(document.querySelector(`input[data-field="matriculados_${i}"]`).value) || 0,
                aprobados: parseInt(document.querySelector(`input[data-field="aprobados_${i}"]`).value) || 0,
                reprobados: parseInt(document.querySelector(`input[data-field="reprobados_${i}"]`).value) || 0,
                desertores: parseInt(document.querySelector(`input[data-field="desertores_${i}"]`).value) || 0,
                foraneos: parseInt(document.querySelector(`input[data-field="foraneos_${i}"]`).value) || 0
            });
        }

        try {
            const response = await fetch(`/guardarcambiosDatos/${periodoId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                mostrarMensaje(result.message || 'Datos guardados correctamente.', 'alert-success');
                vaciarModal();
            } else {
                mostrarMensaje('Error al guardar los datos.', 'alert-danger');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            mostrarMensaje('Error al guardar los datos.', 'alert-danger');
        }
    });

    function mostrarMensaje(mensaje, tipo) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${tipo} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertContainer.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.classList.remove('show');
            alertDiv.addEventListener('transitionend', () => alertDiv.remove());
        }, 3000);
    }

    function vaciarModal() {
        // Solo resetea los campos de la tabla, no elimina la estructura de la tabla
    const dataFields = ['matriculados', 'aprobados', 'reprobados', 'desertores', 'foraneos'];

    dataFields.forEach(field => {
        document.getElementById(`total_${field}`).textContent = '0'; // Restablecer los totales
    });

    for (let i = 1; i <= 9; i++) {
        const fields = ['matriculados', 'aprobados', 'reprobados', 'desertores', 'foraneos'];
        fields.forEach(field => {
            const input = document.querySelector(`input[data-field="${field}_${i}"]`);
            if (input) {
                input.value = ''; // Vaciar los valores de cada ciclo
            }
        });
    }

    selectPeriodo.selectedIndex = 0; // Resetea el combobox a "Seleccione un periodo"
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.getElementById('modificarModal').addEventListener('hidden.bs.modal', vaciarModal);


    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    cycleInputs.forEach(input => {
        input.addEventListener('input', () => {
            const type = input.dataset.type;
            const relatedCycleInputs = document.querySelectorAll(`.cycle[data-type="${type}"]`);
            const totalInput = document.querySelector(`.total[data-type="${type}"]`);

            let sum = 0;
            relatedCycleInputs.forEach(cycleInput => {
                sum += Number(cycleInput.value || 0);
            });
            totalInput.value = sum;
        });
    });

    totalInputs.forEach(input => {
        input.addEventListener('input', () => {
            const type = input.dataset.type;
            const relatedCycleInputs = document.querySelectorAll(`.cycle[data-type="${type}"]`);

            relatedCycleInputs.forEach(cycleInput => {
                cycleInput.value = '';
            });
        });
    });

    const importExcelButton = document.getElementById('importExcel');
    const fileInput = document.getElementById('fileInput');

    importExcelButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            importFromExcel(file);
        }
    });

    async function importFromExcel(file) {
        const reader = new FileReader();
        reader.onload = async (event) => {
            const data = new Uint8Array(event.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            const sheetName = workbook.SheetNames[0];
            const sheet = workbook.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

            populateFields(jsonData);
        };
        reader.readAsArrayBuffer(file);
    }

    function populateFields(data) {
        const headers = data[0].map(header => typeof header === 'string' ? header.toLowerCase() : header);
        const rows = data.slice(1);

        rows.forEach(row => {
            if (row.length > 1) { // Verificar que haya datos en la fila
                const type = (row[0] && typeof row[0] === 'string') ? row[0].toLowerCase() : ''; // Tipo de dato (matriculados, aprobados, etc.)
                row.forEach((value, index) => {
                    if (index > 0 && index < headers.length) { // Ignorar la columna de 'Ciclo' y 'Total'
                        const cycleInput = document.querySelector(`.cycle[data-type="${type}"][data-cycle="${index}"]`);
                        if (cycleInput) {
                            cycleInput.value = value;
                        }
                    }
                });
            }
        });

        // Actualizar los totales después de llenar los ciclos
        cycleInputs.forEach(input => {
            const event = new Event('input');
            input.dispatchEvent(event);
        });
    }

    const toggleColumnsButton = document.getElementById('toggleColumns');
    toggleColumnsButton.addEventListener('click', () => {
        const cycleColumns = document.querySelectorAll('.cycle-col');
        cycleColumns.forEach(column => {
            const cycle = column.getAttribute('data-cycle');
            const cycleCells = document.querySelectorAll(`.cycle[data-cycle="${cycle}"]`);
            cycleCells.forEach(cell => {
                cell.classList.toggle('d-none'); // Usar la clase de Bootstrap para ocultar/mostrar
            });
        });
    });
});
