document.addEventListener("DOMContentLoaded", function () {
    const showContainerBtn = document.getElementById("showContainerBtn");
    const closeContainerBtn = document.getElementById("cancelBtn");
    const exportContainer = document.getElementById("exportContainer");
    const fileName = document.getElementById("fileName");

    showContainerBtn.addEventListener("click", function () {
        exportContainer.style.display = "block";
        fileName.value = ''; 
        fileName.placeholder = "Ingrese el nombre del archivo";
    });

    closeContainerBtn.addEventListener("click", function () {
        exportContainer.style.display = "none";
        fileName.value = ''; 
        fileName.placeholder = "Ingrese el nombre del archivo";
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const dias_Semana = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
    const fecha = new Date();
    const dia = dias_Semana[fecha.getDay()];
    document.getElementById("fecha_actual").innerHTML = `${dia}, ${fecha.toLocaleDateString()}`;
    
    const fileNameInput = document.getElementById('fileName');
    const exportBtn = document.getElementById('exportBtn');

    const selectAllCheckbox = document.getElementById("select-all");
    const rowCheckboxes = document.querySelectorAll(".row-select");
    const btnExport = document.getElementById("btnExport");
    const exportContainer = document.getElementById("exportContainer");
    const dataSections = document.querySelectorAll(".data-section");

    function updateExportButtonState() {
        const isAnyChecked = Array.from(rowCheckboxes).some(checkbox => checkbox.checked);
        btnExport.disabled = !isAnyChecked;//Se actualiza el estado del botón Exportar
    }

    selectAllCheckbox.addEventListener("change", function () {
        rowCheckboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;//Cuando selecciona todos
        });
        updateExportButtonState();
    });

    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function () {//Cuando selecciona algunas
            const allChecked = Array.from(rowCheckboxes).every(checkbox => checkbox.checked);
            selectAllCheckbox.checked = allChecked;
            updateExportButtonState();
        });
    });
    
    btnExport.addEventListener("click", function () {//Abrir modal de acuerdo a seleccion
        const selectedIds = Array.from(rowCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.getAttribute("data-id"));

        dataSections.forEach(section => {
            const sectionId = section.getAttribute("data-id");
            if (selectedIds.includes(sectionId)) {
                section.style.display = "block"; // Mostrar las seleccionadas
            } else {
                section.style.display = "none"; // Ocultar las no seleccionadas
            }
        });
    });

    exportBtn.addEventListener('click', function () {
        const fileName = fileNameInput.value.trim();
        if (fileName) {
            generarPDF(fileName);
        } else {
            alert("Por favor, ingrese un nombre de archivo.");
        }
    });

    function generarPDF(fileName) {
        if (!fileName) {
            alert("Por favor, ingrese un nombre al archivo.");
            return;
        }

        const content = document.getElementById('docPDF');
        const opt = {
            margin: 0.5,
            filename: `${fileName}.pdf`,
            image: {
                type: 'jpeg',
                quality: 0.95
            },
            html2canvas: {
                scale: 4,
                useCORS: true
            },
            jsPDF: {
                unit: 'in',
                format: 'a4',
                orientation: 'portrait'
            }
        };

    // Generar el PDF
    html2pdf().set(opt).from(content).save().then(function () {
        console.log('PDF generado y guardado');
        $('#exportContainer').modal('hide');
        fileNameInput.value = '';
    }).catch(function (error) {
        console.error('Error al generar el PDF:', error);
    });
    }
});
