
const selectedCycles = JSON.parse(localStorage.getItem('selectedCycles'));
console.log("JavaScript is running");
console.log("Selected Cycles from localStorage: ", selectedCycles);

const getObtionChart = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart1/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart1/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

const getObtionChart2 = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart2/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart2/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

const getObtionChart3 = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart3/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart3/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

const getObtionChart4 = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart4/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart4/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

const getObtionChart5 = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart5/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart5/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

const getObtionChart6 = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart6/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart6/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

const getObtionChart7 = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart7/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart7/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

const getObtionChart8 = async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart8/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart8/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};

const getObtionChart9= async (year = null) => {
    try {
        let response;
        if (year) {
            console.log("Enviando solicitud POST con año:", year);
            response = await fetch("http://127.0.0.1:8000/api/get_chart9/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ year: year })
            });
        } else {
            console.log("Enviando solicitud GET");
            response = await fetch("http://127.0.0.1:8000/api/get_chart9/");
        }
        const data = await response.json();
        console.log("Datos recibidos:", data);
        return data;
    } catch (error) {
        console.error("Error al obtener datos del gráfico:", error);
        alert("Error al cargar los datos del gráfico");
    }
};


const chartDataFunctions = {
    'chart1': getObtionChart,
    'chart2': getObtionChart2,
    'chart3': getObtionChart3,
    'chart4': getObtionChart4,
    'chart5': getObtionChart5,
    'chart6': getObtionChart6,
    'chart7': getObtionChart7,
    'chart8': getObtionChart8,
    'chart9': getObtionChart9
};

const initChart = async (chartId) => {
    if (!chartId) {
        console.error("chartId is undefined");
        return;
    }
    console.log(`Initializing ${chartId}`);
    const chartElement = document.getElementById(chartId);
    if (!chartElement) {
        console.error(`Element with id ${chartId} not found`);
        return;
    }
    const myChart = echarts.init(chartElement);
    const getDataFunction = chartDataFunctions[chartId];
    if (!getDataFunction) {
        console.error(`No data function found for ${chartId}`);
        return;
    }
    myChart.setOption(await getDataFunction());
    myChart.resize();
};

const updateChart = async (chartId, year) => {
    if (!chartId) {
        console.error("chartId is undefined");
        return;
    }
    console.log(`Actualizando gráfico ${chartId} con año:`, year);
    
    let chart = echarts.getInstanceByDom(document.getElementById(chartId));
    if (!chart) {
        console.log(`No se encontró la instancia del gráfico ${chartId}, inicializando...`);
        await initChart(chartId);
        chart = echarts.getInstanceByDom(document.getElementById(chartId));
        if (!chart) {
            console.error(`No se pudo inicializar el gráfico ${chartId}`);
            return;
        }
    }

    chart.showLoading({
        text: 'Cargando datos...',
        color: '#c23531',
        textColor: '#000',
        maskColor: 'rgba(255, 255, 255, 0.8)',
        zlevel: 0
    });

    const getDataFunction = chartDataFunctions[chartId];
    if (!getDataFunction) {
        console.error(`No se encontró una función para obtener datos del gráfico ${chartId}`);
        chart.hideLoading();
        return;
    }

    let option;
    try {
        // Comprueba si la función acepta un parámetro 'year'
        if (chartId === 'chart1' || chartId === 'chart2' || chartId === 'chart3' || chartId === 'chart4' || chartId === 'chart5' || chartId === 'chart6' || chartId === 'chart7' || chartId === 'chart8') {
            option = await getDataFunction(year);
        } else {
            option = await getDataFunction();
        }
    } catch (error) {
        console.error(`Error al obtener datos para el gráfico ${chartId}:`, error);
        chart.hideLoading();
        alert(`Error al cargar los datos del gráfico ${chartId}`);
        return;
    }
    
    chart.hideLoading();

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

    const initialOption = {
        ...option,
        series: option.series.map(series => ({
            ...series,
            data: []
        }))
    };

    chart.setOption(initialOption, {
        notMerge: true,
        animation: false
    });

    animateDataLoad(chart, option);


};

const initAllCharts = async () => {
    const selectedCycles = JSON.parse(localStorage.getItem('selectedCycles')) || [];
    for (let i = 1; i <= 9; i++) {
        const chartId = `chart${i}`;
        const cycleName = `Ciclo ${i}`;
        if (selectedCycles.includes(cycleName)) {
            const chartContainer = document.getElementById(`${chartId}Container`);
            if (chartContainer) {
                chartContainer.style.display = 'flex';
                await initChart(chartId);
            } else {
                console.error(`Container for ${chartId} not found`);
            }
        }
    }
};

const showCharts = async () => {
    console.log("Showing charts based on selected cycles");
    const chart1Container = document.getElementById("chart1Container");
    const chart2Container = document.getElementById("chart2Container");
    const chart3Container = document.getElementById("chart3Container");
    const chart4Container = document.getElementById("chart4Container");
    const chart5Container = document.getElementById("chart5Container");
    const chart6Container = document.getElementById("chart6Container");
    const chart7Container = document.getElementById("chart7Container");
    const chart8Container = document.getElementById("chart8Container");
    const chart9Container = document.getElementById("chart9Container");
    const chartsRow = document.getElementById("chartsRow");

    // Oculta todos los contenedores primero
    chart1Container.style.display = "none";
    chart2Container.style.display = "none";
    chart3Container.style.display = "none";
    chart4Container.style.display = "none";
    chart5Container.style.display = "none";
    chart6Container.style.display = "none";
    chart7Container.style.display = "none";
    chart8Container.style.display = "none";
    chart9Container.style.display = "none";
    
    let visibleCharts = 0;

    if (selectedCycles && selectedCycles.includes('Ciclo 1')) {
        console.log("Showing chart1");
        chart1Container.style.display = "flex";
        await initChart();
        visibleCharts++;
    }

    if (selectedCycles && selectedCycles.includes('Ciclo 2')) {
        console.log("Showing chart2");
        chart2Container.style.display = "flex";
        await initChart2();
        visibleCharts++;
    }

    if (selectedCycles && selectedCycles.includes('Ciclo 3')) {
        console.log("Showing chart3");
        chart3Container.style.display = "flex";
        await initChart3();
        visibleCharts++;
    }

    if (selectedCycles && selectedCycles.includes('Ciclo 4')) {
        console.log("Showing chart4");
        chart4Container.style.display = "flex";
        await initChart4();
        visibleCharts++;
    }

    if (selectedCycles && selectedCycles.includes('Ciclo 5')) {
        console.log("Showing chart5");
        chart5Container.style.display = "flex";
        await initChart5();
        visibleCharts++;
    }

    if (selectedCycles && selectedCycles.includes('Ciclo 6')) {
        console.log("Showing chart6");
        chart6Container.style.display = "flex";
        await initChart6();
        visibleCharts++;
    }

    if (selectedCycles && selectedCycles.includes('Ciclo 7')) {
        console.log("Showing chart7");
        chart7Container.style.display = "flex";
        await initChart7();
        visibleCharts++;
    }

    if (selectedCycles && selectedCycles.includes('Ciclo 8')) {
        console.log("Showing chart8");
        chart8Container.style.display = "flex";
        await initChart8();
        visibleCharts++;
    }

    if (selectedCycles && selectedCycles.includes('Ciclo 9')) {
        console.log("Showing chart9");
        chart9Container.style.display = "flex";
        await initChart9();
        visibleCharts++;
    }

    // Ajusta el ancho de los contenedores visibles
    const width = visibleCharts === 1 ? '100%' : '50%';
    if (chart1Container.style.display !== 'none') chart1Container.style.width = width;
    if (chart2Container.style.display !== 'none') chart2Container.style.width = width;
    if (chart3Container.style.display !== 'none') chart1Container.style.width = width;
    if (chart4Container.style.display !== 'none') chart2Container.style.width = width;
    if (chart5Container.style.display !== 'none') chart1Container.style.width = width;
    if (chart6Container.style.display !== 'none') chart2Container.style.width = width;
    if (chart7Container.style.display !== 'none') chart1Container.style.width = width;
    if (chart8Container.style.display !== 'none') chart2Container.style.width = width;
    if (chart9Container.style.display !== 'none') chart1Container.style.width = width;

    // Fuerza un reflow para que los cambios surtan efecto
    chartsRow.offsetHeight;
};

window.addEventListener("load", async () => {
    console.log("Page loaded, executing showCharts"); // Añade esto para depurar
    await showCharts();
});

document.addEventListener('DOMContentLoaded', async () => {
    console.log("DOM cargado, inicializando...");
    await initAllCharts();
    
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
        // Actualiza todos los gráficos visibles
        for (let i = 1; i <= 9; i++) {
            const chartId = `chart${i}`;
            const chartContainer = document.getElementById(`${chartId}Container`);
            if (chartContainer && chartContainer.style.display !== 'none') {
                await updateChart(chartId, selectedYear);
            }
        }
    });
});

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