# Summary
Metastable failures due to Garbage Collection (GC). The mechanism is load-spike -> high queue length -> high GC behavior -> slowdown to requests processing -> high queue length. Please refer to Section 5.1 in the paper for more details.

# Example Usage

```bash
docker build -t exp .
./run 0 -1 1200 0 256m
./analyze.py
./plot.py
```

The output plot is ./measurement_plots.png

## Reference system set up
AWS EC2 m5.large

# Example Results
TBA

