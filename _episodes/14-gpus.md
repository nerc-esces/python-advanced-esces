---
title: "GPUs"
teaching: 35
exercises: 25
questions:
- "What are GPUs and how do we access them?"
- "How can we use a GPU with Numba?"
- "How can we use a GPU in Pandas, Numpy or SciKit Learn?"
objectives:
- "Understand what the difference between a GPU and CPU is and the performance implications"
- "Apply Numba to use a GPU"
- "Understand that there are GPU enabled replacements for many popular Python libraries"
- "Recall that NVIDIA GPUs can be programmed in CUDA, but this is a very low level operation"
keypoints:
- "GPUs are Graphics Processing Units, they have large numbers of very simple processing cores and are suited to some parallel tasks like machine learning and array operations"
- "Many laptops and desktops won't have very powerful GPUs, instead we'll want to use HPC or Cloud systems to access a GPU."
- "Google's Colab provides free access to GPUs with a Jupyter notebooks interface."
- "Numba can use GPUs with minor modifications to the code."
- "NVIDIA have drop in replacements for Pandas, Numpy and SciKit learn that are GPU accelerated."
- "For a GPU to access data it must be copied into the GPU's memory. This can sometimes be a major bottleneck to GPU operations."
---

# What are GPUs and why should we use them?

- GPUs are Graphics Processing Units, they have large numbers (100s to 1000s) of very simple processing cores and are suited to some parallel tasks like machine learning and array operations.
- GPUs have their own RAM (memory) which their processing units can access very quickly. Any data you wish to work on must be copied from the computer (known as the "host")
to the GPU memory and any results must be copied back.
- GPUs used to have to be programmed using specialised languages/libraries such as Cuda (NVIDIA proprietary) or OpenCL (cross platform and open source).
- These are very low level systems that require the programmer to worry about things like moving data to/from GPU memory.
- Today many higher level libraries can use GPUs reducing our need to learn Cuda or OpenCL.
- For some classes of problems GPUs can give speed improvements that are 10s to hundreds of times faster than a CPU.

## How can you access a GPU if your PC doesn't have one

Many laptops and desktops won't have very powerful GPUs, instead we'll want to use HPC or Cloud systems to access a GPU. If you don't have access to any
services which offer one then you can use Google Colab (https://colab.research.google.com). This offers a Jupyter notebook interface with GPUs for free,
but the GPUs aren't very powerful. You can also pay for Google Colab and get access to faster GPUs.

### Orchid

JASMIN has a cluster called [Orchid](https://help.jasmin.ac.uk/docs/batch-computing/orchid-gpu-cluster/) which has 16 nodes with 72 NVIDIA A100 GPUs between them.
These are accessed via the Slurm batch scheduler. For more experimental work there are some A100 GPUs attached to the JASMIN notebook service. To use these
you must be granted access to Orchid and select the GPU option when connecting.

## Checking what GPUs are available to us

Systems with NVIDIA GPUs usually have a command called `nvidia-smi` installed, this will tell us some information about the GPUs that are attached to the system.
We can invoke this either from a Jupyter terminal or in a notebook with the `!` prefix.

~~~
nvidia-smi
~~~
{: .language-bash}

On the JASMIN notebooks service this will return something similar to this.

~~~
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.163.01             Driver Version: 550.163.01     CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA A100-SXM4-40GB          Off |   00000000:41:00.0 Off |                   On |
| N/A   34C    P0             88W /  400W |                  N/A   |     N/A      Default |
|                                         |                        |              Enabled |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA A100-SXM4-40GB          Off |   00000000:C1:00.0 Off |                   On |
| N/A   30C    P0             85W /  400W |                  N/A   |     N/A      Default |
|                                         |                        |              Enabled |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| MIG devices:                                                                            |
+------------------+----------------------------------+-----------+-----------------------+
| GPU  GI  CI  MIG |                     Memory-Usage |        Vol|      Shared           |
|      ID  ID  Dev |                       BAR1-Usage | SM     Unc| CE ENC DEC OFA JPG    |
|                  |                                  |        ECC|                       |
|==================+==================================+===========+=======================|
|  0    5   0   0  |              13MiB /  9856MiB    | 14      0 |  1   0    1    0    0 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+
|  1    5   0   0  |              13MiB /  9856MiB    | 14      0 |  1   0    1    0    0 |
|                  |                 0MiB / 16383MiB  |           |                       |
+------------------+----------------------------------+-----------+-----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
~~~
{: .output}


There are two keys parts to the output here. The top part show's we have two NVIDIA A100 cards with 40GB of GPU RAM each.
However we don't have exclusive use of these and they have been partitioned into smaller virtual GPUs known as MIGs (multi instance GPUs).
Each of these only has 16GB of GPU RAM and we're restriucted to just 10GB of that. This is still more than most desktop GPUs
and is sufficient for many tasks. Where we might need more memory we will have to move our code over to a regular Python script running on Orchid's batch system.

### Checking the GPUs available to use from Python
The numba library provides an interface to Cuda, which is NVIDIA's low level library for GPU operations. To get a list of GPUs
we can just call `cuda.detect()`.

~~~
from numba import cuda

cuda.detect()
~~~
{: .language-python}

> ## Check what GPUs you have access to
> Ensure that you have Cuda installed, this can installed by adding the cupy and cudatoolkit packages to your Conda/Mamba environment.
> Use Numba/Cuda to check what version of Cuda you have installed and what GPUs you have available.
>> ## Solution
>> ~~~
>> mamba install -p ~/.conda/envs/esces cupy cudatoolkit
>> ~~~
>> {: .language-bash}
>>
>> ~~~
>> from numba import cuda
>> print(cuda.__version__)
>> cuda.detect()
>> ~~~
>> {: .language-bash}
> {: .solution}
{: .challenge}


# Using GPUs

## GPU replacements for popular libraries
NVIDIA have drop in replacements for Pandas, Numpy and SciKit learn that are GPU accelerated. The replacemnt for NumPy and SciPy is known as CuPy.

Let's do a calculation using NumPy.

~~~
import numpy as np
a = np.random.random(100_000_000)
result_np = np.mean(a)
~~~
{: .language-python}


Now let's try and do the same thing with CuPy.
We'll use the same array we just created and copy it to the GPU, CuPy's `asarray` function
takes in a NumPy array and converts it to a CuPy array.

~~~
import cupy as cp
b = cp.asarray(a)
result_cp = cp.mean(b)
~~~
{: .language-python}

Let's time how long this is taking, for the NumPy code we can use `%time` or `%timeit`.
Unfortunately `%time` and `%timeit` don't work properly with GPUs as calling a GPU function returns immediately
and the code continues to run on the GPU. So we'll have to take a different approach to measuring the time taken and use CuPy's
built-in profiler which includes a function called `benchmark`.
`timeit` will automatically decide how many runs to do, but defaults to 7,
whereas `benchmark` needs to be told how many times to repeat with the `n_repeat` parameter.

~~~
from cupyx.profiler import benchmark
gpu_times = benchmark(cp.mean, (b,), n_repeat=7)
print(gpu_times)
~~~
{: .language-python}

To ensure we make a comparable run using `timeit` we can us it's `-n` and `-r` options
to control how many times it runs too.

~~~
%timeit -n 1 -r 7 result_np = np.mean(a)
~~~
{: .language-python}

On the JASMIN notebook service this gives the following output for CuPy:

~~~
mean                :    CPU:    54.157 us   +/-  3.656 (min:    50.439 / max:    61.728) us     GPU-0:  2158.267 us   +/-  3.639 (min:  2154.080 / max:  2165.024) us
~~~
{: .output}

and for NumPy:

~~~
66.2 ms ± 0 ns per loop (mean ± std. dev. of 1 run, 7 loops each)
~~~
{: .output}

So we have used about 2ms of GPU time (plus 54us of CPU time) to take the mean of 100,000,000 numbers on the GPU and 66ms on the CPU, so that's a 33 fold speedup!
Although we did not include the time spent copying the array to the GPU.

### Measuring the time taken to copy data to the GPU memory

As previously mentioned we can't use `%timeit` or `%time` to measure how long GPU operations take. We could use `benchmark` to do this, but we lose the return of the function
so this won't actually be usable (without a subsequent call). An alternative is to record the time of the system clock before and after the `asarray` call, but for this
to work we must synchronize with the GPU after the `asarray` call to ensure it's really finished.

~~~
import time
t0 = time.time()
b = cp.asarray(a)
cp.cuda.stream.get_current_stream().synchronize()
print(str((time.time() - t0) * 1_000_000) + "us")
~~~
{: .language-python}

On JAMSIN this is taking around 100,000us or 100ms. So we need to add this to the computation time which was just 2ms. As the CPU version only took 66ms it is actually
faster to do this calculation on the CPU. But this is a very simple example where we've only done one very simple operation on quite a large amount of data.

> ## Create random numbers with CuPy
> So far we have created random numbers using NumPy on the CPU and copied these to the GPU.
> A more efficient way to do this might be to make the random numbers of the GPU.
> Adjust the code to use CuPy to create 1,000,000 random numbers. Use the time library (or Cupyx's benchmark) to measure how long this takes.
> Is this quicker than making the random numbers on the CPU?
>> ## Solution
>> ~~~
>> import cupy as cp
>> import time
>>
>> t0 = time.time()
>> b = cp.random.random(100_000_000)
>> cp.cuda.stream.get_current_stream().synchronize()
>> print(str((time.time() - t0)*1_000) + "ms")
>>
>> #alternative using benchmark
>> from cupyx.profiler import benchmark
>> benchmark(cp.random.random, (100_000_000,), n_repeat=7)
>>
>> cp.mean(b)
>> ~~~
>> {: .language-python}
> {: .solution}
{: .challenge}


## Using GPUs with Numba

Numba code can be converted to run on a GPU using the `@cuda.jit` decorator, which is similar to the `@jit` decorator we saw earlier on. However there are a
few alterations that code might need first due to the way GPUs operate. Firstly the functions we use on the GPU can't return anything, we must instead have an extra
parameter which contains an array where we will save any results.

Here is an example that is similar to the function we used the JIT with earlier on with the CPU.

~~~
@cuda.jit
def sum_arr_example(a, r):
    total = 0.0
    for i in range(a.shape[0]):
        total += a[i,i]
    r[0] = total

a = cp.arange(10_000).reshape(100,100)
result_gpu = cuda.device_array((1,), np.float64)

sum_arr_example[1, 1](a, result_gpu)

result_host = result_gpu.copy_to_host()
print(result_host)
~~~
{: .language-python}

# Further Reading

This has only been a very quick introduction to GPUs, but hopefully it has shown you some of the potential they offer and some simple ways to use them.

 * [NVIDIA Profiling Guide](https://docs.nvidia.com/cuda/profiler-users-guide/) - NVIDIA have a very powerful visual profiling tool which graphically shows which operations are taking the most time.
 * [GPU Programming Carpentries Lesson](https://carpentries-incubator.github.io/lesson-gpu-programming/) - A Carpentries lesson on GPU programming including using CuPy and Numba.
 * [CuPy homepage](https://cupy.dev/)
 * [GPU Hardware Introduction](https://www.youtube.com/watch?v=FcS_kQOIykU) - A short video explaining the hardware architecture of a GPU.

{% include links.md %}
