let latestInventory = [];
let inventoryChart = null;
let predictionRequest = 0;
let inventoryRequest = 0;

document.getElementById("predictionForm").addEventListener("submit", function(event) {
    event.preventDefault();
    sendData();
});

async function sendData() {
    const requestId = ++predictionRequest;
    document.getElementById("predictionResult").textContent = '';
    const form = document.getElementById("predictionForm");
    const formData = new FormData(form);

    // Convert formData to JSON object
    const jsonObject = {};
    formData.forEach((value, key) => {
        jsonObject[key] = value;
    });

    // Parse numerical values
    jsonObject.Store = parseInt(jsonObject.Store);
    jsonObject.Dept = parseInt(jsonObject.Dept);
    jsonObject.Temperature = parseFloat(jsonObject.Temperature);
    jsonObject.MarkDown1 = parseFloat(jsonObject.MarkDown1);
    jsonObject.MarkDown2 = parseFloat(jsonObject.MarkDown2);
    jsonObject.MarkDown4 = parseFloat(jsonObject.MarkDown4);
    jsonObject.MarkDown5 = parseFloat(jsonObject.MarkDown5);
    jsonObject.Size = parseInt(jsonObject.Size);
    jsonObject.Type_A = document.getElementById('Type_A').checked ? 1 : 0;
    jsonObject.Type_B = document.getElementById('Type_B').checked ? 1 : 0;
    jsonObject.Type_C = document.getElementById('Type_C').checked ? 1 : 0;
    jsonObject.Month = parseInt(jsonObject.Month);
    jsonObject.Day = parseInt(jsonObject.Day);
    jsonObject.isHoliday = jsonObject.isHoliday === "true" ? 1 : 0;

    delete jsonObject.type;

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(jsonObject)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Prediction unavailable');
        if (requestId !== predictionRequest) return;
        document.getElementById("predictionResult").textContent = `${data.prediction} $`;
    } catch (error) {
        if (requestId !== predictionRequest) return;
        document.getElementById("predictionResult").textContent = 'Prediction unavailable. Check the inputs and local server.';
    }
}

async function getDataAndPlotGraph() {
    const requestId = ++inventoryRequest;
    latestInventory = [];
    if (inventoryChart) { inventoryChart.destroy(); inventoryChart = null; }
    var storeNumber = document.getElementById("storeSelect").value;
    var deptNumber = document.getElementById("deptSelect").value;

    try {
        const response = await fetch(`/get_data?store_number=${storeNumber}&dept_number=${deptNumber}`, {
            method: 'GET',
            mode: 'cors'
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (!Array.isArray(data)) throw new Error(data.error || "Invalid inventory response");
        const normalizedData = data.map(row => {
            const inventory = Number(row.Last_Known_Inventory);
            if (!Number.isFinite(inventory)) throw new Error("Invalid inventory value");
            return {...row, Last_Known_Inventory: inventory};
        });
        if (requestId !== inventoryRequest) return;
        latestInventory = normalizedData;

        // Extract dates and inventory levels from data
        const dates = normalizedData.map(row => row.Date);
        const inventory = normalizedData.map(row => row.Last_Known_Inventory);

        // Call function to plot graph
        plotGraph(dates, inventory);
    } catch (error) {
        if (requestId !== inventoryRequest) return;
        alert("Inventory unavailable. Check the local server and try again.");
    }
}

function plotGraph(xValues, yValues) {
    if (!yValues.length) return;
    inventoryChart = new Chart("myChart", {
        type: "line",
        data: {
            labels: xValues,
            datasets: [{
                fill: false,
                lineTension: 1,
                backgroundColor: "rgba(0,0,255,1.0)",
                borderColor: "#6e985f",
                data: yValues,
                pointStyle: 'circle', // Change the point style to circle
                pointRadius: 3, // Adjust the point radius
                pointBackgroundColor: '#74b45c', // Set the color of the points
                pointBorderColor: '#92be82', // Set the border color of the points
                pointBorderWidth: 1 ,// Set the border width of the points
                fontWeight: 200 
              }]
        },
        options: {
            legend: { display: false },
            scales: {
                yAxes: [{ ticks: { min: Math.min(...yValues) - 1, max: Math.max(...yValues) + 1 } }],
            }
        }
    });
}

document.getElementById("inventory_form").addEventListener("submit", function(event) {
    event.preventDefault();
    getDataAndPlotGraph();
});

document.getElementById("email-form").addEventListener("submit", function(event) {
    event.preventDefault();

    // Get email address
    const email = document.getElementById("email").value;

    // Get prediction data
    const predictionData = document.getElementById("predictionResult").textContent;

    // Use the same records as the chart, rather than a removed table.
    const inventoryData = latestInventory.map(row => ({
        store: row.Store, dept: row.Dept, date: row.Date,
        isHoliday: row.IsHoliday, inventory: row.Last_Known_Inventory
    }));

    // Prepare data to send to Flask API
    const data = {
        email,
        predictionData,
        inventoryData
    };

    // Send data to Flask API
    fetch('/send-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(async response => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Email delivery failed");
        return data;
    })
    .then(data => {
        alert(data.message); // Show success message
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to send email. Please try again later.');
    });
});

async function populateDropdowns() {
    populateStoreDropdown();
    populateDeptDropdown();
}

function populateStoreDropdown() {
    const storeSelect = document.getElementById("storeSelect");
    for (let i = 1; i <= 45; i++) {
        const option = document.createElement("option");
        option.text = `Store ${i}`;
        option.value = i;
        storeSelect.add(option);
    }
}

function populateDeptDropdown() {
    const deptSelect = document.getElementById("deptSelect");
    for (let i = 1; i <= 99; i++) {
        const option = document.createElement("option");
        option.text = `Dept ${i}`;
        option.value = i;
        deptSelect.add(option);
    }
}

// Initialize the page
populateDropdowns();
