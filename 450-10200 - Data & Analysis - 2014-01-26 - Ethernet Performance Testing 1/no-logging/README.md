
Initial testing showed that logging to disk (in our case an SD card on the raspberry pi) was a bottleneck.

A sequence of screenshots was taken in order to get some data with logging turned off. Starting with 8 nodes (___n___ = 8), the basic method was:

 * take screenshot '___n___a.png'
 * increase all speeds until we just begin to see some dropped nodes
 * take screenshot '___n___b.png'
 * remove one node from the network
 * repeat

Our data covers the cases of 4-8 nodes because below 4, we encountered the maximum limit at which individual nodes are capable of sending data.

CSV files were transcribed with corresponding file names.
