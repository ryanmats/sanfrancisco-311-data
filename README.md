# San Francisco 311 Data Insights
This repository contains a Flask API that connects to San Francisco's 311 
service request data in BigQuery. It also has an interactive Vue.js frontend
that displays data insights about complaints over time and complaint resolution
time using Chart.js.

## Setup

### 1. Clone the repo locally
```bash
git clone https://github.com/ryanmats/sanfrancisco-311-data
cd sanfrancisco-311-data
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add BigQuery Credentials

Acquire a BigQuery service account key JSON file, place it in the project root directory, and name it `service.json`.


### 4. Run the Backend
```bash
python main.py
```

The API will be available at `127.0.0.1:5000/api`. Verify that you see the API endpoints documentation.


### 5. Explore the Backend API Endpoints

Visit `127.0.0.1:5000/api/complaints` to see raw data about complaint counts by day. The default date
range is 2025-10-01 to 2025-10-07 and the default category includes all categories. Try to adjust the
start_date, end_date, and category arguments. For example you can try visiting this URL:
`http://127.0.0.1:5000/api/complaints?start_date=2025-09-01&end_date=2025-09-07&category=Encampment`.

Visit `127.0.0.1:5000/api/complaints_resolution_data` to see raw data about complaint resolution time
broken down into time buckets (<1 Hour, 1 Hour, 2 Hours, ... 10+ Days). The default date
range is 2025-10-01 to 2025-10-07 and the default category includes all categories. Try to adjust the
start_date, end_date, and category arguments. For example you can try visiting this URL:
`http://127.0.0.1:5000/api/complaints_resolution_data?start_date=2025-09-01&end_date=2025-09-07&category=Encampment`.

### 6. Run the Frontend

**Keep the Python Flask Backend application running in one Terminal tab.** Open a new Terminal tab to run
the Frontend web app separately.

```bash
cd client/client
npm install
npm run dev
```
The frontend web app will be available at `http://localhost:5173/`. Verify that you see the picture of
the Golden Gate Bridge and the two data visualization charts of San Francisco 311 Data.

The first chart shows complaint counts by day over time based on the date range and category specified.
The default date range is 10/01/2025 to 10/07/2025 and the default category is All Categories. This data
is surfaced by calling the `/api/complaints` backend API endpoint.

The second chart shows a distribution of how long it took for complaints to be resolved (e.g. <1 Hour,
1 Hour, 2 Hours ... 10+ Days). These are counts based on the date range and category specified. This data
is surfaced by calling the `/api/complaints_resolution_data` backend API endpoint.

Try changing the start date, end date, and category to see the charts update based on your inputs.

### 7. Creative Endpoint Explanation

As discussed above, I created a second backend API endpoint (`api/complaints_resolution_data`) that gets
data about how long it took for complaints to be resolved. For a given date range and category, you are
given a distribution of how many complaints were resolved within different time buckets (e.g. <1 Hour,
2 Hours, 3 Hours ... 10+ Days). I chose to build this endpoint because it would be useful for a variety of
important stakeholders: San Francisco residents, San Francisco government agencies, nonprofit government
accountability groups, and academic researchers:

- San Francisco residents may find this data useful because it shows how long they may expect to wait to have their own 311 complaints resolved. For example, a resident may want to know how long it has been taking for Noise complaints to be addressed.
- San Francisco government agencies may be interested in how quickly different policy priorities are being addressed. They can look at data about how quickly certain complaints (like Street and Sidewalk Cleaning) are being addressed so they can make strategic adjustments and funding adjustments as necessary.
- Nonprofit government accountability groups may be interested in this data so they can advocate for changes when the city government is not doing well. For example, they may be interested in seeing which categories of complaints are taking too long to be resolved, especially if this time to resolution has increased compared to previous years.
- Academic researchers may be interested in looking at how complaint resolution time has changed over time as they study government effectiveness. They could potentially compare this San Francisco 311 data to other cities for a deeper analysis.

### 8. Review Code

For the backend Python Flask code, visit `main.py`. Here you will find code for the two API endpoints.

For the frontend Vue.js/HTML code, visit `client/client/src/components/HelloWorld.vue`.

### 9. Development Notes and Use of AI

I used AI to assist my development of this project primarily by using ChatGPT and Google AI to teach me more
about frontend development with Vue.js, since I have not used it before. This was particularly helpful with
using the Chart.JS library to generate data visualizations. I also used AI to help debug some tricky syntax
issues (often resolved by adjusting something minor like adding a closing parentheses). Additionally, I used
AI to re-teach me how to use BigQuery Scalar Query Parameters (rather than simple string concatenation) to
protect against SQL injection risk from user-provided arguments. I remembered that this was a thing, but used
AI to get the correct syntax necessary.

While AI was very helpful, I made an effort throughout this project to learn the development concepts it was
teaching me rather than just blindly copying and pasting and hoping for the best.

### 10. Future Development

Code Cleanup:
- Clean up the frontend Vue.js code to remove parts of the initial starter project that we don't actually need. For the purposes of this project I did not get around to this yet because of timing and because I am new to Vue.js and didn't want to accidentally break the code.
- Get teammates to review Python and Vue.js code.

User Experience Research:
- Conduct user research (e.g. interviews, surveys) of key stakeholders (e.g. City of SF employees, nonprofit organizations, and academic researchers) to determine helpful additional features.

Potential Future Features:
- Show how complaint resolution time varies depending on time of day or day of week for each complaint.
- Surface information about currently open 311 requests
- Show data about complaints by neighborhood, broken them down by complaint type.
- Use latitude/longitude data to map complaint data on a geographic map of the city.

