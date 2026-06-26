Project Context:

We are building a production-grade aviation crew analytics platform that ingests operational crew data from Excel or CSV files and converts it into interactive dashboards, metrics, comparisons, alerts, and decision-support insights. The current reference input is an Excel file similar to** **`template.xlsx`, which contains detailed operational records for pilots and crew members. The system should support both pilots and cabin crew, and it should be designed to handle large datasets efficiently from the beginning.

The core purpose of the tool is to analyze crew operational workload, flight activity, duty patterns, rest periods, fatigue-related indicators, and crew-level performance/usage trends across configurable time windows. The user should be able to upload a dataset, select one or more crew members, define a time range using** **`t_initial` and** **`t_final`, and obtain clean dashboards, KPI cards, charts, tables, alerts, and downloadable reports.

The dataset includes aviation crew fields such as crew identifiers, full names, rank, home base, fleet plan, trips, duties, flight legs, aircraft type, departure/arrival information, duty start/end timestamps, trip start/end timestamps, block time, duty time, rest time, fatigue or alertness indicators, KSS-like metrics, duty extension flags, flight duty flags, and crew composition fields such as captain, first officer, extra crew, or similar operational roles. Some relevant columns observed or expected include fields like** **`crew_id`,** **`fullname`,** **`rank`,** **`homebase`,** **`fleet_plan`,** **`trip`,** **`trip number`,** **`tstartHB`,** **`tendHB`,** **`duty`,** **`dtype`,** **`dstartHB`,** **`dendHB`,** **`dduty`,** **`dblock`,** **`drest`,** **`ldeparture`,** **`larrival`,** **`lblock`,** **`actype`,** **`lcode`,** **`alertness`,** **`kss`,** **`is duty extension`,** **`flightduty`,** **`onduty`,** **`cp`,** **`fo`,** **`ej`, and** **`so`.

Important domain note: in the current project description,** **`dduty` is being treated as flight/block hours and** **`dblock` as duty/jornada hours, but this must be validated against the actual Excel data and aviation naming conventions. The implementation should not hard-code assumptions blindly. It should include a data dictionary/configuration layer where column semantics can be mapped, corrected, or overridden by the developer or by the user if the source data uses non-standard naming.

The application should be built primarily with Dash and Plotly for the frontend analytics interface. Dash should provide interactive filtering, date range selection, crew member search, comparison views, KPI cards, charts, tables, and exportable reports. The backend should use FastAPI to delegate heavy computations, file processing, API operations, alert generation, and long-running jobs. The architecture should avoid putting expensive data processing directly inside Dash callbacks whenever possible. Dash should act as the interactive UI layer, while FastAPI and background workers should handle heavier backend operations.

The tool must support Excel and CSV uploads, but CSV should be recommended for performance when datasets are large. Excel support is still required because many aviation operations teams work directly with spreadsheet exports. The ingestion layer should validate file format, detect columns, normalize column names, parse dates and times, convert numeric duration fields, handle missing values, detect invalid records, and produce a clean internal representation of the data. The system should be robust against inconsistent spreadsheets, mixed date formats, missing columns, extra columns, duplicate rows, and incorrect data types.

Performance is a major design requirement. The tool should be able to process large operational datasets quickly. The agent should consider high-performance libraries such as Polars, PyArrow, DuckDB, and efficient Pandas usage where appropriate. The system should avoid unnecessary full-data scans in UI callbacks. It should use caching, precomputed aggregations, columnar formats, query optimization, and lazy evaluation where useful. Uploaded files may be converted internally into efficient formats such as Parquet for repeated analysis. The app should be designed so that repeated filters, crew lookups, date range queries, and comparison views are fast.

Core analysis capabilities should include:

* Single crew member analysis over a selected time range.
* Comparison between two or more crew members.
* Duty time / jornada analysis.
* Flight or block hour analysis.
* Rest time analysis.
* Trip and duty pattern analysis.
* Flight leg analysis.
* Aircraft type distribution.
* Route or airport pair analysis.
* Home base and fleet-based filtering.
* Rank-based filtering.
* Monthly, weekly, and daily summaries.
* Crew utilization metrics.
* Fatigue and alertness indicators.
* KSS or similar subjective fatigue metric analysis.
* Detection of duty extensions.
* Detection of unusually high workload.
* Detection of insufficient rest or suspicious operational patterns.
* Identification of outliers and threshold violations.
* Alert generation based on configurable rules.
* Email delivery for alerts.
* Export of filtered data, summaries, charts, and reports.

The dashboard should not be a static report. It should behave like an analytical workspace. Users should be able to ask operational questions such as:

* What happened with this crew member between** **`t_initial` and** **`t_final`?
* How many duty hours, flight hours, rest hours, and flight legs did this crew member accumulate?
* How does crew member A compare against crew member B in the same period?
* Which crew members show the highest workload?
* Which crew members had repeated duty extensions?
* Which records indicate low alertness or possible fatigue risk?
* Which aircraft types, routes, or bases are associated with higher duty load?
* Are there anomalies or operational patterns that require attention?
* Which crew members should trigger an email alert based on predefined thresholds?

The platform should eventually include configurable alert rules. Examples may include thresholds for maximum duty hours, maximum block hours, low rest time, high number of duty extensions, low alertness score, high KSS score, high accumulated workload over a rolling period, or abnormal deviation from a crew member’s baseline. Alerts should be generated by backend logic, stored or logged, shown in the UI, and optionally sent by email. The email system should be implemented in a production-ready way, using environment variables for credentials and avoiding hard-coded secrets.

The system should be modular and maintainable. A strong project architecture is required. 

The first development task is not to build the full application yet. The first task is to create a professional** **`requirements.txt` file that includes the Python dependencies an advanced developer would use to build a robust, scalable, efficient Dash + FastAPI analytics tool for this aviation crew dataset.

The dependency list should cover:

* Dash and Plotly dashboard development.
* FastAPI backend development.
* Efficient Excel and CSV reading.
* High-performance data processing.
* Data validation and schemas.
* Background task processing.
* Caching.
* Email alerts.
* Environment configuration.
* Logging and monitoring.
* Testing.
* Production serving.
* Authentication/session support if useful.
* Exporting reports.
* Code quality tools such as linting, formatting, and type checking.

The resulting** **`requirements.txt` should not be a toy dependency list. It should be realistic for a serious internal analytics product. It should include stable and widely adopted libraries, while avoiding unnecessary obscure packages. The agent should separate core dependencies required for the first version from optional or advanced dependencies useful for scaling, production deployment, background workers, monitoring, authentication, and advanced analytics.

The overall goal is to build something closer to a serious aviation operations analytics product than a simple spreadsheet visualizer. The tool should be fast, reliable, modular, testable, maintainable, and ready to evolve into a production-grade system.
