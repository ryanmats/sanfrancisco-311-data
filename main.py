from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError


app = Flask(__name__)
CORS(app)

# Initialize BigQuery client
client = bigquery.Client.from_service_account_json('service.json')

# Set default start/end dates
DEFAULT_START_DATE = '2025-10-01'
DEFAULT_END_DATE = '2025-10-07'


def parse_request_args():
    """Parse request arguments for start_date, end_date, and category."""

    # Get the start_date parameter, set default if not provided
    start_date = request.args.get('start_date', DEFAULT_START_DATE)

    # Get the start_date parameter, set default if not provided
    end_date = request.args.get('end_date', DEFAULT_END_DATE)

    # Get the category parameter.
    category = request.args.get('category')
    if category == "All Categories":
        category = None

    return start_date, end_date, category


def build_where_sql(start_date, end_date, category):
    """Build SQL WHERE clauses and BigQuery parameters.
       We use BigQuery Scalar Query Parameters to protect against SQL injection."""

    where_clauses = ["DATE(created_date) BETWEEN @start_date AND @end_date"]
    query_params = [
        bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
    ]
    if category:
        where_clauses.append("category = @category")
        query_params.append(bigquery.ScalarQueryParameter("category", "STRING", category))
    where_sql = " AND ".join(where_clauses)
    return where_sql, query_params


@app.route('/')
def index():
    """Root endpoint listing available API routes."""
    return jsonify({
        'message': 'SF 311 Service Requests API',
        'endpoints': [
            'GET /api/complaints - Get number of complaints over time, by category.',
            'GET /api/complaints_resolution_data - Get data about time to resolution for complaints, by category.'
        ]
    })


@app.route('/api/complaints')
def get_complaints():
    """Retrieve SF 311 complaints within the provided date range, with an optional category parameter."""
    
    start_date, end_date, category = parse_request_args()
    where_sql, query_params = build_where_sql(start_date, end_date, category)

    try:
        query = f"""
        SELECT DATE(created_date) created_date, COUNT(*) as date_category_count
        FROM `bigquery-public-data.san_francisco_311.311_service_requests`
        WHERE {where_sql}
        GROUP BY DATE(created_date)
        ORDER BY DATE(created_date)
        """

        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        results = client.query(query, job_config=job_config).result()
        data = [
            {"created_date": row.created_date.isoformat(), "count": row.date_category_count}
            for row in results
        ]

        return jsonify(data)
    except GoogleAPIError as e:
        print(f"BigQuery Error: {e}")
        return jsonify({'status': 'error', 'message': 'Database query failed.'}), 500
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error.'}), 500


@app.route('/api/complaints_resolution_data')
def get_complaints_resolution_data():
    """Retrieve data about how long it took SF 311 complaints to be resolved, with a provided date range and optional category parameter."""
    
    start_date, end_date, category = parse_request_args()
    where_sql, query_params = build_where_sql(start_date, end_date, category)

    try:
        query = f"""
        WITH durations AS (
            SELECT
                TIMESTAMP_DIFF(closed_date, created_date, HOUR) as hours
            FROM `bigquery-public-data.san_francisco_311.311_service_requests`
            WHERE {where_sql}
        )

        SELECT
          CASE
            WHEN hours <= 0 THEN '<1 Hour'
            WHEN hours = 1 THEN '1 Hour'
            WHEN hours = 2 THEN '2 Hours'
            WHEN hours = 3 THEN '3 Hours'
            WHEN hours BETWEEN 4 and 11 THEN '4 to 11 Hours'
            WHEN hours BETWEEN 12 and 23 THEN '12 to 23 Hours'
            WHEN hours BETWEEN 24 and 47 THEN '1 Day'
            WHEN hours BETWEEN 48 and 71 THEN '2 Days'
            WHEN hours between 72 and 143 THEN '3 to 5 Days'
            WHEN hours between 144 and 263 THEN '6 to 10 Days'
            WHEN hours >= 264 THEN '10+ Days'
            ELSE 'Not Resolved'
          END as time_bucket,
          count(*) as count
        FROM durations
        GROUP BY time_bucket
        ORDER BY
          CASE time_bucket
            WHEN '<1 Hour' THEN 1
            WHEN '1 Hour' THEN 2
            WHEN '2 Hours' THEN 3
            WHEN '3 Hours' THEN 4
            WHEN '4 to 11 Hours' THEN 5
            WHEN '12 to 23 Hours' THEN 6
            WHEN '1 Day' THEN 7
            When '2 Days' THEN 8
            WHEN '3 to 5 Days' THEN 9
            WHEN '6 to 10 Days' THEN 10
            WHEN '10+ Days' THEN 11
            WHEN 'Not Resolved' THEN 12
          END;
        """

        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        results = client.query(query, job_config=job_config).result()
        data = [
            {"time_bucket": row.time_bucket, "count": row.count}
            for row in results
        ]
        return jsonify(data)
    except GoogleAPIError as e:
        print(f"BigQuery Error: {e}")
        return jsonify({'status': 'error', 'message': 'Database query failed.'}), 500
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error.'}), 500


if __name__ == '__main__':
    app.run(debug=True)