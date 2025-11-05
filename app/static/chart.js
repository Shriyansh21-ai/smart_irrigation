const ctx = document.getElementById("sensorChart");
const chart = new Chart(ctx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      { label: "Soil Moisture", data: [], borderColor: "green" },
      { label: "Air Temp", data: [], borderColor: "red" },
      { label: "Humidity", data: [], borderColor: "blue" },
      { label: "Light", data: [], borderColor: "orange" }
    ]
  },
  options: { scales: { y: { beginAtZero: true } } }
});

async function updateData() {
  const res = await fetch("/api/sensor_data");
  const data = await res.json();

  document.getElementById("sensorData").innerHTML = `
    <p><b>Soil Temp:</b> ${data.soil_temp} °C</p>
    <p><b>Air Temp:</b> ${data.air_temp} °C</p>
    <p><b>Soil Moisture:</b> ${data.soil_moisture}%</p>
    <p><b>Humidity:</b> ${data.humidity}%</p>
    <p><b>Light:</b> ${data.light} lux</p>
    <p><b>Irrigation:</b> ${data.irrigation}</p>
  `;

  chart.data.labels.push(data.timestamp);
  chart.data.datasets[0].data.push(data.soil_moisture);
  chart.data.datasets[1].data.push(data.air_temp);
  chart.data.datasets[2].data.push(data.humidity);
  chart.data.datasets[3].data.push(data.light);
  if (chart.data.labels.length > 10) {
    chart.data.labels.shift();
    chart.data.datasets.forEach(d => d.data.shift());
  }
  chart.update();
}
setInterval(updateData, 3000);
updateData();
