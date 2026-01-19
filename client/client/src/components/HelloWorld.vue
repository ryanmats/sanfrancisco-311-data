<script setup>
import { ref, onMounted, watch, computed } from 'vue';

import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  BarController,
  BarElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Title,
  Legend
} from "chart.js";

Chart.register(
  LineController,
  LineElement,
  PointElement,
  BarController,
  BarElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Title,
  Legend
);

// Reactive objects to keep track of complaint data being sent from the backend API.
const complaints = ref([]);
const complaintsResolution = ref([]);
const error = ref(null);

const startDate = ref('2025-10-01'); // default
const endDate = ref('2025-10-07');   // default
const category = ref('All Categories'); // default

// Set up these chart variables (for both charts) as computed properties that automatically recalculate when their dependencies change when the backend API is called to fetch data.
const labels = computed(() => complaints.value.map(c => c.created_date));
const values = computed(() => complaints.value.map(c => c.count));
const labelsComplaintsResolution = computed(() => complaintsResolution.value.map(c => c.time_bucket));
const valuesComplaintsResolution = computed(() => complaintsResolution.value.map(c => c.count));

// List of top categories in 2025. There are some other minor categories (and categories that were used in previous years) that we could potentially add as well, but I kept it to the top 28 here for simplicity.
const categories = [
  'All Categories',
  'Street and Sidewalk Cleaning',
  'Parking Enforcement',
  'Graffiti Public',
  'General Request',
  'Encampment',
  'Graffiti Private',
  'Tree Maintenance',
  'Blocked Street and Sidewalk',
  'Sidewalk and Curb',
  'Illegal Postings',
  'Noise',
  'RPD General',
  'Litter Receptacle Maintenance',
  'Street Defect',
  'Sewer',
  'Damage Property',
  'MTA Parking Traffic Signs Normal Priority',
  'Muni Service Feedback',
  'Muni Employee Feedback',
  'MTA Parking Traffic Signs High Priority',
  'Streetlights',
  'Residential Building',
  'Shared Spaces Request',
  'Water Quality',
  'Autonomous Vehicle Complaints',
  'Temporary Sign Applications',
  'Citations Questions Comments'
];

// Set up chart canvas and instance reactive containers (these will be populated later)
const chartCanvas = ref(null);
const chartInstance = ref(null);
const chartCanvasComplaintsResolution = ref(null);
const chartInstanceComplaintsResolution = ref(null);

// --- Helper function to call Python Flask backend ---
const fetchData = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Response Error!');
    return await response.json();
  } catch (err) {
    console.error('Error connecting to backend:', err);
    error.value = err.message;
    return [];
  }
};

// --- Render a chart (for both Complaints Over Time and Time to Resolution Charts) ---
const renderChartInstance = (canvasRef, chartInstanceRef, chartType, chartData, title) => {
  if (!canvasRef.value) return;

  if (chartInstanceRef.value) {
    chartInstanceRef.value.destroy();
    chartInstanceRef.value = null;
  }

  chartInstanceRef.value = new Chart(canvasRef.value, {
    type: chartType,
    data: chartData,
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: title,
          color: 'white',
          font: { size: 20, weight: 'bold' },
        },
      },
      scales: {
        x: { title: { display: true, text: chartData.xLabel || '' } },
        y: { title: { display: true, text: chartData.yLabel || '' }, beginAtZero: true },
      },
    },
  });
};

// --- Updates Complaints Over Time data/chart using backend API call ---
const updateComplaintData = async () => {
  const url = `http://127.0.0.1:5000/api/complaints?start_date=${startDate.value}&end_date=${endDate.value}&category=${category.value}`;
  complaints.value = await fetchData(url);

  renderChartInstance(
    chartCanvas,
    chartInstance,
    'line',
    {
      labels: labels.value,
      datasets: [{ label: 'Number of Complaints', data: values.value, backgroundColor: 'rgba(54,162,235,0.5)', borderColor: 'rgba(54,162,235,1)', borderWidth: 2 }],
      xLabel: 'Date',
      yLabel: 'Number of Complaints',
    },
    `Complaints: ${category.value} (${startDate.value} to ${endDate.value})`
  );
};

// --- Updates Time to Resolution data/chart using backend API call ---
const updateComplaintsResolutionData = async () => {
  const url = `http://127.0.0.1:5000/api/complaints_resolution_data?start_date=${startDate.value}&end_date=${endDate.value}&category=${category.value}`;
  complaintsResolution.value = await fetchData(url);

  renderChartInstance(
    chartCanvasComplaintsResolution,
    chartInstanceComplaintsResolution,
    'bar',
    {
      labels: labelsComplaintsResolution.value,
      datasets: [{ label: 'Number of Complaints', data: valuesComplaintsResolution.value, backgroundColor: 'rgba(54,162,235,0.5)', borderColor: 'rgba(54,162,235,1)', borderWidth: 2 }],
      xLabel: 'Time to Resolution',
      yLabel: 'Number of Complaints',
    },
    'Time to Resolution: ' + category.value + ' (' + startDate.value + ' to ' + endDate.value + ')'
  );
};

// --- Initialization - call backend and create charts using default date ranges / category ---
onMounted(() => {
  updateComplaintData();
  updateComplaintsResolutionData();
});

// --- Watch date range / category filters. When they change, call the backend API and update charts. ---
watch([startDate, endDate, category], () => {
  updateComplaintData();
  updateComplaintsResolutionData();
});
</script>

<template>
  <div class="greetings">
    <h1 class="green">SF 311 Complaint Data</h1>
    <p v-if="error">{{ error }}</p>

    <h2>Filter by Date Range and/or Category</h2>
    <div class="filters">
      <input type="date" :value="startDate" @change="e => startDate = e.target.value" />
      <input type="date" :value="endDate" @change="e => endDate = e.target.value" />

      <select v-model="category">
        <option v-for="option in categories" :key="option" :value="option">{{ option }}</option>
      </select>
    </div>

    <canvas ref="chartCanvas" class="chart"></canvas>
    <canvas ref="chartCanvasComplaintsResolution" class="chart"></canvas>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.chart {
  max-width: 800px;
  width: 100%;
  height: 400px;
  margin: auto;
}
</style>
