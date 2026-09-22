// -------------------------
// GLOBAL CONFIG
// -------------------------
const API_BASE = "http://127.0.0.1:8000";
const $ = id => document.getElementById(id);

// -------------------------
// 1) UPLOAD CSV
// -------------------------
async function uploadDataset() {
    const fileInput = $('csvFile');
    if (!fileInput.files.length) {
        alert("Please select a CSV file!");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    $('uploadStatus').textContent = "Uploading...";

    try {
        const res = await fetch(`${API_BASE}/upload-dataset`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!res.ok) {
            $('uploadStatus').textContent = "Upload failed: " + data.detail;
            return;
        }

        $('uploadStatus').textContent = "Upload successful!";
        await loadProvinces();

    } catch (error) {
        console.error(error);
        $('uploadStatus').textContent = "Could not connect to API.";
    }
}

// -------------------------
// 2) LOAD PROVINCES
// -------------------------
async function loadProvinces() {
    try {
        const res = await fetch(`${API_BASE}/provinces`);
        const data = await res.json();

        if (!res.ok) {
            alert("Error loading provinces: " + data.detail);
            return;
        }

        $('provinceSelect').innerHTML = data.provinces
            .map(p => `<option>${p}</option>`)
            .join("");

    } catch (error) {
        console.error("Error loading provinces:", error);
        alert("Could not reach API for /provinces.");
    }
}

// -------------------------
// 3) MODE SWITCH (Province vs Farmer)
// -------------------------
$('modeSelect').addEventListener('change', () => {
    const mode = $('modeSelect').value;
    $('provinceMode').classList.toggle('hidden', mode !== 'province');
    $('farmerMode').classList.toggle('hidden', mode !== 'farmer');
});

// -------------------------
// 4) TRAIN MODEL
// -------------------------
$('trainBtn').addEventListener('click', async () => {
    const prov = $('provinceSelect').value;
    if (!prov) return alert("Select a province first.");

    $('trainStatus').textContent = "Training...";

    const res = await fetch(`${API_BASE}/train?province=${prov}`, {
        method: "POST"
    });

    const data = await res.json();

    if (!res.ok) {
        $('trainStatus').textContent = "Error: " + data.detail;
        return;
    }

    $('trainStatus').textContent = "Model trained!";
    $('modelInfo').classList.remove('hidden');

    $('statR2').textContent = data.r2;
    $('statRmse').textContent = data.rmse;
    $('statSlope').textContent = data.slope;
    $('statIntercept').textContent = data.intercept;
    $('plotImg').src = "data:image/png;base64," + data.plot_png_base64;
});

// -------------------------
// 5) PREDICT PROVINCE
// -------------------------
$('predictBtn').addEventListener('click', async () => {
    const prov = $('provinceSelect').value;
    const year = $('predYear').value;
    if (!year) return alert("Enter a year.");

    const res = await fetch(`${API_BASE}/predict-province?province=${prov}&year=${year}`);
    const data = await res.json();

    $('predResult').classList.remove('hidden');
    $('predResult').innerHTML = `
    <strong>${prov}</strong> (${year})<br>
    Predicted: <strong>${data.predicted_tons.toFixed(3)} tons</strong><br>
    Productivity: <strong>${data.predicted_tons_per_ha.toFixed(3)} tons/ha</strong>
`;
});

// -------------------------
// 6) PREDICT FARMER
// -------------------------
$('predictFarmerBtn').addEventListener('click', async () => {
    const prov = $('provinceSelect').value;
    const area = $('areaHa').value;
    const year = $('farmerYear').value;

    let url = `${API_BASE}/predict-farmer?province=${prov}&area_ha=${area}`;
    if (year) url += `&year=${year}`;

    const res = await fetch(url);
    const data = await res.json();

    $('farmerResult').classList.remove('hidden');
    $('farmerResult').innerHTML = `
        <strong>${prov}</strong><br>
        Area: ${area} ha <br>
        Predicted: <strong>${data.predicted_tons.toFixed(3)} tons</strong><br>
        Productivity: <strong>${data.predicted_tons_per_ha.toFixed(3)} tons/ha</strong>
    `;
});