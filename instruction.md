Create `/app/report.json` from the Apache-style access log at `/app/access.log`.

Each non-empty line in `/app/access.log` represents one request. The client IP address is the first whitespace-separated field. The request path is the path between the HTTP method and HTTP version inside the quoted request, for example:

`"GET /index.html HTTP/1.1"`

Your `/app/report.json` must satisfy all of the following success criteria:

1. It is a valid JSON object with exactly these fields:
   - `total_requests`: an integer
   - `unique_ips`: an integer
   - `top_path`: a string

2. `total_requests` equals the number of non-empty entries in `/app/access.log`.

3. `unique_ips` equals the number of distinct client IP addresses across the non-empty entries.

4. `top_path` equals the request path that occurs most frequently. If multiple paths are tied for most frequent, use the lexicographically smallest path.

Write the completed report to exactly:

`/app/report.json`
