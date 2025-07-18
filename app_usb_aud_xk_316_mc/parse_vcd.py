from vcdvcd import VCDVCD
import sys
import matplotlib.pyplot as plt

# Path to your VCD file
vcd = VCDVCD(sys.argv[1], store_tvs=True)

def twos_complement_to_signed(bin_str):
    """Convert binary string to signed integer (two's complement)."""
    n = len(bin_str)
    value = int(bin_str, 2)
    if bin_str[0] == '1':  # negative number
        value -= (1 << n)
    return value

# Iterate over each signal
timestamps = []
ferrors = []
for symbol, signal_obj in vcd.data.items():
    # signal_obj.references is a list of signal names (hierarchical)
    full_name = signal_obj.references[0] if signal_obj.references else symbol
    print(f"\nSignal: {full_name}")

    # signal_obj.tv is the list of (timestamp, value) pairs
    for timestamp, value in signal_obj.tv:
        try:
            decimal_val = twos_complement_to_signed(value)
        except:
            decimal_val = value
            assert False, f"Value is not binary, {value}"
        if full_name == "ferror_probe":
            ferrors.append(decimal_val)
            timestamps.append(timestamp)


print(f" {len(timestamps)}")
ts_diff_iter = zip(timestamps[1:], timestamps)
tsd = [(t[0] - t[1])/(1e5) for t in list(ts_diff_iter)]
ts_diffs = [0]
ts_diffs.extend(tsd)
print(len(ts_diffs))
print(len(ferrors))

fig, axs = plt.subplots(4,1, sharex=True)
axs[0].plot(ferrors, label="ferror")
axs[1].plot(ts_diffs, label="timestamp_diff (ms)")

#plt.plot(ts_diffs)
plt.show()

