# Interaction protocol

The client and server communicate with each other over a simple text protocol through TCP sockets. The text protocol has the main advantage - it is visual - you can view the dialogue between the client and server side without using additional tools.

To understand how the client side is implemented, let's look at the interaction between the client and server with specific examples.

Suppose you need to collect operating system metrics: cpu, memory usage, disk usage, network usage, etc. This may be needed to control server load.

Let us have two servers available: palm and eardrum. We will receive the CPU load on the server and send a metric called server_name.cpu

  ```
  client -> server: put palm.cpu 10.6 1501864247\n

  server -> client: ok\n\n

  client -> server: put eardrum.cpu 15.3 1501864259\n

  server -> client: ok\n\n
  ```
  
To send the metric to the server, you send a line of the form to the TCP connection:
<br>
**`put palm.cpu 10.6 1501864247\n`**
<br><br>
The keyword "put" means the send metric command. The following is the name of the metric itself, the value of the metric, and the unix timestamp. Thus, at time 1501864247, the value of the palm.cpu metric was 10.6. Finally, the command ends with the line break character \n.

In response to this put command, the server sends a notification that the metric was successfully saved as a string:
<br>
**`ok\n\n`**
<br><br>
Two line breaks in this case mean a marker of the end of the message from the server to the client.

# Commands

**put** - to save metrics on the server.
<br>

The `put` command format for sending metrics is a line of the form:
<br>
**`put <key> <value> <timestamp>\n`**
<br><br>
Successful response from server:
<br>
**`ok\n\n`**
<br><br>
Server error:
<br>
**`error\nwrong command\n\n`**
<br><br>

**get** - to get metrics.
<br>

The format of the `get` command to get metrics is a line of the form:
<br>
**`get <key>\n`**
<br><br>
The symbol * can be specified as a key, for this symbol all available metrics will be returned

Example of a successful response from the server:
<br>
**`ok\npalm.cpu 10.5 1501864247\neardrum.cpu 15.3 1501864259\n\n`**
<br><br>
If none of the metric does not satisfy the search criteria, then returns the answer:
<br>
**`ok\n\n`**
<br><br>

Note that each successful operation starts with "ok", and the server response always contains two \n characters.
