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

def vcd_bin_to_signed_int(bin_str):
    """
    Convert a binary string from VCD to signed int.
    - If it is 32 bits and starts with '1', treat as two's complement.
    - Otherwise, treat as unsigned positive integer.
    """
    length = len(bin_str)

    # Negative number in 32-bit two's complement
    if length == 32 and bin_str[0] == '1':
        return int(bin_str, 2) - (1 << 32)
    
    # Positive number (minimal bits used)
    return int(bin_str, 2)

# Iterate over each signal
timestamps = []
ferrors = []
mclks_per_sample = []
dco = []
for symbol, signal_obj in vcd.data.items():
    # signal_obj.references is a list of signal names (hierarchical)
    full_name = signal_obj.references[0] if signal_obj.references else symbol
    print(f"\nSignal: {full_name}")

    # signal_obj.tv is the list of (timestamp, value) pairs
    for timestamp, value in signal_obj.tv:
        try:
            decimal_val = vcd_bin_to_signed_int(value)
        except:
            decimal_val = value
            assert False, f"Value is not binary, {value}"
        if full_name == "ferror_probe":           
            ferrors.append(decimal_val)
            timestamps.append(timestamp)
        elif full_name == "samp_rate_probe":
            #print(value)
            mclks_per_sample.append(decimal_val)
        elif full_name == "dco_probe":
            dco.append(decimal_val)


print(f" {len(timestamps)}")
ts_diff_iter = zip(timestamps[1:], timestamps)
tsd = [(t[0] - t[1])/(1e5) for t in list(ts_diff_iter)]
ts_diffs = [0]
ts_diffs.extend(tsd)
print(len(ts_diffs))
print(len(ferrors))

fig, axs = plt.subplots(3,1, sharex=True)
axs[0].plot(ferrors, label="ferror")
axs[0].set_ylabel("ferror")

axs[1].plot(dco, label="dco_setting")
axs[1].set_ylabel("dco_setting")
#axs[1].set_ylim(top=4.745e5, bottom=4.735e5)

axs[2].plot(mclks_per_sample, label="mclks_per_sample")
axs[2].set_ylabel("mclks_per_sample")

#axs[3].plot(ts_diffs, label="timestamp_diff (ms)")
#axs[3].set_ylabel("ts diff")


plt.show()

