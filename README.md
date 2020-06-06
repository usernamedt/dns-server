Daniil Zakhlystov

**Python DNS server**

Usage: python main.py


By default, listening on localhost:53 

By default, cache is saved in /cache folder

Default settings can be overriden by placing custom config.json in the root folder


**Default options**
```javascript
{
  "server_timeout": 100,
  "server_host": "",
  "server_port": 53,
  "forwarder_timeout": 100,
  "forwarder_host": "8.8.8.8",
  "forwarder_port": 53,
  "cache_dir": "cache",
  "log_file": "log.txt",
  "recv_buff_size": 512,
  "threads_count": 15
}
```
