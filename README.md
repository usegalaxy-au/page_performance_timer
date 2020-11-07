# page_performance_timer

A simple utility container to time page load performance and output influxdb stats.

### Usage:

```
export GALAXY_SERVER=https://usegalaxy.org.au
export GALAXY_USERNAME="user"
export GALAXY_PASSWORD="pass"
docker run -e GALAXY_SERVER -e GALAXY_USERNAME -e GALAXY_PASSWORD -it usegalaxyau/page_perf_timer:latest
```

### Output:

```
user_flow_performance,server=https://usegalaxy.org.au,action=login_page_load time_taken=4.472899913787842
user_flow_performance,server=https://usegalaxy.org.au,action=home_page_load time_taken=5.478079080581665
user_flow_performance,server=https://usegalaxy.org.au,action=tool_search_load time_taken=1.4936168193817139
user_flow_performance,server=https://usegalaxy.org.au,action=tool_form_load time_taken=0.9323928356170654
```

### Help
```
docker run -it usegalaxyau/page_perf_timer:latest --help
usage: page_perf_timer.py [-h] [-s SERVER] [-u USERNAME] [-p PASSWORD]

Measure time taken for a typical user flow from login to tool execution in Galaxy.

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Galaxy server url
  -u USERNAME, --username USERNAME
                        Galaxy username to use (or set GALAXY_USERNAME env var)
  -p PASSWORD, --password PASSWORD
                        Password to use (or set GALAXY_PASSWORD env var)
```
