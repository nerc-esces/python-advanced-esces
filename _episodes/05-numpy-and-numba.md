---
title: "Parallelisation with Numpy and Numba"
teaching: 50
exercises: 30
questions:
- "How can we measure the performance of our code?"
- "How can we improve performance by using Numpy array operations instead of loops?"
- "How can we improve performance by using Numba?"
objectives:
- "Apply profiling to measure the performance of code."
- "Understand the benefits of using Numpy array operations instead of loops."
- "Remember that single instruction, multiple data instrcutions can speed up certain operations that have been optimised for their use."
- "Understand that Numba is using Just-in-time compilation and vectorisation extensions."
- "Understand when to use ufuncs to write functions that are compatible with Numba."
keypoints:
- "We can measure how long a Jupyter cell takes to run with %time or %timeit magics."
- "We can use a profiler to measure how long each line of code in a function takes."
- "We should measure performance before attemping to optimise code and target our optimisations at the things which take longest."
- "Numpy can perform operations to whole arrays, this will perform faster than using for loops."
- "Numba can replace some Numpy operations with just in time compilation that is even faster."
- "One way numba achieves higher performance is to use vectorisation extensions of some CPUs that process multiple pieces of data in one instruction."
- "Numba ufuncs let us write arbitary functions for Numba to use. It's Just In Time compiler can still speed these up."
---

This episode is based in material from Ed Bennett's [Performant Numpy lesson](https://github.com/edbennett/performant-numpy)

# Measuring Code Performance

There are several ways to measure the performance of your code.

## Timeit

We can get a reasonable picture of the performance of individual functions and code snippets
by using the `timeit` module. `timeit` will run the code multiple times and take an average runtime.

In Jupyter, `timeit` is provided by line and cell magics. A magic is some special extra helper features added to Python. 

The line magic:

~~~
%timeit result = some_function(argument1, argument2)
~~~
{: .language-python}


will report the time taken to perform the operation on the same line
as the `%timeit` magic. Meanwhile, the cell magic
~~~
%%timeit

intermediate_data = some_function(argument1, argument2)
final_result = some_other_function(intermediate_data, argument3)
~~~
{: .language-python}

will measure and report timing for the entire cell.

Since timings are rarely perfectly reproducible, `timeit` runs the
command multiple times, calculates an average timing per iteration,
and then repeats to get a best-of-*N* measurement. The longer the
function takes, the smaller the relative uncertainty is deemed to be,
and so the fewer repeats are performed. `timeit` will tell you how
many times it ran the function, in addition to the timings.

You can also use `timeit` at the command-line; for example,

~~~
$ python -m timeit --setup='import numpy; x = numpy.arange(1000)' 'x ** 2'
~~~
{: .language-bash}

Notice the `--setup` argument, since you don't usually want to time
how long it takes to import a library, only the operations that you're
going to be doing a lot.

## Time
There is another magic we can use that is simply called `time`. This works very similarly to `timeit` but will only run the code once instead of multiple times.

## Profiling

You can also explore profiling to measure the performance of our Python code. Profiling provides detailed information about how much time is spent on each function, which can help us identify bottlenecks and optimize our code.

In Python, we can use the `cProfile` module to profile our code. Let's
see how we can do this by creating two functions:

~~~
import numpy as np

# A slow function
def my_slow_function():
  data = np.arange(1000000)
  total = 0
  for i in data:
      total += i
  return total

# A fast function using numpy
def my_fast_function():
  return np.sum(np.arange(1000000))
~~~
{: .language-python}

Now run each function using the cProfile command:

~~~
import cProfile
cProfile.run("my_slow_function()")
cProfile.run("my_fast_function()")
~~~
{: .language-python}

This will output detailed profiling information for both functions.
You can use this information to analyze the performance of your code
and optimize it as needed.

> Do you know why the fast function is faster than the slow function?

# Numpy whole array operations

Numpy whole array operations refer to performing operations on entire arrays at once, rather than looping through individual elements. 
This approach leverages the optimized C and Fortran implementations underlying NumPy, leading to significantly faster computations compared to traditional Python loops.

Let's illustrate this with an example:

~~~
import numpy as np
import cProfile

# Traditional loop-based operation
def traditional_multiply(arr):
    result = np.empty_like(arr)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            result[i, j] = arr[i, j] * 2
    return result

# Numpy whole array operation
def numpy_multiply(arr):
    return arr * 2

# Example array
arr = np.random.rand(1000, 1000)
~~~
{: .language-python}

Now calculate the time comparison and the profile performance of the code

~~~
# Time comparison
%timeit traditional_multiply(arr)
%timeit numpy_multiply(arr)

# Profile numpy_multiply
print("Profiling traditional_multiply:")
cProfile.run("traditional_multiply(arr)")
print("\nProfiling numpy_multiply:")
cProfile.run("numpy_multiply(arr)")
~~~
{: .language-python}

In this example, `traditional_multiply` uses nested loops to multiply each element of the array by 2, while `numpy_multiply` performs the same operation using a single NumPy 
operation. When comparing the execution times using `%timeit`, you'll likely observe that `numpy_multiply` is significantly faster.

> The reason why the Numpy operation is faster than the traditional loop-based approach is because:
> 1. **Vectorization**: Numpy operations are vectorized, meaning they are applied element-wise to the entire array at once. This allows for efficient parallelization and takes advantage of optimized low-level implementations.
> 2. **Avoiding Python overhead**: Traditional loops in Python incur significant overhead due to Python's dynamic typing and interpretation. Numpy operations are implemented in C, bypassing much of this overhead.
> 3. **Optimized algorithms**: Numpy operations often use highly optimized algorithms and data structures, further enhancing performance.

# Numba

## What is Numba and how does it work?

We know that due to various design decisions in Python, programs written
using pure Python operations are slow compared to equivalent code written
in a compiled language. We have seen that Numpy provides a lot of
operations written in compiled languages that we can use to escape from
the performance overhead of pure Python. However, sometimes we do still
need to write our own routines from scratch. This is where Numba comes in.
Numba provides a *just-in-time compiler*. If you have used languages like
Java, you may be familiar with this. While Python can't easily be compiled
in the way languages like C and Fortran are, due to its flexible type
system, what we can do is compile a function for a given data type once
we know what type it can be given. Subsequent calls to the same function
with the same type make use of the already-compiled machine code that was
generated the first time. This adds significant overhead to the first
run of a function since the compilation takes longer than the less
optimised compilation that Python does when it runs a function; however,
subsequent calls to that function are generally significantly faster.
If another type is supplied later, then it can be compiled a second time.

Numba makes extensive use of a piece of Python syntax known as
"decorators". Decorators are labels or tags placed before function
definitions and prefixed with `@`; they modify function definitions,
giving them some extra behaviour or properties.

## Universal functions in Numba

(Adapted from the
[Scipy 2017 Numba tutorial](https://github.com/gforsyth/numba_tutorial_scipy2017/blob/master/notebooks/07.Make.your.own.ufuncs.ipynb))

Recall how Numpy gives us many operations that operate on whole arrays,
element-wise. These are known as "universal functions", or "ufuncs"
for short. Numpy has the facility for you to define your own ufuncs,
but it is quite difficult to use. Numba makes this much easier with
the `@vectorize` decorator. With this, you are able to write a
function that takes individual elements, and have it extend to operate
element-wise across entire arrays.

For example, consider the (relatively arbitrary) trigonometric
function:

~~~
import math

def trig(a, b):
    return math.sin(a ** 2) * math.exp(b)
~~~
{: .language-python}

If we try calling this function on a Numpy array, we correctly get an
error, since the `math` library doesn't know about Numpy arrays, only
single numbers.

~~~
%env OMP_NUM_THREADS=1
import numpy as np

a = np.ones((5, 5))
b = np.ones((5, 5))

trig(a, b)
~~~
{: .language-python}

~~~
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-1-0d551152e5fe> in <module>
      9 b = np.ones((5, 5))
    10 
---> 11 trig(a, b)

<ipython-input-1-0d551152e5fe> in trig(a, b)
      2 
      3 def trig(a, b):
----> 4     return math.sin(a ** 2) * math.exp(b)
      5 
      6 import numpy as np

TypeError: only size-1 arrays can be converted to Python scalars
~~~
{: .output}

However, if we use Numba to "vectorize" this function, then it becomes
a ufunc, and will work on Numpy arrays!

~~~
from numba import vectorize

@vectorize
def trig(a, b):
    return math.sin(a ** 2) * math.exp(b)

a = np.ones((5, 5))
b = np.ones((5, 5))

trig(a, b)
~~~
{: .language-python}


How does the performance compare with using the equivalent Numpy
whole-array operation?

~~~
def numpy_trig(a, b):
    return np.sin(a ** 2) * np.exp(b)
  

a = np.random.random((1000, 1000))
b = np.random.random((1000, 1000))

%timeit numpy_trig(a, b)
%timeit trig(a, b)
~~~
{: .language-python}

~~~
Numpy: 19 ms ± 168 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
Numba: 25.4 ms ± 1.06 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
~~~
{: .output}

So Numba isn't quite competitive with Numpy in this case. But Numba
still has more to give here: notice that we've forced Numpy to only
use a single core. What happens if we use four cores with Numpy?
We'll need to restart the kernel again to get Numpy to pick up the
changed value of `OMP_NUM_THREADS`.

~~~
%env OMP_NUM_THREADS=4
import numpy as np
import math
from numba import vectorize

@vectorize()
def trig(a, b):
    return math.sin(a ** 2) * math.exp(b)

def numpy_trig(a, b):
    return np.sin(a ** 2) * np.exp(b)

a = np.random.random((1000, 1000))
b = np.random.random((1000, 1000))

%timeit numpy_trig(a, b)
%timeit trig(a, b)
~~~
{: .language-bash}

~~~
Numpy: 7.84 ms ± 54.7 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
Numba: 24.9 ms ± 134 µs per loop (mean ± std. dev. of 7 runs, 1 loop each)
~~~
{: .output}

Numpy has parallelised this, but isn't incredibly efficient - it's used $$7.84 \times 4 = 31.4$$ core-milliseconds rather than 19. But
Numba can also parallelise. If we alter our call to `vectorize`, we
can pass the keyword argument `target='parallel'`. However, when we do
this, we also need to tell Numba in advance what kind of variables it
will work on&mdash;it can't work this out and also be able to
parallelise. So our `vectorize` decorator becomes:

~~~
@vectorize('float64(float64, float64)', target='parallel')
~~~
{: .language-python}

This tells Numba that the function accepts two variables of type
`float64` (8-byte floats, also known as "double precision"), and
returns a single `float64`. We also need to tell Numba to use as many
threads as we did Numpy; we control this via the `NUMBA_NUM_THREADS`
variable. Restarting the kernel and re-running the timing gives:

~~~
%env NUMBA_NUM_THREADS=4

import numpy as np
import math
from numba import vectorize

@vectorize('float64(float64, float64)', target='parallel')
def trig(a, b):
    return math.sin(a ** 2) * math.exp(b)

a = np.random.random((1000, 1000))
b = np.random.random((1000, 1000))

%timeit trig(a, b)
~~~
{: .language-bash}

~~~
12.3 ms ± 162 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
~~~
{: .output}

In this case this is even less efficient than Numpy's. However, comparing
this against the parallel version running on a single thread tells a different
story. Retrying the above with `NUMBA_NUM_THREADS=1` gives

~~~
47.8 ms ± 962 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
~~~
{: .output}

So in fact, the parallelisation is almost perfectly efficient, just the
parallel implementation is slower than the serial one. If we had more
processor cores available, then using this parallel implementation would
make more sense than Numpy. (If you are running your code on a High-
Performance Computing (HPC) system then this is important!)

> ## Creating your own ufunc
>
> Try creating a ufunc to calculate the discriminant of a quadratic
> equation, $\Delta = b^2 - 4ac$. (For now, make it a serial
> function by just using the @vectorize decorator *WITHOUT* the parallel target). 
> 
> Use the existing 1000x1000 arrays `a` and `b` as the input. Make `c` a single integer value. 
>
> Compare the timings with using Numpy whole-array operations in
> serial. Do you see the results you might expect?
>
> > ## Solution
> >
> > ~~~
> > # recalcuate a and b, just in case they were lost
> > a = np.random.random((1000, 1000))
> > b = np.random.random((1000, 1000))
> > @vectorize
> > def discriminant(a, b, c):
> >     return b**2 - 4 * a * c
> > c = 4
> > %timeit discriminant(a, b, c)
> > # numpy version for comparison
> > %timeit b ** 2 - 4 * a * c
> > ~~~
> > {: .language-python}
> >
> > Timing this gives me 3.73 microseconds, whereas the `b ** 2 - 4 *
> > a * c` Numpy expression takes 13.4 microseconds&mdash;almost four
> > times as long. This is because each of the Numpy arithmetic
> > operations needs to create a temporary array to hold the results,
> > whereas the Numba ufunc can create a single final array, and
> > use smaller intermediary values.
> {: .solution}
{: .challenge}

## Numba Jit decorator

Numba can also speed up things that don't work element-wise at all.
Numba provides the @jit decorator to compile functions and can parallelize loops using prange for NumPy arrays.

~~~
%env NUMBA_NUM_THREADS=4
from numba import jit
import numpy as np

@jit(nopython=True, parallel=True)
def a_plus_tr_tanh_a(a):
    trace = 0.0
    for i in range(a.shape[0]):
        trace += np.tanh(a[i, i])
    return a + trace
~~~
{: .language-python}

Some things to note about this function:

* The decorator `@jit(nopython=True)` tells Numba to compile this code
  in "no Python" mode (i.e. if it can't work out how to compile this
  function entirely to machine code, it should give an error rather than
  partially using Python)
* The decorator `@jit(parallel=True)` tells Numba to compile to run with multiple threads.
  Like previously, we need to control this threads count at run-time using the
  `NUMBA_NUM_THREADS` environment variable.
* The function accepts a Numpy array; Numba performs better with Numpy
  arrays than with e.g. Pandas dataframes or objects from  other libraries.
* The array is operated on with Numpy functions (`np.tanh`) and broadcast
  operations (`+`), rather than arbitrary library functions that Numba
  doesn't know about.
* The function contains a plain Python loop; Numba knows how to turn
  this into an efficient compiled loop.

To time this, it's important to run the function once during the
setup step, so that it gets compiled before we start trying to time
its run time.

~~~
a = np.arange(10_000).reshape((100, 100))
a_plus_tr_tanh_a(a)
%timeit a_plus_tr_tanh_a(a)
~~~
{: .language-python}

~~~
20.9 µs ± 242 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
~~~
{: .output}


> ## Compare Performance
>
> Try to run the same code without any Numba Jit or parallelisation.
> Try decreasing and increasing the matrix size and compare the results.
>
> Which one has the best results?
>
> > ## Solution
> > You might find a smaller matrix shows little or no difference in execution times, but a larger one sees the parallelised/JIT version go faster. 
> > For small computations the overhead of parallelization can outweigh the benefits. It's essential to profile your code and experiment with different approaches to find the most efficient solution for your specific use case.
> {: .solution}
{: .challenge}

{% include links.md %}
