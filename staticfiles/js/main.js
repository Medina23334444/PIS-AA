const getObtionChart = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

let myChart;

const initChart = async () => {
    console.log("Inicializando gráfico");
    myChart = echarts.init(document.getElementById("chart"));
    const option = await getObtionChart();
    myChart.setOption(option);
    myChart.resize();
};

const updateChart = async (year) => {
    console.log("Actualizando gráfico con año:", year);
    
    myChart.showLoading({
        text: 'Cargando datos...',
        color: '#c23531',
        textColor: '#000',
        maskColor: 'rgba(255, 255, 255, 0.8)',
        zlevel: 0
    });

    const option = await getObtionChart(year);
    
    myChart.hideLoading();

    function animateDataLoad(chart, option) {
        const totalDataPoints = option.series[0].data.length;
        const animationDuration = 5000; // Duración total de la animación en milisegundos
        const updateInterval = 30; // Actualizar cada 50ms

        let currentData = option.series.map(() => []);
        let currentIndex = 0;

        function updateFrame() {
            if (currentIndex < totalDataPoints) {
                option.series.forEach((series, seriesIndex) => {
                    currentData[seriesIndex].push(series.data[currentIndex]);
                });

                chart.setOption({
                    series: option.series.map((series, index) => ({
                        ...series,
                        data: currentData[index]
                    }))
                });

                currentIndex++;
                setTimeout(updateFrame, updateInterval);
            }
        }

        updateFrame();
    }

    // Configura las opciones iniciales con series vacías
    const initialOption = {
        ...option,
        series: option.series.map(series => ({
            ...series,
            data: []
        }))
    };

    myChart.setOption(initialOption, {
        notMerge: true,
        animation: false
    });

    // Inicia la animación
    animateDataLoad(myChart, option);
};

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

document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOM cargado, inicializando...");
    await initChart();

    const yearSelect = document.getElementById('yearSelect');
    const predictionButton = document.getElementById('predictionButton');

    if (!yearSelect) console.error("No se encontró el elemento yearSelect");
    if (!predictionButton) console.error("No se encontró el elemento predictionButton");

    predictionButton.addEventListener('click', async () => {
        console.log("Botón de predicción clickeado");
        const selectedYear = yearSelect.value;
        console.log("Año seleccionado:", selectedYear);
        if (selectedYear === 'Seleccion Año Prediccion') {
            alert('Por favor, selecciona un año para la predicción.');
            return;
        }
        await updateChart(selectedYear);
    });
});